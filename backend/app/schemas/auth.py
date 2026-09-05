from pydantic import BaseModel


class LoginRequest(BaseModel):

    officer_id: str

    password: str


class LoginResponse(BaseModel):

    access_token: str

    token_type: str

    officer_id: str

    role: str