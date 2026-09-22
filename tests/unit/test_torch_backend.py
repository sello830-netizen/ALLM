import importlib.util
import unittest


@unittest.skipUnless(importlib.util.find_spec("torch"), "PyTorch is optional locally")
class TorchBackendTests(unittest.TestCase):
    def test_tiny_transformer_trains(self):
        from allm.torch_backend import TorchBaselineConfig, train_tiny_transformer

        model, vocabulary, metrics, device = train_tiny_transformer(
            ["نص عربي للاختبار.", "نص آخر للاختبار."],
            TorchBaselineConfig(epochs=1, d_model=32, nhead=4, dim_feedforward=64),
        )
        self.assertGreater(len(vocabulary.itos), 4)
        self.assertGreater(metrics["perplexity"], 0)
        self.assertIn(device, {"cpu", "cuda"})
        self.assertIsNotNone(model)


if __name__ == "__main__":
    unittest.main()
