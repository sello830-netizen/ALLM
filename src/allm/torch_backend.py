"""Optional PyTorch causal Transformer backend for a small GPU smoke run."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any

from allm.tokenization import BaselineTokenizer


@dataclass(frozen=True)
class TorchBaselineConfig:
    model_id: str = "arabic-causal-tiny"
    version: str = "0.1.0"
    context_length: int = 64
    d_model: int = 128
    nhead: int = 4
    num_layers: int = 2
    dim_feedforward: int = 256
    dropout: float = 0.0
    epochs: int = 3
    learning_rate: float = 3e-4
    seed: int = 17

    def validate(self) -> None:
        if self.context_length <= 1 or self.d_model <= 0 or self.nhead <= 0:
            raise ValueError("model dimensions are invalid")
        if self.d_model % self.nhead:
            raise ValueError("d_model must be divisible by nhead")
        if self.num_layers <= 0 or self.epochs <= 0 or self.learning_rate <= 0:
            raise ValueError("training configuration is invalid")


class Vocabulary:
    def __init__(self, token_sequences: list[list[str]]):
        special = ["<pad>", "<unk>", "<bos>", "<eos>"]
        tokens = sorted({token for sequence in token_sequences for token in sequence})
        self.itos = special + [token for token in tokens if token not in special]
        self.stoi = {token: index for index, token in enumerate(self.itos)}

    @property
    def pad_id(self) -> int:
        return self.stoi["<pad>"]

    def encode(self, tokens: list[str]) -> list[int]:
        unknown = self.stoi["<unk>"]
        return [self.stoi["<bos>"]] + [self.stoi.get(token, unknown) for token in tokens] + [self.stoi["<eos>"]]

    def to_dict(self) -> dict[str, Any]:
        return {"itos": self.itos, "stoi": self.stoi}


def _torch():
    try:
        import torch
        from torch import nn
    except ImportError as error:
        raise RuntimeError("PyTorch is required for the neural baseline") from error
    return torch, nn


def train_tiny_transformer(
    texts: list[str], config: TorchBaselineConfig | None = None
) -> tuple[Any, Vocabulary, dict[str, float], str]:
    """Train a tiny causal Transformer and return model, vocabulary, metrics, device."""
    torch, nn = _torch()
    config = config or TorchBaselineConfig()
    config.validate()
    if not texts:
        raise ValueError("texts must not be empty")

    tokenizer = BaselineTokenizer()
    token_sequences = [tokenizer.tokenize(text) for text in texts]
    if any(not sequence for sequence in token_sequences):
        raise ValueError("texts must produce at least one token")
    vocabulary = Vocabulary(token_sequences)
    sequences = [vocabulary.encode(tokens)[: config.context_length + 1] for tokens in token_sequences]
    inputs = [torch.tensor(sequence[:-1], dtype=torch.long) for sequence in sequences]
    targets = [torch.tensor(sequence[1:], dtype=torch.long) for sequence in sequences]
    input_batch = nn.utils.rnn.pad_sequence(inputs, batch_first=True, padding_value=vocabulary.pad_id)
    target_batch = nn.utils.rnn.pad_sequence(targets, batch_first=True, padding_value=vocabulary.pad_id)

    torch.manual_seed(config.seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    class TinyCausalTransformer(nn.Module):
        def __init__(self):
            super().__init__()
            self.token_embedding = nn.Embedding(len(vocabulary.itos), config.d_model)
            self.position_embedding = nn.Embedding(config.context_length, config.d_model)
            layer = nn.TransformerEncoderLayer(
                d_model=config.d_model,
                nhead=config.nhead,
                dim_feedforward=config.dim_feedforward,
                dropout=config.dropout,
                batch_first=True,
                norm_first=True,
            )
            self.encoder = nn.TransformerEncoder(layer, num_layers=config.num_layers)
            self.lm_head = nn.Linear(config.d_model, len(vocabulary.itos))

        def forward(self, token_ids):
            length = token_ids.size(1)
            positions = torch.arange(length, device=token_ids.device).unsqueeze(0)
            hidden = self.token_embedding(token_ids) + self.position_embedding(positions)
            mask = torch.triu(torch.ones(length, length, device=token_ids.device, dtype=torch.bool), diagonal=1)
            return self.lm_head(self.encoder(hidden, mask=mask))

    model = TinyCausalTransformer().to(device)
    input_batch = input_batch.to(device)
    target_batch = target_batch.to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=config.learning_rate)
    criterion = nn.CrossEntropyLoss(ignore_index=vocabulary.pad_id)
    model.train()
    loss_value = 0.0
    for _ in range(config.epochs):
        optimizer.zero_grad(set_to_none=True)
        logits = model(input_batch)
        loss = criterion(logits.reshape(-1, logits.size(-1)), target_batch.reshape(-1))
        loss.backward()
        optimizer.step()
        loss_value = float(loss.detach().cpu())

    return model, vocabulary, {"loss": loss_value, "perplexity": math.exp(loss_value)}, device


def checkpoint_payload(model: Any, vocabulary: Vocabulary, config: TorchBaselineConfig, metrics: dict[str, float], device: str) -> dict[str, Any]:
    return {
        "model_state_dict": model.state_dict(),
        "vocabulary": vocabulary.to_dict(),
        "config": asdict(config),
        "metrics": metrics,
        "device": device,
    }
