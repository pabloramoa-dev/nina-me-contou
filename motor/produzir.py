#!/usr/bin/env python3
"""produzir.py — do JSON do episódio ao MP4 pronto.

  python motor/produzir.py episodios/ep001-p1.json            # tudo
  python motor/produzir.py episodios/ep001-p1.json --so voz   # só uma etapa
  python motor/produzir.py episodios/ep001-p1.json --rapido   # prévia 540p

Etapas (pula o que já existe; apague o arquivo para refazer):
  voz   -> saida/<id>/voz.wav + segs.json   (Thalita Neural pt-BR, master Pedalboard)
  lip   -> saida/<id>/lip.json              (lip sync por amplitude, 30 fps)
  video -> saida/<id>/<id>.mp4              (Nina original + HyperFrames, padrão)
  tex   -> compatibilidade: mesma composição completa no motor HyperFrames
  mux   -> compatibilidade: mesma composição completa no motor HyperFrames
  capa  -> saida/<id>/capa.png              (capa do Reel)
  post  -> saida/<id>/legenda.txt           (legenda de publicação)

Leva tempo: o Manim renderiza ~1 min de vídeo em ~10-20 min num runner comum.
Em sessão com limite de comando, rode com setsid/nohup e acompanhe o log.
"""
import argparse, json, os, shutil, subprocess, sys

MOTOR = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(MOTOR)
VOZ, RATE, GAP = "pt-BR-ThalitaNeural", "-6%", 0.25
# Master da voz: motor/audio_fx.py (Spotify Pedalboard; cai no ffmpeg se faltar)


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

    ep_json = os.path.abspath(a.episodio)
    sys.path.insert(0, MOTOR)
    from cta import garantir_cta
    from render_version import versao
    ep = garantir_cta(json.load(open(ep_json, encoding="utf-8")))   # CTA de seguir sempre no final
    from visual_images import preparar_roteiro, config as visual_config
    ep = preparar_roteiro(ep)
    ep['visual_images'] = visual_config(ep)
    ep["_render_version"] = versao()
    usa_hf = os.environ.get("NINA_MOTOR", "hyperframes") == "hyperframes"
    pasta = os.path.join(RAIZ, "saida", ep["id"])
    ep_path = os.path.join(pasta, "ep.json")
    novo = json.dumps(ep, ensure_ascii=False, indent=1)
    if os.path.exists(ep_path) and open(ep_path, encoding="utf-8").read() != novo:
        shutil.rmtree(pasta)          # roteiro mudou: refaz tudo
    os.makedirs(pasta, exist_ok=True)
    with open(ep_path, "w", encoding="utf-8") as f:
        f.write(novo)
    P = lambda n: os.path.join(pasta, n)
    quer = lambda e: a.so in (None, e)
    env = dict(os.environ, EPISODIO=ep_path, PASTA=pasta)

    if quer("voz") and not os.path.exists(P("voz.wav")):
        with open(P("roteiro.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(b["fala"] for b in ep["batidas"]) + "\n")
        voice_engine = str(ep.get("voice_engine") or os.environ.get("NINA_VOICE_ENGINE", "thalita")).lower()
        if voice_engine == "kokoro":
            kokoro_voice = str(ep.get("kokoro_voice") or os.environ.get("NINA_KOKORO_VOICE", "pf_dora"))
            kokoro_speed = str(ep.get("kokoro_speed") or os.environ.get("NINA_KOKORO_SPEED", "1.05"))
            sh([sys.executable, os.path.join(MOTOR, "gerar_voz_kokoro.py"), P("roteiro.txt"),
                "--voz", kokoro_voice, "--speed", kokoro_speed, "--gap", str(GAP),
                "--out", P("bruta.wav"), "--seg-json", P("segs.json")])
        else:
            sh([sys.executable, os.path.join(MOTOR, "gerar_voz_thalita.py"), P("roteiro.txt"),
                "--voice", VOZ, f"--rate={RATE}", "--gap", str(GAP),
                "--out", P("bruta.wav"), "--seg-json", P("segs.json")])
        from audio_fx import masterizar_voz
        print("master da voz:", masterizar_voz(P("bruta.wav"), P("voz.wav")), flush=True)

    if quer("lip") and not os.path.exists(P("lip.json")):
        lip = "lipsync_rhubarb.py" if os.environ.get("NINA_LIP", "rhubarb") == "rhubarb" else "lipsync_amplitude.py"
        sh([sys.executable, os.path.join(MOTOR, lip), P("voz.wav"), P("lip.json"), "30" if usa_hf else "24"])

    final = P(ep["id"] + ".mp4")
    if usa_hf and (quer("video") or quer("tex") or quer("mux")) and not os.path.exists(final):
        from hyperframes import renderizar
        if a.rapido:
            os.environ["NINA_HF_BASE_WIDTH"] = "540"
        renderizar(ep, pasta, RAIZ)

    if not usa_hf and quer("video") and not os.path.exists(P("raw.mp4")):
        q = ["-ql"] if a.rapido else []
        extra = ["-r", "540,960"] if a.rapido else []
        sh(["manim", *q, *extra, "--fps", "24", "--disable_caching", "--media_dir", P("media"),
            "-o", "raw", os.path.join(MOTOR, "cena_nina.py"), "Episodio"], env=env, cwd=MOTOR)
        achado = None
        for raiz, _, arqs in os.walk(P("media")):
            if "raw.mp4" in arqs and "partial" not in raiz:
                achado = os.path.join(raiz, "raw.mp4")
        shutil.copy(achado, P("raw.mp4"))

    if not usa_hf and quer("tex") and not os.path.exists(P("tex.mp4")):
        sys.path.insert(0, MOTOR)
        import dvh_vox_papel as V
        V.estilo("papel")
        V.aplicar_textura(P("raw.mp4"), P("tex.mp4"), crf=24)

    final = P(ep["id"] + ".mp4")
    if not usa_hf and quer("mux") and not os.path.exists(final):
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
        if os.path.exists(P("render.json")):
            shutil.copy(P("render.json"), os.path.join(dest, ep["id"] + "-render.json"))
        Image.open(P("capa.png")).convert("RGB").save(os.path.join(dest, ep["id"] + "-capa.jpg"), quality=90)
        from story import fazer_story
        fazer_story(final, os.path.join(dest, ep["id"] + "-story.mp4"))
        sys.path.insert(0, RAIZ)
        from src.fila import assinatura
        with open(os.path.join(dest, ep["id"] + ".hash"), "w") as f:
            f.write(assinatura(ep["id"]) + "\n")

    if quer("post"):
        with open(P("legenda.txt"), "w", encoding="utf-8") as f:
            f.write(ep["legenda_post"] + "\n")

    print("OK", ep["id"], "->", pasta, flush=True)


if __name__ == "__main__":
    main()
