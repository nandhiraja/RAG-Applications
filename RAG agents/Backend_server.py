"""
FastAPI Backend for RAG Agent Application
"""
import os
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import shutil
from pathlib import Path
import Model
# Import your existing modules
import orchestrate
import custom_Agent

# Initialize FastAPI app
app = FastAPI(
    title="RAG Agent API",
    description="API for RAG-based knowledge base management and chat",
    version="1.0.0"
)

# CORS middleware - Allow all origins for development
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

# ================================ Endpoints ================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "message": "RAG Agent API is running",
        "version": "1.0.0"
    }

@app.post("/api/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    collection_name: str = Form("general_knowledge")
):
    """Upload and process file into knowledge base"""
    try:
        print(f"Received file: {file.filename}")
        print(f"Collection: {collection_name}")
        
        allowed_extensions = {".pdf", ".txt", ".doc", ".docx", ".csv"}
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_extension} not supported"
            )
        
        file_path = UPLOAD_DIR / file.filename
        print(f"Saving to: {file_path}")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = file_path.stat().st_size
        print(f"File size: {file_size} bytes")
        
        print("Starting processing...")
        custom_Agent.process_data(str(file_path), collection_name)
        print("Processing complete!")
        
        return FileUploadResponse(
            filename=file.filename,
            size=file_size,
            collection_name=collection_name,
            status="success",
            message=f"File processed and added to {collection_name}"
        )
    
    except Exception as e:
        print(f"ERROR in upload: {str(e)}")
        import traceback
        traceback.print_exc()  # This will show full error trace
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send message to RAG agent"""
    try:
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        print(f"Received message: {request.message}")
        
        try:
            # refine_query = Model.getRespose(request.message)
            refine_query = request.message
            print("Refined Query : ",refine_query)
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
            # If agent fails, provide helpful fallback
            error_msg = str(agent_error)
            if "Failed to call a function" in error_msg:
                return ChatResponse(
                    response="I'm having trouble understanding your question. Could you rephrase it? For example:\n- For IT issues: 'How do I fix system overheating?'\n- For finance/HR: 'What is the travel reimbursement policy?'",
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

@app.delete("/api/files/{collection_name}")
async def delete_collection(collection_name: str):
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
