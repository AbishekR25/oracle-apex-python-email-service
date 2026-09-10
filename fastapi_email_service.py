```python
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import subprocess, tempfile, os, jwt, datetime

app = FastAPI()

# --- Config ---
# Replace with your actual secret key using an environment variable.
# Example:
# SECRET_KEY = os.getenv("SECRET_KEY")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")

ACCESS_EXP_MINUTES = 30
REFRESH_EXP_DAYS = 1

# --- In-memory user store ---
# Do not put real usernames or passwords in GitHub.
# Replace the values below with environment variables or a database.
users_db = {
    "admin": {
        "password": os.getenv("ADMIN_PASSWORD"),
        "refresh_token": None
    },
    "user": {
        "password": os.getenv("USER_PASSWORD"),
        "refresh_token": None
    }
}

# --- JWT Utils ---
def create_token(username: str, expires_delta, token_type: str):
    payload = {
        "user": username,
        "type": token_type,
        "exp": datetime.datetime.utcnow() + expires_delta
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_token(token: str, expected_type: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        if payload.get("type") != expected_type:
            return None

        return payload["user"]

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# --- Auth Middleware ---
auth_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)
):
    return verify_token(credentials.credentials, "access")


# --- Routes ---

@app.get("/")
def home():
    return {"message": "Welcome to the File Scan API"}


@app.post("/login")
async def login(data: dict):
    username = data.get("username")
    password = data.get("password")

    if not username or not password or username not in users_db:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if users_db[username]["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access = create_token(
        username,
        datetime.timedelta(minutes=ACCESS_EXP_MINUTES),
        "access"
    )

    refresh = create_token(
        username,
        datetime.timedelta(days=REFRESH_EXP_DAYS),
        "refresh"
    )

    users_db[username]["refresh_token"] = refresh

    return {
        "access_token": access,
        "refresh_token": refresh
    }


@app.post("/refresh")
async def refresh(data: dict):
    username = data.get("username")
    token = data.get("refresh_token")

    if username not in users_db or users_db[username]["refresh_token"] != token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    verify_token(token, "refresh")

    new_access = create_token(
        username,
        datetime.timedelta(minutes=ACCESS_EXP_MINUTES),
        "access"
    )

    new_refresh = create_token(
        username,
        datetime.timedelta(days=REFRESH_EXP_DAYS),
        "refresh"
    )

    users_db[username]["refresh_token"] = new_refresh

    return {
        "access_token": new_access,
        "refresh_token": new_refresh
    }


@app.post("/scan")
async def scan_file(
    file: UploadFile = File(...),
    user: str = Depends(get_current_user)
):
    # Save file temporarily
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp.write(await file.read())
            file_path = temp.name

        # Run scan using Defender's CLI or your script.
        # Replace the placeholder path with the actual scan script
        # path in your server environment.
        result = subprocess.run(
            ["/path/to/check_file.sh", file_path],
            capture_output=True,
            text=True
        )

        return {
            "user": user,
            "result": result.stdout.strip(),
            "status": "success" if result.returncode == 0 else "infected"
        }

    finally:
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)

