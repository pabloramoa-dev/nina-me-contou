#!/usr/bin/env python3
"""produzir.py — do JSON do episódio ao MP4 pronto.

  python motor/produzir.py episodios/ep001-p1.json            # tudo
  python motor/produzir.py episodios/ep001-p1.json --so voz   # só uma etapa
  python motor/produzir.py episodios/ep001-p1.json --rapido   # prévia 540p

Etapas (pula o que já existe; apague o arquivo para refazer):
  voz   -> saida/<id>/voz.wav + segs.json   (Kokoro pf_dora, masterizada)
  lip   -> saida/<id>/lip.json              (lip sync por amplitude, 24 fps)
  video -> saida/<id>/raw.mp4               (Manim)
  tex   -> saida/<id>/tex.mp4               (grão de papel)
  mux   -> saida/<id>/<id>.mp4              (vídeo + voz)
  capa  -> saida/<id>/capa.png              (capa do Reel)
  post  -> saida/<id>/legenda.txt           (legenda de publicação)

Leva tempo: o Manim renderiza ~1 min de vídeo em ~10-20 min num runner comum.
Em sessão com limite de comando, rode com setsid/nohup e acompanhe o log.
"""
import argparse, json, os, shutil, subprocess, sys

MOTOR = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(MOTOR)
VOZ, SPEED, GAP = "pf_dora", 1.02, 0.25
MASTER = ("highpass=f=90,equalizer=f=3000:width_type=o:width=1.5:g=3,"
          "acompressor=threshold=-17dB:ratio=2.6:attack=6:release=140,volume=1.12")


def sh(cmd, **kw):
    print("+", " ".join(cmd) if isinstance(cmd, list) else cmd, flush=True)
    subprocess.run(cmd, check=True, **kw)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episodio")
    ap.add_argument("--so", default=None)
    ap.add_argument("--rapido", action="store_true")
    ap.add_argument("--publicar-em", default=None, help="copia MP4 + capa.jpg para esta pasta (ex.: reels)")
    a = ap.parse_args()

    ep_path = os.path.abspath(a.episodio)
    ep = json.load(open(ep_path, encoding="utf-8"))
    pasta = os.path.join(RAIZ, "saida", ep["id"])
    os.makedirs(pasta, exist_ok=True)
    P = lambda n: os.path.join(pasta, n)
    quer = lambda e: a.so in (None, e)
    env = dict(os.environ, EPISODIO=ep_path, PASTA=pasta)

    if quer("voz") and not os.path.exists(P("voz.wav")):
        with open(P("roteiro.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(b["fala"] for b in ep["batidas"]) + "\n")
        sh([sys.executable, os.path.join(MOTOR, "gerar_voz_kokoro.py"), P("roteiro.txt"), "--voz", VOZ,
            "--speed", str(SPEED), "--gap", str(GAP), "--out", P("bruta.wav"), "--seg-json", P("segs.json")])
        sh(["ffmpeg", "-y", "-loglevel", "error", "-i", P("bruta.wav"), "-af", MASTER, P("voz.wav")])

    if quer("lip") and not os.path.exists(P("lip.json")):
        sh([sys.executable, os.path.join(MOTOR, "lipsync_amplitude.py"), P("voz.wav"), P("lip.json"), "24"])

    if quer("video") and not os.path.exists(P("raw.mp4")):
        q = ["-ql"] if a.rapido else []
        extra = ["-r", "540,960"] if a.rapido else []
        sh(["manim", *q, *extra, "--fps", "24", "--disable_caching", "--media_dir", P("media"),
            "-o", "raw", os.path.join(MOTOR, "cena_nina.py"), "Episodio"], env=env, cwd=MOTOR)
        achado = None
        for raiz, _, arqs in os.walk(P("media")):
            if "raw.mp4" in arqs and "partial" not in raiz:
                achado = os.path.join(raiz, "raw.mp4")
        shutil.copy(achado, P("raw.mp4"))

    if quer("tex") and not os.path.exists(P("tex.mp4")):
        sys.path.insert(0, MOTOR)
        import dvh_vox_papel as V
        V.estilo("papel")
        V.aplicar_textura(P("raw.mp4"), P("tex.mp4"), crf=24)

    final = P(ep["id"] + ".mp4")
    if quer("mux") and not os.path.exists(final):
        sh(["ffmpeg", "-y", "-loglevel", "error", "-i", P("tex.mp4"), "-i", P("voz.wav"),
            "-af", "apad", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
            "-movflags", "+faststart", final])

    if quer("capa") and not os.path.exists(P("capa.png")):
        sh(["manim", "-s", "--disable_caching", "--media_dir", P("media_capa"), "-o", "capa",
            os.path.join(MOTOR, "cena_nina.py"), "Capa"], env=env, cwd=MOTOR)
        for raiz, _, arqs in os.walk(P("media_capa")):
            for n in arqs:
                if n.startswith("capa") and n.endswith(".png"):
                    shutil.copy(os.path.join(raiz, n), P("capa.png"))

    if a.publicar_em:
        from PIL import Image
        dest = os.path.abspath(a.publicar_em)
        os.makedirs(dest, exist_ok=True)
        shutil.copy(final, os.path.join(dest, ep["id"] + ".mp4"))
        Image.open(P("capa.png")).convert("RGB").save(os.path.join(dest, ep["id"] + "-capa.jpg"), quality=90)

    if quer("post"):
        with open(P("legenda.txt"), "w", encoding="utf-8") as f:
            f.write(ep["legenda_post"] + "\n")

    print("OK", ep["id"], "->", pasta, flush=True)


if __name__ == "__main__":
    main()
