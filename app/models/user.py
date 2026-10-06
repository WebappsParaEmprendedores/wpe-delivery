# models/user.py

from datetime import datetime, timezone
from enum import Enum
from typing import Annotated, Any

from bson import ObjectId
from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)
from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def validate_object_id(value: Any) -> ObjectId:
    if isinstance(value, ObjectId):
        return value

    if isinstance(value, str) and ObjectId.is_valid(value):
        return ObjectId(value)

    raise ValueError("Invalid ObjectId")


PyObjectId = Annotated[
    ObjectId,
    BeforeValidator(validate_object_id),
]


class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    DISPATCHER = "dispatcher"
    DRIVER = "driver"
    VIEWER = "viewer"


class AuthProvider(str, Enum):
    PASSWORD = "password"
    GOOGLE = "google"


class User(BaseModel):
    """
    MongoDB document stored in the `users` collection.

    Users are created by an administrator. There is no public
    registration flow.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        from_attributes=True,
    )

    id: PyObjectId | None = Field(
        default=None,
        alias="_id",
    )

    email: EmailStr
    full_name: str = Field(
        min_length=1,
        max_length=120,
    )

    roles: list[UserRole] = Field(
        default_factory=lambda: [UserRole.VIEWER],
        min_length=1,
    )

    is_active: bool = True

    # The user must replace the administrator-assigned password
    # after their first successful login.
    must_change_password: bool = True

    # Set to True by an administrator when the user has confirmed
    # their email or identity, if your business requires this.
    is_email_verified: bool = False

    # Never expose this field in API responses.
    password_hash: str | None = Field(
        default=None,
        exclude=True,
    )

    # Kept for future Google login support.
    auth_providers: list[AuthProvider] = Field(
        default_factory=lambda: [AuthProvider.PASSWORD],
    )

    # Google's stable user identifier.
    # It remains empty for password-only accounts.
    google_subject: str | None = Field(
        default=None,
        exclude=True,
    )

    last_login_at: datetime | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()

    @field_validator("full_name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return " ".join(value.strip().split())

    @field_validator("roles")
    @classmethod
    def remove_duplicate_roles(
        cls,
        value: list[UserRole],
    ) -> list[UserRole]:
        return list(dict.fromkeys(value))

    @field_validator("auth_providers")
    @classmethod
    def remove_duplicate_providers(
        cls,
        value: list[AuthProvider],
    ) -> list[AuthProvider]:
        return list(dict.fromkeys(value))

    def set_initial_password(self, plain_password: str) -> None:
        """
        Used by the administrator when creating a new user.

        The user is forced to replace this password after login.
        """

        self._set_password(plain_password)
        self.must_change_password = True
        self.updated_at = utc_now()

    def change_password(self, new_password: str) -> None:
        """
        Used by the user after their first login or when changing
        their password later.
        """

        self._set_password(new_password)
        self.must_change_password = False
        self.updated_at = utc_now()

    def _set_password(self, plain_password: str) -> None:
        if len(plain_password) < 12:
            raise ValueError(
                "Password must contain at least 12 characters"
            )

        self.password_hash = password_hash.hash(plain_password)

        if AuthProvider.PASSWORD not in self.auth_providers:
            self.auth_providers.append(AuthProvider.PASSWORD)

    def verify_password(self, plain_password: str) -> bool:
        """
        Used during login.

        This does not change the password or registration state.
        """

        if not self.password_hash:
            return False

        return password_hash.verify(
            plain_password,
            self.password_hash,
        )

    def to_mongo(self) -> dict:
        """
        Convert the model into a MongoDB document.
        """

        document = self.model_dump(
            by_alias=True,
            exclude_none=True,
        )

        if self.id is None:
            document.pop("_id", None)

        return document

    def public_data(self) -> dict:
        """
        Safe user data for API responses.
        """

        return self.model_dump(
            by_alias=True,
            exclude={
                "password_hash",
                "google_subject",
            },
            exclude_none=True,
        )
