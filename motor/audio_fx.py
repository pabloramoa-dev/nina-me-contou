"""Tratamento de áudio da Nina com Spotify Pedalboard.

- masterizar_voz(): cadeia de estúdio para a Thalita (limpa graves, dá presença,
  compressão suave, ambiência curtinha de varanda e limitador). Mantém WAV mono
  44,1 kHz 16-bit e a MESMA duração da narração bruta, então segs.json e o lip
  sync continuam válidos.
- tratar_trilha() / ducking(): deixa a trilha abafada e abaixa sozinha quando a
  Nina fala.
- finalizar(): limitador de saída da mixagem.

Se o pedalboard não funcionar na máquina (falta a lib, ou o binário dela
derruba o Python com "Illegal instruction" em alguns runners do GitHub), tudo
cai numa cadeia equivalente em ffmpeg + numpy. O teste do pedalboard roda num
processo separado, então um travamento dele nunca derruba a produção.
NINA_PEDALBOARD=0 força a cadeia ffmpeg/numpy.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile

import numpy as np
import soundfile as sf

# Mesma cadeia da voz, em ffmpeg (fallback)
MASTER_FFMPEG = ("highpass=f=85,lowshelf=f=220:g=-1.5,equalizer=f=3200:t=q:w=0.8:g=2.5,"
                 "highshelf=f=9500:g=1.5,"
                 "acompressor=threshold=-19dB:ratio=2.8:attack=5:release=120,"
                 "aecho=1.0:1.0:23|41:0.045|0.025,volume=2dB")
TETO_VOZ = 10 ** (-1.5 / 20)
TETO_MIX = 10 ** (-1.5 / 20)

_TESTE = ("import numpy as np, pedalboard as p;"
          "p.Pedalboard([p.Compressor(), p.Reverb(), p.Limiter()])"
          "(np.zeros((1, 4410), dtype=np.float32), 44100)")


def _pedalboard_seguro():
    if os.environ.get("NINA_PEDALBOARD", "1") == "0":
        return None
    try:
        ok = subprocess.run([sys.executable, "-c", _TESTE], capture_output=True,
                            timeout=120).returncode == 0
    except Exception:
        ok = False
    if not ok:
        print("audio_fx: pedalboard indisponível nesta máquina — usando ffmpeg/numpy", flush=True)
        return None
    import pedalboard
    return pedalboard


pb = _pedalboard_seguro()


def disponivel() -> bool:
    return pb is not None


def cadeia_voz():
    return pb.Pedalboard([
        pb.HighpassFilter(cutoff_frequency_hz=85),
        pb.LowShelfFilter(cutoff_frequency_hz=220, gain_db=-1.5, q=0.7),   # tira o "embolado"
        pb.PeakFilter(cutoff_frequency_hz=3200, gain_db=2.5, q=0.8),       # presença
        pb.HighShelfFilter(cutoff_frequency_hz=9500, gain_db=1.5, q=0.7),  # brilho
        pb.Compressor(threshold_db=-19, ratio=2.8, attack_ms=5, release_ms=120),
        pb.Reverb(room_size=0.14, damping=0.7, wet_level=0.045, dry_level=1.0, width=0.0),
        pb.Gain(gain_db=2.0),
        pb.Limiter(threshold_db=-1.5, release_ms=80),
    ])


def masterizar_voz(entrada, saida) -> str:
    audio, sr = sf.read(str(entrada), dtype="float32", always_2d=True)
    mono = audio.mean(axis=1)
    if pb is None:
        with tempfile.TemporaryDirectory() as tmp:
            bruto = os.path.join(tmp, "m.wav")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(entrada), "-ac", "1",
                            "-af", MASTER_FFMPEG, "-ar", str(sr), "-c:a", "pcm_f32le", bruto], check=True)
            out, _ = sf.read(bruto, dtype="float64")
        out = np.pad(out, (0, max(0, len(mono) - len(out))))[: len(mono)]   # mesma duração
        out = _nivelar(out, -14.0, TETO_VOZ)
        sf.write(str(saida), out, sr, subtype="PCM_16")
        return "ffmpeg"
    out = cadeia_voz()(mono[np.newaxis, :], sr)[0][: len(mono)]
    out = np.clip(out, -1.0, 1.0)
    sf.write(str(saida), out, sr, subtype="PCM_16")
    return "pedalboard"


def _nivelar(x, rms_db, teto):
    """Leva a fala ao RMS alvo e segura os picos com limitador suave (tanh)."""
    fala = x[np.abs(x) > 0.01]
    rms = np.sqrt(np.mean(fala ** 2)) if len(fala) else 0.0
    if rms > 0:
        x = x * (10 ** (rms_db / 20) / rms)
    joelho = 0.7 * teto
    a = np.abs(x)
    acima = a > joelho
    a[acima] = joelho + (teto - joelho) * np.tanh((a[acima] - joelho) / (teto - joelho))
    return np.sign(x) * a


def tratar_trilha(bed: np.ndarray, sr: int) -> np.ndarray:
    if pb is None:
        return _trilha_numpy(bed, sr)
    fx = pb.Pedalboard([
        pb.LowpassFilter(cutoff_frequency_hz=2600),
        pb.Chorus(rate_hz=0.25, depth=0.15, mix=0.25),
        pb.Reverb(room_size=0.55, damping=0.5, wet_level=0.30, dry_level=0.8, width=0.0),
    ])
    return fx(bed.astype(np.float32)[np.newaxis, :], sr)[0][: len(bed)]


def _trilha_numpy(bed, sr):
    """Passa-baixa 2,6 kHz + reverberação curta por convolução (FFT)."""
    n = len(bed)
    X = np.fft.rfft(bed)
    f = np.fft.rfftfreq(n, 1 / sr)
    X *= 1 / np.sqrt(1 + (f / 2600) ** 4)
    seco = np.fft.irfft(X, n)
    t = np.arange(int(1.6 * sr)) / sr
    ir = np.random.default_rng(17).normal(size=len(t)) * np.exp(-t * 4.0)
    ir /= np.sqrt(np.sum(ir ** 2)) or 1.0
    m = 1 << int(np.ceil(np.log2(n + len(ir))))
    molhado = np.fft.irfft(np.fft.rfft(seco, m) * np.fft.rfft(ir, m), m)[:n]
    return 0.8 * seco + 0.30 * molhado


def ducking(voz: np.ndarray, sr: int, profundidade: float = 0.65,
            ataque: float = 0.04, soltura: float = 0.45) -> np.ndarray:
    """Ganho 0..1 para a trilha: cai `profundidade` enquanto há voz."""
    hop = max(1, sr // 100)                       # envelope a cada 10 ms
    n = len(voz) // hop + 1
    pad = np.zeros(n * hop)
    pad[: len(voz)] = np.abs(voz)
    env = pad.reshape(n, hop).max(axis=1)
    ativo = (env > 0.02).astype(float)
    a_up = 1 - np.exp(-0.01 / ataque)
    a_dn = 1 - np.exp(-0.01 / soltura)
    sm = np.zeros(n)
    v = 0.0
    for i, x in enumerate(ativo):
        v += (a_up if x > v else a_dn) * (x - v)
        sm[i] = v
    ganho = 1 - profundidade * sm
    return np.interp(np.arange(len(voz)), np.arange(n) * hop, ganho)


def finalizar(mix: np.ndarray, sr: int) -> np.ndarray:
    if pb is None:
        pico = np.max(np.abs(mix)) or 1.0
        return mix * min(1.0, TETO_MIX / pico)
    lim = pb.Pedalboard([pb.Limiter(threshold_db=-1.5, release_ms=60)])
    return np.clip(lim(mix.astype(np.float32)[np.newaxis, :], sr)[0], -0.99, 0.99)
