#!/usr/bin/env python3
"""Lip sync simples por amplitude (RMS) — 3 estados: fechada / meia / aberta.
Mais simples que visemas Rhubarb, mas é o mesmo método que o pipeline real do
Ranzinza já usa na previsão do tempo. Gera uma lista de cues (start/end/estado)
que a cena em Manim consome com o mesmo padrão de anexar_lipsync do dvh_lip.
"""
import sys, json
import numpy as np
import soundfile as sf

def main():
    wav_path, out_json = sys.argv[1], sys.argv[2]
    fps = float(sys.argv[3]) if len(sys.argv) > 3 else 24.0

    audio, sr = sf.read(wav_path, always_2d=False)
    if audio.ndim > 1:
        audio = audio.mean(axis=1)

    win = max(1, int(sr / fps))
    n_frames = len(audio) // win
    rms = np.array([
        np.sqrt(np.mean(audio[i*win:(i+1)*win].astype(np.float64) ** 2) + 1e-12)
        for i in range(n_frames)
    ])
    pico = rms.max() or 1.0
    rms_norm = rms / pico

    def estado_de(v):
        if v < 0.12:
            return "fechada"
        elif v < 0.4:
            return "meia"
        return "aberta"

    estados = [estado_de(v) for v in rms_norm]

    # funde blocos curtos (<2 frames) com o vizinho anterior p/ evitar tremedeira
    for i in range(1, len(estados) - 1):
        if estados[i] != estados[i-1] and estados[i] != estados[i+1]:
            estados[i] = estados[i-1]

    # run-length encode em cues start/end (segundos)
    cues = []
    t0 = 0.0
    atual = estados[0] if estados else "fechada"
    for i in range(1, len(estados)):
        if estados[i] != atual:
            t1 = i / fps
            cues.append({"start": round(t0, 3), "end": round(t1, 3), "estado": atual})
            t0 = t1
            atual = estados[i]
    cues.append({"start": round(t0, 3), "end": round(len(estados) / fps, 3), "estado": atual})

    json.dump(cues, open(out_json, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"ok: {len(cues)} cues, {len(estados)/fps:.2f}s, fps={fps}")

if __name__ == "__main__":
    main()
