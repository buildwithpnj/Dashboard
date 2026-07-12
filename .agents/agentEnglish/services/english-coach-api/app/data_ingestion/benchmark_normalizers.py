"""Benchmark-specific normalizers that map raw HF records to a common schema."""

from typing import Any, Dict, List


def normalize_jfleg(record: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize a raw JFLEG record into the platform evaluation schema.

    Expected raw keys: ``sentence`` (source) and ``corrections`` (list of
    corrected versions).

    Returns
    -------
    dict
        ``{"input": str, "corrections": list[str], "task_type": "correction"}``
    """
    return {
        "input": record.get("sentence", ""),
        "corrections": record.get("corrections", []),
        "task_type": "correction",
    }


def normalize_samanantar(record: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize a raw Samanantar Hindi–English parallel record.

    Expected raw keys: ``src`` (Hindi) and ``tgt`` (English).

    Returns
    -------
    dict
        ``{"source_text": str, "target_text": str, "source_lang": "hi",
        "target_lang": "en", "task_type": "translation"}``
    """
    return {
        "source_text": record.get("src", ""),
        "target_text": record.get("tgt", ""),
        "source_lang": "hi",
        "target_lang": "en",
        "task_type": "translation",
    }


def normalize_massive(record: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize a raw MASSIVE record for intent routing evaluation.

    Expected raw keys: ``utt`` (utterance), ``intent``, ``annot_utt``
    (annotated utterance with slot markup), ``locale``.

    Returns
    -------
    dict
        ``{"utterance": str, "intent": str, "annotated_utterance": str,
        "locale": str, "task_type": "intent_routing"}``
    """
    return {
        "utterance": record.get("utt", ""),
        "intent": record.get("intent", ""),
        "annotated_utterance": record.get("annot_utt", ""),
        "locale": record.get("locale", ""),
        "task_type": "intent_routing",
    }
