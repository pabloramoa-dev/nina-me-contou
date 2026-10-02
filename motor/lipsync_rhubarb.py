#!/usr/bin/env python3
"""Lip sync por fonema com Rhubarb Lip Sync (MIT) — modo fonético, serve p/ português.

    python motor/lipsync_rhubarb.py voz.wav lip.json

Gera cues [{start,end,estado}] com os formatos de boca do Rhubarb:
  X repouso · A M/B/P (lábios fechados) · B dentes (S, T, I) · C aberta (É)
  D bem aberta (A) · E arredondada (Ó) · F bico (U, O fechado) · G F/V · H L
Se o Rhubarb não estiver disponível ou falhar, cai no lip sync por amplitude
(motor/lipsync_amplitude.py), então a produção nunca para por causa dele.

Binário: variável RHUBARB_BIN, ou `rhubarb` no PATH, ou ~/.cache/rhubarb/rhubarb.
"""
import json
import os
import shutil
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))


def achar_bin():
    for c in (os.environ.get("RHUBARB_BIN"), shutil.which("rhubarb"),
              os.path.expanduser("~/.cache/rhubarb/rhubarb")):
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    return None


def rhubarb(wav, out_json):
    exe = achar_bin()
    if not exe:
        raise FileNotFoundError("rhubarb não encontrado")
    r = subprocess.run([exe, "-q", "-r", "phonetic", "-f", "json", "--extendedShapes", "GHX", wav],
                       capture_output=True, text=True, timeout=900)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-500:])
    dados = json.loads(r.stdout)
    cues = [{"start": round(c["start"], 3), "end": round(c["end"], 3),
             "estado": "fechada" if c["value"] == "X" else c["value"]}
            for c in dados["mouthCues"]]
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(cues, f, ensure_ascii=False, indent=1)
    return len(cues)


def main():
    wav, out_json = sys.argv[1], sys.argv[2]
    fps = sys.argv[3] if len(sys.argv) > 3 else "30"
    try:
        n = rhubarb(wav, out_json)
        print(f"ok rhubarb: {n} cues", flush=True)
    except Exception as e:
        print(f"rhubarb indisponível ({e}); usando amplitude", flush=True)
        subprocess.run([sys.executable, os.path.join(AQUI, "lipsync_amplitude.py"), wav, out_json, fps], check=True)


if __name__ == "__main__":
    main()
