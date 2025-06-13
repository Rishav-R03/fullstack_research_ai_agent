import os
from datetime import datetime, timedelta
import uuid
from typing import Union, Any, List # Make sure Any is imported

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from passlib.context import CryptContext
from jose import JWTError, jwt

# LangChain Imports for Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.callbacks import BaseCallbackHandler # For custom callbacks

# --- CORRECTED IMPORTS BELOW (ToolOutput removed from direct import) ---
from langchain_core.outputs import LLMResult, ChatGeneration # Still from outputs
from langchain_core.agents import AgentAction, AgentFinish # Still from agents
# NO LONGER ATTEMPTING TO IMPORT ToolOutput directly.
# We will use 'Any' for its type hint in the callback.
# --- END CORRECTED IMPORTS ---

# Import database functions and models
from database import (
    get_db, create_db_tables,
    User, ResearchSession, ResearchQuery, ResearchOutput, ToolExecution,
    create_new_research_session, create_research_query, update_research_query_metrics,
    create_research_output, create_tool_execution
)
# Assuming tools.py is in backend/tools.py
from tools import search_tool, wiki_tool, save_tool


# --- Configuration for JWT ---
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable not set. Please generate one and add it to your .env file.")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- JWT & Password Utility Functions ---
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
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Research Agent API",
    description="API for a LangChain-powered research assistant using Google Gemini.",
    version="1.0.0"
)

# --- Pydantic Models ---
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    user_id: uuid.UUID
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None

# Pydantic models for Research Agent interaction
class ResearchRequest(BaseModel):
    query: str
    session_id: Union[uuid.UUID, None] = None

class LoginRequest(BaseModel): # NEW: Pydantic Model for Login Request Body
    username: str
    password: str

class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: List[str]
    tools_used: List[str]

    output_id: Union[uuid.UUID, None] = None
    query_id: Union[uuid.UUID, None] = None
    created_at: Union[datetime, None] = None

    class Config:
        from_attributes = True

# --- Startup Event to Create Tables ---
@app.on_event("startup")
async def startup_event():
    print("FastAPI application startup event: Initializing database tables...")
    create_db_tables()
    print("Database initialization complete during startup.")

# --- Helper to get current user (for protected routes) ---
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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

# --- LangChain Agent Setup ---
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))

tools = [search_tool, wiki_tool]

class AgentResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: List[str]
    tools_used: List[str]

agent_parser = PydanticOutputParser(pydantic_object=AgentResearchResponse)

agent_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a research assistant that will help generate research papers.
            Answer the user query by utilizing the provided tools.
            After gathering information, synthesize a comprehensive summary.
            Present your final answer in the specified JSON format, without any additional text or markdown outside the JSON.
            \n{format_instructions}
            """,
        ),
        (
            "placeholder", "{chat_history}"
        ),
        (
            "human", "{query}"
        ),
        (
            "placeholder", "{agent_scratchpad}"
        ),
    ]
).partial(format_instructions=agent_parser.get_format_instructions())

agent_instance = create_tool_calling_agent(
    llm=llm,
    prompt=agent_prompt,
    tools=tools
)
agent_executor = AgentExecutor(agent=agent_instance, tools=tools, verbose=True)

# --- Custom LangChain Callback Handler for Database Logging (ToolOutput type changed to Any) ---
class DBToolLoggerCallbackHandler(BaseCallbackHandler):
    def __init__(self, db: Session, query_id: uuid.UUID):
        self.db = db
        self.query_id = query_id
        self.tool_outputs = {}

    def on_tool_start(self, agent_action: AgentAction, **kwargs: Any) -> None:
        print(f"\n--- Logging Tool Start: {agent_action.tool} ---")
        # Use getattr for safety if attributes are sometimes missing
        tool_input_str = str(getattr(agent_action, 'tool_input', ''))
        create_tool_execution(
            self.db,
            query_id=self.query_id,
            tool_name=agent_action.tool,
            tool_input=tool_input_str,
            tool_output=None,
            status="pending"
        )

    # --- MODIFIED: output type changed to Any ---
    def on_tool_end(self, output: Any, **kwargs: Any) -> None:
        """Called when a tool ends running."""
        print(f"--- Logging Tool End for {getattr(output, 'tool', 'UnknownTool')}: Success ---")
        
        # Safely access attributes of the 'output' object
        tool_name_from_output = getattr(output, 'tool', 'UnknownTool')
        tool_input_from_output = str(getattr(output, 'tool_input', ''))
        tool_log_output = str(getattr(output, 'log', '')) # The actual tool output string

        create_tool_execution(
            self.db,
            query_id=self.query_id,
            tool_name=tool_name_from_output,
            tool_input=tool_input_from_output,
            tool_output=tool_log_output,
            status="success"
        )
        self.tool_outputs[tool_name_from_output] = tool_log_output

    def on_tool_error(self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any) -> None:
        tool_name = kwargs.get("tool_name", "Unknown")
        tool_input = kwargs.get("tool_input", "Unknown")
        print(f"--- Logging Tool Error for {tool_name}: {error} ---")
        create_tool_execution(
            self.db,
            query_id=self.query_id,
            tool_name=tool_name,
            tool_input=str(tool_input),
            tool_output=None,
            status="failed",
            error_message=str(error)
        )
    
    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> Any:
        # Access token usage from the LLMResult
        self.input_tokens = 0
        self.output_tokens = 0
        self.total_tokens = 0
        self.estimated_cost = 0.0

        if response.llm_output and 'token_usage' in response.llm_output:
            self.input_tokens = response.llm_output['token_usage'].get('prompt_tokens', 0)
            self.output_tokens = response.llm_output['token_usage'].get('completion_tokens', 0)
            self.total_tokens = self.input_tokens + self.output_tokens
        elif response.usage_metadata:
            self.input_tokens = response.usage_metadata.get('input_tokens', 0)
            self.output_tokens = response.usage_metadata.get('output_tokens', 0)
            self.total_tokens = response.usage_metadata.get('total_tokens', 0)

        # Calculate a very rough estimated cost (example, replace with actual pricing)
        cost_per_1k_input = 0.00035 # Gemini 1.5 Flash input $/1K tokens
        cost_per_1k_output = 0.00045 # Gemini 1.5 Flash output $/1K tokens
        self.estimated_cost = (self.input_tokens / 1000 * cost_per_1k_input) + \
                              (self.output_tokens / 1000 * cost_per_1k_output)
        print(f"LLM Usage: Input Tokens={self.input_tokens}, Output Tokens={self.output_tokens}, Est. Cost=${self.estimated_cost:.6f}")


# --- API Endpoints (Login, User Creation, etc. as before) ---

@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/token", response_model=Token)
# --- JWT & Password Utility Functions ---
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
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

@app.get("/users/me/", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# --- Research Agent Endpoint ---
@app.post("/research", response_model=ResearchResponse, status_code=status.HTTP_200_OK)
async def perform_research(
    request: ResearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    print(f"\n--- Research Request Received for User: {current_user.username} ---")
    
    session_title = f"Research Query - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    if request.session_id:
        research_session = db.query(ResearchSession).filter(
            ResearchSession.session_id == request.session_id,
            ResearchSession.user_id == current_user.user_id
        ).first()
        if not research_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Research session with ID {request.session_id} not found for this user."
            )
    else:
        research_session = create_new_research_session(db, current_user.user_id, session_title)
        print(f"Created new research session: {research_session.session_id} - '{research_session.session_title}'")

    query_entry = create_research_query(
        db,
        user_id=current_user.user_id,
        session_id=research_session.session_id,
        query_text=request.query,
        llm_model_used=llm.model
    )
    print(f"Created ResearchQuery entry with ID: {query_entry.query_id}")

    # Initialize the callback handler with the current DB session and query_id
    callbacks = [DBToolLoggerCallbackHandler(db, query_entry.query_id)]

    try:
        print(f"Invoking LangChain agent for query ID: {query_entry.query_id}")
        raw_response = await agent_executor.ainvoke(
            {"query": request.query},
            config={"callbacks": callbacks} # Pass the callback handler to the agent
        )
        print("LangChain agent execution complete.")

        llm_output_text = raw_response.get('output', '')
        parsed_successfully = True
        try:
            agent_parsed_response: AgentResearchResponse = agent_parser.parse(llm_output_text)
            print("Agent output parsed successfully.")
        except Exception as parse_error:
            print(f"ERROR: Failed to parse agent output: {parse_error}")
            parsed_successfully = False
            agent_parsed_response = AgentResearchResponse(
                topic="Parsing Error",
                summary=f"Failed to parse agent's response. Raw output: {llm_output_text}. Error: {parse_error}",
                sources=["N/A"],
                tools_used=["N/A"]
            )
            raise HTTPException( # Re-raise immediately if parsing failed
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to parse agent's structured output. Raw response: {llm_output_text}"
            )

        input_tokens = 0
        output_tokens = 0
        estimated_cost = 0.0

        if callbacks and isinstance(callbacks[0], DBToolLoggerCallbackHandler):
            input_tokens = callbacks[0].input_tokens
            output_tokens = callbacks[0].output_tokens
            estimated_cost = callbacks[0].estimated_cost
        
        update_research_query_metrics(
            db,
            query_entry.query_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_cost=estimated_cost
        )
        print(f"ResearchQuery metrics updated for ID: {query_entry.query_id}")

        output_db_entry = create_research_output(
            db,
            query_id=query_entry.query_id,
            topic=agent_parsed_response.topic,
            summary=agent_parsed_response.summary,
            sources=agent_parsed_response.sources,
            tools_used_reported=agent_parsed_response.tools_used,
            parsing_successful=parsed_successfully,
            raw_llm_output=llm_output_text
        )
        print(f"ResearchOutput entry created for ID: {output_db_entry.output_id}")

        return ResearchResponse(
            topic=agent_parsed_response.topic,
            summary=agent_parsed_response.summary,
            sources=agent_parsed_response.sources,
            tools_used=agent_parsed_response.tools_used,
            output_id=output_db_entry.output_id,
            query_id=query_entry.query_id,
            created_at=output_db_entry.created_at
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: An unhandled exception occurred during research: {e}")
        # Ensure the DB session is rolled back if an unhandled error occurs here
        db.rollback() # Add rollback
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal server error occurred during research: {str(e)}. "
                   "Please check server logs for more details."
        )

if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
    print("FastAPI server stopped.")
