"""
nina_lib v2 — Nina, ruiva de ~30 anos, a CONFIDENTE: conta na varanda as
histórias de traição que chegam no direct dela (ficção).

Novidades da v2
- rosto separado do corpo (troca de expressão sem redesenhar a personagem)
- 6 expressões: neutra, desconfiada, chocada, ironica, triste, brava
- piscada automática (pálpebras) e boca de lip sync que respeita a expressão
- cabelo com volume e ondas, sardas nas bochechas, blush, batom
- plano médio (cintura pra cima)
- dois cenários da mesma varanda: "tarde" (parte 1, água de coco) e
  "noite" (parte 2, taça de vinho, lua e varal de lâmpadas)
Tudo com caminhos relativos: a pasta motor/ é autossuficiente.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from manim import *
import numpy as np
import dvh_vox_papel as V

PT = "#111111"
RUIVO, RUIVO_ESC, RUIVO_CL = "#c4502a", "#9c3a1c", "#e8804a"
PELE, BLUSH = "#f4d5bd", "#f0a08a"
BATOM, BOCA_IN = "#b8323c", "#5e1820"
OURO = "#e8b23a"
BLUSA = "#146b5c"
EXPRESSOES = ("neutra", "desconfiada", "chocada", "ironica", "triste", "brava")

# escala e posição padrão do plano médio (usadas pela cena e pela capa)
ESCALA = 1.75
POSICAO = np.array([0.1, -2.6, 0])


def _curva(pts, **kw):
    m = VMobject(**kw)
    m.set_points_smoothly([np.array(p, dtype=float) for p in pts])
    return m


# =============================================================================
#  ROSTO (olhos, pálpebras, sobrancelhas, boca) — depende da expressão
# =============================================================================
_ABERT = {"neutra": 1.0, "desconfiada": 0.55, "chocada": 1.25, "ironica": 0.7,
          "triste": 0.8, "brava": 0.6}
# (inclinação da ponta interna, altura)
_SOB = {"neutra": (0.0, 0.30), "desconfiada": (-0.10, 0.24), "chocada": (0.06, 0.42),
        "ironica": None, "triste": (0.12, 0.30), "brava": (-0.16, 0.24)}


def boca_expr(expr, bc):
    """Boca parada (fechada) de cada expressão, centrada em bc."""
    if expr == "chocada":
        return Ellipse(width=0.24, height=0.30, fill_color=BOCA_IN, fill_opacity=1,
                       stroke_color=BATOM, stroke_width=8).move_to(bc)
    if expr == "ironica":
        return _curva([bc + LEFT * 0.20 + UP * 0.01, bc + DOWN * 0.03, bc + RIGHT * 0.18 + UP * 0.10],
                      stroke_color=BATOM, stroke_width=10)
    if expr == "triste":
        return Arc(radius=0.22, start_angle=PI * 0.25, angle=PI * 0.5,
                   arc_center=bc + DOWN * 0.18).set_stroke(BATOM, 10)
    if expr in ("desconfiada", "brava"):
        return Line(bc + LEFT * 0.16, bc + RIGHT * 0.14 + DOWN * 0.03, stroke_color=BATOM, stroke_width=10)
    return Arc(radius=0.26, start_angle=PI * 1.28, angle=PI * 0.44,
               arc_center=bc + UP * 0.16).set_stroke(BATOM, 10)


def boca_fala(estado, largura=0.30):
    """Boca aberta do lip sync (meia / aberta)."""
    if estado == "meia":
        return Ellipse(width=largura, height=0.13, fill_color=BOCA_IN, fill_opacity=1,
                       stroke_color=BATOM, stroke_width=7)
    return Ellipse(width=largura * 1.05, height=0.27, fill_color=BOCA_IN, fill_opacity=1,
                   stroke_color=BATOM, stroke_width=7)


def rosto(expr, c):
    """VGroup(olhos, palpebras, sobrancelhas, boca) para a cabeça centrada em c."""
    a = _ABERT[expr]

    def olho(l):
        base = c + l * 0.36 + UP * 0.05
        br = Ellipse(width=0.42, height=0.36 * a, fill_color=WHITE, fill_opacity=1,
                     stroke_color=PT, stroke_width=6).move_to(base)
        r = min(0.10 if expr == "chocada" else 0.13, 0.36 * a / 2)
        foco = base + (RIGHT * 0.07 if expr == "desconfiada" else ORIGIN) \
            + (DOWN * 0.03 if expr == "triste" else ORIGIN)
        iris = Circle(radius=r, fill_color="#3f8a4e", fill_opacity=1,
                      stroke_color=PT, stroke_width=4).move_to(foco)
        pup = Dot(foco, radius=min(0.055, r * 0.5), color=PT)
        luz = Dot(foco + UP * 0.045 + RIGHT * 0.04, radius=0.03, color=WHITE)
        cil = VGroup(*[Line(br.get_top() + l * dx, br.get_top() + l * (dx + 0.07) + UP * 0.09,
                            stroke_color=PT, stroke_width=5) for dx in (0.04, 0.12, 0.18)])
        return VGroup(br, iris, pup, luz, cil)

    olhos = VGroup(olho(LEFT), olho(RIGHT))

    # pálpebras: cobrem o olho na piscada (opacidade controlada pela cena)
    palp = VGroup()
    for l in (LEFT, RIGHT):
        base = c + l * 0.36 + UP * 0.05
        palp.add(VGroup(
            Ellipse(width=0.50, height=0.50, fill_color=PELE, fill_opacity=1, stroke_width=0).move_to(base),
            Arc(radius=0.22, start_angle=PI * 1.15, angle=PI * 0.7, arc_center=base + UP * 0.16)
            .set_stroke(PT, 6)))
    for pl in palp:
        pl[0].set_fill(opacity=0); pl[1].set_stroke(opacity=0)

    def sob(l):
        s = -1 if l is LEFT else 1
        cfg = _SOB[expr]
        if cfg is None:  # irônica: uma sobrancelha levantada
            cfg = (0.0, 0.38) if l is RIGHT else (-0.06, 0.26)
        incl, h = cfg
        ext = c + np.array([s * 0.58, h, 0])
        inn = c + np.array([s * 0.16, h + incl, 0])
        return _curva([ext, (ext + inn) / 2 + UP * 0.06, inn], stroke_color=RUIVO_ESC, stroke_width=9)

    sobs = VGroup(sob(LEFT), sob(RIGHT))
    boca = boca_expr(expr, c + DOWN * 0.50)
    return VGroup(olhos, palp, sobs, boca)


# =============================================================================
#  NINA
# =============================================================================
def nina(expr="neutra", cenario="tarde"):
    cab = Circle(radius=0.9, stroke_color=PT, stroke_width=15,
                 fill_color=PELE, fill_opacity=1).shift(UP * 1.4)
    c = cab.get_center()

    # cabelo: nuvem ondulada atrás + cascatas laterais + franja lateral
    pts = []
    for i, ang in enumerate(np.linspace(0, TAU, 17)[:-1]):
        r = 1.30 + (0.13 if i % 2 else 0.0)
        pts.append(c + np.array([np.cos(ang) * r * 1.02, np.sin(ang) * r * 0.98 + 0.05, 0]))
    nuvem = VMobject(fill_color=RUIVO, fill_opacity=1, stroke_color=PT, stroke_width=10)
    nuvem.set_points_smoothly(pts + [pts[0]])

    def cascata(s):
        P = lambda x, y: c + np.array([s * x, y, 0])
        return _curva([P(0.80, 0.2), P(1.40, -0.3), P(1.25, -1.0), P(1.55, -1.7),
                       P(1.35, -2.45), P(1.60, -3.0), P(1.05, -3.05), P(0.95, -2.4),
                       P(0.80, -1.6), P(0.92, -0.9), P(0.72, -0.2), P(0.80, 0.2)],
                      fill_color=RUIVO, fill_opacity=1, stroke_color=PT, stroke_width=9)
    fios = VGroup(*[_curva([c + np.array([s * 1.2, -0.9 - k * 0.55, 0]),
                            c + np.array([s * 1.33, -1.15 - k * 0.55, 0]),
                            c + np.array([s * 1.22, -1.4 - k * 0.55, 0])],
                           stroke_color=RUIVO_ESC, stroke_width=5)
                    for s in (-1, 1) for k in range(3)])
    franja = _curva([c + np.array(p) for p in
                     [(-0.95, 0.25, 0), (-0.75, 0.85, 0), (0.0, 1.02, 0), (0.75, 0.80, 0),
                      (0.98, 0.35, 0), (0.72, 0.55, 0), (0.25, 0.62, 0), (-0.35, 0.40, 0),
                      (-0.80, -0.05, 0), (-0.95, 0.25, 0)]],
                    fill_color=RUIVO_CL, fill_opacity=1, stroke_color=PT, stroke_width=8)
    brilho = Arc(radius=0.72, start_angle=PI * 0.28, angle=PI * 0.22,
                 arc_center=c + UP * 0.12).set_stroke("#f7b27f", 8)

    nariz = _curva([c + UP * 0.02 + LEFT * 0.02, c + DOWN * 0.15 + LEFT * 0.09,
                    c + DOWN * 0.22 + RIGHT * 0.02, c + DOWN * 0.19 + RIGHT * 0.11],
                   stroke_color="#b5794f", stroke_width=6)
    rng = np.random.default_rng(5)
    sardas = VGroup(*[Dot(c + np.array([s * rng.uniform(0.30, 0.58), -0.20 + rng.uniform(-0.06, 0.07), 0]),
                          radius=0.024, color="#c98f6a") for s in (-1, 1) for _ in range(6)])
    blush = VGroup(*[Ellipse(width=0.34, height=0.16, fill_color=BLUSH, fill_opacity=0.55,
                             stroke_width=0).move_to(c + np.array([s * 0.50, -0.30, 0])) for s in (-1, 1)])
    brincos = VGroup(*[Circle(radius=0.17, stroke_color=OURO, stroke_width=7)
                       .move_to(c + np.array([s * 0.92, -0.40, 0])) for s in (-1, 1)])

    # corpo
    pesc = Line(cab.get_bottom(), cab.get_bottom() + DOWN * 0.22, stroke_color=PT, stroke_width=14)
    t = pesc.get_end()
    blusa = VMobject(fill_color=BLUSA, fill_opacity=1, stroke_color=PT, stroke_width=10)
    blusa.set_points_as_corners([t + LEFT * 0.55, t + LEFT * 0.12 + DOWN * 0.05, t + DOWN * 0.45,
                                 t + RIGHT * 0.12 + DOWN * 0.05, t + RIGHT * 0.55,
                                 t + RIGHT * 0.78 + DOWN * 1.65, t + LEFT * 0.78 + DOWN * 1.65,
                                 t + LEFT * 0.55])
    pele_v = Polygon(t + LEFT * 0.12 + DOWN * 0.05, t + DOWN * 0.45, t + RIGHT * 0.12 + DOWN * 0.05,
                     fill_color=PELE, fill_opacity=1, stroke_width=0)
    colar = VGroup(ArcBetweenPoints(t + LEFT * 0.22 + DOWN * 0.02, t + RIGHT * 0.22 + DOWN * 0.02,
                                    angle=-PI / 2.5).set_stroke(OURO, 5),
                   Dot(t + DOWN * 0.24, radius=0.06, color=OURO))
    omb = t + DOWN * 0.18
    be = Line(omb + LEFT * 0.55, omb + DOWN * 1.1 + LEFT * 0.85, stroke_color=PT, stroke_width=15)
    bd = Line(omb + RIGHT * 0.55, omb + DOWN * 0.35 + RIGHT * 1.2, stroke_color=PT, stroke_width=15)
    e = bd.get_end()
    if cenario == "noite":   # taça de vinho
        copo = VGroup(
            Line(e + DOWN * 0.10, e + UP * 0.25, stroke_color=PT, stroke_width=5),
            Line(e + DOWN * 0.10 + LEFT * 0.14, e + DOWN * 0.10 + RIGHT * 0.14, stroke_color=PT, stroke_width=6),
            _curva([e + UP * 0.25, e + UP * 0.35 + LEFT * 0.18, e + UP * 0.72 + LEFT * 0.2,
                    e + UP * 0.72 + RIGHT * 0.2, e + UP * 0.35 + RIGHT * 0.18, e + UP * 0.25],
                   fill_color="#7a1830", fill_opacity=1, stroke_color=PT, stroke_width=6))
    else:                    # água de coco
        copo = VGroup(
            Polygon(e + LEFT * 0.20 + UP * 0.45, e + RIGHT * 0.20 + UP * 0.45, e + RIGHT * 0.14, e + LEFT * 0.14,
                    fill_color="#f4f1e6", fill_opacity=1, stroke_color=PT, stroke_width=6),
            Line(e + UP * 0.40, e + UP * 0.85 + RIGHT * 0.18, stroke_color="#e2483c", stroke_width=7))

    face = rosto(expr, c)
    grupo = VGroup(nuvem, cascata(-1), cascata(1), fios, pesc, blusa, pele_v, colar, be, bd, copo,
                   brincos, cab, blush, sardas, franja, brilho, nariz, face)
    return dict(grupo=grupo, cab=cab, rosto=face, copo=copo, expr=expr)


def posicionar(p, escala=ESCALA, pos=POSICAO):
    p["grupo"].scale(escala).move_to(pos)
    p["escala"] = escala
    return p


def rosto_alinhado(p, expr):
    """Rosto novo, já na escala/posição da Nina p (para Transform)."""
    k = p.get("escala", 1.0)
    novo = rosto(expr, ORIGIN).scale(k, about_point=ORIGIN)
    return novo.shift(p["cab"].get_center())


# =============================================================================
#  VIDA: piscada + lip sync que respeita a expressão
# =============================================================================
def animar_nina(scene, p, cues, semente=7):
    """Liga piscada e lip sync. cues = [{start,end,estado}] do lipsync_amplitude.
    Retorna o estado (dict) — a cena troca p['expr'] e p['rosto'] continua válido."""
    k = p.get("escala", 1.0)
    rng = np.random.default_rng(semente)
    piscadas, t = [], 1.2
    while t < 600:
        piscadas.append(t)
        t += rng.uniform(2.6, 4.8)
    st = {"t": 0.0, "v": None}
    fala = VMobject()
    scene.add(fala)

    def upd(mo, dt):
        # relógio da cena (não acumula dt: o dt some em alguns quadros e dessincroniza)
        tt = scene.renderer.time
        st["t"] = tt
        # piscada (0.12s)
        fechado = any(0 <= tt - b < 0.12 for b in piscadas[:int(tt / 2.5) + 3])
        for pl in p["rosto"][1]:
            pl[0].set_fill(opacity=1 if fechado else 0)
            pl[1].set_stroke(opacity=1 if fechado else 0)
        # lip sync
        v = "fechada"
        for cu in cues:
            if cu["start"] <= tt < cu["end"]:
                v = cu["estado"]; break
            if cu["start"] > tt:
                break
        boca_parada = p["rosto"][3]
        centro = p["cab"].get_center() + DOWN * 0.50 * k
        if v == "fechada":
            boca_parada.set_stroke(opacity=1)
            boca_parada.set_fill(opacity=1 if p["expr"] == "chocada" else 0)
            if st["v"] != v:
                mo.become(VMobject())
        else:
            boca_parada.set_stroke(opacity=0).set_fill(opacity=0)
            if st["v"] != v:
                mo.become(boca_fala(v).scale(k))
            mo.move_to(centro)
        st["v"] = v
    fala.add_updater(upd)
    return st


def trocar_expressao(scene, p, expr, dur=0.18):
    if expr == p["expr"] or expr not in EXPRESSOES:
        return 0.0
    novo = rosto_alinhado(p, expr)
    scene.play(Transform(p["rosto"], novo), run_time=dur)
    p["expr"] = expr
    return dur


# =============================================================================
#  CENÁRIOS — a mesma varanda em dois horários
# =============================================================================
def _coqueiro(x0, y0, tronco="#8a5a3c", folha="#2f7d55", contorno=PT):
    tr = VMobject(stroke_color=tronco, stroke_width=22)
    tr.set_points_smoothly([[x0, y0 - 0.4, 0], [x0 - 0.4, y0 + 1.8, 0], [x0 - 0.1, y0 + 3.6, 0]])
    fo = VGroup(*[_curva([tr.get_end(), tr.get_end() + np.array([dx * 1.5, dy * 1.2 + 0.4, 0]),
                          tr.get_end() + np.array([dx * 2.4, dy, 0]),
                          tr.get_end() + np.array([dx * 1.4, dy - 0.35, 0]), tr.get_end()],
                         fill_color=folha, fill_opacity=1, stroke_color=contorno, stroke_width=6)
                  for dx, dy in [(-1, 0.5), (-0.8, -0.5), (0.9, 0.55), (0.8, -0.45), (0.1, 1.0)]])
    return VGroup(tr, fo)


def _faixas(g, W, H, cores):
    y = H / 2
    for cor, frac in cores:
        alt = H * frac
        g.add(Polygon(*V._contorno_rasgado(W + 2, alt, dente=0.05, semente=int(y * 10) % 97),
                      fill_color=cor, fill_opacity=1, stroke_width=0).move_to([0, y - alt / 2 + 0.05, 0]))
        y -= alt
    return y


def varanda(cenario="tarde"):
    W, H = config.frame_width, config.frame_height
    g = VGroup()
    noite = cenario == "noite"
    ceu = ([("#1e1b3a", 0.16), ("#2c2550", 0.13), ("#40306a", 0.12), ("#5a3a70", 0.10)] if noite else
           [("#f6c86a", 0.16), ("#f0a15a", 0.13), ("#e07a5f", 0.12), ("#c96a6a", 0.10)])
    mar_topo = _faixas(g, W, H, ceu)
    if noite:
        rng = np.random.default_rng(3)
        g.add(*[Dot([rng.uniform(-W / 2, W / 2), rng.uniform(H * 0.12, H / 2 - 0.2), 0],
                    radius=rng.uniform(0.02, 0.05), color="#fff4d0") for _ in range(40)])
        astro_x = 1.8
        lua = Circle(radius=0.85, fill_color="#fff4d0", fill_opacity=1, stroke_color="#e9d8a6",
                     stroke_width=6).move_to([astro_x, H * 0.30, 0])
        g.add(lua, Circle(radius=0.85, fill_color="#1e1b3a", fill_opacity=1, stroke_width=0)
              .move_to(lua.get_center() + LEFT * 0.35 + UP * 0.15))
    else:
        astro_x = -1.4
        g.add(Circle(radius=1.15, fill_color="#fff0b8", fill_opacity=1, stroke_color="#f6c86a",
                     stroke_width=8).move_to([astro_x, H * 0.22, 0]))
    mar = Polygon(*V._contorno_rasgado(W + 2, 3.2, dente=0.06, semente=13),
                  fill_color="#15324a" if noite else "#2f6f8f", fill_opacity=1,
                  stroke_width=0).move_to([0, mar_topo - 1.5, 0])
    ondas = VGroup(*[Line([-W / 2 + 0.4 + (i % 3) * 0.6, mar_topo - 0.5 - i * 0.42, 0],
                          [-W / 2 + 1.7 + (i % 3) * 0.6, mar_topo - 0.5 - i * 0.42, 0],
                          stroke_color="#7fa6c0" if noite else "#bfe0ea", stroke_width=5,
                          stroke_opacity=0.6 if noite else 0.8) for i in range(6)])
    refl = VGroup(*[Line([astro_x - 0.5, mar_topo - 0.35 - i * 0.45, 0], [astro_x + 0.5, mar_topo - 0.35 - i * 0.45, 0],
                         stroke_color="#fff4d0" if noite else "#ffe9a8", stroke_width=6,
                         stroke_opacity=0.6) for i in range(4)])
    g.add(mar, ondas, refl)
    areia_topo = mar_topo - 3.0
    g.add(Polygon(*V._contorno_rasgado(W + 2, 4.0, dente=0.07, semente=21),
                  fill_color="#6e6a86" if noite else "#e8d6ad", fill_opacity=1,
                  stroke_width=0).move_to([0, areia_topo - 1.9, 0]))
    if noite:
        g.add(_coqueiro(W / 2 - 0.9, areia_topo, tronco="#2a2238", folha="#1a2a2a"))
    else:
        g.add(_coqueiro(W / 2 - 0.9, areia_topo))
    piso_y = -H / 2 + 2.3
    g.add(Rectangle(width=W + 2, height=2.6, fill_color="#5e3f2a" if noite else "#b1794c",
                    fill_opacity=1, stroke_width=0).move_to([0, piso_y - 1.3, 0]))
    g.add(*[Line([x, piso_y, 0], [x, piso_y - 2.6, 0], stroke_color="#3e2a1c" if noite else "#8a5a3c",
                 stroke_width=4, stroke_opacity=0.8) for x in np.arange(-W / 2, W / 2 + 1, 0.9)])
    g.add(Line([-W / 2 - 1, piso_y, 0], [W / 2 + 1, piso_y, 0],
               stroke_color="#3e2a1c" if noite else "#8a5a3c", stroke_width=10))
    if noite:  # varal de lâmpadas
        g.add(_curva([[-W / 2 - 0.3, H * 0.36, 0], [0, H * 0.31, 0], [W / 2 + 0.3, H * 0.36, 0]],
                     stroke_color=PT, stroke_width=4))
        for x in np.linspace(-W / 2 + 0.4, W / 2 - 0.4, 9):
            yy = H * 0.31 + 0.05 * (x ** 2) / 4 - 0.2
            g.add(Circle(radius=0.28, fill_color="#ffd27a", fill_opacity=0.25, stroke_width=0).move_to([x, yy, 0]))
            g.add(Circle(radius=0.11, fill_color="#ffe3a0", fill_opacity=1, stroke_color=PT,
                         stroke_width=3).move_to([x, yy, 0]))
    return dict(grupo=g, piso_y=piso_y)
