"""banco_imagens.py — fotos reais de banco de imagens no estilo colagem da Nina.

O motor baixa SOZINHO, a cada episódio, as fotos que o roteiro pede:

  1. Pedido explícito numa batida (recomendado ao escrever roteiros novos):
         "foto": "glove compartment car"            # busca em inglês
         "foto": ["velvet ring box", "CAIXINHA"]    # busca + legenda na polaroid
     Funciona mesmo em batida sem "arte".
  2. Automático: batidas com arte de OBJETO (aliança, relógio, carro, porta,
     celular, café, mala...) viram foto com a busca padrão de FOTO_PADRAO.
     (Para trocar a foto padrão de um objeto, edite a busca em FOTO_PADRAO.)
     O texto curto da arte (ex.: "DATA GRAVADA") vira a legenda da polaroid.
     Objetos repetidos no mesmo episódio pegam fotos diferentes.
  3. Texto (título, direct, conversa, manchete...), coração, interrogação e
     extrato continuam ilustrados — eles carregam informação escrita.

Se a busca falhar (rede, API fora), a batida volta para a ilustração original;
o render nunca quebra por causa de foto.

Regras do canal: só OBJETOS e LUGARES — resultados com gente em destaque são
descartados (história de traição "acusaria" uma pessoa real). Licenças sem
atribuição obrigatória: Pexels, Pixabay, Openverse CC0 (StockSnap/Rawpixel).
Ordem: Pexels (secret PEXELS_API_KEY) -> Pixabay (PIXABAY_API_KEY) -> Openverse
(sem chave). Créditos de cada foto ficam em saida/<id>/fotos.json.

Desligar: NINA_FOTOS=0.
"""
from __future__ import annotations
import hashlib, io, json, os, random, re, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

RAIZ = Path(__file__).resolve().parent.parent
CACHE = Path(os.environ.get("NINA_FOTOS_CACHE", RAIZ / "assets" / "banco"))
FONTE = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
UA = {"User-Agent": "nina-me-contou/1.0 (+https://github.com/pabloramoa-dev/nina-me-contou)"}
# ilustração/recorte/vetor não combina com a "foto colada"
SEM_ARTE = re.compile(r"\b(illustration|vector|clipart|clip art|icon|drawing|png|psd|mockup|3d|render|cartoon|pattern|transparent)\b", re.I)
SEM_GENTE = re.compile(r"\b(woman|women|man|men|girl|boy|people|person|portrait|couple|face|model|selfie|bride|groom|lady|guy|kid|child)\b", re.I)

# objeto do roteiro -> buscas (a 1ª ocorrência no episódio usa a 1ª, a 2ª usa a 2ª...)
FOTO_PADRAO = {
    "alianca":    ["wedding rings"],
    "relogio":    ["vintage clock", "alarm clock", "wall clock"],
    "calendario": ["open planner"],
    "porta":      ["front door house", "wooden door", "garage door"],
    "foto":       ["old photographs", "photo prints on table"],
    "presente":   ["gift box", "wrapped present"],
    "carro":      ["car at night", "car dashboard", "parked car street"],
    "celular":    ["smartphone on table", "smartphone"],
    "cafe":       ["coffee cup", "espresso cup"],
    "caneca":     ["mug on table", "coffee mug"],
    "mapa":       ["empty road", "highway", "map"],
    "mala":       ["suitcase", "old suitcase"],
    "haltere":    ["dumbbells gym", "dumbbell"],
    "perfume":    ["perfume bottle", "glass perfume bottle"],
    "pulseira":   ["bracelet"],
    "batom":      ["lipstick"],
    "navio":      ["ship at sea"],
    "bolo":       ["birthday cake"],
    "controle":   ["remote control"],
}


def ligado() -> bool:
    return os.environ.get("NINA_FOTOS", "1") not in ("0", "false", "nao", "não")


def _leg(txt):
    if txt is None:
        return None
    t = " ".join(str(txt).split())
    return t or None


def plano(ep: dict) -> dict:
    """{indice_batida: (busca, legenda, variacao)} — determinístico."""
    if not ligado():
        return {}
    out, vistos = {}, {}
    for i, b in enumerate(ep.get("batidas", [])):
        spec = b.get("arte") or [None]
        tipo, arg = spec[0], (spec[1] if len(spec) > 1 else None)
        pedido = b.get("foto")
        if pedido:
            if isinstance(pedido, str):
                q, leg = pedido, None
            else:
                q, leg = pedido[0], (pedido[1] if len(pedido) > 1 else None)
            if leg is None and tipo in FOTO_PADRAO:
                leg = arg
        elif tipo == "banco":
            q, leg = arg, (spec[2] if len(spec) > 2 else None)
        elif tipo in FOTO_PADRAO and b.get("foto") is not False:
            n = vistos.get(tipo, 0)
            vistos[tipo] = n + 1
            buscas = FOTO_PADRAO[tipo]
            q, leg = buscas[n % len(buscas)], arg
            out[i] = (q, _leg(leg), n // len(buscas))   # repetiu tudo? pega o próximo resultado
            continue
        else:
            continue
        n = vistos.get(q, 0)
        vistos[q] = n + 1
        out[i] = (q, _leg(leg), n)
    return out


def slug(q: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", q.lower()).strip("-")[:40]
    return f"{s}-{hashlib.sha1(q.encode()).hexdigest()[:6]}"


def _get(url, headers=None):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def _pexels(q):
    k = os.environ.get("PEXELS_API_KEY")
    if not k:
        return []
    d = json.loads(_get("https://api.pexels.com/v1/search?" + urllib.parse.urlencode(
        {"query": q, "per_page": 20, "orientation": "landscape"}), {"Authorization": k}))
    return [{"url": p["src"]["large"], "texto": p.get("alt", ""), "fonte": "pexels",
             "pagina": p["url"], "autor": p.get("photographer", "")} for p in d.get("photos", [])]


def _pixabay(q):
    k = os.environ.get("PIXABAY_API_KEY")
    if not k:
        return []
    d = json.loads(_get("https://pixabay.com/api/?" + urllib.parse.urlencode(
        {"key": k, "q": q, "image_type": "photo", "orientation": "horizontal",
         "safesearch": "true", "per_page": 20})))
    return [{"url": h["largeImageURL"], "texto": h.get("tags", ""), "fonte": "pixabay",
             "pagina": h["pageURL"], "autor": h.get("user", "")} for h in d.get("hits", [])]


def _openverse(q):
    d = json.loads(_get("https://api.openverse.org/v1/images/?" + urllib.parse.urlencode(
        {"q": q, "license": "cc0", "source": "stocksnap,rawpixel", "page_size": 20, "mature": "false"})))
    out = []
    for r in d.get("results", []):
        tags = " ".join(t.get("name", "") for t in (r.get("tags") or []))
        out.append({"url": r["url"], "thumb": f"https://api.openverse.org/v1/images/{r['id']}/thumb/",
                    "texto": f"{r.get('title', '')} {tags}", "fonte": "openverse/" + r["source"],
                    "pagina": r["foreign_landing_url"], "autor": r.get("creator", "")})
    # prioriza resultados cujo título/tags têm as palavras da busca
    palavras = [w for w in q.lower().split() if len(w) > 2]
    out.sort(key=lambda c: -sum(w in c["texto"].lower() for w in palavras))
    return out


def _baixar(c):
    for u in (c["url"], c.get("thumb")):
        if not u:
            continue
        try:
            im = Image.open(io.BytesIO(_get(u))).convert("RGB")
        except Exception:
            continue
        w, h = im.size
        if min(w, h) >= 380 and 0.6 <= w / h <= 2.4:
            return im
    return None


def buscar(q: str, n: int = 0) -> tuple[Path, dict]:
    """Baixa (ou reaproveita do cache) a n-ésima foto boa para a busca."""
    CACHE.mkdir(parents=True, exist_ok=True)
    alvo = CACHE / f"{slug(q)}-{n}.jpg"
    meta_f = CACHE / "creditos.json"
    reg = json.loads(meta_f.read_text()) if meta_f.exists() else {}
    if alvo.exists():
        return alvo, reg.get(alvo.name, {"busca": q})
    erros = []
    for prov in (_pexels, _pixabay, _openverse):
        try:
            cands = [c for c in prov(q) if not SEM_GENTE.search(c.get("texto") or "")
                     and not SEM_ARTE.search(c.get("texto") or "")]
        except Exception as e:
            erros.append(f"{prov.__name__}: {e}")
            continue
        boas = 0
        for c in cands:
            im = _baixar(c)
            if im is None:
                continue
            if boas < n:
                boas += 1
                continue
            im.thumbnail((1280, 1280))
            im.save(alvo, quality=90)
            info = {"busca": q, **{k: c.get(k, "") for k in ("fonte", "pagina", "autor")}}
            reg[alvo.name] = info
            meta_f.write_text(json.dumps(reg, ensure_ascii=False, indent=1))
            return alvo, info
    raise RuntimeError(f"Nenhuma foto para '{q}'. {'; '.join(erros)}")


def _legenda(d, txt, largura, y):
    for size in range(30, 17, -2):
        f = ImageFont.truetype(FONTE, size)
        if d.textlength(txt, font=f) <= largura - 60:
            break
    while d.textlength(txt, font=f) > largura - 60 and len(txt) > 4:
        txt = txt[:-2].rstrip() + "…"
    d.text(((largura - d.textlength(txt, font=f)) / 2, y), txt, font=f, fill="#a53450")


def polaroid(foto, legenda=None, largura=620, seed=0) -> Image.Image:
    """Foto tratada como recorte colado: tom de papel, grão, borda polaroid,
    fita adesiva e sombra dura. Devolve RGBA."""
    im = Image.open(foto).convert("RGB")
    W = largura - 36
    H = round(W * 0.66)
    im = ImageOps.fit(im, (W, H), Image.LANCZOS, centering=(0.5, 0.5))
    im = ImageEnhance.Color(im).enhance(0.72)
    im = ImageEnhance.Contrast(im).enhance(0.94)
    sepia = ImageOps.colorize(ImageOps.grayscale(im), "#2a2030", "#fff3dc")
    im = Image.blend(im, sepia, 0.28)
    g = Image.effect_noise(im.size, 18).convert("L")
    im = Image.blend(im, Image.merge("RGB", (g, g, g)), 0.06)
    base_h = 70 if legenda else 40
    card = Image.new("RGB", (W + 36, H + 18 + base_h), "#fffaf0")
    card.paste(im, (18, 18))
    d = ImageDraw.Draw(card)
    d.rectangle([17, 17, 18 + W, 18 + H], outline="#28232b", width=2)
    if legenda:
        _legenda(d, legenda, card.width, H + 34)
    pad = 40
    out = Image.new("RGBA", (card.width + pad * 2, card.height + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", card.size, (52, 35, 54, 70))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(2)), (pad + 12, pad + 15))
    out.alpha_composite(card.convert("RGBA"), (pad, pad))
    rnd = random.Random(seed)
    fita = Image.new("RGBA", (170, 42), (210, 183, 151, 190))
    fita = fita.rotate(rnd.choice([-6, -4, 4, 6]), expand=True, resample=Image.BICUBIC)
    out.alpha_composite(fita, (out.width // 2 - fita.width // 2 + rnd.randint(-60, 60), pad - 24))
    return out


def preparar_episodio(ep: dict, assets: Path, pasta: Path | None = None) -> dict:
    """Baixa e monta as polaroids do episódio. Devolve {i: legenda} das que deram
    certo; as que falharem ficam com a ilustração original."""
    ok, creditos = {}, {}
    from visual_images import config
    cfg=config(ep)
    for i, (q, leg, n) in plano(ep).items():
        try:
            foto, info = buscar(q, n)
            polaroid(foto, None if cfg["hide_inner_caption_when_image"] or cfg["bottom_caption_only"] else leg, seed=i).save(Path(assets) / f"foto{i}.png")
            ok[i] = leg
            creditos[i] = info
            print(f"foto batida {i}: '{q}' #{n} <- {info.get('fonte')} {info.get('pagina')}", flush=True)
        except Exception as e:
            print(f"foto batida {i}: '{q}' falhou ({e}); mantém a ilustração", flush=True)
    if pasta is not None:
        (Path(pasta) / "fotos.json").write_text(json.dumps(creditos, ensure_ascii=False, indent=1))
    return ok
