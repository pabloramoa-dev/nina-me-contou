#!/usr/bin/env python3
"""Entrega os MP4s recém-renderizados da Nina e suas descrições de TikTok.

Uso no GitHub Actions:
    python tools/telegram_nina.py --video-dir entrega_nina

Configure TELEGRAM_BOT_TOKEN_NINA e TELEGRAM_CHAT_ID_NINA como GitHub Secrets.
Não publica no TikTok; envia o arquivo e o texto para a conversa privada indicada.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
RECIBOS = ROOT / "conteudo" / "telegram_entregues.json"
RX_MP4 = re.compile(r"^ep\d{3}-p[12]\.mp4$")
MAX_UPLOAD = 49_000_000  # margem de segurança para o limite padrão de 50 MB dos bots


def descricao_tiktok(episodio: dict) -> str:
    """Legenda editável, com os detalhes reais do roteiro e sem spoilers adicionados."""
    titulo = str(episodio.get("titulo", "História da Nina")).strip()
    parte = str(episodio.get("parte", "")).strip()
    cabecalho = f"{titulo} — Parte {parte}" if parte in ("1", "2") else titulo
    texto = str(episodio.get("legenda_post", "")).strip()
    if not texto:
        batidas = episodio.get("batidas") or []
        texto = str((batidas[0] if batidas else {}).get("fala", "")).strip()
        texto += "\n\nO que você faria? Conte nos comentários."
        texto += "\n\nHistória de ficção."
    tags = [] if "#ninamecontou" in texto.lower() else ["#ninamecontou"]
    if "#tiktokbrasil" not in texto.lower():
        tags.append("#tiktokbrasil")
    descricao = cabecalho + "\n\n" + texto
    if tags:
        descricao += "\n\n" + " ".join(tags)
    # A mensagem é isolada para facilitar copiar e colar no TikTok.
    return descricao[:3900]


def http_telegram(token: str, method: str, data: dict, arquivo: Path | None = None) -> dict:
    url = f"https://api.telegram.org/bot{token}/{method}"
    try:
        if arquivo is not None:
            with arquivo.open("rb") as stream:
                response = requests.post(
                    url, data=data,
                    files={"document": (arquivo.name, stream, "video/mp4")},
                    timeout=(20, 300),
                )
        else:
            response = requests.post(url, data=data, timeout=(20, 60))
        result = response.json()
    except (requests.RequestException, ValueError) as exc:
        # A URL de exceções HTTP pode conter o token: nunca imprimi-la.
        raise RuntimeError(f"Falha ao acessar Telegram ({type(exc).__name__})") from None
    if not response.ok or not result.get("ok"):
        erro = str(result.get("description", "erro sem detalhes"))[:200]
        raise RuntimeError(f"Telegram rejeitou {method}: {erro}")
    return result["result"]


def validar_mp4(video: Path) -> None:
    """Só envia arquivos finalizados, com vídeo, áudio e duração legível."""
    if not video.is_file() or video.stat().st_size < 1024:
        raise RuntimeError(f"{video.name}: MP4 ausente ou vazio")
    try:
        info = json.loads(subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries",
             "format=duration:stream=codec_type", "-of", "json", str(video)],
            text=True, stderr=subprocess.DEVNULL, timeout=45,
        ))
        duracao = float(info.get("format", {}).get("duration", 0))
        tipos = {s.get("codec_type") for s in info.get("streams", [])}
    except (subprocess.SubprocessError, ValueError, TypeError, KeyError):
        raise RuntimeError(f"{video.name}: MP4 ainda incompleto ou inválido") from None
    if not 3 <= duracao <= 3600 or not {"video", "audio"} <= tipos:
        raise RuntimeError(f"{video.name}: faltam vídeo, áudio ou duração válida")


def preparar_arquivo(video: Path, pasta: Path) -> Path:
    if video.stat().st_size <= MAX_UPLOAD:
        return video
    # MP4 original permanece intacto. Reduz apenas a cópia enviada ao bot.
    duration = float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video)], text=True
    ).strip())
    bps = max(400_000, min(1_800_000, int(44_000_000 * 8 / max(duration, 1) - 96_000)))
    saida = pasta / video.name
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(video),
         "-vf", "scale=720:-2", "-c:v", "libx264", "-preset", "veryfast",
         "-b:v", str(bps), "-maxrate", str(bps), "-bufsize", str(2 * bps),
         "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", str(saida)],
        check=True
    )
    if saida.stat().st_size > MAX_UPLOAD:
        raise RuntimeError(f"{video.name}: MP4 acima do limite de 49 MB mesmo após compressão")
    return saida


def recibos_ler() -> dict:
    if RECIBOS.exists():
        return json.loads(RECIBOS.read_text(encoding="utf-8"))
    return {}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video-dir", type=Path, default=ROOT / "entrega_nina")
    parser.add_argument("--dry-run", action="store_true", help="Mostra legendas sem enviar")
    args = parser.parse_args()
    videos = sorted(p for p in args.video_dir.glob("*.mp4") if RX_MP4.fullmatch(p.name))
    if not videos:
        print("Nenhum MP4 novo para enviar ao Telegram.")
        return 0
    token = os.environ.get("TELEGRAM_BOT_TOKEN_NINA", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID_NINA", "").strip()
    if not args.dry_run and (not token or not chat_id):
        print("::warning::Envio Telegram ainda não ativado: configure os dois GitHub Secrets.")
        return 0

    recebidos = recibos_ler()
    enviados = 0
    with tempfile.TemporaryDirectory(prefix="nina-telegram-") as tmp:
        for video in videos:
            # O workflow já concluiu o render e baixou o artifact. Confirmar
            # também que o MP4 contém áudio e vídeo antes de qualquer envio.
            validar_mp4(video)
            episodio_path = ROOT / "episodios" / f"{video.stem}.json"
            if not episodio_path.exists():
                raise FileNotFoundError(f"Roteiro do MP4 não encontrado: {episodio_path.name}")
            episodio = json.loads(episodio_path.read_text(encoding="utf-8"))
            descricao = descricao_tiktok(episodio)
            with video.open("rb") as stream:
                digest = hashlib.sha256()
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
                hash_mp4 = digest.hexdigest()
            if recebidos.get(video.stem, {}).get("hash") == hash_mp4:
                print(f"Já entregue: {video.name}")
                continue
            if args.dry_run:
                print(f"DRY RUN {video.name}\n{descricao}\n")
                continue

            arquivo = preparar_arquivo(video, Path(tmp))
            validar_mp4(arquivo)
            cabecalho = f"🎬 Nina Me Contou — {episodio.get('titulo', video.stem)} | Parte {episodio.get('parte', '?')}\nMP4 para publicar no TikTok. Descrição na próxima mensagem."
            resultado = http_telegram(
                token, "sendDocument",
                {"chat_id": chat_id, "caption": cabecalho[:1000]},
                arquivo=arquivo,
            )
            # Evitar ultrapassar a taxa de mensagens da conversa no Telegram.
            time.sleep(1.1)
            # Enviar texto separado: o usuário copia apenas a legenda no TikTok.
            http_telegram(token, "sendMessage", {"chat_id": chat_id, "text": descricao})
            recebidos[video.stem] = {
                "hash": hash_mp4,
                "telegram_message_id": resultado.get("message_id"),
            }
            RECIBOS.parent.mkdir(parents=True, exist_ok=True)
            RECIBOS.write_text(
                json.dumps(recebidos, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            enviados += 1
            print(f"Entregue {video.name} e descrição para TikTok")
    print(f"Enviados: {enviados}; MP4 novos encontrados: {len(videos)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
