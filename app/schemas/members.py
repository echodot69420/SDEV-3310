from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


class MemberFields(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    membership_id: str = Field(min_length=1, max_length=64)
    phone: str = Field(pattern=r"^\+?[1-9]\d{7,14}$")

    @field_validator("name", "membership_id", "phone", mode="before")
    @classmethod
    def trim_member_text(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value


class MemberCreate(MemberFields):
    pass


class MemberUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    email: Optional[EmailStr] = None
    membership_id: Optional[str] = Field(default=None, min_length=1, max_length=64)
    phone: Optional[str] = Field(default=None, pattern=r"^\+?[1-9]\d{7,14}$")

    @field_validator("name", "membership_id", "phone", mode="before")
    @classmethod
    def trim_member_update_text(cls, value: object) -> object:
        if value is None or not isinstance(value, str):
            return value
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value

    @model_validator(mode="after")
    def require_update_field(self) -> "MemberUpdate":
        if not self.model_fields_set:
            raise ValueError("at least one field is required")
        return self


class MemberResponse(MemberFields):
    id: int
    model_config = ConfigDict(from_attributes=True)
