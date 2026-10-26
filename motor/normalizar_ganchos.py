#!/usr/bin/env python3
"""Atualiza JSONs históricos de episódios e avulsos. --check apenas simula."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from ganchos import aplicar_gancho
except ImportError:
    from motor.ganchos import aplicar_gancho

ROOT = Path(__file__).resolve().parents[1]
DIRS = ("episodios", "avulsos", "avulsos_fast")


def normalizar(root: Path, check: bool = False) -> dict:
    total = alterados = preservados = 0
    exemplos = []
    for pasta in DIRS:
        base = root / pasta
        if not base.exists():
            continue
        for path in sorted(base.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or not isinstance(data.get("batidas"), list):
                continue
            total += 1
            atualizado = aplicar_gancho(data)
            if atualizado == data:
                preservados += 1
                continue
            alterados += 1
            if len(exemplos) < 5:
                exemplos.append({"arquivo": str(path.relative_to(root)),
                                 "antes": data["batidas"][0]["fala"],
                                 "depois": atualizado["batidas"][0]["fala"]})
            if not check:
                path.write_text(json.dumps(atualizado, ensure_ascii=False, indent=1) + "\n",
                                encoding="utf-8")
    return {"analisados": total, "alterados": alterados, "preservados": preservados,
            "modo": "ensaio" if check else "gravação", "exemplos": exemplos}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    print(json.dumps(normalizar(ROOT, args.check), ensure_ascii=False))


if __name__ == "__main__":
    main()
