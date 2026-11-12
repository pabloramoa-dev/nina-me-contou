#!/usr/bin/env python3
"""Dois roteiros curtos e originais por dia para a Nina (12h e 15h BRT).

Os temas foram curados a partir de formatos de Reels e referências sobre
amizades, limites e comunicação. Não diagnostica pessoas, não inventa
pesquisa em tempo real e nunca reaproveita um roteiro já publicado.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone, date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EPISODIOS = ROOT / "episodios"
BRT = timezone(timedelta(hours=-3))
FORMATO = "lista_3_sinais"

# Três comportamentos observáveis, não "provas" de mentira, traição ou caráter.
TEMAS = [
    ("uma amizade está ficando unilateral", ("a conversa só começa quando precisam de favor", "ninguém pergunta como você está", "seus convites ficam sempre sem resposta")),
    ("uma amizade precisa de limites", ("brincadeiras continuam depois que você pede para parar", "dizem que seu não é exagero", "você termina os encontros se sentindo desrespeitado")),
    ("uma conversa merece mais clareza", ("os combinados mudam sem ninguém avisar", "as versões sobre o mesmo assunto não batem", "perguntas simples ficam sem resposta direta")),
    ("você está carregando a amizade sozinho", ("só você propõe encontros", "só você pede desculpas", "só você tenta resolver os desentendimentos")),
    ("o grupo não está respeitando você", ("fazem piada quando você fala sério", "compartilham o que você contou em segredo", "decidem por você sem perguntar")),
    ("uma pessoa respeita seus limites", ("aceita um não sem insistir", "pergunta antes de contar seus assuntos", "muda a atitude quando você explica o incômodo")),
    ("uma amizade é recíproca", ("a pessoa lembra de você sem pedir nada", "escuta quando o dia foi difícil", "comemora suas conquistas sem competir")),
    ("um pedido de desculpas precisa de atitude", ("a mesma situação acontece várias vezes", "a culpa sempre acaba sendo sua", "a mudança prometida nunca chega")),
    ("está faltando diálogo numa relação", ("assuntos difíceis ficam sempre para depois", "a outra pessoa interrompe toda conversa", "ninguém confirma o que foi combinado")),
    ("sua opinião não está sendo ouvida", ("falam por cima de você", "suas escolhas são ignoradas", "sua explicação é tratada como drama")),
    ("uma amizade merece uma conversa honesta", ("você sente que não pode discordar", "o silêncio vira castigo", "os problemas se acumulam sem conversa")),
    ("alguém só aparece quando precisa", ("chega pedindo ajuda antes de perguntar por você", "some depois que recebe o favor", "ignora suas mensagens em outros dias")),
    ("uma parceria está desequilibrada", ("as tarefas ficam sempre para você", "seu esforço passa despercebido", "os acordos só valem quando favorecem o outro")),
    ("uma pessoa sabe escutar", ("deixa você terminar a frase", "faz perguntas antes de concluir", "lembra do que você realmente disse")),
    ("uma amizade te faz bem", ("vocês podem discordar com respeito", "ninguém precisa fingir ser outra pessoa", "o apoio aparece nos dias difíceis")),
    ("é hora de rever um combinado", ("as expectativas nunca foram explicadas", "o acordo muda toda semana", "um dos lados sempre sai prejudicado")),
    ("você pode estar dizendo sim demais", ("aceita compromissos por medo de desagradar", "abandona planos importantes para ajudar", "fica esgotado depois de atender todo mundo")),
    ("alguém valoriza sua presença", ("faz questão de incluir você", "respeita seu tempo", "procura você também nos dias comuns")),
    ("está faltando respeito nas mensagens", ("cobram resposta imediata o tempo todo", "mandam indiretas para resolver problemas", "exigem acesso a conversas privadas")),
    ("um mal-entendido está crescendo", ("cada pessoa conta uma versão", "ninguém perguntou o que aconteceu", "o grupo só conversa por indiretas")),
    ("uma amizade mudou de fase", ("os interesses já não combinam tanto", "os encontros ficaram mais raros", "vocês precisam renegociar expectativas")),
    ("uma crítica passou do ponto", ("o comentário humilha em público", "a piada se repete apesar do incômodo", "o erro vira rótulo permanente")),
    ("seus limites estão ficando claros", ("você consegue dizer não com respeito", "explica suas necessidades sem atacar", "aceita ouvir o limite dos outros")),
    ("uma relação merece mais confiança", ("pequenos acordos são esquecidos", "informações importantes são omitidas", "o combinado não é confirmado depois")),
    ("alguém demonstra consideração", ("avisa quando precisa mudar os planos", "lembra de datas importantes para você", "agradece as pequenas ajudas")),
    ("o trabalho em equipe precisa de ajuste", ("as decisões chegam sem consulta", "o crédito nunca é dividido", "ninguém sabe quem fará cada tarefa")),
    ("uma conversa está virando disputa", ("tudo vira comparação", "ninguém admite não saber", "o objetivo é vencer e não entender")),
    ("é hora de cuidar da sua energia", ("você nunca tem espaço para descansar", "todo convite vem com cobrança", "seu tempo livre vira obrigação")),
    ("você encontrou uma boa amizade", ("a pessoa respeita seu ritmo", "vocês riem sem humilhar ninguém", "há espaço para dizer a verdade com carinho")),
    ("um segredo virou fofoca", ("o assunto passa de grupo em grupo", "ninguém pergunta à pessoa envolvida", "detalhes mudam a cada repetição")),
    ("você merece conversas mais claras", ("há dúvidas que nunca são esclarecidas", "respostas vagas viram hábito", "ninguém aceita revisar os combinados")),
]


def roteiro(dia: date, hora: int) -> dict:
    if hora not in (12, 15):
        raise ValueError("A lista viral só pode ocupar 12h ou 15h")
    indice = (dia.toordinal() * 2 + (0 if hora == 12 else 1)) % len(TEMAS)
    assunto, sinais = TEMAS[indice]
    ep_id = f"ep9{dia:%Y%m%d}{hora:02d}"
    titulo = f"3 SINAIS DE QUE {assunto.upper()}"
    falas = [
        f"Três sinais de que {assunto}.",
        "Um.",
        sinais[0].capitalize() + ".",
        "Dois.",
        sinais[1].capitalize() + ".",
        "Três.",
        sinais[2].capitalize() + ".",
        "Se isso acontece sempre,",
        "vale conversar com calma.",
        "Um sinal sozinho não define ninguém.",
    ]
    artes = ["titulo", "interrogacao", "conversa", "interrogacao", "celular",
             "interrogacao", "conversa", "relogio", "conversa", "coracao"]
    batidas = [
        {"fala": fala, "expr": "ironica" if i in (0, 9) else "neutra",
         "arte": [artes[i]], "destaque": [],
         "hf": {"titulo": ("3 SINAIS" if i == 0 else f"SINAL {(i+1)//2}" if i in (2,4,6) else ""),
                "selo": "NINA EM 30 SEGUNDOS"}}
        for i, fala in enumerate(falas)
    ]
    legenda = (f"{titulo}\n\n"
               + "\n".join(f"{i+1}. {sinal.capitalize()}." for i, sinal in enumerate(sinais))
               + "\n\nSão comportamentos para observar e conversar, não provas sobre uma pessoa. "
               + "Manda pra quem merece relações com mais respeito.\n\n"
               + "#ninamecontou #3sinais #amizade #relacionamentos #reflexao")
    return {
        "id": ep_id, "parte": "unica", "formato": FORMATO,
        "horario_destino": f"{hora:02d}h", "data_editorial": dia.isoformat(),
        "titulo": titulo, "temporada": "Listas rápidas",
        "cenario": "tarde", "batidas": batidas, "fim": "COMPARTILHE",
        "legenda_post": legenda, "legenda_tiktok": legenda,
        "gerado_automaticamente": True,
        "referencia_editorial": "Pesquisa sobre retenção/compartilhamento de Reels e comunicação saudável; ver docs/listas-virais.md",
    }


def abastecer(dias: int = 10, hoje: date | None = None, pasta: Path = EPISODIOS) -> list[str]:
    hoje = hoje or datetime.now(BRT).date()
    pasta.mkdir(parents=True, exist_ok=True)
    novos = []
    for delta in range(max(1, dias)):
        dia = hoje + timedelta(days=delta)
        for hora in (12, 15):
            ep = roteiro(dia, hora)
            arq = pasta / f"{ep['id']}.json"
            if arq.exists():  # nunca altera roteiros enviados ou já produzidos
                continue
            arq.write_text(json.dumps(ep, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
            novos.append(ep["id"])
    return novos


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--dias", type=int, default=10)
    args = p.parse_args()
    print(json.dumps({"novos": abastecer(args.dias)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
