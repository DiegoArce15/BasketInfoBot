from datetime import UTC, datetime

from src.application.process_scraped_matches_use_case import (
    ProcessScrapedMatchesUseCase,
)
from src.domain.entities import Match, MatchId, MatchStatus, Team, TeamId


def test_process_scraped_matches_preserves_all_match_and_team_data(
    team_repo, match_repo
):
    # Given: Datos detallados provenientes del scraper
    home_team = Team(
        id=TeamId("real-madrid"),
        name="Real Madrid",
        country="Spain",
        logo_url="https://example.com/logos/rm.png",
    )
    away_team = Team(
        id=TeamId("barcelona"),
        name="FC Barcelona",
        country="Spain",
        logo_url="https://example.com/logos/fcb.png",
    )

    match_time = datetime(2026, 10, 25, 21, 0, tzinfo=UTC)
    scraped_match = Match(
        id=MatchId("2026-10-25-rm-barca"),
        home_team=home_team,
        away_team=away_team,
        start_time=match_time,
        channel="DAZN / Movistar LaLiga",
        league="EuroLeague",
        status=MatchStatus.SCHEDULED,
    )

    use_case = ProcessScrapedMatchesUseCase(team_repo, match_repo)

    # When: Ingerimos los datos
    use_case.execute([scraped_match])

    # Then 1: Verificamos que el equipo local se guardó íntegramente
    saved_home_team = team_repo.find_by_id(home_team.id)
    assert saved_home_team is not None
    assert saved_home_team.id == TeamId("real-madrid")
    assert saved_home_team.name == "Real Madrid"
    assert saved_home_team.country == "Spain"
    assert saved_home_team.logo_url == "https://example.com/logos/rm.png"

    # Then 2: Verificamos que el equipo visitante se guardó íntegramente
    saved_away_team = team_repo.find_by_id(away_team.id)
    assert saved_away_team is not None
    assert saved_away_team.id == TeamId("barcelona")
    assert saved_away_team.name == "FC Barcelona"

    # Then 3: Verificamos toda la información del partido
    saved_match = match_repo.find_by_id(scraped_match.id)
    assert saved_match is not None
    assert saved_match.id == MatchId("2026-10-25-rm-barca")
    assert saved_match.home_team.id == home_team.id
    assert saved_match.away_team.id == away_team.id
    assert saved_match.start_time == match_time
    assert saved_match.channel == "DAZN / Movistar LaLiga"
    assert saved_match.league == "EuroLeague"
    assert saved_match.status == MatchStatus.SCHEDULED


def test_process_scraped_matches_handles_missing_optional_data(
    team_repo, match_repo
):
    # Given: Datos con campos opcionales no informados (None/Vacíos)
    home_team = Team(id=TeamId("unicaja"), name="Unicaja Málaga")
    away_team = Team(id=TeamId("baskonia"), name="Baskonia")

    match_time = datetime(2026, 11, 15, 18, 0, tzinfo=UTC)
    scraped_match = Match(
        id=MatchId("2026-11-15-unicaja-baskonia"),
        home_team=home_team,
        away_team=away_team,
        start_time=match_time,
        channel=None,  # El scraper no encontró canal de TV asignado
        league=None,   # Tampoco se extrajo la competición
        status=MatchStatus.SCHEDULED,
    )

    use_case = ProcessScrapedMatchesUseCase(team_repo, match_repo)

    # When: Se procesa el partido incompleto
    use_case.execute([scraped_match])

    # Then: Se verifica que se guarda sin errores y preserva los valores nulos
    saved_match = match_repo.find_by_id(scraped_match.id)
    assert saved_match is not None
    assert saved_match.channel is None
    assert saved_match.league is None

    # Verificamos que los datos requeridos mínimos sí persisten correctamente
    assert saved_match.home_team.name == "Unicaja Málaga"
    assert saved_match.away_team.name == "Baskonia"
    assert saved_match.start_time == match_time

def test_process_scraped_matches_updates_existing_match_information(
    team_repo, match_repo
):
    # Given: Un partido ya existente en el repositorio sin canal asignado
    team_home = Team(id=TeamId("valencia-basket"), name="Valencia Basket")
    team_away = Team(id=TeamId("gran-canaria"), name="Dreamland Gran Canaria")
    match_id = MatchId("2026-12-01-valencia-granca")
    match_time = datetime(2026, 12, 1, 18, 30, tzinfo=UTC)

    initial_match = Match(
        id=match_id,
        home_team=team_home,
        away_team=team_away,
        start_time=match_time,
        channel=None,  # Aún no hay canal
        league="ACB",
        status=MatchStatus.SCHEDULED,
    )
    
    # Guardamos el estado previo en los repositorios
    team_repo.save(team_home)
    team_repo.save(team_away)
    match_repo.save(initial_match)

    # Scraper obtiene la información actualizada con canal confirmado
    updated_scraped_match = Match(
        id=match_id,
        home_team=team_home,
        away_team=team_away,
        start_time=match_time,
        channel="Movistar Plus+",  # Canal recién asignado
        league="ACB",
        status=MatchStatus.SCHEDULED,
    )

    use_case = ProcessScrapedMatchesUseCase(team_repo, match_repo)

    # When: Reingerimos el partido con los nuevos datos
    use_case.execute([updated_scraped_match])

    # Then: Verificamos que el registro en la base de datos se actualizó correctamente
    saved_match = match_repo.find_by_id(match_id)
    assert saved_match is not None
    assert saved_match.channel == "Movistar Plus+"
    assert saved_match.id == match_id