"""Aplicação do visual Remotion aprovado ao vídeo pronto do HyperFrames.

Nenhuma publicação aqui. Mantém personagem real, fonemas, voz e trilha originais;
troca somente a composição visual final. Falhas impedem a cópia para reels/.
"""
from __future__ import annotations
import json, math, os, shutil, subprocess
from pathlib import Path

def executar(cmd, cwd=None):
    print("+", " ".join(str(x) for x in cmd), flush=True)
    subprocess.run([str(x) for x in cmd], cwd=cwd, check=True)

def duracao_ffprobe(path):
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path)
    ], text=True)
    return float(out.strip())

def montar_props(ep, segs, dur):
    if len(segs) != len(ep["batidas"]):
        raise ValueError("Cenas e falas não correspondem")
    scenes = []
    for i, seg in enumerate(segs):
        b = ep["batidas"][i]
        art = b.get("arte") or []
        hf = b.get("hf") if isinstance(b.get("hf"), dict) else {}
        titulo = (b.get("tela") or hf.get("titulo") or
                  (art[1] if len(art) > 1 and art[0] in
                   ("titulo", "manchete", "manchete_v", "interrogacao", "seguir") else None) or
                  " ".join(b["fala"].split()[:7]))
        start = float(seg.get("ini", seg.get("inicio", seg.get("start", 0))))
        end = float(seg["fim"])
        if end <= start or start < -0.01 or end > dur + 0.5:
            raise ValueError(f"Timeline inválida no bloco {i}: {start} - {end}")
        scenes.append({
            "start": start, "end": end, "title": str(titulo),
            "fala": b["fala"], "expr": b.get("expr", "neutra")
        })
    return {"durationFrames": math.ceil(dur * 30), "scenes": scenes}

def finalizar(ep, pasta, raiz):
    pasta, raiz = Path(pasta), Path(raiz)
    projeto = raiz / "video" / "remotion"
    base = pasta / "hyperframes" / "assets"
    if not (base / "base.mp4").is_file() or not (base / "mix.wav").is_file():
        raise FileNotFoundError("Base da Nina ou trilha HyperFrames indisponível")
    if not (projeto / "src" / "index.ts").is_file():
        raise FileNotFoundError("Projeto Remotion de produção ausente")
    public = projeto / "public"
    public.mkdir(parents=True, exist_ok=True)
    shutil.copy2(base / "base.mp4", public / "nina-base.mp4")
    shutil.copy2(base / "mix.wav", public / "mix.wav")
    segs = json.loads((pasta / "segs.json").read_text(encoding="utf-8"))
    duration = duracao_ffprobe(public / "nina-base.mp4")
    props = montar_props(ep, segs, duration)
    propsfile = pasta / "remotion-props.json"
    propsfile.write_text(json.dumps(props, ensure_ascii=False, indent=2), encoding="utf-8")
    # Instala em diretório separado: NÃO substitui nem altera o HyperFrames.
    if not (projeto / "node_modules" / "@remotion" / "cli").exists():
        executar(["npm", "install", "--no-audit", "--no-fund"], cwd=projeto)
    executar(["npx", "--no-install", "remotion", "browser", "ensure"], cwd=projeto)
    saida = pasta / (ep["id"] + ".remotion.mp4")
    executar([
        "npx", "--no-install", "remotion", "render", "src/index.ts",
        "NinaRemotion", saida, f"--props={propsfile}", "--codec=h264",
        "--crf=21", "--concurrency=2"
    ], cwd=projeto)

    # QA rigoroso: vídeo + áudio, 1080x1920, 30fps, duração correspondente.
    from hyperframes import conferir
    esperado = props["durationFrames"] / 30
    conferir(saida, esperado)
    final = pasta / (ep["id"] + ".mp4")
    os.replace(saida, final)
    metap = pasta / "render.json"
    meta = json.loads(metap.read_text(encoding="utf-8"))
    meta.update(motor="remotion", motor_base="hyperframes",
                versao_final="nina-remotion-aprovado-legenda-inferior-v1",
                legenda="solta_sem_faixa_inferior",
                voz=ep.get("kokoro_voice") if ep.get("voice_engine") == "kokoro"
                    else "pt-BR-ThalitaNeural",
                duracao=esperado)
    metap.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[Remotion] aprovado: {final} ({esperado:.1f}s)", flush=True)
    return final
