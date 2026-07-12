import pytest
from app.data_ingestion.connectors.hf_loader import HFDatasetLoader

def test_hf_loader_mock_fallback():
    loader = HFDatasetLoader()
    # If datasets package is missing or network fails, loader raises ImportError or loads successfully.
    # Let's test that loading handles max_examples gracefully.
    try:
        data = loader.load("jhu-clsp/jfleg", subset=None, split="test", max_examples=5)
        assert isinstance(data, list)
        assert len(data) <= 5
    except ImportError:
        # Graceful handling if datasets is not in current active env path
        pytest.skip("datasets package not installed in the testing environment")
