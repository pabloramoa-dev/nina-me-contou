"""Tratamento de áudio da Nina com Spotify Pedalboard.

- masterizar_voz(): cadeia de estúdio para a voz da Nina (de-esser, tira o som de
  caixa e o anasalado, dicção clara, compressão suave, ambiência curtinha de
  varanda e limitador suave, sem estourar picos). Mantém WAV mono
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

# Equalização da voz da Nina (feminina). Mesma curva nas duas cadeias:
#   90 Hz   passa-altas: tira ronco e estalo de grave
#   190 Hz  +1,0 dB: um pouco de calor, voz menos fina
#   480 Hz  -2,0 dB: tira o som "de caixa"
#   1 kHz   -1,5 dB: tira o tom anasalado
#   3,4 kHz +2,0 dB (largo): dicção clara no alto-falante do celular
#   7 kHz   +2,0 dB (prateleira): um pouco de ar, sem chiar (o de-esser segura o "s")
#   12 kHz  passa-baixas: corta o resíduo metálico do TTS
# Depois: compressão suave e ambiência curtinha de varanda.
MASTER_FFMPEG = ("highpass=f=90,equalizer=f=190:t=q:w=0.9:g=1.0,"
                 "equalizer=f=480:t=q:w=1.1:g=-2.0,equalizer=f=1000:t=q:w=1.2:g=-1.5,"
                 "equalizer=f=3400:t=q:w=0.7:g=2.0,highshelf=f=7000:g=2.0,lowpass=f=12000,"
                 "acompressor=threshold=-21dB:ratio=2.2:attack=10:release=150,"
                 "aecho=1.0:1.0:23|41:0.035|0.018")
RMS_VOZ = -13.0                      # nível da fala (dB RMS) antes do limitador suave
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
        pb.HighpassFilter(cutoff_frequency_hz=90),
        pb.PeakFilter(cutoff_frequency_hz=190, gain_db=1.0, q=0.9),      # calor
        pb.PeakFilter(cutoff_frequency_hz=480, gain_db=-2.0, q=1.1),     # tira o som "de caixa"
        pb.PeakFilter(cutoff_frequency_hz=1000, gain_db=-1.5, q=1.2),    # tira o anasalado
        pb.PeakFilter(cutoff_frequency_hz=3400, gain_db=2.0, q=0.7),     # dicção
        pb.HighShelfFilter(cutoff_frequency_hz=7000, gain_db=2.0, q=0.7),  # ar
        pb.LowpassFilter(cutoff_frequency_hz=12000),                     # resíduo metálico do TTS
        pb.Compressor(threshold_db=-21, ratio=2.2, attack_ms=10, release_ms=150),
        pb.Reverb(room_size=0.14, damping=0.75, wet_level=0.035, dry_level=1.0, width=0.0),
    ])


def deesser(x, sr, lo=5800.0, hi=11500.0, limiar=0.55, max_db=6.0):
    """De-esser: abaixa só a faixa do chiado, e só nos instantes em que o "s" domina.

    Compara a energia da faixa 6–11 kHz com a da voz inteira; por ser relativo,
    funciona igual em qualquer volume. Fase linear (FFT) e mesma duração."""
    n = len(x)
    if n < sr // 10:
        return x
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / sr)
    sobe = np.clip((f - lo * 0.85) / (lo * 0.15), 0, 1)
    desce = np.clip((hi * 1.15 - f) / (hi * 0.15), 0, 1)
    faixa = np.fft.irfft(X * (0.5 - 0.5 * np.cos(np.pi * sobe)) * (0.5 - 0.5 * np.cos(np.pi * desce)), n)

    def rms(s, ms):
        k = max(1, int(sr * ms / 1000))
        c = np.cumsum(np.concatenate([[0.0], s.astype(np.float64) ** 2]))
        m = (c[k:] - c[:-k]) / k
        return np.sqrt(np.pad(m, (k // 2, n - len(m) - k // 2), mode="edge"))

    ef, et = rms(faixa, 8), rms(x, 8) + 1e-6
    razao = ef / et
    g = np.where(razao > limiar, (limiar / np.maximum(razao, 1e-6)) ** 1.2, 1.0)
    g = np.maximum(g, 10 ** (-max_db / 20))
    k = max(1, int(sr * 0.006))                     # suaviza o ganho (6 ms)
    g = np.convolve(np.pad(g, (k // 2, k - 1 - k // 2), mode="edge"), np.ones(k) / k, mode="valid")
    return x - faixa * (1 - g)


def masterizar_voz(entrada, saida) -> str:
    audio, sr = sf.read(str(entrada), dtype="float32", always_2d=True)
    mono = deesser(audio.mean(axis=1).astype(np.float64), sr)
    if pb is None:
        with tempfile.TemporaryDirectory() as tmp:
            limpo, bruto = os.path.join(tmp, "d.wav"), os.path.join(tmp, "m.wav")
            sf.write(limpo, mono, sr, subtype="FLOAT")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", limpo, "-ac", "1",
                            "-af", MASTER_FFMPEG, "-ar", str(sr), "-c:a", "pcm_f32le", bruto], check=True)
            out, _ = sf.read(bruto, dtype="float64")
        motor = "ffmpeg"
    else:
        out = cadeia_voz()(mono.astype(np.float32)[np.newaxis, :], sr)[0].astype(np.float64)
        motor = "pedalboard"
    out = np.pad(out, (0, max(0, len(mono) - len(out))))[: len(mono)]       # mesma duração
    out = _nivelar(out, RMS_VOZ, TETO_VOZ)
    sf.write(str(saida), out, sr, subtype="PCM_16")
    return motor


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
