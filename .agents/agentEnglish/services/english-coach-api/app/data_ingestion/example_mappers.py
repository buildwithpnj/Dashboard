"""Maps normalized benchmark records to evaluation examples with deterministic IDs."""

import hashlib
import json
from typing import Any, Dict


class ExampleMapper:
    """Produces evaluation-ready examples with reproducible identifiers.

    Every mapped example receives:

    * **example_id** – a deterministic SHA-256 hex digest derived from the
      dataset name and the serialised content, ensuring stable IDs across
      repeated ingestion runs.
    * **content_hash** – a SHA-256 hex digest of the content alone, useful
      for deduplication checks.
    """

    @staticmethod
    def generate_deterministic_id(dataset_name: str, content: str) -> str:
        """Return a SHA-256 hex digest of ``dataset_name + content``."""
        payload = f"{dataset_name}:{content}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @staticmethod
    def generate_content_hash(content: str) -> str:
        """Return a SHA-256 hex digest of *content*."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    @classmethod
    def map_to_eval_example(
        cls,
        normalized: Dict[str, Any],
        dataset_name: str,
    ) -> Dict[str, Any]:
        """Wrap a normalized record as a full evaluation example.

        Parameters
        ----------
        normalized:
            A dict produced by one of the benchmark normalizers.
        dataset_name:
            The logical name of the source dataset (used in ID generation).

        Returns
        -------
        dict
            The original *normalized* fields plus ``example_id``,
            ``content_hash``, and ``dataset_name``.
        """
        # Serialise content deterministically for hashing.
        content_str = json.dumps(normalized, sort_keys=True, ensure_ascii=False)

        example: Dict[str, Any] = {
            **normalized,
            "dataset_name": dataset_name,
            "example_id": cls.generate_deterministic_id(dataset_name, content_str),
            "content_hash": cls.generate_content_hash(content_str),
        }
        return example

