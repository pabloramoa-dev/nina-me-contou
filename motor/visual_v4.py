"""Visual v4 da Nina — blocos do catálogo HyperFrames adaptados ao estilo papel.

Padrão desde out/2026. NINA_VISUAL=v3 volta ao visual anterior.

- Legenda "Pill Karaoke": grupos de até 4 palavras numa pílula de papel; as
  palavras acendem conforme a Nina fala e ficam acesas.
- "Particle Burst": palavras-chave (traição, amante, aliança...) ficam
  vermelhas, crescem e soltam partículas coloridas.
- Título "Handwritten Write-On" + "Marker Highlight": título do cartão em letra
  manuscrita (Caveat), escrito da esquerda para a direita, com traço de caneta
  marca-texto desenhado por baixo.
- "Headline Slam": nas batidas "chocada" o título despenca com tremida de 3
  quadros no lugar da escrita à mão.

Palavras-chave: automáticas por lista, ou explícitas no roteiro com
"hf": {"destaque": ["palavra", ...]}.
"""
from __future__ import annotations

import html
import math
import os
import re
import unicodedata

from PIL import ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTES = os.path.join(RAIZ, "video", "assets", "fonts")
CAVEAT = os.path.join(FONTES, "Caveat.ttf")
POPPINS = os.path.join(FONTES, "Poppins-ExtraBold.ttf")

CSS = """
@font-face{font-family:Mao;src:url(assets/caveat.ttf);font-weight:400 700}
@font-face{font-family:Pill;src:url(assets/poppins-xb.ttf);font-weight:800}
.v4 h1{font-family:Mao,cursive;font-weight:700;letter-spacing:0;line-height:.98;position:relative;color:#221e25}
.v4 h1 .ink{display:inline-block}
.v4 .marker{position:absolute;left:-6px;bottom:-14px;width:72%;height:34px;overflow:visible}
.v4 .marker path{fill:none;stroke:#ffd24a;stroke-width:16;stroke-linecap:round;opacity:.9}
.v4 .pill{display:inline-block;max-width:930px;background:#fff9ea;border:3px solid #28232b;border-radius:30px;
  padding:16px 34px 18px;box-shadow:9px 10px 0 #0004;transform:rotate(-1deg);font-family:Pill,Bold,sans-serif;font-weight:800;
  line-height:1.18;letter-spacing:-.5px}
.v4 .pill .ln{display:block;white-space:nowrap}
.v4 .pill span{display:inline-block;color:#b8aa98;margin:0 .14em;position:relative;transform-origin:50% 70%}
.v4 .pill .kw{margin:0 .32em}
.v4 .pill .pt{position:absolute;left:50%;top:45%;width:15px;height:15px;border-radius:50%;opacity:0;pointer-events:none}
"""

CORES_PARTICULA = ["#ffd24a", "#d76577", "#b94959", "#417854", "#6ca3ac", "#fff9ea", "#ff8a3d"]

_FORTES = {
    "traicao", "traiu", "traindo", "trair", "traida", "traido", "amante", "amantes", "mentira", "mentiu",
    "mentindo", "gravida", "gravido", "divorcio", "alianca", "aliancas", "segredo", "segredos", "flagra",
    "flagrou", "beijo", "beijando", "motel", "hotel", "outra", "outro", "nome", "descobriu", "descobri",
    "verdade", "policia", "dna", "filho", "filha", "casamento", "casada", "casado", "noiva", "noivo",
    "sumiu", "escondido", "escondida", "foto", "fotos", "mensagem", "mensagens", "celular", "senha",
    "mae", "pai", "irma", "irmao", "cunhada", "cunhado", "chefe", "vizinho", "vizinha", "melhor", "amiga",
}
_FRACAS = {"outra", "outro", "nome", "melhor", "mae", "pai", "filho", "filha", "foto", "fotos", "celular"}


def _norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", w)


def palavras_chave(b, palavras):
    """Índices das palavras da fala que recebem destaque (máx. 2 por batida)."""
    pedidas = b.get("hf", {}).get("destaque")
    if pedidas:
        alvo = {_norm(x) for x in pedidas}
        return {i for i, w in enumerate(palavras) if _norm(w) in alvo}
    fortes = [i for i, w in enumerate(palavras) if _norm(w) in _FORTES and _norm(w) not in _FRACAS]
    if not fortes and b.get("expr") == "chocada":
        fortes = [i for i, w in enumerate(palavras) if _norm(w) in _FORTES]
        if not fortes:
            longas = sorted(range(len(palavras)), key=lambda i: -len(_norm(palavras[i])))
            fortes = [i for i in longas[:1] if len(_norm(palavras[i])) >= 5]
    return set(fortes[:2])


def tempos(b, a, fim_fala):
    """(palavra, início, fim) — mesma regra de duração do motor v3."""
    ws = b["fala"].split()
    total = sum(max(2, len(w)) for w in ws) or 1
    t, out = a, []
    for w in ws:
        e = t + (fim_fala - a) * max(2, len(w)) / total
        out.append((w, t, e))
        t = e
    return out


def _fonte(path, size, peso=None):
    f = ImageFont.truetype(path, size)
    if peso:
        try:
            f.set_variation_by_axes([peso])
        except Exception:
            pass
    return f


def _grupos(ws):
    grupos, g = [], []
    for k, (w, t, e) in enumerate(ws):
        g.append(k)
        fim = re.search(r"[,.:;!?…]$", w)
        if len(g) == 4 or fim or k == len(ws) - 1:
            grupos.append(g)
            g = []
    return grupos


def _linhas_pill(palavras, size, largura=850):
    f = _fonte(POPPINS, size)
    esp = f.getlength(" ") * 1.6
    out, cur, lw = [], [], 0.0
    for w in palavras:
        wl = f.getlength(w) * 1.05
        if cur and lw + esp + wl > largura:
            out.append(cur)
            cur, lw = [], 0.0
        cur.append(w)
        lw += (esp if len(cur) > 1 else 0) + wl
        if wl > largura:
            return None
    if cur:
        out.append(cur)
    return out if len(out) <= 2 else None


def legenda(i, b, s, ws, kws, z_fim):
    """Clips HTML + animações GSAP da legenda pílula de uma batida."""
    parts, anim = [], []
    grupos = _grupos(ws)
    for gi, g in enumerate(grupos):
        palavras = [ws[k][0] for k in g]
        size = 54
        while size > 36 and not _linhas_pill(palavras, size):
            size -= 2
        linhas = _linhas_pill(palavras, size) or [palavras]
        ini = ws[g[0]][1]
        fim = ws[grupos[gi + 1][0]][1] if gi + 1 < len(grupos) else z_fim
        k = g[0]
        html_lin = []
        for ln in linhas:
            spans = []
            for w in ln:
                pts = ""
                if k in kws:
                    pts = "".join(f'<i id="pt{i}_{k}_{p}" class="pt" style="background:{CORES_PARTICULA[p % len(CORES_PARTICULA)]}"></i>'
                                  for p in range(10))
                cls = ' class="kw"' if k in kws else ''
                spans.append(f'<span id="v{i}_{k}"{cls}>{html.escape(w)}{pts}</span>')
                k += 1
            html_lin.append('<span class="ln">' + "".join(spans) + "</span>")
        parts.append(f'<div id="cap{i}_{gi}" class="clip caps" data-start="{ini}" data-duration="{max(.05, fim - ini)}" '
                     f'data-track-index="3"><div class="speaker">NINA ME CONTOU</div><br>'
                     f'<div class="pill" style="font-size:{size}px">{"".join(html_lin)}</div></div>')
        anim.append(f'tl.fromTo("#cap{i}_{gi} .pill",{{scale:.9,y:14}},{{scale:1,y:0,duration:.22,immediateRender:false,ease:"back.out(1.6)"}},{ini});')
        for k in g:
            w, t, e = ws[k]
            if k in kws:
                anim.append(f'tl.set("#v{i}_{k}",{{color:"#b94959"}},{t});'
                            f'tl.fromTo("#v{i}_{k}",{{scale:1}},{{scale:1.14,duration:.1,immediateRender:false,ease:"power3.out"}},{t});'
                            f'tl.to("#v{i}_{k}",{{scale:1.04,duration:.2,ease:"power2.inOut"}},{t + .1});')
                semente = (i * 131 + k * 17) % 97
                for p in range(10):
                    ang = (p / 10) * 6.2832 + ((semente * (p + 3)) % 10) * 0.06
                    dist = 110 + ((semente * 7 + p * 29) % 110)
                    dx, dy = round(dist * math.cos(ang), 1), round(-dist * math.sin(ang), 1)
                    anim.append(f'tl.fromTo("#pt{i}_{k}_{p}",{{x:0,y:0,opacity:0,scale:1}},{{x:{dx},y:{dy},opacity:1,duration:.16,immediateRender:false,ease:"power3.out"}},{t + p * .012});'
                                f'tl.to("#pt{i}_{k}_{p}",{{opacity:0,scale:.3,duration:.45,ease:"power1.in"}},{t + .16 + p * .012});')
            else:
                anim.append(f'tl.to("#v{i}_{k}",{{color:"#221e25",duration:.08,ease:"none"}},{max(ini, t - .04)});'
                            f'tl.fromTo("#v{i}_{k}",{{y:0}},{{y:-4,duration:.08,immediateRender:false,yoyo:true,repeat:1}},{t});')
    return parts, anim


def bloco_titulo(txt, largura=850, altura=132, maximo=84, minimo=46):
    txt = " ".join(str(txt).split())
    for size in range(maximo, minimo - 1, -2):
        f = _fonte(CAVEAT, size, 700)
        out, cur = [], ""
        ok = True
        for w in txt.split():
            if f.getlength(w) > largura:
                ok = False
                break
            c = (cur + " " + w).strip()
            if f.getlength(c) > largura and cur:
                out.append(cur)
                cur = w
            else:
                cur = c
        if cur:
            out.append(cur)
        if ok and len(out) <= 2 and len(out) * size * 1.0 <= altura:
            return "<br>".join(html.escape(x) for x in out), size
    return html.escape(txt[:40] + "…"), minimo


def titulo(i, a, chocada, primeiro):
    """Animações do título do cartão #c{i}."""
    sel = f"#c{i} h1 .ink"
    if chocada:
        return [f'tl.fromTo("{sel}",{{scale:1.7,opacity:0}},{{scale:1,opacity:1,duration:.26,immediateRender:false,ease:"power4.in"}},{a});'
                f'tl.to("#c{i} h1",{{keyframes:[{{x:11,duration:.034}},{{x:-9,duration:.034}},{{x:5,duration:.034}},{{x:0,duration:.034}}]}},{a + .26});'
                f'tl.fromTo("#c{i} .marker path",{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:.3,immediateRender:false,ease:"power2.out"}},{a + .4});']
    d = .5 if primeiro else .75
    return [f'tl.fromTo("{sel}",{{clipPath:"inset(-20% 100% -20% 0)"}},{{clipPath:"inset(-20% 0% -20% 0)",duration:{d},immediateRender:false,ease:"none"}},{a + .15});'
            f'tl.fromTo("#c{i} .marker path",{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:.45,immediateRender:false,ease:"power2.out"}},{a + .15 + d});']


MARKER = ('<svg class="marker" viewBox="0 0 600 34" preserveAspectRatio="none">'
          '<path pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" '
          'd="M6 22 C 120 12, 240 28, 360 18 S 540 14, 594 20"/></svg>')


def eventos_extra(ep, segs):
    """Pops sonoros nas palavras-chave (as partículas)."""
    ev = []
    for b, s in zip(ep["batidas"], segs):
        a = float(s["ini"])
        fim = max(a + .01, min(float(s["fim"]), float(s.get("fim_fala", s["fim"]))))
        ws = tempos(b, a, fim)
        for k in palavras_chave(b, [w for w, _, _ in ws]):
            ev.append((ws[k][1], "brilho", 0.06))
            ev.append((ws[k][1], "pop", 0.10))
    return ev
