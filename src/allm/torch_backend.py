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
    max_steps: int = 100
    batch_size: int = 4
    learning_rate: float = 3e-4
    seed: int = 17

    def validate(self) -> None:
        if self.context_length <= 1 or self.d_model <= 0 or self.nhead <= 0:
            raise ValueError("model dimensions are invalid")
        if self.d_model % self.nhead:
            raise ValueError("d_model must be divisible by nhead")
        if self.num_layers <= 0 or self.epochs <= 0 or self.max_steps <= 0 or self.batch_size <= 0 or self.learning_rate <= 0:
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

    def encode_prompt(self, tokens: list[str]) -> list[int]:
        unknown = self.stoi["<unk>"]
        return [self.stoi["<bos>"]] + [self.stoi.get(token, unknown) for token in tokens]

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "Vocabulary":
        vocabulary = cls.__new__(cls)
        vocabulary.itos = list(value["itos"])
        vocabulary.stoi = {str(token): int(index) for token, index in value["stoi"].items()}
        return vocabulary

    def decode(self, token_ids: list[int]) -> str:
        special = {"<pad>", "<unk>", "<bos>", "<eos>"}
        tokens = [self.itos[index] for index in token_ids if 0 <= index < len(self.itos)]
        tokens = [token for token in tokens if token not in special]
        text = " ".join(tokens)
        return text.replace(" .", ".").replace(" ،", "،").replace(" ؟", "؟").replace(" ؛", "؛")

    def to_dict(self) -> dict[str, Any]:
        return {"itos": self.itos, "stoi": self.stoi}


def vocabulary_oov_rate(texts: list[str], vocabulary: Vocabulary) -> float:
    """Measure held-out token coverage without changing the vocabulary."""
    tokenizer = BaselineTokenizer()
    tokens = [token for text in texts for token in tokenizer.tokenize(text)]
    if not tokens:
        return 0.0
    unknown = sum(token not in vocabulary.stoi for token in tokens)
    return unknown / len(tokens)


def _torch():
    try:
        import torch
        from torch import nn
    except ImportError as error:
        raise RuntimeError("PyTorch is required for the neural baseline") from error
    return torch, nn


def create_tiny_model(vocab_size: int, config: TorchBaselineConfig):
    """Build the same architecture used by training and checkpoint loading."""
    torch, nn = _torch()
    config.validate()

    class TinyCausalTransformer(nn.Module):
        def __init__(self):
            super().__init__()
            self.token_embedding = nn.Embedding(vocab_size, config.d_model)
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
            self.lm_head = nn.Linear(config.d_model, vocab_size)

        def forward(self, token_ids):
            length = token_ids.size(1)
            if length > config.context_length:
                raise ValueError("sequence exceeds configured context length")
            positions = torch.arange(length, device=token_ids.device).unsqueeze(0)
            hidden = self.token_embedding(token_ids) + self.position_embedding(positions)
            mask = torch.triu(torch.ones(length, length, device=token_ids.device, dtype=torch.bool), diagonal=1)
            return self.lm_head(self.encoder(hidden, mask=mask))

    return TinyCausalTransformer()


def train_tiny_transformer(
    texts: list[str],
    config: TorchBaselineConfig | None = None,
    eval_texts: list[str] | None = None,
) -> tuple[Any, Vocabulary, dict[str, float], str]:
    """Train with fixed mini-batches and optionally report held-out loss."""
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

    def encode_sequences(values: list[str]) -> list[tuple[Any, Any]]:
        pairs = []
        for value in values:
            sequence = vocabulary.encode(tokenizer.tokenize(value))[: config.context_length + 1]
            if len(sequence) < 2:
                continue
            pairs.append((torch.tensor(sequence[:-1], dtype=torch.long), torch.tensor(sequence[1:], dtype=torch.long)))
        return pairs

    train_pairs = encode_sequences(texts)
    eval_pairs = encode_sequences(eval_texts or [])
    torch.manual_seed(config.seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = create_tiny_model(len(vocabulary.itos), config).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=config.learning_rate)
    criterion = nn.CrossEntropyLoss(ignore_index=vocabulary.pad_id)
    generator = torch.Generator().manual_seed(config.seed)
    order = torch.randperm(len(train_pairs), generator=generator).tolist()
    cursor = 0
    model.train()
    loss_value = 0.0
    loss_total = 0.0
    for _ in range(config.max_steps):
        if cursor + config.batch_size > len(order):
            order = torch.randperm(len(train_pairs), generator=generator).tolist()
            cursor = 0
        indices = order[cursor : cursor + config.batch_size]
        cursor += config.batch_size
        inputs = [train_pairs[index][0] for index in indices]
        targets = [train_pairs[index][1] for index in indices]
        input_batch = nn.utils.rnn.pad_sequence(inputs, batch_first=True, padding_value=vocabulary.pad_id).to(device)
        target_batch = nn.utils.rnn.pad_sequence(targets, batch_first=True, padding_value=vocabulary.pad_id).to(device)
        optimizer.zero_grad(set_to_none=True)
        logits = model(input_batch)
        loss = criterion(logits.reshape(-1, logits.size(-1)), target_batch.reshape(-1))
        loss.backward()
        optimizer.step()
        loss_value = float(loss.detach().cpu())
        loss_total += loss_value

    mean_loss = loss_total / config.max_steps
    metrics = {
        "loss": mean_loss,
        "perplexity": math.exp(mean_loss),
        "last_batch_loss": loss_value,
        "train_steps": float(config.max_steps),
        "train_examples": float(len(train_pairs)),
        "effective_epochs": (config.max_steps * config.batch_size) / len(train_pairs),
    }
    if eval_texts:
        eval_tokens = [token for text in eval_texts for token in tokenizer.tokenize(text)]
        metrics["eval_oov_rate"] = vocabulary_oov_rate(eval_texts, vocabulary)
        metrics["eval_token_count"] = float(len(eval_tokens))
    if eval_pairs:
        model.eval()
        with torch.no_grad():
            eval_inputs = [pair[0] for pair in eval_pairs]
            eval_targets = [pair[1] for pair in eval_pairs]
            eval_input_batch = nn.utils.rnn.pad_sequence(eval_inputs, batch_first=True, padding_value=vocabulary.pad_id).to(device)
            eval_target_batch = nn.utils.rnn.pad_sequence(eval_targets, batch_first=True, padding_value=vocabulary.pad_id).to(device)
            eval_logits = model(eval_input_batch)
            eval_loss = criterion(eval_logits.reshape(-1, eval_logits.size(-1)), eval_target_batch.reshape(-1))
            known_targets = eval_target_batch.clone()
            known_targets[known_targets == vocabulary.stoi["<unk>"]] = vocabulary.pad_id
            known_token_count = int((known_targets != vocabulary.pad_id).sum().item())
            known_loss = criterion(eval_logits.reshape(-1, eval_logits.size(-1)), known_targets.reshape(-1))
        metrics["eval_loss"] = float(eval_loss.detach().cpu())
        metrics["eval_perplexity"] = math.exp(metrics["eval_loss"])
        metrics["eval_known_token_count"] = float(known_token_count)
        if known_token_count:
            metrics["eval_known_loss"] = float(known_loss.detach().cpu())
            metrics["eval_known_perplexity"] = math.exp(metrics["eval_known_loss"])
    return model, vocabulary, metrics, device


def checkpoint_payload(model: Any, vocabulary: Vocabulary, config: TorchBaselineConfig, metrics: dict[str, float], device: str) -> dict[str, Any]:
    return {
        "model_state_dict": model.state_dict(),
        "vocabulary": vocabulary.to_dict(),
        "config": asdict(config),
        "metrics": metrics,
        "device": device,
    }


def load_checkpoint(path: str, device: str | None = None) -> tuple[Any, Vocabulary, TorchBaselineConfig, str]:
    """Load a checkpoint produced by train_torch_baseline."""
    torch, _ = _torch()
    requested_device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    if requested_device == "cuda" and not torch.cuda.is_available():
        requested_device = "cpu"
    payload = torch.load(path, map_location=requested_device, weights_only=False)
    config = TorchBaselineConfig(**payload["config"])
    vocabulary = Vocabulary.from_dict(payload["vocabulary"])
    model = create_tiny_model(len(vocabulary.itos), config).to(requested_device)
    model.load_state_dict(payload["model_state_dict"])
    model.eval()
    return model, vocabulary, config, requested_device


def generate_text(
    model: Any,
    vocabulary: Vocabulary,
    prompt: str,
    *,
    max_new_tokens: int = 20,
    temperature: float = 0.0,
) -> str:
    """Generate a short continuation using greedy or temperature sampling."""
    torch, _ = _torch()
    if max_new_tokens <= 0:
        raise ValueError("max_new_tokens must be positive")
    tokenizer = BaselineTokenizer()
    token_ids = vocabulary.encode_prompt(tokenizer.tokenize(prompt))
    device = next(model.parameters()).device
    generated = torch.tensor([token_ids], dtype=torch.long, device=device)
    eos_id = vocabulary.stoi["<eos>"]
    with torch.no_grad():
        for _ in range(max_new_tokens):
            context = generated[:, -model.position_embedding.num_embeddings :]
            logits = model(context)[:, -1, :]
            if temperature <= 0:
                next_token = logits.argmax(dim=-1, keepdim=True)
            else:
                probabilities = torch.softmax(logits / temperature, dim=-1)
                next_token = torch.multinomial(probabilities, num_samples=1)
            generated = torch.cat([generated, next_token], dim=1)
            if int(next_token.item()) == eos_id:
                break
    return vocabulary.decode(generated[0].tolist())
