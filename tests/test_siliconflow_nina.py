"""Tests for SiliconFlow opt-in API protocol (no network, no paid usage)."""
import hashlib
import io
import os
import unittest
from unittest.mock import Mock, patch
from PIL import Image
from motor import visual_images as V


def fake_png():
    buf=io.BytesIO()
    Image.new("RGB",(768,512),"orange").save(buf,format="PNG")
    return buf.getvalue()


class SiliconFlowTest(unittest.TestCase):
    def test_config_10_images_horizontal_panel(self):
        cfg=V.config()
        self.assertEqual(cfg["image_provider"],"siliconflow")
        self.assertEqual(cfg["image_size"],"768x512")
        self.assertEqual(cfg["target_images"],10)
        ep={"titulo":"Ficção","batidas":[{"fala":f"História na cena numero {i}."} for i in range(12)]}
        segs=[{"ini":i*5,"fim":i*5+5} for i in range(12)]
        scenes=V.planejar(ep,segs,cfg)
        self.assertEqual(len(scenes),10)
        self.assertEqual(sorted(i for s in scenes for i in s["beats"]),list(range(12)))

    def test_paid_api_requires_opt_in(self):
        with patch.dict(os.environ,{"NINA_ALLOW_PAID_IMAGE_API":"0","SILICONFLOW_API_KEY":"fake"}):
            with patch.object(V.requests,"post",side_effect=AssertionError("Network prohibited")) as post:
                with self.assertRaisesRegex(V.ImageFailure,"paid_image_api_disabled"):
                    V.gerar("scene",V.config())
                post.assert_not_called()

    def test_siliconflow_download_url_immediately(self):
        response=Mock(status_code=200)
        response.json.return_value={"images":[{"url":"https://images.example.net/frame.png"}]}
        image=Mock(content=fake_png())
        with patch.dict(os.environ,{"NINA_ALLOW_PAID_IMAGE_API":"1","SILICONFLOW_API_KEY":"test-only"}):
            with patch.object(V.requests,"post",return_value=response) as post:
                with patch.object(V.requests,"get",return_value=image) as get:
                    out=V.gerar("illustrated story",V.config())
        self.assertEqual(out,fake_png())
        args=post.call_args
        self.assertEqual(args.args[0],"https://api.siliconflow.com/v1/images/generations")
        self.assertEqual(args.kwargs["json"]["model"],"black-forest-labs/FLUX.1-schnell")
        self.assertEqual(args.kwargs["json"]["image_size"],"768x512")
        self.assertEqual(args.kwargs["json"]["seed"],
                         int(hashlib.sha256(b"illustrated story").hexdigest()[:8],16))
        get.assert_called_once_with("https://images.example.net/frame.png",
                                    timeout=(15,V.config()["image_timeout_seconds"]))

    def test_no_key_no_network(self):
        with patch.dict(os.environ,{"NINA_ALLOW_PAID_IMAGE_API":"1"},clear=True):
            with patch.object(V.requests,"post") as post:
                with self.assertRaisesRegex(V.ImageFailure,"missing_siliconflow_api_key"):
                    V.gerar("scene",V.config())
                post.assert_not_called()

if __name__=="__main__":
    unittest.main()
