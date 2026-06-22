# tests/test_brood.py
from custom_components.biterisk import const
from custom_components.biterisk.brood import BroodBuffer


def test_empty_buffer_scores_zero():
    buf = BroodBuffer()
    assert buf.score() == 0.0


def test_rain_in_peak_window_scores_higher_than_recent_rain():
    recent = BroodBuffer()
    # rain 1 day ago (index 0..23) — should barely count
    for h in range(24):
        recent.set_hour(h, 5.0)

    peak = BroodBuffer()
    # rain ~10 days ago (within 7-14 day peak window)
    for h in range(const.LAG_PEAK_START_H, const.LAG_PEAK_START_H + 24):
        peak.set_hour(h, 5.0)

    assert peak.score() > recent.score()


def test_heavy_rain_is_capped():
    capped = BroodBuffer()
    huge = BroodBuffer()
    idx = const.LAG_PEAK_START_H + 1
    capped.set_hour(idx, const.HEAVY_RAIN_CAP_MM)
    huge.set_hour(idx, const.HEAVY_RAIN_CAP_MM * 10)
    assert capped.score() == huge.score()


def test_score_is_clamped_0_1():
    buf = BroodBuffer()
    for h in range(const.LAG_PEAK_START_H, const.LAG_PEAK_END_H):
        buf.set_hour(h, const.HEAVY_RAIN_CAP_MM)
    s = buf.score()
    assert 0.0 <= s <= 1.0


def test_advance_shifts_buffer():
    buf = BroodBuffer()
    buf.set_hour(0, 4.0)  # "now" bucket
    buf.advance_hours(1)  # shift: that rain is now 1 hour old
    assert buf.get_hour(0) == 0.0
    assert buf.get_hour(1) == 4.0


def test_serialize_roundtrip():
    buf = BroodBuffer()
    buf.set_hour(100, 3.5)
    data = buf.to_dict()
    restored = BroodBuffer.from_dict(data)
    assert restored.get_hour(100) == 3.5
