from datetime import UTC, datetime

import pytest

from src.application.sync_upcoming_matches_command import SyncMatchCommand
from src.domain.entities import Channel, MatchStatus, Score
from src.infrastructure.out.scrapers.acb_scraper import AcbScraper


@pytest.fixture
def acb_html_fixture() -> str:
    """Fixture con fragmentos de HTML reales de la ACB."""
    return """
    <div id="calendar-round-6015" class="Round-module-scss-module__oJf34a__round">
        <div class="RoundTitle-module-scss-module__-M5MOG__roundTitle">Jornada 1</div>
        <div class="Round-module-scss-module__oJf34a__round__days">
            <div>
                <h3 class="heading heading--subhead DayTitle-module-scss-module__WF90Ba__dayTitle">26 de septiembre de 2026</h3>

                <div class="RoundMatch-module-scss-module__q1UjKa__roundMatch">
                    <p class="text--body-1 RoundMatch-module-scss-module__q1UjKa__roundMatch__time">
                        <span>18:00 h</span>
                    </p>

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

                <div class="RoundMatch-module-scss-module__q1UjKa__roundMatch">
                    <p class="text--body-1 RoundMatch-module-scss-module__q1UjKa__roundMatch__time">
                        <span>12:00 h</span>
                    </p>

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


def test_parse_html_extracts_matches_correctly(acb_html_fixture: str) -> None:
    # Given
    scraper = AcbScraper(
        target_url="https://www.acb.com/resultados-clasificacion/index"
    )

    # When
    matches = scraper.parse_html(acb_html_fixture)

    # Then
    assert matches == [
        SyncMatchCommand(
            home_team_name="Surne Bilbao",
            away_team_name="Kids&Us Manresa",
            start_time=datetime(2026, 9, 26, 18, 0, tzinfo=UTC),
            league="ACB",
            status=MatchStatus.SCHEDULED,
            channels=[Channel(name="DAZN"), Channel(name="Movistar Plus +")],
            score=None,
        ),
        SyncMatchCommand(
            home_team_name="Río Breogán",
            away_team_name="Asisa Joventut",
            start_time=datetime(2026, 9, 27, 12, 0, tzinfo=UTC),
            league="ACB",
            status=MatchStatus.FINISHED,
            channels=[Channel(name="DAZN"), Channel(name="TV3/3Cat")],
            score=Score(home=86, away=79),
        ),
    ]
