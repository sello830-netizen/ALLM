"""Generate a short continuation from a saved tiny Transformer checkpoint."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from allm.torch_backend import generate_text, load_checkpoint


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("checkpoint", type=Path)
    parser.add_argument("prompt")
    parser.add_argument("--max-new-tokens", type=int, default=20)
    parser.add_argument("--temperature", type=float, default=0.0)
    args = parser.parse_args()

    model, vocabulary, config, device = load_checkpoint(str(args.checkpoint))
    generated = generate_text(
        model,
        vocabulary,
        args.prompt,
        max_new_tokens=args.max_new_tokens,
        temperature=args.temperature,
    )
    print(json.dumps({
        "model_id": config.model_id,
        "device": device,
        "prompt": args.prompt,
        "generated": generated,
        "max_new_tokens": args.max_new_tokens,
        "temperature": args.temperature,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
