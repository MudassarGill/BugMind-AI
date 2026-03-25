"""
BugMind AI — FastAPI Main Application
Backend entry point with all API routes.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from auth import (
    hash_password, verify_password, create_access_token, get_current_user
)
from models import (
    SignupRequest, LoginRequest, AuthResponse,
    RunCodeRequest, RunCodeResponse,
    AIAnalysisRequest, AIAnalysisResponse,
    AutoFixRequest
)
from database import (
    init_db, create_user, get_user_by_email,
    save_code_run, increment_fixes,
    get_user_stats, get_code_history, get_recent_errors
)
from code_runner import run_python_code, validate_code_safety
from ai_engine import analyze_error, quick_analyze

# --- Lifespan ---
@asynccontextmanager
async def lifespan(application):
    init_db()
    print("🧠 BugMind AI Backend started!")
    yield

# --- App Setup ---
app = FastAPI(
    title="BugMind AI",
    description="AI-powered coding assistant with real-time error detection",
    version="1.0.0",
    lifespan=lifespan
)

# CORS — allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Serve Frontend ---
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

# Mount static files (CSS, JS, assets)
if os.path.exists(FRONTEND_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIR, "assets")), name="assets")


@app.get("/")
def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "signup.html"))


@app.get("/index.html")
def serve_editor():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/login.html")
def serve_login():
    return FileResponse(os.path.join(FRONTEND_DIR, "login.html"))


@app.get("/signup.html")
def serve_signup():
    return FileResponse(os.path.join(FRONTEND_DIR, "signup.html"))


@app.get("/dashboard.html")
def serve_dashboard():
    return FileResponse(os.path.join(FRONTEND_DIR, "dashboard.html"))


@app.get("/styles.css")
def serve_css():
    return FileResponse(os.path.join(FRONTEND_DIR, "styles.css"))


@app.get("/app.js")
def serve_js():
    return FileResponse(os.path.join(FRONTEND_DIR, "app.js"))


# ===================================
# AUTH ENDPOINTS
# ===================================

@app.post("/api/auth/signup", response_model=AuthResponse)
def signup(req: SignupRequest):
    """Register a new user."""
    # Check if user exists
    existing = get_user_by_email(req.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists"
        )

    # Hash password and create user
    password_hash = hash_password(req.password)
    user = create_user(req.name, req.email, password_hash)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create account"
        )

    # Generate JWT token
    token = create_access_token({
        "user_id": user["id"],
        "email": user["email"],
        "name": user["name"]
    })

    return AuthResponse(
        token=token,
        user={"id": user["id"], "name": user["name"], "email": user["email"]},
        message="Account created successfully!"
    )


@app.post("/api/auth/login", response_model=AuthResponse)
def login(req: LoginRequest):
    """Login and get JWT token."""
    user = get_user_by_email(req.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No account found with this email"
        )

    if not verify_password(req.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )

    token = create_access_token({
        "user_id": user["id"],
        "email": user["email"],
        "name": user["name"]
    })

    return AuthResponse(
        token=token,
        user={"id": user["id"], "name": user["name"], "email": user["email"]},
        message="Login successful!"
    )


@app.get("/api/auth/me")
def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user info from token."""
    return current_user


# ===================================
# CODE EXECUTION ENDPOINTS
# ===================================

@app.post("/api/code/run", response_model=RunCodeResponse)
def run_code(req: RunCodeRequest, current_user: dict = Depends(get_current_user)):
    """Execute Python code safely and return output."""
    user_id = current_user["user_id"]

    # Safety check
    is_safe, reason = validate_code_safety(req.code)
    if not is_safe:
        return RunCodeResponse(
            success=False,
            output="",
            error=f"⚠️ Security restriction: {reason}",
            error_type="SecurityError",
            execution_time=0.0
        )

    # Execute code
    result = run_python_code(req.code)

    # AI analysis if there's an error
    ai_analysis = None
    if not result["success"] and result.get("error_type"):
        ai_result = analyze_error(
            req.code,
            result.get("error", ""),
            result.get("error_type")
        )
        ai_analysis = ai_result

    # Save to database
    save_code_run(
        user_id=user_id,
        code=req.code,
        language=req.language,
        output=result.get("output", ""),
        error_type=result.get("error_type"),
        error_message=result.get("error"),
        ai_explanation=ai_analysis.get("explanation") if ai_analysis else None,
        ai_fix=ai_analysis.get("suggested_fix") if ai_analysis else None,
        is_error=not result["success"]
    )

    return RunCodeResponse(
        success=result["success"],
        output=result.get("output", ""),
        error=result.get("error"),
        error_type=result.get("error_type"),
        execution_time=result.get("execution_time", 0.0),
        ai_analysis=ai_analysis
    )


@app.post("/api/code/analyze")
def analyze_code(req: AIAnalysisRequest, current_user: dict = Depends(get_current_user)):
    """Get AI analysis for an error without running code."""
    result = analyze_error(req.code, req.error_message, req.error_type)
    return result


@app.post("/api/code/quick-check")
def quick_check(req: RunCodeRequest, current_user: dict = Depends(get_current_user)):
    """Quick static analysis for real-time error detection."""
    issues = quick_analyze(req.code)
    return {"issues": issues}


@app.post("/api/code/autofix")
def auto_fix(req: AutoFixRequest, current_user: dict = Depends(get_current_user)):
    """Get auto-fix suggestion for code."""
    result = analyze_error(req.code, req.error_message, req.error_type)
    user_id = current_user["user_id"]
    increment_fixes(user_id)
    return {
        "fixed_code": result["fixed_code"],
        "explanation": result["explanation"],
        "suggestion": result["suggested_fix"]
    }


# ===================================
# DASHBOARD / STATS ENDPOINTS
# ===================================

@app.get("/api/dashboard/stats")
def dashboard_stats(current_user: dict = Depends(get_current_user)):
    """Get user learning statistics."""
    user_id = current_user["user_id"]
    stats = get_user_stats(user_id)
    if not stats:
        return {
            "total_runs": 0, "total_errors": 0, "total_fixes": 0,
            "type_errors": 0, "syntax_errors": 0, "name_errors": 0,
            "value_errors": 0, "index_errors": 0, "other_errors": 0,
            "streak_days": 0
        }
    return stats


@app.get("/api/dashboard/history")
def code_history(limit: int = 20, current_user: dict = Depends(get_current_user)):
    """Get code execution history."""
    user_id = current_user["user_id"]
    history = get_code_history(user_id, limit)
    return {"history": history}


@app.get("/api/dashboard/errors")
def recent_errors(limit: int = 10, current_user: dict = Depends(get_current_user)):
    """Get recent errors."""
    user_id = current_user["user_id"]
    errors = get_recent_errors(user_id, limit)
    return {"errors": errors}


# ===================================
# HEALTH CHECK
# ===================================

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "app": "BugMind AI", "version": "1.0.0"}


# --- Run Server ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
