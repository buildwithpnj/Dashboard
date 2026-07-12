"""License compliance checker for dataset manifests."""

import logging
from typing import Dict, List

from app.data_ingestion.connectors.dataset_manifest import DatasetManifest

logger = logging.getLogger(__name__)


class LicenseChecker:
    """Validates whether a dataset manifest is cleared for a given environment.

    In *production* mode, any dataset with ``commercial_restriction=True`` is
    blocked outright.  In other environments (e.g. ``development``, ``test``)
    a warning is emitted but ingestion is allowed.
    """

    def validate_manifest(
        self,
        manifest: DatasetManifest,
        app_env: str = "development",
    ) -> Dict[str, object]:
        """Check *manifest* against licensing rules for *app_env*.

        Returns
        -------
        dict
            ``{"allowed": bool, "warnings": list[str]}``
        """
        warnings: List[str] = []
        allowed = True

        if manifest.commercial_restriction:
            if app_env == "production":
                msg = (
                    f"Dataset '{manifest.dataset_name}' has commercial restrictions "
                    f"(license: {manifest.license}) and CANNOT be used in production."
                )
                warnings.append(msg)
                logger.warning(msg)
                allowed = False
            else:
                msg = (
                    f"Dataset '{manifest.dataset_name}' has commercial restrictions "
                    f"(license: {manifest.license}). Allowed in '{app_env}' environment "
                    f"but blocked in production."
                )
                warnings.append(msg)
                logger.warning(msg)

        if not manifest.source_url:
            msg = f"Dataset '{manifest.dataset_name}' is missing a source URL."
            warnings.append(msg)
            logger.warning(msg)

        if warnings:
            logger.info(
                "License check for '%s' completed with %d warning(s).",
                manifest.dataset_name,
                len(warnings),
            )
        else:
            logger.info(
                "License check for '%s' passed – no restrictions.",
                manifest.dataset_name,
            )

        return {"allowed": allowed, "warnings": warnings}
