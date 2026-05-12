from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

app = FastAPI(title="RCA Chat API", version="1.0.0")
KB_DIR = Path("knowledge_base")
ALLOWED_KB_EXTENSIONS = {".txt", ".log", ".md"}
KB_DIR.mkdir(exist_ok=True)

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name=os.getenv("MODEL_NAME", "llama-3.1-70b-versatile")
)

class ChatRequest(BaseModel):
    message: str
    message_type: str = None

class ChatResponse(BaseModel):
    response: str
    message_type: str

def load_knowledge_base():
    """Load uploaded knowledge base files from the backend service."""
    content = []
    for file_path in sorted(KB_DIR.glob("*")):
        if file_path.suffix.lower() not in ALLOWED_KB_EXTENSIONS:
            continue
        try:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            content.append(f"\n\n--- {file_path.name} ---\n{text}")
        except OSError:
            continue
    return "".join(content)

def get_message_type(text):
    """Detect message type to determine response style"""
    text_lower = text.lower()
    
    greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]
    if any(greeting in text_lower for greeting in greetings) and len(text) < 20:
        return "greeting"
    
    error_keywords = ["error", "exception", "failed", "traceback", "stack trace", "connection refused", "timeout", "null pointer"]
    if any(kw in text_lower for kw in error_keywords) or len(text) > 150:
        return "error_log"
    
    simple_questions = ["what is", "how to", "can you", "do you", "is it"]
    if any(q in text_lower for q in simple_questions) and len(text) < 50:
        return "simple_question"
    
    if "?" in text and len(text) > 50:
        return "complex_question"
    
    return "general"

def get_system_prompt(message_type):
    """Get system prompt based on message type"""
    prompts = {
        "greeting": """You are a friendly RCA assistant. Respond to greetings warmly but briefly (1-2 sentences). Offer to help with error analysis or technical questions.""",
        
        "error_log": """You are an expert RCA (Root Cause Analysis) assistant. Analyze the error log and provide:

1. **Error Summary**: What happened?
2. **Root Cause**: Why did it happen?
3. **Solution**: How to fix it?
4. **Prevention**: How to avoid it in future?

Be thorough but organized. Use bullet points for clarity.""",
        
        "simple_question": """You are a helpful technical assistant. Answer the question concisely in 1-3 sentences. Be direct and practical.""",
        
        "complex_question": """You are a technical expert. Provide a detailed, well-structured answer. Use examples and explanations as needed. Be thorough but organized.""",
        
        "general": """You are a helpful AI assistant specializing in system troubleshooting. Respond appropriately to the user's message. Keep it conversational and offer to help with technical issues."""
    }
    return prompts.get(message_type, prompts["general"])

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "RCA Chat API",
        "version": "1.0.0",
        "description": "Root Cause Analysis Chat Assistant API",
        "endpoints": {
            "health": "/health",
            "chat": "/chat (POST)",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "RCA Chat API",
        "version": "1.0.0",
        "groq_configured": bool(os.getenv("GROQ_API_KEY")),
        "knowledge_base_files": len([
            file_path for file_path in KB_DIR.glob("*")
            if file_path.suffix.lower() in ALLOWED_KB_EXTENSIONS
        ])
    }

@app.get("/knowledge-base")
async def list_knowledge_base():
    """List uploaded knowledge base files."""
    files = [
        file_path.name
        for file_path in sorted(KB_DIR.glob("*"))
        if file_path.suffix.lower() in ALLOWED_KB_EXTENSIONS
    ]
    return {"files": files}

@app.post("/knowledge-base/upload")
async def upload_knowledge_base(files: list[UploadFile] = File(...)):
    """Upload knowledge base files to the backend service."""
    saved_files = []

    for uploaded_file in files:
        filename = Path(uploaded_file.filename or "").name
        if not filename:
            continue

        if Path(filename).suffix.lower() not in ALLOWED_KB_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type for {filename}. Use .txt, .log, or .md."
            )

        destination = KB_DIR / filename
        destination.write_bytes(await uploaded_file.read())
        saved_files.append(filename)

    return {"uploaded": saved_files, "count": len(saved_files)}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint that processes user messages and returns AI responses
    
    Args:
        request: ChatRequest with message and optional message_type
        
    Returns:
        ChatResponse with response text and detected message type
    """
    try:
        # Detect message type if not provided
        message_type = request.message_type or get_message_type(request.message)
        
        # Get appropriate system prompt
        system_prompt = get_system_prompt(message_type)
        kb_content = load_knowledge_base()
        if kb_content:
            system_prompt += f"\n\nKnowledge Base Context:\n{kb_content[:4000]}"
        
        # Create message for LLM
        messages = [HumanMessage(content=system_prompt + "\n\nUser message:\n" + request.message)]
        
        # Get response from LLM
        response = llm.invoke(messages)
        
        return ChatResponse(
            response=response.content,
            message_type=message_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
