import pytest
from datetime import date

from apps.study_plan.models import StudyChapter, StudyModule
from apps.study_plan.services.plan_service import PlanService


@pytest.fixture
def module(db):
    return StudyModule.objects.create(
        title="Módulo Views Fase4",
        slug="modulo-views-fase4",
        order=98,
        master_file="fase4v.md",
        category="specific",
        study_phase="1",
        estimated_hours=1.0,
    )


@pytest.fixture
def chapter(db, module):
    return StudyChapter.objects.create(
        module=module,
        title="Capítulo Views Fase4",
        slug="capitulo-views-fase4",
        order=1,
        estimated_minutes=30,
    )


# ── ProgressView ──────────────────────────────────────────────────────

@pytest.mark.django_db
def test_progress_view_redirects_anonymous(client):
    resp = client.get("/plano/progresso/")
    assert resp.status_code == 302
    assert "/conta/login/" in resp["Location"]


@pytest.mark.django_db
def test_progress_view_renders_for_logged_in_user(client_logged):
    resp = client_logged.get("/plano/progresso/")
    assert resp.status_code == 200


@pytest.mark.django_db
def test_progress_view_context_has_required_keys(client_logged):
    resp = client_logged.get("/plano/progresso/")
    assert "stats" in resp.context
    assert "calendar_weeks" in resp.context
    assert "calendar_year" in resp.context
    assert "calendar_month" in resp.context
    assert "calendar_month_name" in resp.context
    assert "prev_year" in resp.context
    assert "prev_month" in resp.context
    assert "next_year" in resp.context
    assert "next_month" in resp.context


@pytest.mark.django_db
def test_progress_view_without_activity_shows_zero_streak(client_logged):
    resp = client_logged.get("/plano/progresso/")
    assert resp.context["stats"].current_streak == 0
    assert resp.context["stats"].total_study_days == 0


@pytest.mark.django_db
def test_progress_view_month_navigation_get_params(client_logged):
    resp = client_logged.get("/plano/progresso/?year=2026&month=1")
    assert resp.status_code == 200
    assert resp.context["calendar_year"] == 2026
    assert resp.context["calendar_month"] == 1
    assert resp.context["calendar_month_name"] == "Janeiro"


@pytest.mark.django_db
def test_progress_view_invalid_month_falls_back_to_today(client_logged):
    today = date.today()
    resp = client_logged.get("/plano/progresso/?year=2026&month=99")
    assert resp.status_code == 200
    assert resp.context["calendar_month"] == today.month


@pytest.mark.django_db
def test_progress_view_prev_next_month_navigation(client_logged):
    resp = client_logged.get("/plano/progresso/?year=2026&month=6")
    assert resp.context["prev_month"] == 5
    assert resp.context["prev_year"] == 2026
    assert resp.context["next_month"] == 7
    assert resp.context["next_year"] == 2026


@pytest.mark.django_db
def test_progress_view_year_boundary_prev(client_logged):
    resp = client_logged.get("/plano/progresso/?year=2026&month=1")
    assert resp.context["prev_month"] == 12
    assert resp.context["prev_year"] == 2025


@pytest.mark.django_db
def test_progress_view_year_boundary_next(client_logged):
    resp = client_logged.get("/plano/progresso/?year=2026&month=12")
    assert resp.context["next_month"] == 1
    assert resp.context["next_year"] == 2027


@pytest.mark.django_db
def test_progress_view_calendar_weeks_structure(client_logged):
    resp = client_logged.get("/plano/progresso/?year=2026&month=6")
    weeks = resp.context["calendar_weeks"]
    assert isinstance(weeks, list)
    for week in weeks:
        assert len(week) == 7
        for day, active in week:
            assert isinstance(day, int)
            assert isinstance(active, bool)


@pytest.mark.django_db
def test_progress_view_reflects_completed_chapter(client_logged, user, chapter):
    PlanService.mark_chapter_completed(user, chapter)
    resp = client_logged.get("/plano/progresso/")
    assert resp.context["stats"].completed_chapters >= 1
    assert resp.context["stats"].current_streak >= 1
    assert resp.context["stats"].total_study_days >= 1
