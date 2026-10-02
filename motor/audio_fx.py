"""Tratamento de áudio da Nina com Spotify Pedalboard.

- masterizar_voz(): cadeia de estúdio para a Thalita (limpa graves, dá presença,
  compressão suave, ambiência curtinha de varanda e limitador). Mantém WAV mono
  44,1 kHz 16-bit e a MESMA duração da narração bruta, então segs.json e o lip
  sync continuam válidos.
- tratar_trilha() / ducking(): deixa a trilha abafada e abaixa sozinha quando a
  Nina fala.
- finalizar(): limitador de saída da mixagem.

Se o pedalboard não estiver instalado, cai no filtro ffmpeg antigo (mesmo som
de antes), para a produção nunca parar por causa disso.
"""
from __future__ import annotations

import subprocess

import numpy as np
import soundfile as sf

MASTER_FFMPEG = ("highpass=f=90,equalizer=f=3000:width_type=o:width=1.5:g=3,"
                 "acompressor=threshold=-17dB:ratio=2.6:attack=6:release=140,volume=1.12")

try:
    import pedalboard as pb
except Exception:  # pragma: no cover - ambiente sem pedalboard
    pb = None


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
    if pb is None:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(entrada),
                        "-af", MASTER_FFMPEG, str(saida)], check=True)
        return "ffmpeg"
    audio, sr = sf.read(str(entrada), dtype="float32", always_2d=True)
    mono = audio.mean(axis=1)
    out = cadeia_voz()(mono[np.newaxis, :], sr)[0][: len(mono)]
    out = np.clip(out, -1.0, 1.0)
    sf.write(str(saida), out, sr, subtype="PCM_16")
    return "pedalboard"


def tratar_trilha(bed: np.ndarray, sr: int) -> np.ndarray:
    if pb is None:
        return bed
    fx = pb.Pedalboard([
        pb.LowpassFilter(cutoff_frequency_hz=2600),
        pb.Chorus(rate_hz=0.25, depth=0.15, mix=0.25),
        pb.Reverb(room_size=0.55, damping=0.5, wet_level=0.30, dry_level=0.8, width=0.0),
    ])
    return fx(bed.astype(np.float32)[np.newaxis, :], sr)[0][: len(bed)]


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
        return mix * min(1.0, 0.89 / pico)
    lim = pb.Pedalboard([pb.Limiter(threshold_db=-1.5, release_ms=60)])
    return np.clip(lim(mix.astype(np.float32)[np.newaxis, :], sr)[0], -0.99, 0.99)
