#!/usr/bin/env python3
"""Gera histórias ficcionais da Nina e mantém um buffer automático.

O canal publica 4 vídeos/dia = 2 histórias completas/dia. O plano anual reserva
730 histórias (1460 partes), suficientes para 365 dias. Para não lotar o Git
com centenas de vídeos de uma vez, só os roteiros do buffer são materializados;
à medida que são publicados, novos pares entram automaticamente.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
EP_DIR = ROOT / "episodios"
PUB = ROOT / "conteudo" / "publicados.json"
STATE = ROOT / "conteudo" / "geracao_anual.json"

TOTAL_ANUAL = 730
ALVO_PADRAO = 60  # 30 dias a 2 histórias/dia

NOMES = [
    "Mariana","Paula","Renata","Camila","Bianca","Fernanda","Larissa","Bruna",
    "Carolina","Letícia","Amanda","Juliana","Natália","Isabela","Patrícia","Débora",
    "Rafael","Lucas","André","Caio","Felipe","Gustavo","Marcelo","Thiago",
    "Daniel","Bruno","Henrique","Eduardo","Rodrigo","Leandro","Vinícius","Gabriel",
]
BAIRROS = [
    "um bairro antigo", "um condomínio novo", "uma rua tranquila", "o centro da cidade",
    "um prédio perto do trabalho", "uma cidade vizinha", "um bairro de casas", "a região da rodoviária",
]
OBJETOS = [
    ("uma chave que não abria nenhuma porta da casa", "chave_hotel"),
    ("um recibo dobrado dentro de um livro", "extrato"),
    ("uma foto impressa sem data", "foto"),
    ("um cartão de estacionamento de outro prédio", "carro"),
    ("um envelope com um endereço escrito à mão", "presente"),
    ("um comprovante de reserva que ninguém reconhecia", "calendario"),
    ("um segundo carregador de celular na mochila", "celular"),
    ("um bilhete preso atrás de uma moldura", "foto"),
    ("uma etiqueta de bagagem de uma viagem nunca contada", "mala"),
    ("uma cópia de contrato com outro endereço", "extrato"),
    ("uma chave de armário numerada", "chave_hotel"),
    ("um nome diferente salvo como contato de emergência", "celular"),
]
SEGREDOS = [
    "mantinha um pequeno apartamento alugado havia meses",
    "estava organizando uma mudança sem contar a ninguém",
    "tinha aberto uma empresa com outra pessoa",
    "guardava documentos de uma compra importante",
    "frequentava o mesmo café em todas as viagens",
    "ajudava financeiramente alguém em segredo",
    "planejava sair do emprego e mudar de cidade",
    "usava um segundo perfil nas redes sociais",
    "tinha feito uma reserva recorrente no mesmo lugar",
    "guardava caixas em um depósito que ninguém conhecia",
    "estava preparando uma surpresa grande, mas cheia de mentiras pequenas",
    "escondia uma amizade antiga que nunca mencionava",
]
REVELACOES = [
    "o endereço aparecia também em três compras antigas",
    "a mesma data se repetia no calendário dos últimos meses",
    "o nome do contato apareceu em outra foto guardada",
    "o porteiro reconheceu a pessoa pelo primeiro nome",
    "uma mensagem automática confirmou que aquilo não era a primeira vez",
    "o comprovante mostrava uma rotina, não um episódio isolado",
    "a chave tinha uma etiqueta com o número do apartamento",
    "uma segunda pista estava no histórico de viagens",
    "a foto tinha sido tirada no mesmo lugar do recibo",
    "o contrato tinha uma assinatura feita meses antes",
    "o mapa do celular marcava o endereço como favorito",
    "a caixa guardada no depósito tinha documentos com duas datas diferentes",
]
MOTIVOS = [
    "porque dizia que precisava de privacidade",
    "porque sempre mudava de assunto quando perguntavam",
    "porque aquilo não combinava com a rotina que contava",
    "porque a explicação veio rápida demais",
    "porque já havia pequenas contradições acumuladas",
    "porque ninguém lembrava de ter ouvido aquele nome antes",
    "porque o horário não fechava com a história",
    "porque a viagem tinha durado menos do que foi contado",
]
GANCHOS = [
    "Uma chave apareceu onde não deveria existir.",
    "O recibo custava pouco. O endereço custou a confiança.",
    "Ela só queria pegar um carregador. Encontrou uma segunda vida.",
    "Uma foto antiga tinha sido tirada três dias antes.",
    "O detalhe estranho não era o nome. Era a repetição.",
    "Tudo começou com um papel dobrado no bolso de uma mala.",
    "A mentira parecia pequena até o calendário entrar na história.",
    "O porteiro fez uma pergunta que ninguém estava preparado para ouvir.",
]
PERGUNTAS = [
    "Você perguntaria na hora ou juntaria mais uma prova?",
    "Você mostraria tudo e pediria uma explicação?",
    "Você iria ao endereço ou esperaria a pessoa falar?",
    "Você contaria para alguém de confiança antes de confrontar?",
    "Você daria uma chance para a explicação ou encerraria a conversa ali?",
    "Você faria uma pergunta direta ou deixaria a pessoa contar sozinha?",
]
TEMPORADAS = ["Segredos", "Casais", "Amizades", "Família", "Trabalho", "Vizinhança"]

def _ler_json(path: Path, padrao):
    if not path.exists():
        return padrao
    return json.loads(path.read_text(encoding="utf-8"))

def _salvar(path: Path, dados):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dados, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

def _nums_existentes() -> list[int]:
    nums = []
    for p in EP_DIR.glob("ep*-p1.json"):
        try:
            nums.append(int(p.stem[2:5]))
        except Exception:
            pass
    return sorted(set(nums))

def _publicados() -> set[str]:
    return {x.get("id") for x in _ler_json(PUB, []) if not x.get("ensaio")}

def _estado() -> dict:
    if STATE.exists():
        return _ler_json(STATE, {})
    atual = max(_nums_existentes() or [0]) + 1
    return {
        "inicio": atual,
        "proximo": atual,
        "total_planejado": TOTAL_ANUAL,
        "criado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "descricao": "730 historias x 2 partes = 1460 videos, suficientes para 365 dias a 4 videos/dia",
    }

def _reserva_atual() -> int:
    feitos = _publicados()
    total = 0
    for n in _nums_existentes():
        if f"ep{n:03d}-p2" not in feitos:
            total += 1
    return total

def _pick(seq: int, itens: list):
    return itens[seq % len(itens)]

def _beats_parte1(seq: int, a: str, b: str, c: str, objeto: str, arte: str,
                  segredo: str, bairro: str, motivo: str, revelacao: str, gancho: str):
    anos = 2 + (seq % 8)
    dia = ["terça", "quarta", "quinta", "sexta"][seq % 4]
    return [
        {"fala": gancho, "expr": "ironica", "arte": ["titulo"], "destaque": ["não", "deveria"]},
        {"fala": f"A história chegou pela {a}. {b} fazia parte da rotina dela havia {anos} anos.", "expr": "neutra",
         "arte": ["direct", f"{a.upper()}"], "destaque": [a]},
        {"fala": f"Naquele {dia}, {a} encontrou {objeto}.", "expr": "desconfiada",
         "arte": [arte], "destaque": ["encontrou"]},
        {"fala": f"No começo ela tentou ignorar, {motivo}.", "expr": "neutra",
         "arte": ["interrogacao"], "destaque": ["ignorar"]},
        {"fala": f"Mas havia um detalhe: a pista apontava para {bairro}.", "expr": "desconfiada",
         "arte": ["mapa"], "destaque": ["detalhe"]},
        {"fala": f"{a} perguntou de forma casual se {b} conhecia aquele lugar. A resposta foi não.", "expr": "desconfiada",
         "arte": ["conversa", "NÃO CONHEÇO"], "destaque": ["não"]},
        {"fala": f"Na mesma noite, outra pista apareceu: {revelacao}.", "expr": "chocada",
         "arte": ["foto"], "destaque": ["outra", "pista"], "zoom": True},
        {"fala": f"Foi aí que {a} ligou os pontos. {b} {segredo}.", "expr": "brava",
         "arte": ["manchete_v", "AS PEÇAS COMEÇARAM A FECHAR"], "destaque": ["segredo"]},
        {"fala": f"E o nome de {c} apareceu no meio dos documentos.", "expr": "chocada",
         "arte": ["celular", c.upper()], "destaque": [c]},
        {"fala": f"{a} não disse nada naquela noite. Fotografou o que encontrou e colocou tudo no mesmo lugar.", "expr": "desconfiada",
         "arte": ["foto"], "destaque": ["mesmo", "lugar"]},
        {"fala": f"No dia seguinte, {b} avisou que sairia mais cedo. Justamente para {bairro}.", "expr": "ironica",
         "arte": ["calendario", "SAIU MAIS CEDO"], "destaque": ["justamente"]},
        {"fala": "O que aconteceu quando ela decidiu seguir a pista eu conto na parte dois.", "expr": "ironica",
         "arte": ["manchete_v", "CONTINUA NA PARTE 2"], "destaque": ["parte", "dois"]},
    ]

def _beats_parte2(seq: int, a: str, b: str, c: str, objeto: str, arte: str,
                  segredo: str, bairro: str, revelacao: str, pergunta: str):
    hora = 17 + (seq % 4)
    desfechos = [
        f"{c} abriu a porta e ficou em silêncio quando ouviu o nome de {b}.",
        f"{c} respondeu a mensagem dizendo que também precisava entender o que estava acontecendo.",
        f"{c} mostrou um segundo documento que {a} nunca tinha visto.",
        f"{c} acreditava numa versão completamente diferente da história.",
    ]
    d = _pick(seq, desfechos)
    return [
        {"fala": "Se você caiu aqui agora, volta na parte um. A pista principal está lá.", "expr": "ironica",
         "arte": ["titulo"], "destaque": ["parte", "um"]},
        {"fala": f"{a} esperou até as {hora} horas e foi até {bairro}.", "expr": "desconfiada",
         "arte": ["relogio", f"{hora}H"], "destaque": [f"{hora}"]},
        {"fala": f"Ela levou só a foto de {objeto}. Nada de discussão preparada.", "expr": "neutra",
         "arte": [arte], "destaque": ["foto"]},
        {"fala": f"Quando chegou, reconheceu o nome de {c} numa caixa de correspondência.", "expr": "chocada",
         "arte": ["porta", c.upper()], "destaque": [c], "zoom": True},
        {"fala": d, "expr": "chocada", "arte": ["conversa"], "destaque": ["silêncio"]},
        {"fala": f"Em poucos minutos ficou claro que {b} {segredo}.", "expr": "brava",
         "arte": ["manchete_v", "A HISTÓRIA ERA MAIOR"], "destaque": ["claro"]},
        {"fala": f"E ainda tinha mais: {revelacao}.", "expr": "desconfiada",
         "arte": ["foto"], "destaque": ["mais"]},
        {"fala": f"{a} mandou uma única mensagem para {b}: preciso que você me conte a verdade inteira.", "expr": "triste",
         "arte": ["conversa", "A VERDADE INTEIRA"], "destaque": ["verdade"]},
        {"fala": "A resposta demorou quarenta minutos. Veio com três parágrafos e nenhuma explicação completa.", "expr": "ironica",
         "arte": ["celular", "40 MINUTOS"], "destaque": ["nenhuma"]},
        {"fala": f"{a} voltou para casa sem decidir nada naquela noite.", "expr": "neutra",
         "arte": ["carro"], "destaque": ["decidir"]},
        {"fala": "No dia seguinte ela me mandou a história e uma pergunta só.", "expr": "neutra",
         "arte": ["direct"], "destaque": ["pergunta"]},
        {"fala": pergunta + " Me conta nos comentários.", "expr": "ironica",
         "arte": ["manchete_v", "O QUE VOCÊ FARIA?"], "destaque": ["você"]},
    ]

def gerar_um(n: int, seq: int) -> tuple[dict, dict]:
    a = NOMES[(seq * 3) % 16]  # mantém a narradora da história no feminino
    b = NOMES[(seq * 5 + 7) % len(NOMES)]
    c = NOMES[(seq * 7 + 13) % len(NOMES)]
    if len({a, b, c}) < 3:
        c = NOMES[(seq * 11 + 17) % len(NOMES)]
    objeto, arte = _pick(seq * 2 + 1, OBJETOS)
    segredo = _pick(seq * 3 + 2, SEGREDOS)
    revelacao = _pick(seq * 5 + 3, REVELACOES)
    bairro = _pick(seq * 7 + 1, BAIRROS)
    motivo = _pick(seq * 11 + 5, MOTIVOS)
    gancho = _pick(seq * 13 + 2, GANCHOS)
    pergunta = _pick(seq * 17 + 1, PERGUNTAS)
    temporada = _pick(seq, TEMPORADAS)
    titulo = (objeto.split(" dentro")[0].split(" de ")[0].replace("uma ", "").replace("um ", "")).upper()[:28]
    p1_id, p2_id = f"ep{n:03d}-p1", f"ep{n:03d}-p2"
    base_leg = (
        f"{gancho}\n\nUma pista levou {a} a uma história que não fechava. "
        "A continuação está no perfil.\n\n"
        "Tem uma história assim? Me manda no direct — eu conto sem nome e sem rosto.\n\n"
        "História de ficção, inspirada em situações comuns do cotidiano.\n\n"
        "#storytime #historia #fofoca #segredo #relacionamentos #ninamecontou"
    )
    p1 = {
        "id": p1_id, "ep": n, "parte": 1, "titulo": titulo, "temporada": temporada,
        "cenario": "tarde",
        "batidas": _beats_parte1(seq, a, b, c, objeto, arte, segredo, bairro, motivo, revelacao, gancho),
        "fim": "CONTINUA NA PARTE 2", "legenda_post": base_leg,
        "gerado_automaticamente": True, "serie_anual": seq + 1,
    }
    p2 = {
        "id": p2_id, "ep": n, "parte": 2, "titulo": titulo, "temporada": temporada,
        "cenario": "noite",
        "batidas": _beats_parte2(seq, a, b, c, objeto, arte, segredo, bairro, revelacao, pergunta),
        "fim": "SEGUE A NINA",
        "legenda_post": (
            f"A parte dois de {titulo.lower()}. A pista parecia pequena, mas revelou uma história inteira.\n\n"
            f"{pergunta}\n\nTem uma história assim? Me manda no direct — eu conto sem nome e sem rosto.\n\n"
            "História de ficção, inspirada em situações comuns do cotidiano.\n\n"
            "#storytime #historia #fofoca #segredo #relacionamentos #ninamecontou"
        ),
        "gerado_automaticamente": True, "serie_anual": seq + 1,
    }
    return p1, p2

def abastecer(alvo: int) -> dict:
    EP_DIR.mkdir(parents=True, exist_ok=True)
    state = _estado()
    reserva = _reserva_atual()
    faltam = max(0, alvo - reserva)
    limite = int(state["inicio"]) + int(state.get("total_planejado", TOTAL_ANUAL))
    gerados = []
    while faltam > 0 and int(state["proximo"]) < limite:
        n = int(state["proximo"])
        seq = n - int(state["inicio"])
        p1, p2 = gerar_um(n, seq)
        _salvar(EP_DIR / f"{p1['id']}.json", p1)
        _salvar(EP_DIR / f"{p2['id']}.json", p2)
        gerados.append(n)
        state["proximo"] = n + 1
        faltam -= 1
    state["atualizado_em"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    state["reserva_antes"] = reserva
    state["reserva_depois"] = reserva + len(gerados)
    state["gerados_nesta_execucao"] = len(gerados)
    state["restantes_no_plano"] = max(0, limite - int(state["proximo"]))
    _salvar(STATE, state)
    return {"gerados": gerados, "estado": state}

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--alvo", type=int, default=ALVO_PADRAO)
    a = ap.parse_args()
    r = abastecer(max(4, a.alvo))
    print(json.dumps({
        "ok": True,
        "novos_episodios": len(r["gerados"]),
        "primeiro": r["gerados"][0] if r["gerados"] else None,
        "ultimo": r["gerados"][-1] if r["gerados"] else None,
        "reserva_depois": r["estado"]["reserva_depois"],
        "restantes_no_plano_anual": r["estado"]["restantes_no_plano"],
    }, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
