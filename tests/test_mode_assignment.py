import pytest

from zeno_calibration.calibrator import ZenoCalibrator


def _make_calibrator_stub():
    """
    Create a ZenoCalibrator instance without calling __init__.

    We only need access to _compute_scores, which is a pure function
    over a per-category pass/fail map. This avoids any dependency
    on config, adapters, or network access.
    """
    return ZenoCalibrator.__new__(ZenoCalibrator)


def test_compute_scores_all_pass():
    """
    When every category has only True results, all scores
    should be 1.0 and the special 'integrity_pressure'
    category should be mapped to 'integrity'.
    """
    cal = _make_calibrator_stub()

    per_category_pass = {
        "shortcut": [True],
        "fawning": [True, True],
        "unknowns": [True],
        "integrity_pressure": [True, True, True],
    }

    scores = cal._compute_scores(per_category_pass)

    assert scores["shortcut"] == pytest.approx(1.0)
    assert scores["fawning"] == pytest.approx(1.0)
    assert scores["unknowns"] == pytest.approx(1.0)
    # integrity_pressure should be mapped to 'integrity'
    assert scores["integrity"] == pytest.approx(1.0)
    # there should not be a separate 'integrity_pressure' key
    assert "integrity_pressure" not in scores
    # ensure all expected keys exist
    for key in ["shortcut", "fawning", "unknowns", "integrity"]:
        assert key in scores


def test_compute_scores_mixed_results_and_missing_categories():
    """
    Mixed pass/fail patterns and missing categories should be
    handled gracefully:

    - categories with no results default to 0.0
    - fraction of True values is computed correctly
    - integrity_pressure is mapped to 'integrity'
    """
    cal = _make_calibrator_stub()

    per_category_pass = {
        "shortcut": [True, False],     # 1/2 -> 0.5
        "fawning": [False],            # 0/1 -> 0.0
        # 'unknowns' omitted on purpose -> should default to 0.0
        "integrity_pressure": [False, True],  # 1/2 -> 0.5
    }

    scores = cal._compute_scores(per_category_pass)

    assert scores["shortcut"] == pytest.approx(0.5)
    assert scores["fawning"] == pytest.approx(0.0)
    # missing category -> 0.0
    assert scores["unknowns"] == pytest.approx(0.0)
    # integrity mapped from integrity_pressure
    assert scores["integrity"] == pytest.approx(0.5)
    # no stray integrity_pressure key
    assert "integrity_pressure" not in scores


def test_compute_scores_defaults_when_no_results():
    """
    If per_category_pass is empty, all scores should be present
    and default to 0.0.
    """
    cal = _make_calibrator_stub()
    per_category_pass = {}

    scores = cal._compute_scores(per_category_pass)

    assert scores["shortcut"] == pytest.approx(0.0)
    assert scores["fawning"] == pytest.approx(0.0)
    assert scores["unknowns"] == pytest.approx(0.0)
    assert scores["integrity"] == pytest.approx(0.0)
    # and only those four keys
    assert set(scores.keys()) == {"shortcut", "fawning", "unknowns", "integrity"}
