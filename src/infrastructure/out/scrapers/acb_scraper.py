import re
from datetime import UTC, datetime

import httpx
from bs4 import BeautifulSoup, Tag

from src.application.sync_upcoming_matches_command import SyncMatchCommand
from src.domain.entities import Channel, MatchStatus, Score
from src.domain.match_fetcher import MatchFetcher


class AcbScraper(MatchFetcher):
    def __init__(self, target_url: str):
        self._target_url = target_url

    def fetch_upcoming_matches(self) -> list[SyncMatchCommand]:
        response = httpx.get(
            self._target_url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
            },
            timeout=10.0,
        )
        response.raise_for_status()

        return self.parse_html(response.text)

    def parse_html(self, html_content: str) -> list[SyncMatchCommand]:
        soup = BeautifulSoup(html_content, "html.parser")
        matches: list[SyncMatchCommand] = []

        day_blocks = soup.select("div[class*='Round-module'][class*='__days'] > div")

        for day_block in day_blocks:
            date_header = day_block.select_one("h3[class*='DayTitle-module']")

            if not date_header:
                continue

            date_str = date_header.text.strip()

            match_cards = day_block.select(
                "div[class*='Round-module'][class*='__days'] > div > div[class*='RoundMatch-module']"
            )

            for card in match_cards:
                time_el = card.select_one("p[class*='__roundMatch__time'] span")

                time_str = (
                    time_el.text.strip().replace(" h", "") if time_el else "00:00"
                )

                home_team_div = card.select_one("div[class*='__roundMatch__homeTeam']")
                away_team_div = card.select_one("div[class*='__roundMatch__awayTeam']")

                if not home_team_div or not away_team_div:
                    continue

                home_el = home_team_div.select_one(
                    "span[class*='__teamName--fullName']"
                )
                away_el = away_team_div.select_one(
                    "span[class*='__teamName--fullName']"
                )

                if not home_el or not away_el:
                    continue

                home_team_name = home_el.text.strip()
                away_team_name = away_el.text.strip()

                tv_imgs = card.select(
                    "div[class*='__roundMatch__tv'] img[class*='__tvLogo']"
                )

                channels = []

                for img in tv_imgs:
                    alt = img.get("alt")

                    if not isinstance(alt, str):
                        continue

                    channels.append(Channel(name=alt.strip()))

                match_datetime = self._parse_datetime(date_str, time_str)

                score = self._extract_match_score(home_team_div, away_team_div)

                status = (
                    MatchStatus.FINISHED if score is not None else MatchStatus.SCHEDULED
                )

                matches.append(
                    SyncMatchCommand(
                        home_team_name=home_team_name,
                        away_team_name=away_team_name,
                        start_time=match_datetime,
                        channels=channels,
                        league="ACB",
                        status=status,
                        score=score,
                    )
                )

        return matches

    def _extract_match_score(self, home_div: Tag, away_div: Tag) -> Score | None:
        """Extrae las puntuaciones de ambos equipos."""

        home_score = self._extract_single_score(home_div)
        away_score = self._extract_single_score(away_div)

        if home_score is not None and away_score is not None:
            return Score(home=home_score, away=away_score)

        return None

    def _extract_single_score(self, team_div: Tag) -> int | None:
        """Busca el marcador de un equipo."""

        score_el = team_div.select_one("p[class*='__teamScore']")

        if score_el and score_el.text.strip().isdigit():
            return int(score_el.text.strip())

        return None

    def _parse_datetime(self, date_str: str, time_str: str) -> datetime:
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

        match = re.search(r"(\d+)\s+de\s+([a-z]+)\s+de\s+(\d{4})", date_str.lower())

        if not match:
            return datetime.now(UTC)

        day = int(match.group(1))
        month = months.get(match.group(2), 1)
        year = int(match.group(3))

        hour, minute = map(int, time_str.split(":"))

        return datetime(year, month, day, hour, minute, tzinfo=UTC)
