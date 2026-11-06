"""Revisa histórias completas da Nina sem inventar acontecimentos.

Preserva os fatos e a sequência original, remove textos genéricos repetidos,
e sinaliza roteiros que precisam de edição humana. Idempotente.
"""
from __future__ import annotations
import argparse
import copy
import json
import re
from pathlib import Path

VERSAO = "nina-clareza-20261106-v1"
RAIZ = Path(__file__).resolve().parents[1]
INICIOS_GENERICOS = (
    "A protagonista desta história é", "O detalhe parecia pequeno à primeira vista",
    "E aqui começa a parte mais surpreendente", "O curioso é como os detalhes",
    "Até aquele momento, cada pessoa", "A Nina conta isso porque",
    "E tinha uma coisa importante naquela história", "Ninguém precisava transformar",
    "O silêncio também estava", "A cada pergunta, surgia",
    "Antes de tomar uma decisão, era preciso", "O mais difícil não era",
    "Quem acompanha uma história assim", "Só que nenhuma explicação resolve",
    "E enquanto a história avançava", "No fim, a conversa trouxe consequências",
    "Quem estava envolvido teve de assumir", "Não foi uma resposta que chegou pronta",
    "Foi nesse momento que", "Até ali, os detalhes pareciam",
    "Ninguém ali tinha uma solução pronta", "E foi aí que o rumo da conversa mudou",
    "A conversa começou cheia de justificativas",
)
PERGUNTAS_GENERICAS = ("Se fosse com você,", "Se você estivesse no lugar de")
CONEXOES_CURTAS = (
    "Ela quis entender a situação antes de decidir o que fazer.",
    "Ainda faltava esclarecer o que tinha acontecido.",
    "A explicação precisava combinar com o que ela já sabia.",
)

def _fala(b: dict) -> str:
    return str(b.get("fala", "")).strip()

def _intro(fala: str) -> str:
    return re.sub(r"^Essa é a história de [^.!?]+[.!?]\s*", "", fala).strip()

def _generica(fala: str) -> bool:
    return fala.casefold().startswith(tuple(x.casefold() for x in INICIOS_GENERICOS))

def _simplificar_pergunta(fala: str) -> str:
    m = re.search(r"(?:reagido como|lugar de)\s+([A-ZÀ-Ý][\wÀ-ÿ-]+)", fala)
    return f"E você, teria feito o mesmo que {m.group(1)}?" if m else "E você, faria diferente?"

def _separar(b: dict) -> list[dict]:
    fala = _fala(b)
    sentencas = [x.strip() for x in re.split(r"(?<=[.!?])\s+(?=[A-ZÀ-Ý])", fala) if x.strip()]
    if len(sentencas) < 2 or len(fala.split()) < 19:
        return [b]
    saida = []
    for frase in sentencas:
        item = copy.deepcopy(b)
        item["fala"] = frase
        item["destaque"] = [p for p in item.get("destaque", [])
                             if p.lower().strip(".,!?") in frase.lower()]
        item.pop("tela", None)
        saida.append(item)
    return saida

def revisar(ep: dict) -> tuple[dict, dict]:
    bats = ep.get("batidas", [])
    if ep.get("parte") != "unica" or not re.fullmatch(r"ep\d{3,}", str(ep.get("id", ""))):
        return ep, {"status": "fora_do_escopo"}
    if ep.get("revisao_clareza") == VERSAO:
        return ep, {"status": "ja_revisado"}
    if not bats or len(bats) < 10:
        return ep, {"status": "revisao_manual", "motivo": "menos de dez cenas"}
    concretas, dispensaveis, perguntas = [], [], []
    intro = len(bats) > 1 and _fala(bats[1]).startswith("Essa é a história de ")
    for idx, original in enumerate(bats):
        b = copy.deepcopy(original)
        fala = _intro(_fala(b))
        if not fala:
            dispensaveis.append((idx, b))
            continue
        b["fala"] = fala
        if _generica(fala):
            dispensaveis.append((idx, b))
        elif fala.startswith(PERGUNTAS_GENERICAS):
            b["fala"] = _simplificar_pergunta(fala)
            b["destaque"] = []
            perguntas.append((idx, b))
        else:
            concretas.extend((idx + subidx / 100, x) for subidx, x in enumerate(_separar(b)))
    if not dispensaveis and not perguntas and not intro:
        return ep, {"status": "sem_mudancas"}
    if intro:
        segundo = next(((idx, b) for idx, b in concretas if idx == 1), None)
        if segundo and concretas and concretas[0][0] == 0:
            concretas = [(0, segundo[1]), (1, concretas[0][1])] + [
                x for x in concretas if x[0] not in (0, 1)]
    faltam = max(0, 10 - len(concretas) - bool(perguntas))
    conexoes = 0
    for idx, b in dispensaveis:
        if not faltam or conexoes >= 3:
            break
        if _fala(b).startswith("No fim, a conversa trouxe"):
            continue
        novo = copy.deepcopy(b)
        novo["fala"] = CONEXOES_CURTAS[conexoes]
        novo["destaque"] = []
        novo.pop("tela", None)
        concretas.append((idx, novo))
        faltam -= 1
        conexoes += 1
    if faltam:
        return ep, {"status": "revisao_manual",
                    "motivo": "poucos fatos para dez cenas", "faltam": faltam}
    concretas.sort(key=lambda x: x[0])
    out = copy.deepcopy(ep)
    out["batidas"] = [b for _, b in concretas] + [b for _, b in perguntas[-1:]]
    out["revisao_clareza"] = VERSAO
    out["estrutura"] = "gancho-inicio-meio-revelacao-desfecho"
    return out, {"status": "revisado", "antes": len(bats),
                 "depois": len(out["batidas"]), "removidas": len(dispensaveis),
                 "conexoes": conexoes}

def revisar_pasta(pasta: Path, gravar: bool = False) -> dict:
    relatorio = {"total": 0, "revisados": 0, "sem_mudancas": 0,
                 "revisao_manual": [], "arquivos": []}
    for path in sorted(pasta.glob("ep[0-9][0-9][0-9].json")):
        ep = json.loads(path.read_text(encoding="utf-8"))
        novo, resultado = revisar(ep)
        relatorio["total"] += 1
        estado = resultado["status"]
        if estado == "revisado":
            relatorio["revisados"] += 1
            relatorio["arquivos"].append({"arquivo": path.name, **resultado})
            if gravar:
                path.write_text(json.dumps(novo, ensure_ascii=False, indent=1) + "\n",
                                encoding="utf-8")
        elif estado == "revisao_manual":
            relatorio["revisao_manual"].append({"arquivo": path.name, **resultado})
        elif estado == "sem_mudancas":
            relatorio["sem_mudancas"] += 1
    return relatorio

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--aplicar", action="store_true")
    parser.add_argument("--pasta", type=Path, default=RAIZ / "episodios")
    args = parser.parse_args()
    print(json.dumps(revisar_pasta(args.pasta, args.aplicar),
                     ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
