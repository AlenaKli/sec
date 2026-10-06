from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
import re


class UserCreate(BaseModel):
    username: str = Field(..., min_length=4, max_length=20)
    email: EmailStr
    password: str
    confirm_password: str
    age: int = Field(..., ge=18, le=100)

    @field_validator("username")
    def username_alphanumeric(cls, v):
        if not re.match(r"^[a-zA-Z0-9]+$", v):
            raise ValueError("Username must contain only letters and digits")
        return v

    @field_validator("password")
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*]", v):
            raise ValueError("Password must contain at least one special character: !@#$%^&*")
        return v

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self
