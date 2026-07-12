import os
import tempfile
from app.data_ingestion.connectors.dataset_manifest import DatasetManifest
from app.data_ingestion.connectors.license_checker import LicenseChecker

def test_manifest_serialization():
    manifest = DatasetManifest.jfleg()
    d = manifest.to_dict()
    assert d["dataset_name"] == "jfleg"
    assert d["commercial_restriction"] is True

    # Roundtrip from dict
    manifest2 = DatasetManifest.from_dict(d)
    assert manifest2.dataset_name == "jfleg"

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = os.path.join(tmpdir, "manifest.json")
        manifest.save_to_file(tmp_path)
        
        loaded = DatasetManifest.load_from_file(tmp_path)
        assert loaded.dataset_name == "jfleg"

def test_license_checker():
    checker = LicenseChecker()
    jfleg = DatasetManifest.jfleg()
    massive = DatasetManifest.massive()

    # Development environment checks
    dev_jfleg = checker.validate_manifest(jfleg, app_env="development")
    assert dev_jfleg["allowed"] is True
    assert len(dev_jfleg["warnings"]) > 0

    # Production environment checks
    prod_jfleg = checker.validate_manifest(jfleg, app_env="production")
    assert prod_jfleg["allowed"] is False
    assert any("cannot" in w.lower() or "blocked" in w.lower() for w in prod_jfleg["warnings"])


    # Commercial-friendly check
    prod_massive = checker.validate_manifest(massive, app_env="production")
    assert prod_massive["allowed"] is True
    assert len(prod_massive["warnings"]) == 0
