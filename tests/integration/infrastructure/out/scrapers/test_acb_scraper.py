from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from src.application.sync_upcoming_matches_command import SyncMatchCommand
from src.domain.match import Channel, MatchStatus, Score
from src.infrastructure.out.scrapers.acb_scraper import AcbScraper


@pytest.fixture
def scraper() -> AcbScraper:
    return AcbScraper(target_url="https://www.acb.com/resultados-clasificacion/index")


def test_parse_html_returns_scheduled_match_with_channels(
    scraper: AcbScraper,
) -> None:
    # Given
    html = """
        <div class="Round-module-scss-module__oJf34a__round__days">
            <div>
                <h3 class="DayTitle-module-scss-module__WF90Ba__dayTitle">
                    26 de septiembre de 2026
                </h3>

                <div class="RoundMatch-module-scss-module__q1UjKa__roundMatch">
                    <p class="RoundMatch-module-scss-module__q1UjKa__roundMatch__time">
                        <span>18:00 h</span>
                    </p>

                    <div class="RoundMatch-module-scss-module__q1UjKa__roundMatch__homeTeam">
                        <span class="RoundMatch-module-scss-module__q1UjKa__roundMatch__teamName--fullName">
                            Surne Bilbao
                        </span>
                    </div>

                    <div class="RoundMatch-module-scss-module__q1UjKa__roundMatch__awayTeam">
                        <span class="RoundMatch-module-scss-module__q1UjKa__roundMatch__teamName--fullName">
                            Kids&amp;Us Manresa
                        </span>
                    </div>

                    <div class="RoundMatch-module-scss-module__q1UjKa__roundMatch__tv">
                        <img
                            alt="DAZN"
                            class="RoundMatch-module-scss-module__q1UjKa__roundMatch__tvLogo"
                        />
                        <img
                            alt="Movistar Plus +"
                            class="RoundMatch-module-scss-module__q1UjKa__roundMatch__tvLogo"
                        />
                    </div>
                </div>
            </div>
        </div>
    """

    # When
    matches = scraper.parse_html(html)

    # Then
    assert matches == [
        SyncMatchCommand(
            home_team_name="Surne Bilbao",
            away_team_name="Kids&Us Manresa",
            start_time=datetime(2026, 9, 26, 18, 0, tzinfo=ZoneInfo("Europe/Madrid")),
            league="ACB",
            status=MatchStatus.SCHEDULED,
            channels=[
                Channel(name="DAZN"),
                Channel(name="Movistar Plus +"),
            ],
            score=None,
        )
    ]


def test_parse_html_returns_finished_match_with_score(
    scraper: AcbScraper,
) -> None:
    # Given
    html = """
        <div class="Round-module-scss-module__oJf34a__round__days">
            <div>
                <h3 class="DayTitle-module-scss-module__WF90Ba__dayTitle">
                    27 de septiembre de 2026
                </h3>

                <div class="RoundMatch-module-scss-module__q1UjKa__roundMatch">
                    <p class="RoundMatch-module-scss-module__q1UjKa__roundMatch__time">
                        <span>12:00 h</span>
                    </p>

                    <div class="RoundMatch-module-scss-module__q1UjKa__roundMatch__homeTeam">
                        <span class="RoundMatch-module-scss-module__q1UjKa__roundMatch__teamName--fullName">
                            Río Breogán
                        </span>
                        <p class="RoundMatch-module-scss-module__q1UjKa__roundMatch__teamScore">
                            86
                        </p>
                    </div>

                    <div class="RoundMatch-module-scss-module__q1UjKa__roundMatch__awayTeam">
                        <span class="RoundMatch-module-scss-module__q1UjKa__roundMatch__teamName--fullName">
                            Asisa Joventut
                        </span>
                        <p class="RoundMatch-module-scss-module__q1UjKa__roundMatch__teamScore">
                            79
                        </p>
                    </div>
                </div>
            </div>
        </div>
    """

    # When
    matches = scraper.parse_html(html)

    # Then
    assert matches == [
        SyncMatchCommand(
            home_team_name="Río Breogán",
            away_team_name="Asisa Joventut",
            start_time=datetime(2026, 9, 27, 12, 0, tzinfo=ZoneInfo("Europe/Madrid")),
            league="ACB",
            status=MatchStatus.FINISHED,
            channels=[],
            score=Score(home=86, away=79),
        )
    ]


def test_parse_html_returns_empty_list_when_there_are_no_matches(
    scraper: AcbScraper,
) -> None:
    # Given
    html = """
        <div class="Round-module__days"></div>
    """

    # When
    matches = scraper.parse_html(html)

    # Then
    assert matches == []


def test_parse_html_ignores_match_without_date(
    scraper: AcbScraper,
) -> None:
    # Given
    html = """
        <div class="Round-module__days">
            <div>
                <div class="RoundMatch-module__roundMatch">
                    <p class="RoundMatch-module__roundMatch__time">
                        <span>18:00 h</span>
                    </p>

                    <div class="RoundMatch-module__roundMatch__homeTeam">
                        <span class="teamName--fullName">Surne Bilbao</span>
                    </div>

                    <div class="RoundMatch-module__roundMatch__awayTeam">
                        <span class="teamName--fullName">Kids&amp;Us Manresa</span>
                    </div>
                </div>
            </div>
        </div>
    """

    # When
    matches = scraper.parse_html(html)

    # Then
    assert matches == []


def test_parse_html_ignores_match_without_home_team(
    scraper: AcbScraper,
) -> None:
    # Given
    html = """
        <div class="Round-module__days">
            <div>
                <h3 class="DayTitle-module">26 de septiembre de 2026</h3>

                <div class="RoundMatch-module__roundMatch">
                    <p class="RoundMatch-module__roundMatch__time">
                        <span>18:00 h</span>
                    </p>

                    <div class="RoundMatch-module__roundMatch__awayTeam">
                        <span class="teamName--fullName">Kids&amp;Us Manresa</span>
                    </div>
                </div>
            </div>
        </div>
    """

    # When
    matches = scraper.parse_html(html)

    # Then
    assert matches == []


def test_parse_html_ignores_match_without_away_team(
    scraper: AcbScraper,
) -> None:
    # Given
    html = """
        <div class="Round-module__days">
            <div>
                <h3 class="DayTitle-module">26 de septiembre de 2026</h3>

                <div class="RoundMatch-module__roundMatch">
                    <p class="RoundMatch-module__roundMatch__time">
                        <span>18:00 h</span>
                    </p>

                    <div class="RoundMatch-module__roundMatch__homeTeam">
                        <span class="teamName--fullName">Surne Bilbao</span>
                    </div>
                </div>
            </div>
        </div>
    """

    # When
    matches = scraper.parse_html(html)

    # Then
    assert matches == []


def test_parse_html_returns_match_without_channels_when_channels_are_not_available(
    scraper: AcbScraper,
) -> None:
    # Given
    html = """
        <div class="Round-module-scss-module__oJf34a__round__days">
            <div>
                <h3 class="DayTitle-module-scss-module__WF90Ba__dayTitle">
                    26 de septiembre de 2026
                </h3>

                <div class="RoundMatch-module-scss-module__q1UjKa__roundMatch">
                    <p class="RoundMatch-module-scss-module__q1UjKa__roundMatch__time">
                        <span>18:00 h</span>
                    </p>

                    <div class="RoundMatch-module-scss-module__q1UjKa__roundMatch__homeTeam">
                        <span class="RoundMatch-module-scss-module__q1UjKa__roundMatch__teamName--fullName">
                            Surne Bilbao
                        </span>
                    </div>

                    <div class="RoundMatch-module-scss-module__q1UjKa__roundMatch__awayTeam">
                        <span class="RoundMatch-module-scss-module__q1UjKa__roundMatch__teamName--fullName">
                            Kids&amp;Us Manresa
                        </span>
                    </div>
                </div>
            </div>
        </div>
    """

    # When
    matches = scraper.parse_html(html)

    # Then
    assert matches == [
        SyncMatchCommand(
            home_team_name="Surne Bilbao",
            away_team_name="Kids&Us Manresa",
            start_time=datetime(2026, 9, 26, 18, 0, tzinfo=ZoneInfo("Europe/Madrid")),
            league="ACB",
            status=MatchStatus.SCHEDULED,
            channels=[],
            score=None,
        )
    ]
