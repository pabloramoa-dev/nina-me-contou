#!/usr/bin/env python3
"""Gera a narração oficial da Nina com Microsoft Thalita Neural (pt-BR).

A voz canônica da Nina é pt-BR-ThalitaNeural em rate=-6%.
Cada linha do roteiro vira um segmento independente para preservar os limites
usados pela timeline, legendas e lip sync.

Uso:
  python motor/gerar_voz_thalita.py roteiro.txt --out narracao.wav \
      --seg-json segs.json --gap 0.25 --rate=-6%
"""

import argparse
import asyncio
import json
import os
import subprocess
import tempfile
import wave

import edge_tts

SR = 44100
VOICE = "pt-BR-ThalitaNeural"
RATE = "-6%"
TTS_ATTEMPTS = 6


def sh(cmd):
    subprocess.run(cmd, check=True)


def wav_pcm(path):
    with wave.open(path, "rb") as w:
        if w.getnchannels() != 1 or w.getsampwidth() != 2 or w.getframerate() != SR:
            raise RuntimeError(f"WAV inesperado: {path}")
        return w.readframes(w.getnframes()), w.getnframes()


async def sintetizar(texto: str, destino_mp3: str, voice: str, rate: str):
    """Sintetiza com novas conexões e espera progressiva em falhas transitórias."""
    ultimo_erro = None
    for tentativa in range(1, TTS_ATTEMPTS + 1):
        try:
            if os.path.exists(destino_mp3):
                os.remove(destino_mp3)
            await edge_tts.Communicate(texto, voice, rate=rate).save(destino_mp3)
            if not os.path.exists(destino_mp3) or os.path.getsize(destino_mp3) == 0:
                raise RuntimeError("Edge TTS retornou áudio vazio")
            return
        except Exception as exc:
            ultimo_erro = exc
            # 403 no websocket é bloqueio do serviço, não instabilidade de rede:
            # insistir seis vezes só atrasa o fallback local do pipeline.
            if getattr(exc, "status", None) == 403 or "403" in str(exc):
                print("[thalita] serviço respondeu 403; interrompendo Thalita para o pipeline aplicar a política de contingência.", flush=True)
                break
            if tentativa == TTS_ATTEMPTS:
                break
            espera = min(20, 3 * (2 ** (tentativa - 1)))
            print(
                f"[thalita] tentativa {tentativa}/{TTS_ATTEMPTS} falhou: "
                f"{type(exc).__name__}; nova tentativa em {espera}s",
                flush=True,
            )
            await asyncio.sleep(espera)
    raise RuntimeError(
        f"Thalita indisponível após {tentativa} tentativa(s)"
    ) from ultimo_erro


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("roteiro", help="txt: uma batida de narração por linha")
    ap.add_argument("--voice", default=VOICE)
    ap.add_argument("--rate", default=RATE)
    ap.add_argument("--gap", type=float, default=0.25, help="silêncio entre batidas (s)")
    ap.add_argument("--out", default="narracao.wav")
    ap.add_argument("--seg-json", default=None)
    a = ap.parse_args()

    linhas = [l.strip() for l in open(a.roteiro, encoding="utf-8") if l.strip()]
    gap_frames = max(0, int(round(a.gap * SR)))
    silencio = b"\x00\x00" * gap_frames
    partes = []
    segs = []
    t = 0.0

    with tempfile.TemporaryDirectory(prefix="nina-thalita-") as tmp:
        for i, txt in enumerate(linhas):
            mp3 = os.path.join(tmp, f"{i:03d}.mp3")
            wav = os.path.join(tmp, f"{i:03d}.wav")
            asyncio.run(sintetizar(txt, mp3, a.voice, a.rate))
            sh([
                "ffmpeg", "-y", "-loglevel", "error", "-i", mp3,
                "-ac", "1", "-ar", str(SR), "-c:a", "pcm_s16le", wav,
            ])
            pcm, frames = wav_pcm(wav)
            dur = frames / SR
            ini = t
            partes.append(pcm)
            partes.append(silencio)
            t += dur + a.gap
            segs.append({
                "i": i,
                "texto": txt,
                "ini": round(ini, 3),
                "fim_fala": round(ini + dur, 3),
                "fim": round(t, 3),
            })
            print(f"[thalita] linha {i}: {dur:.2f}s")

    with wave.open(a.out, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(b"".join(partes) if partes else b"\x00\x00")

    if a.seg_json:
        with open(a.seg_json, "w", encoding="utf-8") as f:
            json.dump(segs, f, ensure_ascii=False, indent=2)

    print(f"ok: {a.out} ({t:.1f}s, {len(linhas)} batidas, voz={a.voice}, rate={a.rate})")


if __name__ == "__main__":
    main()
