from unittest.mock import Mock

import pytest


@pytest.fixture
def mock_user_repo() -> Mock:
    return Mock()


@pytest.fixture
def mock_team_repo() -> Mock:
    return Mock()

@pytest.fixture
def mock_match_repo() -> Mock:
    return Mock()

@pytest.fixture
def mock_id_generator() -> Mock:
    return Mock()
