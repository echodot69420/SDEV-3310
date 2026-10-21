from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class BookFields(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=120)
    isbn: str = Field(min_length=1, max_length=32)
    published_year: int
    member_id: int = Field(gt=0)

    @field_validator("title", "author", "isbn", mode="before")
    @classmethod
    def trim_required_text(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value

    @field_validator("published_year")
    @classmethod
    def validate_published_year(cls, value: int) -> int:
        if value < 1450 or value > date.today().year:
            raise ValueError(f"must be between 1450 and {date.today().year}")
        return value


class BookCreate(BookFields):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    author: Optional[str] = Field(default=None, min_length=1, max_length=120)
    isbn: Optional[str] = Field(default=None, min_length=1, max_length=32)
    published_year: Optional[int] = None
    member_id: Optional[int] = Field(default=None, gt=0)

    @field_validator("title", "author", "isbn", mode="before")
    @classmethod
    def trim_update_text(cls, value: object) -> object:
        if value is None or not isinstance(value, str):
            return value
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value

    @field_validator("published_year")
    @classmethod
    def validate_update_year(cls, value: Optional[int]) -> Optional[int]:
        if value is not None and (value < 1450 or value > date.today().year):
            raise ValueError(f"must be between 1450 and {date.today().year}")
        return value

    @model_validator(mode="after")
    def require_update_field(self) -> "BookUpdate":
        if not self.model_fields_set:
            raise ValueError("at least one field is required")
        return self


class BookResponse(BookFields):
    id: int
    model_config = ConfigDict(from_attributes=True)
