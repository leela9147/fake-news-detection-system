from pydantic import BaseModel, EmailStr, Field, field_validator

class RegisterIn(BaseModel):
    full_name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str

    @field_validator('full_name')
    @classmethod
    def name_ok(cls, v):
        if not v.strip():
            raise ValueError('Please enter your full name.')
        return v.strip()

    @field_validator('confirm_password')
    @classmethod
    def pw_match(cls, v, info):
        if info.data.get('password') != v:
            raise ValueError('Passwords do not match.')
        return v

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    created_at: str
    analyses: int = 0
    class Config:
        from_attributes = True

class TokenOut(BaseModel):
    access_token: str
    token_type: str = 'bearer'

class ForgotIn(BaseModel):
    email: EmailStr

class ResetIn(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)
    confirm_password: str

    @field_validator('confirm_password')
    @classmethod
    def pw_match(cls, v, info):
        if info.data.get('new_password') != v:
            raise ValueError('Passwords do not match.')
        return v

class ProfileUpdateIn(BaseModel):
    full_name: str = Field(min_length=1, max_length=120)

class PredictIn(BaseModel):
    headline: str
    article_content: str

    @field_validator('headline')
    @classmethod
    def h_ok(cls, v):
        if not v or not v.strip():
            raise ValueError('Please enter the news headline.')
        return v.strip()

    @field_validator('article_content')
    @classmethod
    def a_ok(cls, v):
        if not v or not v.strip():
            raise ValueError('Please enter the news article content.')
        return v.strip()
