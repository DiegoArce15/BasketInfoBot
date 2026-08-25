import logging
import re
from datetime import date, datetime
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup, Tag
from playwright.sync_api import sync_playwright

from src.application.sync_upcoming_matches_command import SyncMatchCommand
from src.domain.entities import Channel, MatchStatus, Score
from src.domain.match_fetcher import MatchFetcher

logger = logging.getLogger(__name__)


class AcbScraper(MatchFetcher):
    def __init__(self, target_url: str) -> None:
        self._target_url = target_url

    def fetch_upcoming_matches(self) -> list[SyncMatchCommand]:
        logger.info("Starting ACB matches scraping")

        html = self._fetch_page_html()
        matches = self.parse_html(html)

        logger.info("ACB matches scraping completed: %d matches found", len(matches))

        return matches

    def _fetch_page_html(self) -> str:
        logger.info("Opening ACB page: %s", self._target_url)

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)

            try:
                page = browser.new_page(
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    )
                )

                page.goto(
                    self._target_url, wait_until="domcontentloaded", timeout=30_000
                )

                logger.info("ACB page loaded. Waiting for matches")

                self._wait_for_matches(page)

                logger.info("Matches found. Waiting for schedules")

                self._wait_for_match_times(page)

                logger.info("Match schedules loaded")

                return page.content()

            finally:
                browser.close()

    def _wait_for_matches(self, page) -> None:
        page.wait_for_selector("div[class$='__roundMatch']", timeout=30_000)

    def _wait_for_match_times(self, page) -> None:
        page.wait_for_function(
            """
            () => Array.from(
                document.querySelectorAll(
                    "p[class*='__roundMatch__time'] span"
                )
            ).some(
                element => /^\\d{2}:\\d{2}/.test(
                    element.textContent.trim()
                )
            )
            """,
            timeout=30_000,
        )

    def parse_html(self, html_content: str) -> list[SyncMatchCommand]:
        logger.info("Parsing ACB page")

        soup = BeautifulSoup(html_content, "html.parser")
        matches: list[SyncMatchCommand] = []

        day_blocks = soup.select("div[class*='Round-module'][class*='__days'] > div")

        for day_block in day_blocks:
            match_date = self._extract_match_date(day_block)

            if match_date is None:
                continue

            matches.extend(
                self._parse_day_matches(
                    day_block=day_block,
                    match_date=match_date,
                )
            )

        logger.info("ACB page parsing completed: %d matches parsed", len(matches))

        return matches

    def _extract_match_date(self, day_block: Tag) -> date | None:
        date_header = day_block.select_one("h3[class*='DayTitle-module']")

        if not date_header:
            return None

        return self._parse_date(date_header.text.strip())

    def _parse_day_matches(
        self,
        day_block: Tag,
        match_date: date,
    ) -> list[SyncMatchCommand]:
        match_cards = day_block.select(":scope > div[class*='RoundMatch-module']")

        matches: list[SyncMatchCommand] = []

        for card in match_cards:
            match = self._parse_match_card(
                card=card,
                match_date=match_date,
            )

            if match is not None:
                matches.append(match)

        return matches

    def _parse_match_card(
        self,
        card: Tag,
        match_date: date,
    ) -> SyncMatchCommand | None:
        home_team = self._extract_team(card, "home")
        away_team = self._extract_team(card, "away")

        if home_team is None or away_team is None:
            return None

        time_str = self._extract_match_time(card)
        start_time = self._parse_time(match_date=match_date, time_str=time_str)

        score = self._extract_match_score(
            home_team_div=self._get_team_div(card, "home"),
            away_team_div=self._get_team_div(card, "away"),
        )

        return SyncMatchCommand(
            home_team_name=home_team,
            away_team_name=away_team,
            start_time=start_time,
            league="ACB",
            status=(
                MatchStatus.FINISHED if score is not None else MatchStatus.SCHEDULED
            ),
            channels=self._extract_channels(card),
            score=score,
        )

    def _extract_team(
        self,
        card: Tag,
        side: str,
    ) -> str | None:
        team_div = self._get_team_div(card, side)

        if team_div is None:
            return None

        team_name = team_div.select_one("span[class*='__teamName--fullName']")

        if team_name is None:
            return None

        return team_name.text.strip()

    def _get_team_div(
        self,
        card: Tag,
        side: str,
    ) -> Tag | None:
        return card.select_one(f"div[class*='__roundMatch__{side}Team']")

    def _extract_match_time(self, card: Tag) -> str:
        time_el = card.select_one("p[class*='__roundMatch__time'] span")

        if time_el is None:
            return "--:--"

        return time_el.text.strip().replace(" h", "")

    def _extract_channels(self, card: Tag) -> list[Channel]:
        tv_imgs = card.select("div[class*='__roundMatch__tv'] img[class*='__tvLogo']")

        channels: list[Channel] = []

        for img in tv_imgs:
            alt = img.get("alt")

            if isinstance(alt, str) and alt.strip():
                channels.append(Channel(name=alt.strip()))

        return channels

    def _extract_match_score(
        self,
        home_team_div: Tag | None,
        away_team_div: Tag | None,
    ) -> Score | None:
        if home_team_div is None or away_team_div is None:
            return None

        home_score = self._extract_single_score(home_team_div)
        away_score = self._extract_single_score(away_team_div)

        if home_score is None or away_score is None:
            return None

        return Score(
            home=home_score,
            away=away_score,
        )

    def _extract_single_score(
        self,
        team_div: Tag,
    ) -> int | None:
        score_el = team_div.select_one("p[class*='__teamScore']")

        if score_el is None:
            return None

        score = score_el.text.strip()

        return int(score) if score.isdigit() else None

    def _parse_date(self, date_str: str) -> date | None:
        months = {
            "enero": 1,
            "febrero": 2,
            "marzo": 3,
            "abril": 4,
            "mayo": 5,
            "junio": 6,
            "julio": 7,
            "agosto": 8,
            "septiembre": 9,
            "octubre": 10,
            "noviembre": 11,
            "diciembre": 12,
        }

        match = re.search(
            r"(\d+)\s+de\s+([a-z]+)\s+de\s+(\d{4})",
            date_str.lower(),
        )

        if not match:
            return None

        day = int(match.group(1))
        month = months.get(match.group(2))

        if month is None:
            return None

        year = int(match.group(3))

        return date(year, month, day)

    def _parse_time(
        self,
        match_date: date,
        time_str: str,
    ) -> datetime | None:
        if not re.fullmatch(r"\d{2}:\d{2}", time_str):
            return None

        hour, minute = map(int, time_str.split(":"))

        return datetime(
            match_date.year,
            match_date.month,
            match_date.day,
            hour,
            minute,
            tzinfo=ZoneInfo("Europe/Madrid"),
        )
