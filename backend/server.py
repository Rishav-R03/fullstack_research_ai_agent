# ... (existing imports)
import os
from datetime import datetime, timedelta # Import datetime and timedelta
import uuid # For UUID types
from typing import Union, Any

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from passlib.context import CryptContext # For password hashing
from jose import JWTError, jwt # For JWT handling

from database import get_db, create_db_tables # Import create_db_tables
from models.user_model import User

# --- Explicit Import of the User CLASS ---
# IMPORTANT: Adjust 'user_model' below if your file is actually named something else.
from models.user_model import User as UserModelClass # <-- Alias to be super clear
from models.user_model import User # <-- Alias to be super clear

# --- FastAPI App Initialization ---
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256" # HMAC SHA256 is common for JWT
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # How long the access token is valid for

if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable not set. Please generate one and add it to your .env file.")

# Password hashing context (GLOBAL)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2PasswordBearer for getting token from Authorization header (used for protected routes) (GLOBAL)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- JWT & Password Utility Functions (GLOBAL) ---
def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    """Creates a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15) # Default expiration
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hashes a plain password."""
    return pwd_context.hash(password)

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Research Agent API",
    description="API for a LangChain-powered research assistant using Google Gemini.",
    version="1.0.0"
)

# --- Pydantic Models (GLOBAL) ---
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    user_id: uuid.UUID
    username: str
    email: EmailStr
    created_at: datetime
    # last_login_at: Union[datetime, None] = None # Include if you want to expose this

    class Config:
        from_attributes = True # Pydantic v2: enables reading from ORM models

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None # Stores subject of token (e.g., username)

# --- Startup Event to Create Tables ---
@app.on_event("startup")
async def startup_event():
    """
    Called when the FastAPI application starts up.
    Attempts to create all defined database tables.
    """
    print("FastAPI application startup event: Initializing database tables...")
    create_db_tables() # Call the function to create tables
    print("Database initialization complete during startup.")

# --- Helper to get current user (for protected routes) ---
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Authenticates a user based on the provided JWT token.
    Raises HTTPException if authentication fails.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

# --- API Endpoints ---

# User registration endpoint
@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user in the database.
    Hashes the password before storing.
    """
    # Check if username or email already exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed_password = get_password_hash(user_data.password) # Use the global helper function
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user) # Refresh to get the generated user_id and created_at
    return new_user # FastAPI will automatically convert the ORM object to UserResponse Pydantic model

# Login endpoint (to get an access token)
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticates a user and returns a JWT access token.
    """
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash): # Use the global helper function
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token( # Use the global helper function
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    # Update last login time
    user.last_login_at = datetime.utcnow()
    db.add(user)
    db.commit()
    return {"access_token": access_token, "token_type": "bearer"}

# Example of a protected endpoint (requires authentication)
@app.get("/users/me/", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Retrieves details of the currently authenticated user."""
    return current_user

# --- LangChain Agent Integration (Placeholder - assumed to be part of your server.py) ---
# You'll need to define ResearchResponse and parser if not already, and potentially ResearchRequest.
# Also ensure llm, tools, prompt, agent, agent_executor are initialized.
# from main import get_research_agent_executor_and_parser
# agent_executor, parser, ResearchResponse = get_research_agent_executor_and_parser()

# class ResearchRequest(BaseModel):
#    query: str

# @app.post("/research", response_model=ResearchResponse)
# async def perform_research(request: ResearchRequest, current_user: User = Depends(get_current_user)):
#     # You can now use current_user.user_id to link research to the logged-in user
#     print(f"User {current_user.username} (ID: {current_user.user_id}) submitted research query: {request.query}")
#     try:
#         raw_response = await agent_executor.ainvoke({"query": request.query})
#         llm_output_text = raw_response.get('output', '')
#         parsed_response = parser.parse(llm_output_text)
#         # Link this research to the user and potentially a session here (future DB design step)
#         return parsed_response
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Research failed: {e}")


if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
    print("FastAPI server stopped.")
