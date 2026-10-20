import datetime as dt

from traininglog.ingest import key, load_log, load_program, parse_date


def test_dates_are_day_first():
    assert parse_date("06/10/2026 07:10:00") == dt.date(2026, 10, 6)
    assert parse_date("19/10/2026") == dt.date(2026, 10, 19)
    assert parse_date("not a date") is None


def test_key_collapses_case_and_spacing():
    assert key("Calf Raises") == key("Calf raises") == key("  calf   raises ")
    assert key("Wall Sit") == key("Wall sit")


def test_only_completed_sets_are_kept(log):
    assert all(s.exercise != "Skipped Thing" for s in log.sets)
    assert all(s.exercise != "Meditation" for s in log.sets)


def test_blank_and_zero_load_both_mean_bodyweight(log):
    pullups = [s for s in log.sets if key(s.exercise) == "pull up" and s.date.day == 6]
    assert {s.load for s in pullups} == {0.0, None}
    assert all(s.added_load == 0.0 for s in pullups)


def test_daily_and_session_streams_split_out(log):
    assert log.sleep == [(dt.date(2026, 10, 6), 7.0), (dt.date(2026, 10, 12), 8.0)]
    assert log.bodyweight == [(dt.date(2026, 10, 6), 73.0)]
    assert log.sessions == [(dt.date(2026, 10, 6), 55), (dt.date(2026, 10, 12), 62)]


def test_program_returns_one_dated_snapshot(program):
    assert {p.valid_from for p in program} == {dt.date(2026, 10, 3)}
    assert [p.exercise for p in program if p.session == "Upper"] == [
        "Bench Press",
        "Pull Up",
        "Never Logged",
    ]


def test_program_snapshot_respects_the_as_of_date(source):
    earlier = load_program(source.fetch("program"), on=dt.date(2026, 6, 1))
    assert {p.valid_from for p in earlier} == {dt.date(2026, 1, 1)}
    assert all(p.exercise != "Never Logged" for p in earlier)


def test_fixed_target_formats_without_a_range(program):
    wall = next(p for p in program if p.exercise == "Wall sit")
    assert wall.target == "3×30 sec"


def test_a1_notation_survives_awkward_tab_names():
    from traininglog.sources.sheets import SheetsSource

    assert SheetsSource._a1("program") == "'program'"
    assert SheetsSource._a1("Body weight") == "'Body weight'"
    assert SheetsSource._a1("Bob's log") == "'Bob''s log'"


def test_sheets_errors_say_what_to_do():
    from traininglog.sources.sheets import _explain

    assert "TRAININGLOG_SHEET_ID" in _explain(404, "tracking")
    assert "client_email" in _explain(403, "tracking")
    assert "'tracking'" in _explain(400, "tracking")
    assert "500" in _explain(500, "tracking")


def test_sheets_source_requires_an_id(cfg):
    import dataclasses

    import pytest

    from traininglog.sources import build_source

    with pytest.raises(RuntimeError, match="TRAININGLOG_SHEET_ID"):
        build_source(dataclasses.replace(cfg, source="sheets", sheet_id=""))


def test_non_exercise_rows_match_whatever_the_case():
    rows = [
        {"date": "06/10/2026 07:00:00", "exercise": "workout start", "checkbox": "TRUE"},
        {"date": "06/10/2026 08:00:00", "exercise": "WORKOUT END", "checkbox": "TRUE"},
        {"date": "06/10/2026", "exercise": " body weight ", "checkbox": "TRUE", "value1": "73"},
        {"date": "06/10/2026", "exercise": "MEDITATION", "checkbox": "TRUE", "value1": "10"},
    ]
    out = load_log(rows)
    assert out.sessions == [(dt.date(2026, 10, 6), 60)]
    assert out.bodyweight == [(dt.date(2026, 10, 6), 73.0)]
    assert out.sets == []
