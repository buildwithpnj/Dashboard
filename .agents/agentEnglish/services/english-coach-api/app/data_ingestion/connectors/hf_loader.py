"""Hugging Face dataset loader with lazy import and example capping."""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class HFDatasetLoader:
    """Loads datasets from Hugging Face Hub with lazy dependency import.

    The ``datasets`` library is imported inside :meth:`load` so that the rest
    of the application can start even when the library is not installed.
    """

    def load(
        self,
        dataset_name: str,
        subset: Optional[str] = None,
        split: str = "test",
        max_examples: int = 1000,
    ) -> List[dict]:
        """Download / cache a HF dataset split and return raw dicts.

        Parameters
        ----------
        dataset_name:
            Repository ID on the Hugging Face Hub (e.g. ``"jhu-clsp/jfleg"``).
        subset:
            Optional dataset configuration / subset name.
        split:
            Which split to load (default ``"test"``).
        max_examples:
            Hard cap on the number of examples returned.  The dataset is
            sliced *after* download so that the full cache is preserved.

        Returns
        -------
        List[dict]
            A list of at most *max_examples* raw records.

        Raises
        ------
        ImportError
            If the ``datasets`` library is not installed.
        """
        try:
            import datasets  # noqa: WPS433 – lazy import by design
        except ImportError:
            raise ImportError(
                "The 'datasets' library is required for HFDatasetLoader. "
                "Install it with:  pip install datasets"
            )

        logger.info(
            "Loading HF dataset '%s' (subset=%s, split=%s, max=%d) …",
            dataset_name,
            subset,
            split,
            max_examples,
        )

        ds = datasets.load_dataset(dataset_name, subset, split=split)

        # Enforce the example cap via slicing.
        if len(ds) > max_examples:
            ds = ds.select(range(max_examples))

        records: List[dict] = [dict(row) for row in ds]

        logger.info(
            "Loaded %d examples from '%s' (split=%s).",
            len(records),
            dataset_name,
            split,
        )
        return records
