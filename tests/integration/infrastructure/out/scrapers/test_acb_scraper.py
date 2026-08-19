import uuid
from datetime import UTC, datetime

import pytest

from src.domain.entities import Channel, Match, MatchId, MatchStatus, Score, TeamId
from src.infrastructure.out.scrapers.acb_scraper import AcbScraper


@pytest.fixture
def sample_team_mapping() -> dict[str, TeamId]:
    """Mapeo simulado de nombres de equipos de la ACB a TeamIds de dominio."""
    return {
        "Surne Bilbao": TeamId(str(uuid.uuid4())),
        "Kids&Us Manresa": TeamId(str(uuid.uuid4())),
        "MoraBanc Andorra": TeamId(str(uuid.uuid4())),
        "Monbus Obradoiro": TeamId(str(uuid.uuid4())),
        "Barça": TeamId(str(uuid.uuid4())),
        "Leyma Coruña": TeamId(str(uuid.uuid4())),
        "Río Breogán": TeamId(str(uuid.uuid4())),
        "Asisa Joventut": TeamId(str(uuid.uuid4())),
    }


@pytest.fixture
def acb_html_fixture() -> str:
    """Fixture con fragmentos de HTML reales de la ACB (uno sin finalizar y otro finalizado con score)."""
    return """
    <div id="calendar-round-6015" class="Round-module-scss-module__oJf34a__round">
        <div class="RoundTitle-module-scss-module__-M5MOG__roundTitle">Jornada 1</div>
        <div class="Round-module-scss-module__oJf34a__round__days">
            <div>
                <h3 class="heading heading--subhead DayTitle-module-scss-module__WF90Ba__dayTitle">26 de septiembre de 2026</h3>
                <!-- Partido pendiente / sin jugar -->
                <div class="RoundMatch-module-scss-module__q1UjKa__roundMatch">
                    <p class="text--body-1 RoundMatch-module-scss-module__q1UjKa__roundMatch__time"><span>18:00 h</span></p>
                    <div class="RoundMatch-module-scss-module__q1UjKa__roundMatch__teams">
                        <div class="RoundMatch-module-scss-module__q1UjKa__roundMatch__homeTeam">
                            <a class="RoundMatch-module-scss-module__q1UjKa__roundMatch__teamLink">
                                <p class="heading RoundMatch-module-scss-module__q1UjKa__roundMatch__teamName">
                                    <span class="RoundMatch-module-scss-module__q1UjKa__roundMatch__teamName--fullName">Surne Bilbao</span>
                                </p>
                            </a>
                        </div>
                        <p class="RoundMatch-module-scss-module__q1UjKa__roundMatch__separator">-</p>
                        <div class="RoundMatch-module-scss-module__q1UjKa__roundMatch__awayTeam">
                            <a class="RoundMatch-module-scss-module__q1UjKa__roundMatch__teamLink">
                                <p class="heading RoundMatch-module-scss-module__q1UjKa__roundMatch__teamName">
                                    <span class="RoundMatch-module-scss-module__q1UjKa__roundMatch__teamName--fullName">Kids&amp;Us Manresa</span>
                                </p>
                            </a>
                        </div>
                    </div>
                    <div class="RoundMatch-module-scss-module__q1UjKa__roundMatch__tv">
                        <a class="RoundMatch-module-scss-module__q1UjKa__roundMatch__tvLink">
                            <img alt="DAZN" class="RoundMatch-module-scss-module__q1UjKa__roundMatch__tvLogo" />
                        </a>
                        <a class="RoundMatch-module-scss-module__q1UjKa__roundMatch__tvLink">
                            <img alt="Movistar Plus +" class="RoundMatch-module-scss-module__q1UjKa__roundMatch__tvLogo" />
                        </a>
                    </div>
                </div>
            </div>
            <div>
                <h3 class="heading heading--subhead DayTitle-module-scss-module__WF90Ba__dayTitle">27 de septiembre de 2026</h3>
                <!-- Partido finalizado con marcador -->
                <div class="RoundMatch-module-scss-module__q1UjKa__roundMatch">
                    <p class="text--body-1 RoundMatch-module-scss-module__q1UjKa__roundMatch__time"><span>12:00 h</span></p>
                    <div class="RoundMatch-module-scss-module__q1UjKa__roundMatch__teams">
                        <div class="RoundMatch-module-scss-module__q1UjKa__roundMatch__homeTeam">
                            <a class="RoundMatch-module-scss-module__q1UjKa__roundMatch__teamLink">
                                <p class="heading RoundMatch-module-scss-module__q1UjKa__roundMatch__teamName">
                                    <span class="RoundMatch-module-scss-module__q1UjKa__roundMatch__teamName--fullName">Río Breogán</span>
                                </p>
                            </a>
                            <p class="RoundMatch-module-scss-module__q1UjKa__roundMatch__teamScore RoundMatch-module-scss-module__q1UjKa__roundMatch__teamScore--winner">86</p>
                        </div>
                        <p class="RoundMatch-module-scss-module__q1UjKa__roundMatch__separator">-</p>
                        <div class="RoundMatch-module-scss-module__q1UjKa__roundMatch__awayTeam">
                            <a class="RoundMatch-module-scss-module__q1UjKa__roundMatch__teamLink">
                                <p class="heading RoundMatch-module-scss-module__q1UjKa__roundMatch__teamName">
                                    <span class="RoundMatch-module-scss-module__q1UjKa__roundMatch__teamName--fullName">Asisa Joventut</span>
                                </p>
                            </a>
                            <p class="RoundMatch-module-scss-module__q1UjKa__roundMatch__teamScore">79</p>
                        </div>
                    </div>
                    <div class="RoundMatch-module-scss-module__q1UjKa__roundMatch__tv">
                        <a class="RoundMatch-module-scss-module__q1UjKa__roundMatch__tvLink">
                            <img alt="DAZN" class="RoundMatch-module-scss-module__q1UjKa__roundMatch__tvLogo" />
                        </a>
                        <a class="RoundMatch-module-scss-module__q1UjKa__roundMatch__tvLink">
                            <img alt="TV3/3Cat" class="RoundMatch-module-scss-module__q1UjKa__roundMatch__tvLogo" />
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """


def test_parse_html_extracts_matches_correctly(
    acb_html_fixture: str, sample_team_mapping: dict[str, TeamId]
):
    # Given
    scraper = AcbScraper(
        target_url="https://www.acb.com/resultados-clasificacion/index",
        team_mapping=sample_team_mapping,
    )

    expected_matches = [
        Match(
            id=MatchId("surne-bilbao-vs-kids-us-manresa-2026-09-26"),
            home_team_id=sample_team_mapping["Surne Bilbao"],
            away_team_id=sample_team_mapping["Kids&Us Manresa"],
            start_time=datetime(2026, 9, 26, 18, 0, tzinfo=UTC),
            league="ACB",
            status=MatchStatus.SCHEDULED,
            channels=[Channel(name="DAZN"), Channel(name="Movistar Plus +")],
            score=None,
        ),
        Match(
            id=MatchId("rio-breogan-vs-asisa-joventut-2026-09-27"),
            home_team_id=sample_team_mapping["Río Breogán"],
            away_team_id=sample_team_mapping["Asisa Joventut"],
            start_time=datetime(2026, 9, 27, 12, 0, tzinfo=UTC),
            league="ACB",
            status=MatchStatus.SCHEDULED,
            channels=[Channel(name="DAZN"), Channel(name="TV3/3Cat")],
            score=Score(home=86, away=79),
        ),
    ]

    # When
    matches = scraper.parse_html(acb_html_fixture)

    # Then
    assert matches == expected_matches


def test_parse_html_ignores_unmapped_teams(acb_html_fixture: str):
    # Given: Mapeo donde solo existe uno de los dos equipos del partido
    incomplete_mapping = {
        "Surne Bilbao": TeamId(str(uuid.uuid4()))
    }
    scraper = AcbScraper(
        target_url="https://www.acb.com", team_mapping=incomplete_mapping
    )

    # When
    matches = scraper.parse_html(acb_html_fixture)

    # Then
    assert len(matches) == 0