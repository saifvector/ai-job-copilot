import uuid
import pytest
from core.exceptions import NotFoundException, ConflictException, BadRequestException
from schemas.user import UserCreate, UserRead
from schemas.profile import ProfileCreate, ProfileRead
from models.user import UserModel
from models.profile import ProfileModel


def test_user_schema_validation():
    """Verify User Pydantic schema validation rules."""
    user = UserCreate(name="Jane Doe", email="jane.doe@example.com")
    assert user.name == "Jane Doe"
    assert user.email == "jane.doe@example.com"

    # Verify invalid email fails
    with pytest.raises(Exception):
        UserCreate(name="Invalid", email="not-an-email")


def test_profile_schema_validation():
    """Verify Profile Pydantic schema validation rules."""
    uid = uuid.uuid4()
    profile = ProfileCreate(
        user_id=uid,
        preferred_roles=["Lead Backend Engineer"],
        preferred_locations=["Remote"],
        years_of_experience=5,
    )
    assert profile.user_id == uid
    assert profile.years_of_experience == 5
    assert len(profile.preferred_roles) == 1

    # Verify negative experience fails
    with pytest.raises(Exception):
        ProfileCreate(user_id=uid, years_of_experience=-1)


def test_exception_status_mapping():
    """Verify domain exceptions status codes and codes."""
    nf = NotFoundException("User", "test-id")
    assert nf.status_code == 404
    assert nf.code == "RESOURCE_NOT_FOUND"

    cf = ConflictException("Already exists")
    assert cf.status_code == 409
    assert cf.code == "CONFLICT"

    br = BadRequestException("Malformed data")
    assert br.status_code == 400
    assert br.code == "BAD_REQUEST"


def test_model_instantiation():
    """Verify SQLAlchemy models instantiate correctly."""
    user = UserModel(name="Test User", email="test@example.com")
    assert user.name == "Test User"
    assert user.email == "test@example.com"
