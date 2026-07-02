"""
test_data_quality.py — pytest wrappers around the most critical business-logic
data quality checks (01, 02, 12, 13, 15) so they also run in CI.
"""

import importlib.util
import os

import pytest

# Load pipeline/data_quality_checks.py by path (pipeline/ is not an import package).
_DQC_PATH = os.path.join(os.path.dirname(__file__), "..", "pipeline", "data_quality_checks.py")
_spec = importlib.util.spec_from_file_location("data_quality_checks", _DQC_PATH)
dqc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dqc)


@pytest.fixture(scope="module")
def df():
    return dqc._load()


def test_check_01_row_count(df):
    assert dqc.check_01_row_count(df)[0]


def test_check_02_unique_patients(df):
    assert dqc.check_02_unique_patients(df)[0]


def test_check_12_mortality_rate(df):
    assert dqc.check_12_mortality_rate(df)[0]


def test_check_13_emergency_rate(df):
    assert dqc.check_13_emergency_rate(df)[0]


def test_check_15_expired_count(df):
    assert dqc.check_15_expired_count(df)[0]
