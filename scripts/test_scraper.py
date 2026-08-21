from src.infrastructure.out.scrapers.acb_scraper import AcbScraper

scraper = AcbScraper("https://www.acb.com/es/liga/calendario")

matches = scraper.fetch_upcoming_matches()

print(f"Partidos encontrados: {len(matches)}")

for match in matches[:5]:
    print(
        match.home_team_name,
        "vs",
        match.away_team_name,
        "|",
        match.match_date,
        "|",
        match.start_time,
    )
