import importlib.util
import tempfile
import unittest
from pathlib import Path


@unittest.skipUnless(importlib.util.find_spec("torch"), "PyTorch is optional locally")
class TorchInferenceTests(unittest.TestCase):
    def test_checkpoint_round_trip_and_generation(self):
        import torch

        from allm.torch_backend import (
            TorchBaselineConfig,
            checkpoint_payload,
            generate_text,
            load_checkpoint,
            train_tiny_transformer,
        )

        config = TorchBaselineConfig(epochs=1, d_model=32, nhead=4, dim_feedforward=64)
        model, vocabulary, _, device = train_tiny_transformer(["نص عربي للاختبار."], config)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "model.pt"
            torch.save(checkpoint_payload(model, vocabulary, config, {"loss": 1.0}, device), path)
            loaded_model, loaded_vocab, _, loaded_device = load_checkpoint(str(path), device="cpu")
            output = generate_text(loaded_model, loaded_vocab, "نص", max_new_tokens=2)
        self.assertIn("نص", output)
        self.assertEqual(loaded_device, "cpu")


if __name__ == "__main__":
    unittest.main()
