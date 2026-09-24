"""Configuração do @ninamecontou. Nenhum segredo em código: tudo vem dos
Secrets/Variables do GitHub Actions."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
EPISODIOS = RAIZ / "episodios"
REELS = RAIZ / "reels"
PUBLICADOS_JSON = RAIZ / "conteudo" / "publicados.json"

RESERVA_MINIMA = 3        # episódios completos (p1+p2) prontos; abaixo disso abre alerta
DURACAO_MIN_S = 15.0
DURACAO_MAX_S = 90.0


@dataclass(frozen=True)
class Config:
    ig_user_id: str
    ig_token: str
    raw_base_url: str
    graph_version: str
    publicar_ativo: bool
    dry_run: bool

    HOST = "https://graph.instagram.com"   # rota "API do Instagram com login do Instagram"

    @property
    def base_conta(self) -> str:
        return f"{self.HOST}/{self.graph_version}/{self.ig_user_id}"

    @property
    def base_graph(self) -> str:
        return f"{self.HOST}/{self.graph_version}"


def _flag(nome: str, padrao: str = "false") -> bool:
    return os.getenv(nome, padrao).strip().lower() in {"1", "true", "yes", "sim"}


def carregar(exigir_credenciais: bool = True) -> Config:
    obrigatorias = ["IG_USER_ID_NINA", "IG_ACCESS_TOKEN_NINA", "RAW_BASE_URL"]
    if exigir_credenciais:
        faltando = [k for k in obrigatorias if not os.getenv(k)]
        if faltando:
            raise RuntimeError(f"Variáveis obrigatórias ausentes: {faltando}")
    return Config(
        ig_user_id=os.getenv("IG_USER_ID_NINA", ""),
        ig_token=os.getenv("IG_ACCESS_TOKEN_NINA", ""),
        raw_base_url=os.getenv("RAW_BASE_URL", "").rstrip("/"),
        graph_version=os.getenv("GRAPH_API_VERSION", "v22.0"),
        publicar_ativo=_flag("PUBLICAR_ATIVO", "false"),
        dry_run=_flag("DRY_RUN", "true"),
    )


def esconder(texto: str) -> str:
    tok = os.getenv("IG_ACCESS_TOKEN_NINA", "")
    if tok and len(tok) > 8:
        texto = texto.replace(tok, "***TOKEN***")
    return texto
