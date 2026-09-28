"""Versão do vídeo para os Stories (a API aceita no máximo 60 s).

    python motor/story.py reels/ep006-p1.mp4 reels/ep006-p1-story.mp4

Se o vídeo já cabe em 59 s, copia igual. Se passa, mantém o começo e os
últimos FINAL_S segundos (o CTA de seguir + a placa final), com um corte seco
no meio — o CTA do fim nunca é perdido.
"""
from __future__ import annotations

import shutil
import subprocess
import sys

MAX_S = 59.0
FINAL_S = 7.5


def duracao(p: str) -> float:
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                   "-of", "csv=p=0", p])
    return float(out.strip())


def fazer_story(entrada: str, saida: str) -> str:
    d = duracao(entrada)
    if d <= MAX_S:
        shutil.copy(entrada, saida)
        return saida
    cabeca = MAX_S - FINAL_S - 0.3
    cauda = d - FINAL_S
    filtro = (f"[0:v]trim=0:{cabeca:.3f},setpts=PTS-STARTPTS[v1];"
              f"[0:a]atrim=0:{cabeca:.3f},asetpts=PTS-STARTPTS,afade=t=out:st={cabeca-0.15:.3f}:d=0.15[a1];"
              f"[0:v]trim=start={cauda:.3f},setpts=PTS-STARTPTS[v2];"
              f"[0:a]atrim=start={cauda:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.15[a2];"
              f"[v1][a1][v2][a2]concat=n=2:v=1:a=1[v][a]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", entrada, "-filter_complex", filtro,
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "22", "-preset", "medium",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", saida],
                   check=True)
    return saida


if __name__ == "__main__":
    print(fazer_story(sys.argv[1], sys.argv[2]), f"{duracao(sys.argv[2]):.1f}s")
