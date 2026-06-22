import pytest

from custom_components.biterisk import const
from custom_components.biterisk.scoring import (
    apply_floor,
    combine,
    humidity_factor,
    temp_factor,
    time_factor,
    to_label,
    wind_factor,
)


@pytest.mark.parametrize(
    "t,expected",
    [
        (5.0, 0.0),  # below active
        (10.0, 0.0),  # threshold
        (22.0, 1.0),  # in optimum plateau
        (25.0, 1.0),  # optimum high edge
        (40.0, 0.0),  # above active
    ],
)
def test_temp_factor(t, expected):
    assert temp_factor(t) == pytest.approx(expected, abs=0.01)


def test_temp_factor_ramps_between_min_and_opt():
    mid = temp_factor(15.0)  # halfway 10->20
    assert 0.0 < mid < 1.0


@pytest.mark.parametrize(
    "h,expected",
    [
        (40.0, 0.0),
        (50.0, 0.0),
        (80.0, 1.0),
        (95.0, 1.0),
    ],
)
def test_humidity_factor(h, expected):
    assert humidity_factor(h) == pytest.approx(expected, abs=0.01)


@pytest.mark.parametrize(
    "w,expected",
    [
        (0.0, 1.0),
        (0.5, 1.0),
        (3.0, 0.0),
        (5.0, 0.0),
    ],
)
def test_wind_factor(w, expected):
    assert wind_factor(w) == pytest.approx(expected, abs=0.01)


def test_time_factor_peaks_at_dusk():
    # 0 min offset from sunset is inside the peak window
    assert time_factor(0) == pytest.approx(const.TIME_PEAK)
    # deep day (6h before sunset) = day base
    assert time_factor(-360) == pytest.approx(const.TIME_DAY_BASE)


def test_combine_weighted_sum():
    score = combine(brood=1.0, temp=1.0, humidity=1.0, wind=1.0, time=1.0)
    assert score == pytest.approx(100.0)
    zero = combine(brood=0.0, temp=0.0, humidity=0.0, wind=0.0, time=0.0)
    assert zero == pytest.approx(0.0)


def test_combine_hard_cutoff_cold():
    # temp below active forces ~0 regardless of other factors
    score = combine(
        brood=1.0,
        temp=0.0,
        humidity=1.0,
        wind=1.0,
        time=1.0,
        temp_c=5.0,
        wind_ms=0.0,
    )
    assert score == 0.0


def test_combine_hard_cutoff_wind():
    score = combine(
        brood=1.0,
        temp=1.0,
        humidity=1.0,
        wind=0.0,
        time=1.0,
        temp_c=22.0,
        wind_ms=3.0,
    )
    assert score == 0.0


def test_apply_floor():
    assert apply_floor(100.0, const.FLOOR_FIRST) == pytest.approx(80.0)
    assert apply_floor(100.0, const.FLOOR_SECOND_PLUS) == pytest.approx(60.0)
    assert apply_floor(100.0, const.FLOOR_GROUND) == pytest.approx(100.0)


@pytest.mark.parametrize(
    "score,label",
    [
        (0, const.RISK_LOW),
        (33, const.RISK_LOW),
        (34, const.RISK_MEDIUM),
        (66, const.RISK_MEDIUM),
        (67, const.RISK_HIGH),
        (100, const.RISK_HIGH),
    ],
)
def test_to_label(score, label):
    assert to_label(score) == label
