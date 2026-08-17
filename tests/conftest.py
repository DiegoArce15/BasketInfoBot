import pytest

from tests.unit.infrastructure.out.persistence.in_memory_match_repository import (
    InMemoryMatchRepository,
)
from tests.unit.infrastructure.out.persistence.in_memory_team_repository import (
    InMemoryTeamRepository,
)
from tests.unit.infrastructure.out.persistence.in_memory_user_repository import (
    InMemoryUserRepository,
)


@pytest.fixture
def user_repo():
    return InMemoryUserRepository()


@pytest.fixture
def team_repo():
    return InMemoryTeamRepository()


@pytest.fixture
def match_repo():
    return InMemoryMatchRepository()