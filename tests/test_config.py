import pytest

from trc_lcs.config import TRCLCSConfig


def test_config_rejects_invalid_budget():
    with pytest.raises(ValueError):
        TRCLCSConfig(budget=0)


def test_config_serializes():
    cfg = TRCLCSConfig(budget=2)
    assert cfg.to_dict()["budget"] == 2
