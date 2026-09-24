"""
dvh_vox_papel — camada visual "Vox colagem de papel" do DVH.

Ideia (portada do bestuserever121/vox-explainer, MIT, reescrita em Manim):
folha de papel com grão e vincos, recortes com borda RASGADA, fita adesiva,
retícula de pontos (halftone), manchete recortada com desalinhamento de
impressão, recorte de jornal, carimbo, seta grossa e câmera em "degraus" de
12fps que termina se afastando para mostrar o quadro inteiro.

O personagem continua 100% da dvh_lib (idêntico entre cenas). Aqui ele só
ganha a borda branca de ADESIVO + sombra, que é o que faz ele "morar" na colagem.

Desempenho (medido): a retícula é PNG (ImageMobject) e custa pouco. O grão do
papel NÃO entra no Manim (imagem do tamanho da folha deixou o render ~10x mais
lento); ele é aplicado no fim, por ffmpeg, com aplicar_textura().

Estilos (mesmos nomes de paleta em todos, então trocar o estilo não quebra a cena):
    "papel"  — branco quente, grão e vincos (padrão)
    "noite"  — quase preto, bom para o noir do DVH
    "planta" — papel quadriculado azul, técnico (explicar o esquema do golpe)
    "riso"   — creme com duotone deslocado
"""
from manim import *
import numpy as np
import os, hashlib, tempfile
from PIL import Image, ImageDraw, ImageFilter

FONTE = "Poppins"
PT = "#111111"
CACHE = os.path.join(tempfile.gettempdir(), "dvh_vox_cache")
os.makedirs(CACHE, exist_ok=True)

ESTILOS = {
    "papel":  dict(fundo="#efe7d6", tinta="#1a1a1a", grao=0.10, amarelo="#ffd240",
                   vermelho="#e2483c", azul="#3a6fd8", verde="#32a06e",
                   recorte="#f7f3ea", jornal="#e4ddcc", fita="#f3e9b8", sombra=0.28),
    "noite":  dict(fundo="#16161b", tinta="#f2efe6", grao=0.16, amarelo="#ffd240",
                   vermelho="#ff5a4d", azul="#4d86ff", verde="#3fc185",
                   recorte="#26262e", jornal="#2e2e36", fita="#6b6440", sombra=0.55),
    "planta": dict(fundo="#1f4f8f", tinta="#eaf2ff", grao=0.06, amarelo="#ffe27a",
                   vermelho="#ff7a6b", azul="#9cc4ff", verde="#7fe0b0",
                   recorte="#2a5fa6", jornal="#2f6ab5", fita="#c9dcf5", sombra=0.35),
    "riso":   dict(fundo="#f4ecd8", tinta="#1d2a5a", grao=0.12, amarelo="#ffcf3a",
                   vermelho="#ff4f6d", azul="#2f5bd3", verde="#1fa37a",
                   recorte="#fbf6ea", jornal="#efe3c6", fita="#ffd9e0", sombra=0.22),
}
_EST = {"atual": "papel"}


def estilo(nome=None):
    """estilo("noite") troca; estilo() devolve a paleta atual."""
    if nome:
        _EST["atual"] = nome
    return ESTILOS[_EST["atual"]]


def _cor(nome):
    p = estilo()
    return p.get(nome, nome)


def _hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _png(chave, gerar):
    """Cache em disco: a mesma textura não é gerada duas vezes."""
    nome = hashlib.md5(chave.encode()).hexdigest()[:12] + ".png"
    caminho = os.path.join(CACHE, nome)
    if not os.path.exists(caminho):
        gerar().save(caminho)
    return caminho


# =====================================================================
#  FUNDO: folha de papel
# =====================================================================
def folha(largura=None, altura=None, semente=3, vincos=True):
    """Folha de papel: cor base + vincos em vetor (barato de renderizar).
    O GRÃO e o escurecimento das bordas NÃO vão aqui: imagem grande em Manim
    deixa o render ~10x mais lento (medido). Eles entram no final, por ffmpeg,
    com aplicar_textura() — custo quase zero."""
    W = largura or config.frame_width * 1.8
    H = altura or config.frame_height * 1.8
    p = estilo(); nome = _EST["atual"]
    rng = np.random.default_rng(semente)
    g = VGroup(Rectangle(width=W, height=H, fill_color=p["fundo"], fill_opacity=1, stroke_width=0))
    escuro = nome in ("noite", "planta")
    if nome == "planta":
        for x in np.arange(-W / 2, W / 2, 0.5):
            g.add(Line([x, -H / 2, 0], [x, H / 2, 0], stroke_color=WHITE, stroke_width=1,
                       stroke_opacity=0.28 if abs(x / 2.5 - round(x / 2.5)) < 1e-6 else 0.12))
        for y in np.arange(-H / 2, H / 2, 0.5):
            g.add(Line([-W / 2, y, 0], [W / 2, y, 0], stroke_color=WHITE, stroke_width=1,
                       stroke_opacity=0.28 if abs(y / 2.5 - round(y / 2.5)) < 1e-6 else 0.12))
    if vincos:
        esc = WHITE if escuro else BLACK
        cla = BLACK if escuro else WHITE
        for _ in range(max(3, int(W / 6))):
            x0 = rng.uniform(-W / 2, W / 2); dx = rng.uniform(-2.5, 2.5)
            a, b = [x0, H / 2, 0], [x0 + dx, -H / 2, 0]
            g.add(Line(a, b, stroke_color=esc, stroke_width=2.5, stroke_opacity=0.07))
            g.add(Line(np.add(a, [0.03, 0, 0]), np.add(b, [0.03, 0, 0]),
                       stroke_color=cla, stroke_width=2.5, stroke_opacity=0.10))
    return g


def textura_png(largura=1920, altura=1080, semente=3):
    """PNG do grão + bordas escurecidas, do tamanho do vídeo (para o ffmpeg)."""
    p = estilo(); nome = _EST["atual"]
    def gerar():
        rng = np.random.default_rng(semente)
        tom = 255 if nome in ("noite", "planta") else 0
        a = (rng.random((altura, largura)) ** 6 * 255 * p["grao"] * 2.2).astype(np.uint8)
        img = Image.new("RGBA", (largura, altura), (tom, tom, tom, 0))
        img.putalpha(Image.fromarray(a))
        v = Image.new("L", (largura, altura), 0)
        ImageDraw.Draw(v).rectangle([0, 0, largura, altura], outline=70, width=int(largura * 0.06))
        v = v.filter(ImageFilter.GaussianBlur(largura * 0.07))
        borda = Image.new("RGBA", (largura, altura), (20, 16, 10, 0)); borda.putalpha(v)
        return Image.alpha_composite(img, borda)
    return _png(f"tex-{nome}-{largura}x{altura}-{semente}", gerar)


def aplicar_textura(entrada, saida, crf=20):
    """Passa o grão de papel por cima do vídeo já renderizado (ffmpeg overlay).
    Rodar ANTES do montador (a textura vai só nas cenas de colagem)."""
    import subprocess, json
    info = json.loads(subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height", "-of", "json", entrada]))["streams"][0]
    tex = textura_png(info["width"], info["height"])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", entrada, "-loop", "1", "-i", tex,
                    "-filter_complex", "[0:v][1:v]overlay=shortest=1:format=auto,format=yuv420p[v]",
                    "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-crf", str(crf),
                    "-preset", "medium", "-c:a", "copy", "-movflags", "+faststart", saida],
                   check=True)
    return saida


# =====================================================================
#  RECORTES
# =====================================================================
def _contorno_rasgado(w, h, dente=0.07, passo=0.12, semente=1):
    """Pontos de um retângulo com as quatro bordas irregulares (papel rasgado)."""
    rng = np.random.default_rng(semente)
    pts = []
    def lado(a, b):
        n = max(2, int(np.linalg.norm(b - a) / passo))
        normal = np.array([-(b - a)[1], (b - a)[0], 0]); normal /= np.linalg.norm(normal)
        for i in range(n):
            t = i / n
            pts.append(a + (b - a) * t + normal * rng.uniform(-dente, dente))
    c = [np.array([-w / 2, -h / 2, 0]), np.array([w / 2, -h / 2, 0]),
         np.array([w / 2, h / 2, 0]), np.array([-w / 2, h / 2, 0])]
    for i in range(4):
        lado(c[i], c[(i + 1) % 4])
    return pts


def recorte(w, h, cor="recorte", girar=0.0, sombra=True, semente=1, borda_branca=True):
    """Pedaço de papel rasgado. cor aceita nome da paleta ('amarelo') ou hex."""
    p = estilo()
    pts = _contorno_rasgado(w, h, semente=semente)
    g = VGroup()
    if sombra:
        g.add(Polygon(*pts, fill_color=BLACK, fill_opacity=p["sombra"], stroke_width=0)
              .shift(RIGHT * 0.09 + DOWN * 0.11))
    if borda_branca:   # a fibra branca que aparece no rasgo
        g.add(Polygon(*_contorno_rasgado(w + 0.1, h + 0.1, dente=0.05, semente=semente + 7),
                      fill_color="#fbf8f0", fill_opacity=1, stroke_width=0))
    g.add(Polygon(*pts, fill_color=_cor(cor), fill_opacity=1, stroke_width=0))
    return g.rotate(girar)


def fita(ponto=ORIGIN, girar=0.0, w=1.1, h=0.34):
    """Fita adesiva translúcida com pontas serrilhadas."""
    n = 6; pts = []
    for i in range(n + 1):
        pts.append([-w / 2 + (0.05 if i % 2 else -0.02), -h / 2 + h * i / n, 0])
    dir_ = [[w / 2 + (0.05 if i % 2 else -0.02), h / 2 - h * i / n, 0] for i in range(n + 1)]
    f = Polygon(*(pts + dir_), fill_color=_cor("fita"), fill_opacity=0.88, stroke_width=0)
    return f.rotate(girar).move_to(ponto)


def reticula(w=3.0, h=3.0, cor="vermelho", forma="circulo", passo=26, semente=0):
    """Retícula de pontos (halftone) que diminui do centro para a borda."""
    rgb = _hex_rgb(_cor(cor))
    def gerar():
        px = 900; py = int(px * h / w)
        img = Image.new("RGBA", (px, py), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
        cx, cy = px / 2, py / 2
        for j, y in enumerate(range(0, py + passo, passo)):
            for x in range(0, px + passo, passo):
                xx = x + (passo / 2 if j % 2 else 0)
                if forma == "circulo":
                    dist = np.hypot((xx - cx) / cx, (y - cy) / cy)
                else:   # gradiente diagonal, com borda que some (sem quina dura)
                    dist = (xx / px + y / py) / 2
                    dist = max(dist, np.hypot((xx - cx) / cx, (y - cy) / cy) * 0.95)
                r = max(0.0, (1 - dist)) * passo * 0.55
                if r > 1:
                    d.ellipse([xx - r, y - r, xx + r, y + r], fill=rgb + (255,))
        return img
    im = ImageMobject(_png(f"ret-{cor}-{rgb}-{w}-{h}-{forma}-{passo}", gerar))
    im.stretch_to_fit_width(w).stretch_to_fit_height(h)
    return im


# =====================================================================
#  TIPOGRAFIA DE COLAGEM
# =====================================================================
def manchete(txt, cor_papel="amarelo", cor_texto=None, tam=64, girar=0.04, semente=5,
             desalinho=True, juntar=False):
    """Cada palavra num pedaço de papel rasgado, levemente torto, com o
    desalinhamento de impressão (uma cópia colorida deslocada atrás)."""
    rng = np.random.default_rng(semente)
    p = estilo(); cor_texto = cor_texto or "#111111"
    pecas = Group()
    for i, palavra in enumerate([txt] if juntar else txt.split()):
        t = Text(palavra, font=FONTE, weight=BOLD, font_size=tam, color=_cor(cor_texto))
        papel = recorte(t.width + 0.45, t.height + 0.32, cor=cor_papel, semente=semente + i)
        camadas = [papel]
        if desalinho:
            camadas.append(t.copy().set_color(p["vermelho"]).set_opacity(0.55)
                           .shift(LEFT * 0.035 + UP * 0.03))
        camadas.append(t)
        peca = Group(*camadas).rotate(rng.uniform(-girar, girar) * 2)
        pecas.add(peca)
    pecas.arrange(RIGHT, buff=0.12)
    if pecas.width > config.frame_width * 0.92:
        pecas.arrange_in_grid(cols=max(1, len(pecas) // 2), buff=0.12)
    return pecas


def recorte_jornal(titulo, linhas=6, w=3.2, girar=-0.06, semente=11):
    """Recorte de jornal: manchete serifada + linhas de texto simuladas."""
    p = estilo()
    tit = Text(titulo, font="DejaVu Serif", weight=BOLD, font_size=30, color="#1a1a1a")
    if tit.width > w - 0.4:
        tit.scale((w - 0.4) / tit.width)
    rng = np.random.default_rng(semente)
    corpo = VGroup(*[Line(LEFT * (w / 2 - 0.25), LEFT * (w / 2 - 0.25) + RIGHT * rng.uniform(w * 0.55, w - 0.5),
                          stroke_color="#6d675c", stroke_width=5) for _ in range(linhas)])
    corpo.arrange(DOWN, buff=0.14, aligned_edge=LEFT)
    miolo = VGroup(tit, corpo).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
    papel = recorte(w, miolo.height + 0.6, cor="#e4ddcc" if _EST["atual"] != "noite" else "#d9d2c0",
                    semente=semente, borda_branca=False)
    return Group(papel, miolo.move_to(papel[-1])).rotate(girar)


def carimbo(txt="FRAUDE", cor="vermelho", tam=58, girar=0.22, sobre="fundo"):
    """Carimbo de borracha: moldura dupla, tinta falhada.
    sobre = cor do que fica embaixo (as falhas de tinta têm essa cor):
    "fundo" (na folha) ou "jornal" (em cima de um recorte de jornal)."""
    c = _cor(cor)
    t = Text(txt, font=FONTE, weight=BOLD, font_size=tam, color=c)
    m1 = RoundedRectangle(width=t.width + 0.5, height=t.height + 0.4, corner_radius=0.08,
                          stroke_color=c, stroke_width=9, fill_opacity=0)
    m2 = m1.copy().scale(1.08).set_stroke(width=4)
    g = VGroup(m2, m1, t).rotate(girar)
    # falhas de tinta: riscos da cor do papel por cima
    rng = np.random.default_rng(len(txt))
    falhas = VGroup(*[Line(ORIGIN, RIGHT * rng.uniform(0.1, 0.35), stroke_color=("#d9d2c0" if (sobre == "jornal" and _EST["atual"] == "noite") else _cor(sobre)),
                           stroke_width=rng.uniform(2, 5), stroke_opacity=0.8)
                      .move_to(g.get_center() + RIGHT * rng.uniform(-g.width / 2.3, g.width / 2.3)
                               + UP * rng.uniform(-g.height / 2.5, g.height / 2.5))
                      .rotate(rng.uniform(0, PI)) for _ in range(14)])
    return VGroup(g, falhas)


def etiqueta(txt, cor="tinta", tam=26):
    """Rótulo manuscrito curto (para apontar com seta)."""
    return Text(txt, font=FONTE, weight=BOLD, font_size=tam, color=_cor(cor))


def seta_grossa(inicio, fim, cor="tinta", curva=0.35, largura=12):
    """Seta preta grossa e levemente curva, como traço de pincel."""
    s = CurvedArrow(np.array(inicio), np.array(fim), angle=curva, color=_cor(cor),
                    stroke_width=largura, tip_length=0.34)
    return s


# =====================================================================
#  PERSONAGEM COMO ADESIVO (sem redesenhar: usa o da dvh_lib)
# =====================================================================
def adesivo(pers, espessura=26, sombra=True):
    """Borda branca de adesivo + sombra atrás do personagem da dvh_lib.
    Devolve o VGroup do contorno; ele SEGUE o grupo (respirar, susto, golpe)."""
    G = pers["grupo"] if isinstance(pers, dict) else pers
    p = estilo()
    borda = G.copy().clear_updaters()
    for m in borda.get_family():
        if isinstance(m, VMobject):
            w = m.get_stroke_width()
            m.set_stroke(color="#fbf8f0", width=w + espessura, opacity=1)
            if m.get_fill_opacity() > 0:
                m.set_fill("#fbf8f0", opacity=1)
    grupo = VGroup(borda)
    if sombra:
        sb = borda.copy()
        for m in sb.get_family():
            if isinstance(m, VMobject):
                m.set_stroke(color=BLACK, opacity=p["sombra"])
                if m.get_fill_opacity() > 0:
                    m.set_fill(BLACK, opacity=p["sombra"])
        sb.shift(RIGHT * 0.12 + DOWN * 0.14)
        grupo.add_to_back(sb)
    desloc = grupo.get_center() - G.get_center()
    grupo.add_updater(lambda m: m.move_to(G.get_center() + desloc))
    return grupo


def colar(scene, pers, espessura=26):
    """Atalho: põe adesivo + personagem na cena, adesivo atrás."""
    G = pers["grupo"]
    ad = adesivo(pers, espessura)
    scene.add(ad, G)
    return ad


# =====================================================================
#  MOVIMENTO "PAPEL": 12fps em degraus, entrada colando, câmera do quadro
# =====================================================================
def degraus(rate_func=smooth, fps=12, dur=1.0):
    """Rate function quantizada: o movimento anda em 'passos' de 12fps
    (a trepidação de animação de recorte). O resto do quadro segue a 60fps."""
    n = max(1, int(round(fps * dur)))
    return lambda t: rate_func(np.floor(t * n) / n) if t < 1 else rate_func(1.0)


def colar_entrada(scene, mob, girar=0.18, dur=0.45):
    """Entra como papel colado: cresce um pouco maior, gira e assenta (degraus)."""
    alvo = mob.copy()
    mob.scale(1.35).rotate(girar).set_opacity(0)
    scene.add(mob)
    scene.play(Transform(mob, alvo), run_time=dur, rate_func=degraus(smooth, dur=dur))
    return mob


def _frame(scene):
    return getattr(getattr(scene, "camera", None), "frame", None)


def camera_ate(scene, alvo, z=1.0, dur=1.2, fps=12):
    """Câmera viaja até o alvo (Mobject ou ponto) em degraus de 12fps."""
    fr = _frame(scene)
    if fr is None:
        scene.wait(dur); return
    p = alvo if isinstance(alvo, np.ndarray) else alvo.get_center()
    tgt = fr.copy().set(width=config.frame_width / z).move_to(p)
    scene.play(fr.animate.become(tgt), run_time=dur, rate_func=degraus(smooth, fps, dur))


def revelar_quadro(scene, conteudo, margem=1.08, dur=1.6):
    """Afastamento final: mostra o quadro inteiro — o 'argumento' completo."""
    fr = _frame(scene)
    if fr is None:
        scene.wait(dur); return
    alvo_w = max(conteudo.width, conteudo.height * config.frame_width / config.frame_height) * margem
    tgt = fr.copy().set(width=alvo_w).move_to(conteudo.get_center())
    scene.play(fr.animate.become(tgt), run_time=dur, rate_func=degraus(smooth, 12, dur))


def legenda_papel(txt, tam=30):
    """Legenda do DVH (banda escura + Poppins Bold branco, SEM contorno — lição #4),
    só com a banda levemente torta para conversar com a colagem.
    Presa à câmera: chame fixar_legenda() se a câmera se move."""
    t = Text(txt, font=FONTE, weight=BOLD, font_size=tam, color=WHITE)
    if t.width > 11.2:
        t.scale(11.2 / t.width)
    band = Polygon(*_contorno_rasgado(t.width + 0.8, t.height + 0.45, dente=0.03, semente=2),
                   fill_color=BLACK, fill_opacity=0.72, stroke_width=0)
    return VGroup(band, t).to_edge(DOWN, buff=0.4)


def fixar_legenda(scene, leg):
    """Mantém a legenda no rodapé do enquadramento mesmo com a câmera andando."""
    fr = _frame(scene)
    if fr is None:
        return leg
    base_w = config.frame_width
    off = leg.get_center() - ORIGIN
    h0 = leg.height
    def _u(m):
        k = fr.width / base_w
        m.set(height=h0 * k)
        m.move_to(fr.get_center() + off * k)
    leg.add_updater(_u); _u(leg)
    return leg
