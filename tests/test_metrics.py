import datetime as dt

from traininglog.metrics import exercise_series, program_panel, status_of
from traininglog.render import payload

TODAY = dt.date(2026, 10, 19)


def _flat(panel):
    return {e["label"]: e for s in panel for e in s["ex"]}


def test_every_set_at_the_ceiling_means_add_load(program, log, cfg):
    rows = _flat(program_panel(program, log.sets, cfg, TODAY))
    assert rows["Bench Press"]["status"] == "add-load"
    assert rows["Bench Press"]["actual"] == "60×8, 60×8"


def test_under_the_range_is_flagged(program, log, cfg):
    rows = _flat(program_panel(program, log.sets, cfg, TODAY))
    assert rows["Calf Raises"]["status"] == "below-range"


def test_meeting_a_fixed_target_is_on_target_not_a_ceiling(program, log, cfg):
    rows = _flat(program_panel(program, log.sets, cfg, TODAY))
    assert rows["Wall sit"]["status"] == "on-target"


def test_unlogged_exercise_is_untracked(program, log, cfg):
    rows = _flat(program_panel(program, log.sets, cfg, TODAY))
    assert rows["Never Logged"]["status"] == "untracked"


def test_stale_wins_over_the_rep_rules(program, log, cfg):
    rows = _flat(program_panel(program, log.sets, cfg, dt.date(2026, 11, 30)))
    assert {r["status"] for r in rows.values() if r["sets"]} == {"stale"}


def test_panel_preserves_session_and_exercise_order(program, log, cfg):
    """Sheet order, not alphabetical: the fixture lists Upper before Lower A."""
    panel = program_panel(program, log.sets, cfg, TODAY)
    assert [s["name"] for s in panel] == ["Upper", "Lower A"]
    assert [e["label"] for e in panel[0]["ex"]] == ["Bench Press", "Pull Up", "Never Logged"]
    assert [e["label"] for e in panel[1]["ex"]] == ["Wall sit", "Calf Raises"]


def test_series_needs_two_sessions_and_tracks_the_limiting_set(program, log, cfg):
    series = exercise_series(program, log.sets, cfg)
    assert "Never Logged" not in series
    bench = series["Bench Press"]["series"]
    assert [p["minr"] for p in bench] == [7.0, 8.0]
    assert [p["load"] for p in bench] == [55.0, 60.0]


def test_timed_hold_is_not_treated_as_loaded(program, log, cfg):
    series = exercise_series(program, log.sets, cfg)
    assert series["Wall sit"]["loaded"] is False
    assert series["Wall sit"]["unit"] == "sec"


def test_status_rules_in_isolation(program, cfg):
    from traininglog.ingest import Set

    bench = next(p for p in program if p.exercise == "Bench Press")
    at_ceiling = [Set(TODAY, "Bench Press", 60, 8, None)] * 2
    mid = [Set(TODAY, "Bench Press", 60, 7, None)] * 2
    assert status_of(bench, at_ceiling, 0, cfg) == "add-load"
    assert status_of(bench, mid, 0, cfg) == "on-target"
    assert status_of(bench, mid, 99, cfg) == "stale"


def test_fixed_target_with_too_few_sets_is_short(program, cfg):
    from traininglog.ingest import Set

    wall = next(p for p in program if p.exercise == "Wall sit")
    two_of_three = [Set(TODAY, "Wall sit", None, 30, None)] * 2
    assert status_of(wall, two_of_three, 0, cfg) == "short-sets"
    assert status_of(wall, two_of_three * 2, 0, cfg) == "on-target"


def test_bodyweight_exercise_names_match_case_insensitively(program, log, cfg):
    import dataclasses

    shouty = dataclasses.replace(cfg, bodyweight_exercises=frozenset({"PULL UP"}))
    assert exercise_series(program, log.sets, shouty)["Pull Up"]["bw"] is True


def test_payload_has_the_keys_the_template_reads(log, program, cfg):
    data = payload(log, program, cfg, TODAY)
    assert set(data) == {
        "bodyweight",
        "weekly",
        "sessions",
        "sleep",
        "totalSets",
        "span",
        "exCount",
        "program",
        "exSessions",
    }
    assert data["bodyweight"] == 73.0
    assert data["span"] == ["2026-10-06", "2026-10-12"]


def test_render_writes_a_noindexed_page_and_robots(log, program, cfg, tmp_path):
    from traininglog.render import render

    out = render(payload(log, program, cfg, TODAY), tmp_path / "site" / "index.html")
    assert '<meta name="robots" content="noindex, nofollow">' in out.read_text()
    assert (out.parent / "robots.txt").read_text() == "User-agent: *\nDisallow: /\n"


def test_too_few_sets_outranks_the_ceiling(program, cfg):
    from traininglog.ingest import Set

    bench = next(p for p in program if p.exercise == "Bench Press")
    one_at_the_top = [Set(TODAY, "Bench Press", 60, 8, None)]
    assert status_of(bench, one_at_the_top, 0, cfg) == "short-sets"


def test_series_load_comes_from_the_limiting_set(program, cfg):
    """A session mixing loads plots the limiting set, not a pairing that never happened."""
    from traininglog.ingest import Set

    sets = [
        Set(dt.date(2026, 10, 6), "Bench Press", 60, 8, None),
        Set(dt.date(2026, 10, 12), "Bench Press", 100, 8, None),
        Set(dt.date(2026, 10, 12), "Bench Press", 60, 6, None),
    ]
    series = exercise_series(program, sets, cfg)["Bench Press"]["series"]
    assert [(p["minr"], p["load"]) for p in series] == [(8.0, 60.0), (6.0, 60.0)]


def test_payload_cannot_close_the_script_tag(log, program, cfg, tmp_path):
    import dataclasses

    from traininglog.render import render

    sneaky = [dataclasses.replace(p, exercise="</script> Curl") for p in program]
    page = render(payload(log, sneaky, cfg, TODAY), tmp_path / "index.html").read_text()
    assert "</script> Curl" not in page
    assert "<\\/script> Curl" in page
