"""Train and register the tiny optional PyTorch baseline."""

import argparse
import json
from dataclasses import replace
from pathlib import Path
import subprocess

from allm.domain import Run, RunStatus, stable_hash
from allm.registry import RunRegistry
from allm.tokenization import BaselineTokenizer
from allm.torch_backend import TorchBaselineConfig, checkpoint_payload, train_tiny_transformer


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="UTF-8 newline-delimited text")
    parser.add_argument("registry", type=Path, help="JSONL run registry")
    parser.add_argument("checkpoint", type=Path, help="PyTorch checkpoint destination")
    parser.add_argument("--dev-input", type=Path, help="optional held-out newline-delimited text")
    parser.add_argument("--max-steps", type=int, default=100)
    parser.add_argument("--batch-size", type=int, default=4)
    args = parser.parse_args()

    import torch

    texts = [line.strip() for line in args.input.read_text(encoding="utf-8").splitlines() if line.strip()]
    dev_texts = None
    if args.dev_input:
        dev_texts = [line.strip() for line in args.dev_input.read_text(encoding="utf-8").splitlines() if line.strip()]
    config = replace(TorchBaselineConfig(), max_steps=args.max_steps, batch_size=args.batch_size)
    model, vocabulary, metrics, device = train_tiny_transformer(texts, config, eval_texts=dev_texts)
    dataset_hash = stable_hash(texts)
    try:
        code_revision = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=Path(__file__).resolve().parents[1], text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        code_revision = "working-tree"
    config_hash = stable_hash({"config": config.__dict__, "torch": torch.__version__})
    run = Run(
        run_id=f"torch-{dataset_hash[:12]}-{config.version}-{code_revision[:12]}-{config_hash[:8]}",
        experiment_id="torch-tiny-baseline-v0",
        status=RunStatus.COMPLETED,
        code_revision=code_revision,
        config_hash=config_hash,
        dataset_hash=dataset_hash,
        tokenizer_hash=stable_hash(vocabulary.to_dict()),
        evaluation_hash="unigram-and-bigram-v0",
        seed=config.seed,
        steps=int(metrics["train_steps"]),
        tokens=sum(len(BaselineTokenizer().tokenize(text)) + 2 for text in texts),
        metrics={**metrics, "device_cuda": float(device == "cuda")},
    )
    args.checkpoint.parent.mkdir(parents=True, exist_ok=True)
    torch.save(checkpoint_payload(model, vocabulary, config, metrics, device), args.checkpoint)
    recorded_run = RunRegistry(args.registry).append_once(run)
    print(json.dumps(recorded_run.to_dict(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
