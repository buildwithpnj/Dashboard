"""Dataset manifest dataclass with pre-built benchmark definitions."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass


@dataclass
class DatasetManifest:
    """Immutable metadata envelope for an ingested benchmark dataset.

    Captures provenance, licensing, and ingestion parameters so that every
    downstream consumer can trace *exactly* what was loaded and under which
    terms.
    """

    dataset_name: str
    source_url: str
    split: str
    language: str
    license: str
    intended_use: str
    commercial_restriction: bool
    ingestion_version: str
    max_examples: int

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Return a plain-dict representation suitable for JSON."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> DatasetManifest:
        """Reconstruct a :class:`DatasetManifest` from a plain dict."""
        return cls(**data)

    def save_to_file(self, path: str) -> None:
        """Persist this manifest as a pretty-printed JSON file."""
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self.to_dict(), fh, indent=2, ensure_ascii=False)

    @classmethod
    def load_from_file(cls, path: str) -> DatasetManifest:
        """Load a :class:`DatasetManifest` from a JSON file on disk."""
        with open(path, "r", encoding="utf-8") as fh:
            return cls.from_dict(json.load(fh))

    # ------------------------------------------------------------------
    # Pre-built benchmark manifests
    # ------------------------------------------------------------------

    @classmethod
    def jfleg(cls) -> DatasetManifest:
        """JFLEG – grammar-error-correction benchmark (CC BY-NC-SA 4.0)."""
        return cls(
            dataset_name="jfleg",
            source_url="https://huggingface.co/datasets/jhu-clsp/jfleg",
            split="test",
            language="en",
            license="CC BY-NC-SA 4.0",
            intended_use="Grammar error correction benchmark evaluation",
            commercial_restriction=True,
            ingestion_version="v8.0",
            max_examples=1000,
        )

    @classmethod
    def samanantar_hi(cls) -> DatasetManifest:
        """Samanantar Hindi–English parallel corpus (CC BY 4.0, research-only documented)."""
        return cls(
            dataset_name="samanantar_hi",
            source_url="https://huggingface.co/datasets/ai4bharat/samanantar",
            split="train",
            language="hi-en",
            license="CC BY 4.0",
            intended_use="Hindi-English parallel translation benchmark",
            commercial_restriction=True,
            ingestion_version="v8.0",
            max_examples=1000,
        )

    @classmethod
    def massive(cls) -> DatasetManifest:
        """MASSIVE – intent classification & slot filling (CC BY 4.0)."""
        return cls(
            dataset_name="massive",
            source_url="https://huggingface.co/datasets/qanastek/MASSIVE",
            split="test",
            language="en",
            license="CC BY 4.0",
            intended_use="Intent classification and slot filling benchmark",
            commercial_restriction=False,
            ingestion_version="v8.0",
            max_examples=1000,
        )
