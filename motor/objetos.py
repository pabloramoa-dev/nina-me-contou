"""objetos.py — biblioteca de artes em recorte de papel da Nina (topo do quadro).

Uso no roteiro: "arte": ["tipo", "argumento"]  — argumento é opcional.
Tipos (ver CATALOGO no fim): titulo, direct, conversa, notificacao, celular,
haltere, batom, chave_hotel, pulseira, cracha, perfume, alianca, estetoscopio,
relogio, presente, carro, porta, foto, calendario, extrato, mala, mapa, cafe,
caneca, coracao, interrogacao, manchete, manchete_v, carimbo, jornal, seguir.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from manim import *
import numpy as np
import dvh_vox_papel as V

PT = V.PT
VERM, AMAR, VERDE, AZUL = "#e2483c", "#f2d24b", "#2f6f5e", "#3a6fd8"
PAPEL = "#f4f0e4"


def _T(txt, tam=28, cor="#111111", peso=BOLD):
    # Pango come espaços em fonte pequena: gera grande e reduz
    base = max(tam, 48)
    return Text(str(txt), font=V.FONTE, weight=peso, font_size=base, color=cor).scale(tam / base)


def _card(w, h, sem, girar=0.03):
    return V.recorte(w, h, cor="recorte", semente=sem, girar=girar)


def _caber(m, w):
    if m.width > w:
        m.scale(w / m.width)
    return m


# ---------------------------------------------------------------- mensagens
def direct(arg="ANÔNIMA"):
    """Cartão de 'mensagem no direct' com quem mandou a história."""
    p = _card(5.2, 3.2, 201)
    c = p.get_center()
    tela = RoundedRectangle(width=4.5, height=2.5, corner_radius=0.25, fill_color="#fbf8f0",
                            fill_opacity=1, stroke_color=PT, stroke_width=7).move_to(c)
    topo = RoundedRectangle(width=4.5, height=0.6, corner_radius=0.2, fill_color=VERM,
                            fill_opacity=1, stroke_color=PT, stroke_width=6).move_to(tela.get_top() + DOWN * 0.3)
    tit = _T("NOVA MENSAGEM", 22, WHITE).move_to(topo)
    av = Circle(radius=0.36, fill_color="#e8c39e", fill_opacity=1, stroke_color=PT,
                stroke_width=5).move_to(c + LEFT * 1.55 + DOWN * 0.25)
    nome = _caber(_T(arg, 30), 2.9).next_to(av, RIGHT, buff=0.25).shift(UP * 0.22)
    linhas = VGroup(*[Line(ORIGIN, RIGHT * w, stroke_color="#b0aa9c", stroke_width=6)
                      for w in (2.6, 1.9)]).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
    linhas.next_to(nome, DOWN, buff=0.18, aligned_edge=LEFT)
    return Group(p, tela, topo, tit, av, nome, linhas)


def conversa(arg="Precisamos conversar."):
    """Balões de WhatsApp com a frase-chave."""
    p = _card(5.6, 3.4, 211, -0.03)
    c = p.get_center()
    b1 = RoundedRectangle(width=2.6, height=0.55, corner_radius=0.2, fill_color="#ffffff",
                          fill_opacity=1, stroke_color=PT, stroke_width=5).move_to(c + UP * 0.95 + LEFT * 0.9)
    l1 = Line(b1.get_left() + RIGHT * 0.25, b1.get_right() + LEFT * 0.6, stroke_color="#b0aa9c",
              stroke_width=6)
    txt = _caber(_P(_quebra(arg, 22), 26, "#111111"), 4.3)
    b2 = RoundedRectangle(width=txt.width + 0.5, height=txt.height + 0.4, corner_radius=0.22,
                          fill_color="#c9f0b8", fill_opacity=1, stroke_color=PT, stroke_width=6)
    b2.move_to(c + DOWN * 0.35 + RIGHT * (2.5 - b2.width / 2 - 0.2))
    txt.move_to(b2)
    ticks = _T("✓✓", 20, AZUL).next_to(b2, DOWN, buff=0.06, aligned_edge=RIGHT)
    return Group(p, b1, l1, b2, txt, ticks)


def notificacao(arg="Nova notificação"):
    p = _card(5.8, 2.6, 221)
    c = p.get_center()
    ban = RoundedRectangle(width=5.2, height=1.6, corner_radius=0.3, fill_color="#fbf8f0",
                           fill_opacity=1, stroke_color=PT, stroke_width=7).move_to(c)
    ic = RoundedRectangle(width=0.8, height=0.8, corner_radius=0.18, fill_color=VERM,
                          fill_opacity=1, stroke_color=PT, stroke_width=5).move_to(ban.get_left() + RIGHT * 0.65)
    sino = _T("!", 34, WHITE).move_to(ic)
    t = _caber(_P(_quebra(arg, 20), 26, "#111111"), 3.6)
    t.next_to(ic, RIGHT, buff=0.3)
    return Group(p, ban, ic, sino, t)


def celular(arg=None):
    p = _card(3.2, 4.4, 61, 0.05)
    c = p.get_center()
    tela = RoundedRectangle(width=2.3, height=3.5, corner_radius=0.2, fill_color="#1c1c1e",
                            fill_opacity=1, stroke_color=PT, stroke_width=7).move_to(c)
    g = Group(p, tela)
    if arg:
        b = RoundedRectangle(width=2.0, height=1.0, corner_radius=0.15, fill_color="#fbf8f0",
                             fill_opacity=1, stroke_width=0).move_to(c + UP * 0.8)
        g.add(b, _caber(_P(_quebra(arg, 14), 20, "#111"), 1.8).move_to(b))
    else:
        g.add(*[Line(c + LEFT * 0.8 + DOWN * (0.2 + i * 0.35), c + LEFT * 0.8 + RIGHT * w + DOWN * (0.2 + i * 0.35),
                     stroke_color="#9aa0a6", stroke_width=6) for i, w in enumerate([1.6, 1.1, 1.4])])
    return g


# ---------------------------------------------------------------- lugares e pessoas
def haltere(arg=None):
    p = _card(5.0, 3.0, 231)
    c = p.get_center()
    barra = Line(c + LEFT * 1.6, c + RIGHT * 1.6, stroke_color="#6b6b6b", stroke_width=18)
    pesos = VGroup(*[RoundedRectangle(width=0.45, height=h, corner_radius=0.08, fill_color="#2b2b2b",
                                      fill_opacity=1, stroke_color=PT, stroke_width=5).move_to(c + RIGHT * x)
                     for x, h in [(-1.35, 1.7), (-0.9, 1.3), (0.9, 1.3), (1.35, 1.7)]])
    return Group(p, barra, pesos)


def batom(arg=None):
    """Colarinho de camisa branca com marca de batom."""
    p = _card(4.6, 3.6, 241)
    c = p.get_center()
    cam = Rectangle(width=3.4, height=2.6, fill_color="#fbf8f0", fill_opacity=1,
                    stroke_color=PT, stroke_width=7).move_to(c + DOWN * 0.2)
    top = cam.get_top()
    decote = Polygon(top + LEFT * 0.45, top + RIGHT * 0.45, top + DOWN * 0.7, fill_color="#e8c39e",
                     fill_opacity=1, stroke_color=PT, stroke_width=6)
    gola = VGroup(*[Polygon(top + s * RIGHT * 0.45, top + s * RIGHT * 1.25 + DOWN * 0.15,
                            top + s * RIGHT * 0.75 + DOWN * 0.95, top + DOWN * 0.7,
                            fill_color="#ece6d6", fill_opacity=1, stroke_color=PT, stroke_width=6)
                    for s in (-1, 1)])
    botoes = VGroup(*[Dot(top + DOWN * (1.05 + i * 0.5), radius=0.07, color="#b0aa9c") for i in range(3)])
    lab = VGroup(Ellipse(width=0.62, height=0.24, fill_color=VERM, fill_opacity=0.9, stroke_width=0),
                 Ellipse(width=0.56, height=0.22, fill_color=VERM, fill_opacity=0.9, stroke_width=0).shift(DOWN * 0.17)
                 ).rotate(0.35).move_to(top + RIGHT * 0.95 + DOWN * 0.45)
    return Group(p, cam, decote, gola, botoes, lab)


def chave_hotel(arg="QUARTO 214"):
    p = _card(4.8, 3.2, 251, -0.04)
    c = p.get_center()
    cart = RoundedRectangle(width=3.6, height=2.2, corner_radius=0.2, fill_color="#1f2a44",
                            fill_opacity=1, stroke_color=PT, stroke_width=7).move_to(c)
    faixa = Rectangle(width=3.6, height=0.35, fill_color=AMAR, fill_opacity=1,
                      stroke_width=0).move_to(cart.get_bottom() + UP * 0.45)
    t = _caber(_T(arg, 30, "#fbf8f0"), 3.2).move_to(cart.get_center() + UP * 0.35)
    return Group(p, cart, faixa, t)


def pulseira(arg="VIP"):
    """Pulseira de balada (neon)."""
    p = _card(4.6, 3.0, 261)
    c = p.get_center()
    arco = Ellipse(width=3.4, height=1.4, stroke_color="#ff3fa4", stroke_width=26).move_to(c)
    borda = Ellipse(width=3.4, height=1.4, stroke_color=PT, stroke_width=36).move_to(c)
    tag = V.recorte(1.3, 0.6, cor="amarelo", semente=262).move_to(c + DOWN * 0.7)
    return Group(p, borda, arco, tag, _T(arg, 24).move_to(tag))


def cracha(arg="VISITANTE"):
    p = _card(4.0, 4.4, 271, 0.04)
    c = p.get_center()
    fita = VGroup(Line(c + UP * 2.0 + LEFT * 0.6, c + UP * 1.0, stroke_color=AZUL, stroke_width=14),
                  Line(c + UP * 2.0 + RIGHT * 0.6, c + UP * 1.0, stroke_color=AZUL, stroke_width=14))
    cart = RoundedRectangle(width=2.6, height=2.9, corner_radius=0.18, fill_color="#fbf8f0",
                            fill_opacity=1, stroke_color=PT, stroke_width=7).move_to(c + DOWN * 0.45)
    foto = Rectangle(width=1.0, height=1.1, fill_color="#c9d7cf", fill_opacity=1,
                     stroke_color=PT, stroke_width=5).move_to(cart.get_center() + UP * 0.5)
    t = _caber(VGroup(*[_T(l, 24) for l in _quebra(arg, 12)]).arrange(DOWN, buff=0.06), 2.3).move_to(cart.get_center() + DOWN * 0.75)
    return Group(p, fita, cart, foto, t)


def perfume(arg=None):
    p = _card(3.8, 4.0, 281)
    c = p.get_center()
    fr = RoundedRectangle(width=1.9, height=2.0, corner_radius=0.3, fill_color="#f2b8c6",
                          fill_opacity=1, stroke_color=PT, stroke_width=8).move_to(c + DOWN * 0.5)
    tampa = Rectangle(width=0.7, height=0.6, fill_color=OURO_C, fill_opacity=1, stroke_color=PT,
                      stroke_width=6).next_to(fr, UP, buff=0)
    rot = V.recorte(1.2, 0.5, cor="recorte", semente=283).move_to(fr)
    nuvem = VGroup(*[Circle(radius=r, stroke_color="#b9b2a2", stroke_width=5).move_to(c + RIGHT * x + UP * y)
                     for x, y, r in [(1.2, 1.3, 0.14), (1.5, 1.0, 0.1), (1.0, 1.6, 0.08)]])
    return Group(p, fr, tampa, rot, nuvem)


OURO_C = "#d8b23f"


def alianca(arg=None):
    p = _card(4.2, 3.4, 291, -0.03)
    c = p.get_center()
    a1 = Circle(radius=0.8, stroke_color=PT, stroke_width=34).move_to(c + LEFT * 0.45)
    a1b = Circle(radius=0.8, stroke_color=OURO_C, stroke_width=22).move_to(a1)
    a2 = Circle(radius=0.8, stroke_color=PT, stroke_width=34).move_to(c + RIGHT * 0.55 + DOWN * 0.1)
    a2b = Circle(radius=0.8, stroke_color=OURO_C, stroke_width=22).move_to(a2)
    g = Group(p, a1, a1b, a2, a2b)
    if arg:
        g.add(V.etiqueta(arg, tam=26).move_to(c + DOWN * 1.35))
    return g


def estetoscopio(arg=None):
    p = _card(4.4, 3.8, 301)
    c = p.get_center()
    tubo = _cv([c + LEFT * 1.2 + UP * 1.2, c + LEFT * 1.4 + DOWN * 0.3, c + DOWN * 1.0,
                c + RIGHT * 1.0 + DOWN * 0.4, c + RIGHT * 1.1 + UP * 0.5], PT, 16)
    tubo2 = _cv([c + LEFT * 1.2 + UP * 1.2, c + LEFT * 1.4 + DOWN * 0.3, c + DOWN * 1.0,
                 c + RIGHT * 1.0 + DOWN * 0.4, c + RIGHT * 1.1 + UP * 0.5], AZUL, 9)
    disco = Circle(radius=0.38, fill_color="#c0c4c8", fill_opacity=1, stroke_color=PT,
                   stroke_width=7).move_to(c + RIGHT * 1.1 + UP * 0.85)
    return Group(p, tubo, tubo2, disco)


def relogio(arg="06:00"):
    p = _card(4.0, 3.6, 311, 0.04)
    c = p.get_center()
    cx = RoundedRectangle(width=3.2, height=1.6, corner_radius=0.25, fill_color="#1c1c1e",
                          fill_opacity=1, stroke_color=PT, stroke_width=8).move_to(c)
    t = _T(arg, 60, "#ff5a4d").move_to(cx)
    pes = VGroup(*[Line(cx.get_bottom() + RIGHT * x, cx.get_bottom() + RIGHT * x + DOWN * 0.3,
                        stroke_color=PT, stroke_width=10) for x in (-1.1, 1.1)])
    return Group(p, cx, t, pes)


def presente(arg=None):
    p = _card(4.0, 3.8, 321)
    c = p.get_center()
    cx = Rectangle(width=2.4, height=1.9, fill_color=VERM, fill_opacity=1, stroke_color=PT,
                   stroke_width=8).move_to(c + DOWN * 0.4)
    fitav = Rectangle(width=0.35, height=1.9, fill_color=AMAR, fill_opacity=1, stroke_width=0).move_to(cx)
    tampa = Rectangle(width=2.7, height=0.5, fill_color=VERM, fill_opacity=1, stroke_color=PT,
                      stroke_width=8).next_to(cx, UP, buff=0)
    laco = VGroup(*[Ellipse(width=0.8, height=0.45, fill_color=AMAR, fill_opacity=1, stroke_color=PT,
                            stroke_width=6).rotate(a).move_to(tampa.get_top() + RIGHT * dx + UP * 0.15)
                    for a, dx in [(0.4, -0.35), (-0.4, 0.35)]])
    g = Group(p, cx, fitav, tampa, laco)
    if arg:
        g.add(V.recorte(1.5, 0.5, cor="amarelo", semente=325).move_to(cx.get_corner(DR) + UP * 0.2),
              _T(arg, 20).move_to(cx.get_corner(DR) + UP * 0.2))
    return g


def carro(arg=None):
    p = _card(5.4, 3.2, 331, -0.03)
    c = p.get_center()
    corpo = RoundedRectangle(width=4.0, height=1.0, corner_radius=0.3, fill_color="#3a6fd8",
                             fill_opacity=1, stroke_color=PT, stroke_width=8).move_to(c + DOWN * 0.2)
    teto = Polygon(c + LEFT * 1.1 + UP * 0.3, c + LEFT * 0.6 + UP * 1.0, c + RIGHT * 0.8 + UP * 1.0,
                   c + RIGHT * 1.3 + UP * 0.3, fill_color="#3a6fd8", fill_opacity=1, stroke_color=PT,
                   stroke_width=8)
    jan = Polygon(c + LEFT * 0.85 + UP * 0.35, c + LEFT * 0.5 + UP * 0.85, c + RIGHT * 0.7 + UP * 0.85,
                  c + RIGHT * 1.05 + UP * 0.35, fill_color="#c9e3ef", fill_opacity=1, stroke_color=PT,
                  stroke_width=5)
    rodas = VGroup(*[Circle(radius=0.42, fill_color="#222", fill_opacity=1, stroke_color=PT,
                            stroke_width=6).move_to(c + RIGHT * x + DOWN * 0.75) for x in (-1.2, 1.2)])
    g = Group(p, teto, jan, corpo, rodas)
    if arg:
        pl = Rectangle(width=1.3, height=0.4, fill_color="#fbf8f0", fill_opacity=1, stroke_color=PT,
                       stroke_width=4).move_to(corpo.get_center())
        g.add(pl, _caber(_T(arg, 18), 1.2).move_to(pl))
    return g


def porta(arg=None):
    p = _card(4.0, 4.6, 161, -0.03)
    c = p.get_center()
    bat = Rectangle(width=2.7, height=3.9, fill_color="#8a8172", fill_opacity=1, stroke_color=PT,
                    stroke_width=8).move_to(c)
    fo = Rectangle(width=2.3, height=3.5, fill_color="#7d5a3c", fill_opacity=1, stroke_color=PT,
                   stroke_width=7).move_to(c)
    pain = VGroup(*[Rectangle(width=1.5, height=1.2, stroke_color="#5e4229", stroke_width=6,
                              fill_opacity=0).move_to(c + UP * dy) for dy in (0.85, -0.75)])
    maca = Circle(radius=0.14, fill_color=OURO_C, fill_opacity=1, stroke_color=PT,
                  stroke_width=5).move_to(c + RIGHT * 0.85)
    g = Group(p, bat, fo, pain, maca)
    if arg:
        g.add(V.etiqueta(str(arg), cor="amarelo", tam=28).move_to(c + UP * 1.85))
    return g


def foto(arg=None):
    p = _card(4.4, 4.2, 141, -0.05)
    c = p.get_center()
    mold = Rectangle(width=3.2, height=3.5, fill_color="#fbf8f0", fill_opacity=1, stroke_color=PT,
                     stroke_width=8).move_to(c)
    img = Rectangle(width=2.7, height=2.5, fill_color="#c9d7cf", fill_opacity=1, stroke_color=PT,
                    stroke_width=6).move_to(c + UP * 0.35)
    duas = VGroup()
    for dx, cor in ((-0.55, VERM), (0.55, VERDE)):
        cab = Circle(radius=0.28, fill_color="#e8c39e", fill_opacity=1, stroke_color=PT,
                     stroke_width=6).move_to(img.get_center() + RIGHT * dx + UP * 0.45)
        tor = Polygon([-0.38, 0, 0], [0.38, 0, 0], [0.5, -0.95, 0], [-0.5, -0.95, 0], fill_color=cor,
                      fill_opacity=1, stroke_color=PT, stroke_width=6).move_to(cab.get_center() + DOWN * 0.72)
        duas.add(tor, cab)
    g = Group(p, mold, img, duas)
    if arg:
        g.add(_caber(_T(arg, 24), 2.8).move_to(mold.get_bottom() + UP * 0.4))
    return g


def calendario(arg="SEGUNDA"):
    p = _card(4.0, 3.6, 71, -0.04)
    c = p.get_center()
    topo = Rectangle(width=3.0, height=0.6, fill_color=VERM, fill_opacity=1, stroke_color=PT,
                     stroke_width=6).move_to(c + UP * 1.05)
    mes = _caber(_T(arg, 24, WHITE), 2.7).move_to(topo)
    grade = VGroup(*[Square(side_length=0.5, stroke_color="#8a8172", stroke_width=3).move_to(
        c + RIGHT * (i - 2) * 0.56 + DOWN * (j * 0.56 - 0.1)) for j in range(3) for i in range(5)])
    x = VGroup(Line(LEFT * 0.2 + UP * 0.2, RIGHT * 0.2 + DOWN * 0.2, stroke_color=VERM, stroke_width=8),
               Line(LEFT * 0.2 + DOWN * 0.2, RIGHT * 0.2 + UP * 0.2, stroke_color=VERM, stroke_width=8)
               ).move_to(grade[7].get_center())
    return Group(p, topo, mes, grade, x)


def extrato(arg=None):
    p = _card(4.8, 4.4, 131, 0.03)
    c = p.get_center()
    folha = Rectangle(width=3.8, height=3.6, fill_color=PAPEL, fill_opacity=1, stroke_color=PT,
                      stroke_width=7).move_to(c)
    topo = Rectangle(width=3.8, height=0.45, fill_color=VERDE, fill_opacity=1, stroke_color=PT,
                     stroke_width=6).move_to(folha.get_top() + DOWN * 0.22)
    lin = VGroup(*[Line(c + UP * (1.1 - j * 0.45) + LEFT * 1.6, c + UP * (1.1 - j * 0.45) + RIGHT * 1.6,
                        stroke_color="#8a8172", stroke_width=6) for j in range(6)])
    g = Group(p, folha, topo, lin)
    if arg:
        m = Rectangle(width=3.5, height=0.5, fill_color=AMAR, fill_opacity=0.9, stroke_width=0).move_to(c + DOWN * 0.25)
        g.add(m, _caber(_T(arg, 24), 3.3).move_to(m))
    return g


def mala(arg=None):
    p = _card(4.4, 3.8, 111, -0.04)
    c = p.get_center()
    corpo = RoundedRectangle(width=2.9, height=2.1, corner_radius=0.18, fill_color="#7d5a3c",
                             fill_opacity=1, stroke_color=PT, stroke_width=8).move_to(c + DOWN * 0.15)
    alca = Arc(radius=0.46, start_angle=0, angle=PI, arc_center=corpo.get_top()).set_stroke(PT, 12)
    faixa = Rectangle(width=2.9, height=0.34, fill_color="#5e4229", fill_opacity=1, stroke_color=PT,
                      stroke_width=6).move_to(corpo)
    return Group(p, corpo, faixa, alca)


def mapa(arg=None):
    p = _card(5.0, 4.0, 121, 0.03)
    c = p.get_center()
    fundo = Rectangle(width=4.1, height=3.1, fill_color="#e8e2d3", fill_opacity=1, stroke_color=PT,
                      stroke_width=7).move_to(c)
    ruas = VGroup(*[Line(c + RIGHT * dx + UP * 1.5, c + RIGHT * dx + DOWN * 1.5, stroke_color="#c3bba7",
                         stroke_width=9) for dx in (-1.1, 0.35)],
                  *[Line(c + LEFT * 2 + UP * dy, c + RIGHT * 2 + UP * dy, stroke_color="#c3bba7",
                         stroke_width=9) for dy in (0.95, -0.55)])
    rota = VMobject(stroke_color=VERM, stroke_width=14)
    rota.set_points_as_corners([c + LEFT * 1.6 + DOWN * 1.15, c + LEFT * 1.1 + DOWN * 1.15,
                                c + LEFT * 1.1 + UP * 0.95, c + RIGHT * 0.35 + UP * 0.95, c + RIGHT * 0.35 + DOWN * 0.1])
    pino = Circle(radius=0.24, fill_color=VERM, fill_opacity=1, stroke_color=PT,
                  stroke_width=6).move_to(rota.get_end() + UP * 0.2)
    return Group(p, fundo, ruas, rota, pino)


def cafe(arg=None):
    p = _card(4.2, 3.6, 131, 0.04)
    c = p.get_center()
    pires = Ellipse(width=2.9, height=0.7, fill_color="#efe9db", fill_opacity=1, stroke_color=PT,
                    stroke_width=7).move_to(c + DOWN * 0.95)
    corpo = Polygon([-0.85, 0.75, 0], [0.85, 0.75, 0], [0.62, -0.62, 0], [-0.62, -0.62, 0],
                    fill_color=PAPEL, fill_opacity=1, stroke_color=PT, stroke_width=8).shift(c + DOWN * 0.1)
    asa = Arc(radius=0.42, start_angle=-PI / 2, angle=PI, arc_center=c + RIGHT * 0.92).set_stroke(PT, 12)
    return Group(p, pires, asa, corpo)


def caneca(arg="2019"):
    p = _card(4.0, 3.4, 151, 0.04)
    c = p.get_center()
    corpo = RoundedRectangle(width=1.8, height=1.9, corner_radius=0.14, fill_color=PAPEL, fill_opacity=1,
                             stroke_color=PT, stroke_width=8).move_to(c)
    alca = Arc(radius=0.42, start_angle=-PI / 2, angle=PI,
               arc_center=corpo.get_right() + RIGHT * 0.1).set_stroke(PT, 14)
    return Group(p, alca, corpo, _coracao(0.9).move_to(c + UP * 0.22),
                 _T(arg or "", 26, "#8a8172").move_to(c + DOWN * 0.5))


def coracao(arg=None):
    """Coração partido."""
    p = _card(4.0, 3.6, 341)
    c = p.get_center()
    h = _coracao(2.4).move_to(c)
    rach = VMobject(stroke_color=PT, stroke_width=10)
    rach.set_points_as_corners([h.get_top() + DOWN * 0.15, c + LEFT * 0.2 + UP * 0.3, c + RIGHT * 0.2,
                                c + LEFT * 0.15 + DOWN * 0.4, h.get_bottom() + UP * 0.1])
    return Group(p, h, rach)


def interrogacao(arg=None):
    p = _card(3.4, 3.8, 351, -0.05)
    return Group(p, _T("?", 160, VERM).move_to(p))


def seguir(arg="SEGUE A NINA"):
    g = Group(V.manchete(arg, cor_papel="amarelo", tam=46))
    return g


def titulo(arg, ep=None, parte=None):
    """Selo de abertura: 'EP 01 · PARTE 1' + nome do episódio."""
    cor = "vermelho" if parte == 2 else "amarelo"
    m = V.manchete(arg, cor_papel=cor, cor_texto="#fbf8f0" if cor == "vermelho" else None, tam=58)
    if ep is None:
        return Group(m)
    et = _T(f"EP {ep:02d} · PARTE {parte}", 30)
    fb = V.recorte(et.width + 0.5, et.height + 0.35, cor="recorte", semente=9)
    return Group(Group(fb, et.move_to(fb)), m).arrange(DOWN, buff=0.15)


# ---------------------------------------------------------------- auxiliares
def _cv(pts, cor, w):
    m = VMobject(stroke_color=cor, stroke_width=w)
    m.set_points_smoothly(pts)
    return m


def _coracao(tam):
    pts = []
    for t in np.linspace(0, TAU, 120):
        x = 16 * np.sin(t) ** 3
        y = 13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)
        pts.append(np.array([x, y, 0]) / 34.0)
    h = VMobject(fill_color=VERM, fill_opacity=1, stroke_color=PT, stroke_width=6)
    h.set_points_smoothly(pts)
    return h.scale(tam)


def _P(linhas, tam, cor="#111111"):
    return VGroup(*[_T(l, tam, cor) for l in linhas]).arrange(DOWN, buff=0.08, aligned_edge=LEFT)


def _quebra(txt, larg):
    linhas, atual = [], ""
    for w in str(txt).split():
        if len(atual) + len(w) + 1 > larg and atual:
            linhas.append(atual); atual = w
        else:
            atual = (atual + " " + w).strip()
    if atual:
        linhas.append(atual)
    return linhas[:4] or [" "]


CATALOGO = dict(direct=direct, conversa=conversa, notificacao=notificacao, celular=celular,
                haltere=haltere, batom=batom, chave_hotel=chave_hotel, pulseira=pulseira, cracha=cracha,
                perfume=perfume, alianca=alianca, estetoscopio=estetoscopio, relogio=relogio,
                presente=presente, carro=carro, porta=porta, foto=foto, calendario=calendario,
                extrato=extrato, mala=mala, mapa=mapa, cafe=cafe, caneca=caneca, coracao=coracao,
                interrogacao=interrogacao, seguir=seguir)


def arte(tipo, arg=None):
    if tipo in CATALOGO:
        return CATALOGO[tipo](arg) if arg is not None else CATALOGO[tipo]()
    if tipo == "manchete":
        return Group(V.manchete(arg, cor_papel="amarelo", tam=46))
    if tipo == "manchete_v":
        return Group(V.manchete(arg, cor_papel="vermelho", cor_texto="#fbf8f0", tam=46))
    if tipo == "carimbo":
        return Group(V.carimbo(arg, cor="vermelho", tam=50, girar=-0.2))
    if tipo == "jornal":
        return Group(V.recorte_jornal(arg, linhas=5, w=5.0))
    return Group(V.manchete(arg or "…", tam=40))
