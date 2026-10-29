import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

tg = module('telegram_nina', 'tools/telegram_nina.py')
cleanup = module('limpar_reels', 'motor/limpar_reels.py')

class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.video_dir = self.root / 'reels'
        self.video_dir.mkdir()
        self.video = self.video_dir / 'ep045-p1.mp4'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i',
                        'color=s=160x240:r=10', '-f', 'lavfi', '-i',
                        'sine=frequency=440', '-t', '4', '-c:v', 'libx264',
                        '-c:a', 'aac', str(self.video)], check=True)
        (self.root / 'episodios').mkdir()
        (self.root / 'episodios/ep045-p1.json').write_text(json.dumps({
            'titulo': 'A festa', 'parte': 1, 'legenda_post': 'Uma festa inesperada. #festa'}))
        self.receipts = self.root / 'conteudo/telegram_entregues.json'
        self.patches = [patch.object(tg, 'ROOT', self.root), patch.object(tg, 'RECIBOS', self.receipts),
                        patch.object(tg.time, 'sleep'), patch.dict(os.environ, {
                            'TELEGRAM_BOT_TOKEN_NINA': 'test-only', 'TELEGRAM_CHAT_ID_NINA': '123'})]
        for p in self.patches:
            p.start()
    def tearDown(self):
        for p in self.patches:
            p.stop()
        self.tmp.cleanup()
    def run_delivery(self):
        with patch.object(tg, 'diagnostico', return_value=None):
            return self._run()
    def _run(self):
        with patch.object(sys, 'argv', ['telegram_nina', '--video-dir', str(self.video_dir)]):
            return tg.main()
    def test_delivery_and_no_duplicate(self):
        with patch.object(tg, 'http_telegram', side_effect=[
            {'message_id': 1, 'document': {'file_id': 'test-file', 'file_size': self.video.stat().st_size}},
            {'message_id': 2}]) as api:
            self.assertEqual(self.run_delivery(), 0)
            self.assertEqual(self.run_delivery(), 0)
            self.assertEqual(api.call_count, 2)
        self.assertEqual(json.loads(self.receipts.read_text())['ep045-p1']['status'], 'complete')
    def test_uncertain_description_resends_only_description(self):
        with patch.object(tg, 'http_telegram', side_effect=[
            {'message_id': 1, 'document': {'file_id': 'test-file'}}, RuntimeError('timeout')]):
            self.assertEqual(self.run_delivery(), 1)
        with patch.object(tg, 'http_telegram', return_value={'message_id': 3}) as api:
            self.assertEqual(self.run_delivery(), 0)
            self.assertEqual(api.call_count, 1)
            self.assertEqual(api.call_args.args[1], 'sendMessage')
        self.assertEqual(json.loads(self.receipts.read_text())['ep045-p1']['status'], 'complete')
    def test_uncertain_video_gives_up_after_limit(self):
        with patch.object(tg, 'http_telegram', side_effect=RuntimeError('timeout')) as api:
            for _ in range(4):
                self.assertEqual(self.run_delivery(), 1)
            self.assertEqual(api.call_count, 4)  # 1 envio + 3 repetições, depois para
            self.assertEqual(self.run_delivery(), 1)
            self.assertEqual(api.call_count, 4)
    def test_one_bad_video_does_not_block_others(self):
        bad = self.video_dir / 'ep044-p2.mp4'
        bad.write_bytes(b'x' * 2048)
        with patch.object(tg, 'http_telegram', side_effect=[
            {'message_id': 1, 'document': {'file_id': 'f'}}, {'message_id': 2}]) as api:
            self.assertEqual(self.run_delivery(), 1)
            self.assertEqual(api.call_count, 2)
        self.assertEqual(json.loads(self.receipts.read_text())['ep045-p1']['status'], 'complete')
    def test_tiktok_description_has_story_tags_and_part(self):
        d = tg.descricao_tiktok({'titulo': 'CARTÃO', 'parte': 1, 'temporada': 'Casais',
            'legenda_post': 'Isabela achou um cartão. A continuação está no perfil.\n\n#storytime #fofoca'})
        self.assertIn('CARTÃO — Parte 1/2', d)
        for tag in ('#fofoca', '#casais', '#traicao', '#ninamecontou', '#tiktokbrasil'):
            self.assertIn(tag, d)
        self.assertEqual(d.count('#storytime'), 1)
        self.assertIn('parte 2', d)
    def test_config_error_stops_and_limit_counts_attempts(self):
        other = self.video_dir / 'ep046-p1.mp4'
        other.write_bytes(self.video.read_bytes())
        (self.root / 'episodios/ep046-p1.json').write_text(json.dumps({'titulo': 'B', 'parte': 1}))
        with patch.object(tg, 'http_telegram', side_effect=tg.TelegramRejected('Telegram rejeitou sendDocument: Bad Request: chat not found')) as api:
            self.assertEqual(self.run_delivery(), 1)
            self.assertEqual(api.call_count, 1)
        with patch.object(sys, 'argv', ['telegram_nina', '--video-dir', str(self.video_dir), '--limit', '1']), \
             patch.object(tg, 'http_telegram', side_effect=RuntimeError('timeout')) as api:
            with patch.object(tg, 'diagnostico', return_value=None):
                self.assertEqual(tg.main(), 1)
            self.assertEqual(api.call_count, 1)
    def test_invalid_video_rejected(self):
        self.video.write_bytes(b'x' * 2048)
        with patch.object(tg, 'http_telegram') as api:
            self.assertEqual(self.run_delivery(), 1)
            api.assert_not_called()
    def test_missing_credentials_fails(self):
        with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN_NINA': ''}):
            self.assertEqual(self.run_delivery(), 1)
    def test_cleanup_requires_matching_complete_receipt(self):
        with patch.object(cleanup, 'RAIZ', self.root), patch.object(cleanup, 'REELS', self.video_dir), patch.object(cleanup, 'publicados', return_value={'ep045-p1'}):
            self.assertEqual(cleanup.limpar()['removidos'], 0)
            self.receipts.parent.mkdir(parents=True)
            self.receipts.write_text(json.dumps({'ep045-p1': {'hash': 'wrong', 'status': 'complete'}}))
            self.assertEqual(cleanup.limpar()['removidos'], 0)
            digest = hashlib.sha256(self.video.read_bytes()).hexdigest()
            self.receipts.write_text(json.dumps({'ep045-p1': {'hash': digest, 'status': 'complete'}}))
            self.assertEqual(cleanup.limpar()['removidos'], 1)

if __name__ == '__main__':
    unittest.main()
