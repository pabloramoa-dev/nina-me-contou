import pytest


@pytest.fixture(autouse=True)
def modo_legado_em_testes_sinteticos(monkeypatch):
    # Os testes anteriores usam episódios sintéticos que não pertencem ao acervo.
    # A suíte test_prompts_banco ativa explicitamente o caminho de produção.
    monkeypatch.setenv('NINA_REQUIRE_STORED_PROMPTS', '0')
