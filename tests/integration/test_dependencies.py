# tests/auth/test_dependencies.py

import pytest
from unittest.mock import MagicMock, patch, ANY
from fastapi import HTTPException, status
from app.auth.dependencies import get_current_user, get_current_active_user
from app.schemas.user import UserResponse
from app.models.user import User
from app.models.calculation import Calculation  # Make sure Calculation is imported
from uuid import uuid4
from datetime import datetime

#
# --- FIX: Convert global variables to fixtures ---
#
# By defining these as fixtures, we ensure they are created
# AFTER all models are loaded, solving the InvalidRequestError.
#
@pytest.fixture
def sample_user():
    """Provides a sample active user object."""
    return User(
        id=uuid4(),
        username="testuser",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        is_active=True,
        is_verified=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

@pytest.fixture
def inactive_user():
    """Provides a sample inactive user object."""
    return User(
        id=uuid4(),
        username="inactiveuser",
        email="inactive@example.com",
        first_name="Inactive",
        last_name="User",
        is_active=False,
        is_verified=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
# --- End of FIX ---


# Fixture for mocking the database session
@pytest.fixture
def mock_db():
    return MagicMock()

# Fixture for mocking token verification
@pytest.fixture
def mock_verify_token():
    with patch.object(User, 'verify_token') as mock:
        yield mock

#
# --- FIX: Update tests to accept fixtures ---
#
# Notice `sample_user` and `inactive_user` are now passed
# as arguments to the test functions that need them.
#
def test_get_current_user_valid_token_existing_user(
    mock_db, mock_verify_token, sample_user
):
    mock_verify_token.return_value = sample_user.id
    mock_db.query.return_value.filter.return_value.first.return_value = sample_user

    user_response = get_current_user(db=mock_db, token="validtoken")

    assert isinstance(user_response, UserResponse)
    assert user_response.id == sample_user.id
    assert user_response.username == sample_user.username
    assert user_response.email == sample_user.email
    assert user_response.first_name == sample_user.first_name
    assert user_response.last_name == sample_user.last_name
    assert user_response.is_active == sample_user.is_active
    assert user_response.is_verified == sample_user.is_verified
    assert user_response.created_at == sample_user.created_at
    assert user_response.updated_at == sample_user.updated_at

    mock_verify_token.assert_called_once_with("validtoken")
    mock_db.query.assert_called_once_with(User)
    mock_db.query.return_value.filter.assert_called_once_with(ANY)
    mock_db.query.return_value.filter.return_value.first.assert_called_once()

def test_get_current_user_invalid_token(mock_db, mock_verify_token):
    mock_verify_token.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(db=mock_db, token="invalidtoken")

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Could not validate credentials"

    mock_verify_token.assert_called_once_with("invalidtoken")
    mock_db.query.assert_not_called()

def test_get_current_user_valid_token_nonexistent_user(
    mock_db, mock_verify_token, sample_user
):
    mock_verify_token.return_value = sample_user.id
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(db=mock_db, token="validtoken")

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Could not validate credentials"

    mock_verify_token.assert_called_once_with("validtoken")
    mock_db.query.assert_called_once_with(User)
    mock_db.query.return_value.filter.assert_called_once_with(ANY)
    mock_db.query.return_value.filter.return_value.first.assert_called_once()

def test_get_current_active_user_active(
    mock_db, mock_verify_token, sample_user
):
    mock_verify_token.return_value = sample_user.id
    mock_db.query.return_value.filter.return_value.first.return_value = sample_user

    current_user = get_current_user(db=mock_db, token="validtoken")
    active_user = get_current_active_user(current_user=current_user)

    assert isinstance(active_user, UserResponse)
    assert active_user.is_active is True

def test_get_current_active_user_inactive(
    mock_db, mock_verify_token, inactive_user
):
    mock_verify_token.return_value = inactive_user.id
    mock_db.query.return_value.filter.return_value.first.return_value = inactive_user

    current_user = get_current_user(db=mock_db, token="validtoken")

    with pytest.raises(HTTPException) as exc_info:
        get_current_active_user(current_user=current_user)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Inactive user"