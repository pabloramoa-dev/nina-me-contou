"""Gancho de antecipação na abertura, antes da voz e dos visuais.

Usa fatos do roteiro, sem inventar personagens, esconder o final ou abrir
parte 2. O corpo e o desfecho permanecem intactos.
"""
from __future__ import annotations

import copy
import re

VERSAO = "nina-antecipacao-20261102-v2"
FATO = re.compile(r"\b(?:segund[ao]|outr[ao]s?|duas|dois|foto|recibo|mensagem|bilhete|"
                  r"chave|áudio|video|vídeo|reserva|bolo|casamento|documento)\b", re.I)
SUSPENSE = re.compile(r"\b(?:mas|só que|quando|até que|sem imaginar|sem saber|"
                      r"porém|ninguém|então|antes que|inesperad[ao])\b", re.I)
GENERICA = re.compile(r"^(?:hoje vou|vou te contar|essa história começa|"
                      r"o que aconteceu depois|a protagonista desta|"
                      r"e aqui começa|se você chegou)", re.I)
FIM = re.compile(r"\b(?:no fim|no final|acabou|terminou|resolveram|"
                 r"decidiram encerrar|desfecho|me segue)\b", re.I)
RX_SENTENCA = re.compile(r"(?<=[.!?])\s+")
FATO_NOME = re.compile(r"\b(?:foto|recibo|mensagem|bilhete|chave|áudio|vídeo|video|reserva|bolo|"
                       r"casamento|documento)\b", re.I)
# Segunda chance, só quando FATO não acha nada: objetos concretos no plural e
# outros itens que os roteiros automáticos usam como pista.
FATO_EXTRA = re.compile(r"\b(?:fotos|recibos|mensagens|bilhetes|chaves|áudios|vídeos|documentos|"
                        r"etiquetas?|perfil|convites?|caixas?|malas?|cartas?|anéis|anel|"
                        r"celular|e-mails?|print|prints|comprovantes?|ingressos?|passagens?|"
                        r"rascunhos?|contrato|extrato|presentes?|caderno|diário|endereço|"
                        r"senha|pacote|encomenda|câmera|gravação|planilha|cartão|nota|cadeira|lista|discos)\b", re.I)


FEMININOS = {"foto", "mensagem", "chave", "reserva", "fotos", "mensagens", "chaves", "etiqueta", "etiquetas", "caixa", "caixas", "mala",
             "malas", "carta", "cartas", "passagem", "passagens", "senha", "câmera",
             "gravação", "planilha", "nota", "encomenda", "cadeira", "lista"}


def _com_artigo(palavra: str) -> str:
    plural = palavra.endswith("s") and palavra not in {"diário"}
    art = ("as" if plural else "a") if palavra in FEMININOS else ("os" if plural else "o")
    return f"{art} {palavra} {'tinham' if plural else 'tinha'}"


def _frase(fala: str) -> str:
    return RX_SENTENCA.split(fala.strip(), maxsplit=1)[0].strip()


def antecipar(ep: dict) -> dict:
    out = copy.deepcopy(ep)
    if out.get("formato") == "lista_3_sinais":
        # Preserva o gancho original da lista e informa a versao ao portao de qualidade.
        out["gancho_antecipacao_versao"] = VERSAO
        out["gancho_antecipacao_modelo"] = "lista_curta_gancho_proprio"
        return out
    bats = out.get("batidas")
    if (not isinstance(bats, list) or len(bats) < 5 or
        not (out.get("parte") == "unica" or out.get("avulso")) or
        re.search(r"promo|quiz|teste de voz", str(out.get("titulo", "")), re.I)):
        return out
    if out.get("gancho_antecipacao_versao") == VERSAO:
        return out
    abertura = str(bats[0].get("fala", "")).strip()
    inicio = _frase(abertura)
    if not inicio or len(inicio.split()) < 5:
        raise ValueError("História sem fato concreto para gancho de antecipação")
    # Aberturas já concretas e com virada explícita não precisam ser reescritas.
    if (len(abertura.split()) >= 14 and SUSPENSE.search(abertura)
            and FATO.search(abertura) and not FIM.search(abertura)
            and not GENERICA.search(abertura)):
        modelo = "antecipacao_existente_validada"
    else:
        if GENERICA.search(inicio):
            concreto = next((_frase(str(b.get("fala", ""))) for b in bats[1:5]
                             if FATO.search(str(b.get("fala", "")))), "")
            if concreto:
                inicio = concreto
        # Busca uma pista concreta descrita antes do desfecho, nunca cria eventos.
        trecho = " ".join(str(b.get("fala", "")) for b in bats[1:max(5, len(bats)//2)])
        pista = re.search(r"\b(?:uma?|o|a)\s+(?:segund[ao]|outr[ao])\s+"
                          r"(?:[\wÀ-ÿ]+)(?:\s+[\wÀ-ÿ]+)?", trecho, re.I)
        if pista:
            ancora = pista.group(0).rstrip(".,;:")
            ancora = re.sub(r"\s+(?:e|de|da|do|que|com|em|na|no|a|o|para|pra)$", "", ancora, flags=re.I)
            pergunta = f"Mas por que apareceu {ancora}?"
            modelo = "antecipacao_pista_concreta"
        else:
            # Prefere um substantivo concreto ("a foto", "o recibo"); numerais e
            # pronomes ("dois", "outra") geravam "Mas o que dois tinha a ver...".
            trecho_todo = " ".join(str(b.get("fala", "")) for b in bats[1:-1])
            nome = (FATO_NOME.search(trecho) or FATO_EXTRA.search(trecho)
                    or FATO_NOME.search(trecho_todo) or FATO_EXTRA.search(trecho_todo)
                    )
            if nome:
                pergunta = f"Mas o que {_com_artigo(nome.group(0).lower())} a ver com isso?"
            else:
                # Sem objeto concreto citado: pergunta neutra, sem inventar pista.
                pergunta = "Mas ninguém imaginava o que estava por trás disso."
            modelo = "antecipacao_pergunta_concreta"
        novo = inicio.rstrip(".!?") + ". " + pergunta
        if len(novo.split()) > 43:
            raise ValueError("Gancho de antecipação longo demais")
        bats[0]["fala"] = novo
        bats[0]["expr"] = "desconfiada"
        bats[0]["destaque"] = [p for p in re.findall(r"[\wÀ-ÿ]{5,}", novo)[:3]]
        bats[0].pop("tela", None)
    out["gancho_antecipacao_versao"] = VERSAO
    out["gancho_antecipacao_modelo"] = modelo
    return out
