
import os
from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import shutil
from pathlib import Path
from datetime import datetime
import Model
import orchestrate
import custom_Agent

# Initialize FastAPI app
app = FastAPI(
    title="RAG Agent API",
    description="API for RAG-based knowledge base management and chat",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

KNOWLEDGE_BASE_DIR = Path("KnowledgeBase")
KNOWLEDGE_BASE_DIR.mkdir(exist_ok=True)

# Admin credentials (move to environment variables in production)
ADMIN_USERS = {
    "admin": "admin123"
}

# ================================ Models ================================

class ChatRequest(BaseModel):
    message: str
    chat_history: Optional[List[dict]] = []

class ChatResponse(BaseModel):
    response: str
    status: str = "success"

class FileUploadResponse(BaseModel):
    filename: str
    size: int
    collection_name: str
    status: str
    message: str

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str
    message: str
    status: str = "success"

# ================================ Auth Dependency ================================

def verify_token(authorization: str = Header(None)):
    """Verify admin token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized - No token provided")
    
    token = authorization.replace("Bearer ", "")
    if not token.startswith("token_"):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return True

# ================================ Endpoints ================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "message": "RAG Agent API is running",
        "version": "1.0.0"
    }

# ============ NEW AUTH ENDPOINT ============

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """Admin login endpoint"""
    try:
        username = credentials.username
        password = credentials.password
        
        if ADMIN_USERS.get(username) == password:
            return LoginResponse(
                token=f"token_{username}_{datetime.now().timestamp()}",
                message="Login successful",
                status="success"
            )
        else:
            raise HTTPException(status_code=401, detail="Invalid username or password")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ UPDATED UPLOAD ENDPOINT ============

@app.post("/api/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    domain: str = Form(...),
    auth: bool = Depends(verify_token)
):
    """Upload file to specific domain knowledge base"""
    try:
        print(f"Received file: {file.filename}")
        print(f"Domain: {domain}")
        
        allowed_extensions = {".pdf", ".txt", ".doc", ".docx", ".csv"}
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_extension} not supported"
            )
        
        # Create domain-specific directory
        domain_dir = KNOWLEDGE_BASE_DIR / domain
        domain_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file in domain directory
        file_path = domain_dir / file.filename
        print(f"Saving to: {file_path}")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = file_path.stat().st_size
        print(f"File size: {file_size} bytes")
        
        # Process with domain-specific collection
        collection_name = f"{domain}_datas"
        print(f"Processing into collection: {collection_name}")
        custom_Agent.process_data(str(file_path), collection_name)
        print("Processing complete!")
        
        return FileUploadResponse(
            filename=file.filename,
            size=file_size,
            collection_name=collection_name,
            status="success",
            message=f"File processed and added to {domain} domain"
        )
    
    except Exception as e:
        print(f"ERROR in upload: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ============ NEW FILE MANAGEMENT ENDPOINTS ============

@app.get("/api/files/{domain}")
async def get_domain_files(
    domain: str,
    auth: bool = Depends(verify_token)
):
    """Get all files from a specific domain"""
    try:
        domain_dir = KNOWLEDGE_BASE_DIR / domain
        
        if not domain_dir.exists():
            return {
                "files": [],
                "domain": domain,
                "count": 0,
                "status": "success"
            }
        
        files = []
        for file_path in domain_dir.glob("*.*"):
            if file_path.is_file():
                stat = file_path.stat()
                files.append({
                    "id": hash(file_path.name),
                    "name": file_path.name,
                    "size": f"{stat.st_size / 1024:.2f} KB",
                    "uploadTime": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                })
        
        return {
            "files": files,
            "domain": domain,
            "count": len(files),
            "status": "success"
        }
    
    except Exception as e:
        print(f"Error getting files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/files/{domain}/{filename}")
async def delete_file(
    domain: str,
    filename: str,
    auth: bool = Depends(verify_token)
):
    """Delete a specific file from domain"""
    try:
        file_path = KNOWLEDGE_BASE_DIR / domain / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Delete the file
        os.remove(file_path)
        print(f"Deleted file: {file_path}")
        
        return {
            "status": "success",
            "message": f"File '{filename}' deleted from {domain} domain",
            "filename": filename,
            "domain": domain
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/files/{domain}/{filename}/content")
async def get_file_content(
    domain: str,
    filename: str,
    auth: bool = Depends(verify_token)
):
    """Get content of a specific file"""
    try:
        file_path = KNOWLEDGE_BASE_DIR / domain / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "content": content,
            "filename": filename,
            "domain": domain,
            "status": "success"
        }
    
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Cannot read file - binary format not supported for viewing"
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/domains")
async def get_domains(auth: bool = Depends(verify_token)):
    """Get list of all available domains"""
    try:
        domains = []
        for item in KNOWLEDGE_BASE_DIR.iterdir():
            if item.is_dir():
                file_count = len(list(item.glob("*.*")))
                domains.append({
                    "name": item.name,
                    "fileCount": file_count
                })
        
        return {
            "domains": domains,
            "count": len(domains),
            "status": "success"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ EXISTING ENDPOINTS ============

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send message to RAG agent"""
    try:
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        print(f"Received message: {request.message}")
        
        try:
            refine_query = request.message
            print("Refined Query : ", refine_query)
            response = orchestrate.agent_executor.invoke({
                "input": refine_query,
                "chat_history": request.chat_history or []
            })
            
            print(f"Agent response: {response['output']}")
            
            return ChatResponse(
                response=response["output"],
                status="success"
            )
            
        except Exception as agent_error:
            error_msg = str(agent_error)
            if "Failed to call a function" in error_msg:
                return ChatResponse(
                    response="I'm having trouble understanding your question. Could you rephrase it?",
                    status="success"
                )
            else:
                raise agent_error
    
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/collections")
async def list_collections():
    """List all collections"""
    try:
        collections = custom_Agent.vector_database.client.list_collections()
        collection_names = [col.name for col in collections]
        
        return {
            "collections": collection_names,
            "count": len(collection_names),
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/collections/{collection_name}")
async def delete_collection(collection_name: str, auth: bool = Depends(verify_token)):
    """Delete a collection"""
    try:
        custom_Agent.vector_database.client.delete_collection(collection_name)
        return {
            "status": "success",
            "message": f"Collection '{collection_name}' deleted"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run server
if __name__ == "__main__":
    import uvicorn
    print("Starting RAG Backend Server...")
    print("API will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    uvicorn.run("Backend_server:app", host="0.0.0.0", port=8000, reload=True)
