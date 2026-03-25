"""
BugMind AI — Pydantic Models
Request/Response schemas for the API.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# --- Auth Models ---

class SignupRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=100)
    password: str = Field(..., min_length=6, max_length=100)


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    token: str
    user: dict
    message: str


# --- Code Execution Models ---

class RunCodeRequest(BaseModel):
    code: str = Field(..., min_length=1)
    language: str = Field(default="python")


class RunCodeResponse(BaseModel):
    success: bool
    output: str
    error: Optional[str] = None
    error_type: Optional[str] = None
    execution_time: float = 0.0
    ai_analysis: Optional[dict] = None


# --- AI Analysis Models ---

class AIAnalysisRequest(BaseModel):
    code: str
    error_message: str
    error_type: Optional[str] = None


class AIAnalysisResponse(BaseModel):
    explanation: str
    suggested_fix: str
    fixed_code: str
    learning_tip: str
    error_category: str


# --- Dashboard Models ---

class UserStats(BaseModel):
    total_runs: int = 0
    total_errors: int = 0
    total_fixes: int = 0
    type_errors: int = 0
    syntax_errors: int = 0
    name_errors: int = 0
    value_errors: int = 0
    index_errors: int = 0
    other_errors: int = 0
    streak_days: int = 0


class CodeHistoryItem(BaseModel):
    id: int
    code: str
    language: str
    output: Optional[str]
    error_type: Optional[str]
    error_message: Optional[str]
    ai_explanation: Optional[str]
    is_error: bool
    created_at: str


class AutoFixRequest(BaseModel):
    code: str
    error_type: str
    error_message: str
