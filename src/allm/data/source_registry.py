"""Source provenance and license gates for the corpus layers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path
from typing import Any, Iterable


class CorpusLayer(str, Enum):
    REDISTRIBUTABLE_TRAIN = "redistributable_train"
    RESEARCH_ONLY_TRAIN = "research_only_train"
    AUXILIARY_ANNOTATIONS = "auxiliary_annotations"
    GOLD_EVALUATION = "gold_evaluation"


class SourceStatus(str, Enum):
    PROPOSED = "proposed"
    UNDER_REVIEW = "under_review"
    APPROVED_RESEARCH = "approved_research"
    APPROVED_REDISTRIBUTABLE = "approved_redistributable"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass(frozen=True)
class SourceSpec:
    source_id: str
    title: str
    provider: str
    release: str
    uri: str
    license: str
    layer: CorpusLayer
    status: SourceStatus
    language: str
    register: str
    domain: str
    era: str
    provenance: str
    commercial_training_allowed: bool = False
    redistribution_allowed: bool = False
    derived_model_allowed: bool = False
    attribution_required: bool = True
    non_commercial: bool = True
    notes: str = ""

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "SourceSpec":
        return cls(
            source_id=value["source_id"],
            title=value["title"],
            provider=value["provider"],
            release=value["release"],
            uri=value["uri"],
            license=value["license"],
            layer=CorpusLayer(value["layer"]),
            status=SourceStatus(value["status"]),
            language=value["language"],
            register=value["register"],
            domain=value["domain"],
            era=value["era"],
            provenance=value["provenance"],
            commercial_training_allowed=bool(value.get("commercial_training_allowed", False)),
            redistribution_allowed=bool(value.get("redistribution_allowed", False)),
            derived_model_allowed=bool(value.get("derived_model_allowed", False)),
            attribution_required=bool(value.get("attribution_required", True)),
            non_commercial=bool(value.get("non_commercial", True)),
            notes=value.get("notes", ""),
        )

    def validate(self) -> None:
        required = {
            "source_id": self.source_id,
            "title": self.title,
            "provider": self.provider,
            "release": self.release,
            "uri": self.uri,
            "license": self.license,
            "language": self.language,
            "register": self.register,
            "domain": self.domain,
            "era": self.era,
            "provenance": self.provenance,
        }
        missing = [name for name, value in required.items() if not str(value).strip() or value == "TBD"]
        if missing:
            raise ValueError(f"source metadata is incomplete: {', '.join(missing)}")
        if self.status is SourceStatus.APPROVED_REDISTRIBUTABLE:
            if not (self.commercial_training_allowed and self.redistribution_allowed and self.derived_model_allowed):
                raise ValueError("redistributable approval requires all model-use permissions")


@dataclass(frozen=True)
class GateDecision:
    allowed: bool
    source_id: str
    layer: CorpusLayer
    reason: str


class LicenseGate:
    """Policy gate; approval is explicit and never inferred from a URL."""

    def check(self, source: SourceSpec, requested_layer: CorpusLayer | None = None) -> GateDecision:
        layer = requested_layer or source.layer
        if source.status in {SourceStatus.REJECTED, SourceStatus.EXPIRED, SourceStatus.PROPOSED, SourceStatus.UNDER_REVIEW}:
            return GateDecision(False, source.source_id, layer, f"source status is {source.status.value}")
        if layer is CorpusLayer.REDISTRIBUTABLE_TRAIN:
            allowed = (
                source.status is SourceStatus.APPROVED_REDISTRIBUTABLE
                and source.commercial_training_allowed
                and source.redistribution_allowed
                and source.derived_model_allowed
            )
            reason = "redistributable permissions are complete" if allowed else "redistributable training permissions are incomplete"
            return GateDecision(allowed, source.source_id, layer, reason)
        if layer is CorpusLayer.RESEARCH_ONLY_TRAIN:
            allowed = source.status in {SourceStatus.APPROVED_RESEARCH, SourceStatus.APPROVED_REDISTRIBUTABLE}
            return GateDecision(allowed, source.source_id, layer, "research approval exists" if allowed else "research approval is missing")
        if layer in {CorpusLayer.AUXILIARY_ANNOTATIONS, CorpusLayer.GOLD_EVALUATION}:
            allowed = source.status in {SourceStatus.APPROVED_RESEARCH, SourceStatus.APPROVED_REDISTRIBUTABLE}
            return GateDecision(allowed, source.source_id, layer, "evaluation/annotation approval exists" if allowed else "approval is missing")
        return GateDecision(False, source.source_id, layer, "unsupported corpus layer")

    def require(self, source: SourceSpec, requested_layer: CorpusLayer | None = None) -> None:
        decision = self.check(source, requested_layer)
        if not decision.allowed:
            raise PermissionError(f"license gate rejected {decision.source_id}: {decision.reason}")


class SourceRegistry:
    def __init__(self, sources: Iterable[SourceSpec]):
        self._sources = {source.source_id: source for source in sources}
        if len(self._sources) == 0:
            raise ValueError("source registry must not be empty")
        for source in self._sources.values():
            source.validate()

    @classmethod
    def from_json(cls, path: str | Path) -> "SourceRegistry":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(SourceSpec.from_dict(value) for value in payload["sources"])

    def get(self, source_id: str) -> SourceSpec:
        try:
            return self._sources[source_id]
        except KeyError as error:
            raise KeyError(f"unknown source: {source_id}") from error

    def list(self) -> list[SourceSpec]:
        return [self._sources[key] for key in sorted(self._sources)]

    def gate(self, source_id: str, requested_layer: CorpusLayer | None = None) -> GateDecision:
        source = self.get(source_id)
        return LicenseGate().check(source, requested_layer)
