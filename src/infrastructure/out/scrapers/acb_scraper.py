import re
from datetime import date, datetime
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup, Tag
from playwright.sync_api import sync_playwright

from src.application.sync_upcoming_matches_command import SyncMatchCommand
from src.domain.entities import Channel, MatchStatus, Score
from src.domain.match_fetcher import MatchFetcher


class AcbScraper(MatchFetcher):
    def __init__(self, target_url: str):
        self._target_url = target_url

    def fetch_upcoming_matches(self) -> list[SyncMatchCommand]:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)

            page = browser.new_page(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            )

            try:
                print("Abriendo ACB...")

                page.goto(
                    self._target_url,
                    wait_until="domcontentloaded",
                    timeout=30_000,
                )

                print("Página cargada. Esperando partidos...")

                page.wait_for_selector(
                    "div[class$='__roundMatch']",
                    timeout=30_000,
                )

                print("Partidos encontrados. Esperando horarios...")

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

                print("Horarios cargados.")

                print("HTML obtenido. Comenzando parseo...")
                html = page.content()

            finally:
                browser.close()

        matches = self.parse_html(html)

        print(f"Parseo terminado: {len(matches)} partidos.")

        return matches

    def parse_html(self, html_content: str) -> list[SyncMatchCommand]:
        soup = BeautifulSoup(html_content, "html.parser")
        matches: list[SyncMatchCommand] = []

        day_blocks = soup.select("div[class*='Round-module'][class*='__days'] > div")

        for day_block in day_blocks:
            date_header = day_block.select_one("h3[class*='DayTitle-module']")

            if not date_header:
                continue

            date_str = date_header.text.strip()
            match_date = self._parse_date(date_str)

            if match_date is None:
                continue

            match_cards = day_block.select(":scope > div[class*='RoundMatch-module']")

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
        time_el = card.select_one("p[class*='__roundMatch__time'] span")

        time_str = time_el.text.strip().replace(" h", "") if time_el else "--:--"

        home_team_div = card.select_one("div[class*='__roundMatch__homeTeam']")
        away_team_div = card.select_one("div[class*='__roundMatch__awayTeam']")

        if not home_team_div or not away_team_div:
            return None

        home_el = home_team_div.select_one("span[class*='__teamName--fullName']")
        away_el = away_team_div.select_one("span[class*='__teamName--fullName']")

        if not home_el or not away_el:
            return None

        home_name = home_el.text.strip()
        away_name = away_el.text.strip()

        start_time = self._parse_time(
            match_date=match_date,
            time_str=time_str,
        )

        channels = self._extract_channels(card)

        score = self._extract_match_score(
            home_team_div,
            away_team_div,
        )

        status = MatchStatus.FINISHED if score is not None else MatchStatus.SCHEDULED

        return SyncMatchCommand(
            home_team_name=home_name,
            away_team_name=away_name,
            start_time=start_time,
            league="ACB",
            status=status,
            channels=channels,
            score=score,
        )

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
        home_div: Tag,
        away_div: Tag,
    ) -> Score | None:
        home_score = self._extract_single_score(home_div)
        away_score = self._extract_single_score(away_div)

        if home_score is not None and away_score is not None:
            return Score(
                home=home_score,
                away=away_score,
            )

        return None

    def _extract_single_score(
        self,
        team_div: Tag,
    ) -> int | None:
        score_el = team_div.select_one("p[class*='__teamScore']")

        if score_el and score_el.text.strip().isdigit():
            return int(score_el.text.strip())

        return None

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

        return date(
            year,
            month,
            day,
        )

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
