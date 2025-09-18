"""
API Server for Investment Screening System - Fixed for LightOn Integration
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import tempfile
import os
from typing import List
import logging

# Import your actual clients
from workflows.investment_screening import execute_workflow
from clients.paradigm_client import ParadigmClient
from config.settings import LIGHTON_API_KEY, LIGHTON_BASE_URL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Investment Screening API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Paradigm client
paradigm_client = ParadigmClient(LIGHTON_API_KEY, LIGHTON_BASE_URL)

# Store uploaded document info locally
uploaded_documents = {}

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the frontend HTML page"""
    try:
        with open("frontend.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Frontend not found</h1><p>Please ensure frontend.html is in the same directory</p>")

@app.post("/api/files/upload")  # Changed to match your working frontend
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a document using ParadigmClient (matches your working frontend pattern)
    """
    try:
        logger.info(f"Uploading file via ParadigmClient: {file.filename}")
        
        # Read file content
        content = await file.read()
        
        # Create a temporary file for ParadigmClient upload
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Use your existing ParadigmClient upload method
            # You'll need to add this method to your ParadigmClient
            upload_result = await paradigm_client.upload_file(temp_file_path, file.filename)
            
            # Store document info locally
            document_info = {
                "id": upload_result["id"],
                "filename": upload_result.get("filename", file.filename),
                "bytes": len(content),
                "status": upload_result.get("status", "uploaded"),
                "content_type": file.content_type
            }
            
            uploaded_documents[upload_result["id"]] = document_info
            
            logger.info(f"File uploaded successfully via ParadigmClient: ID {upload_result['id']}")
            
            return {
                "id": upload_result["id"],
                "filename": file.filename,
                "bytes": len(content),
                "status": "uploaded",
                "content_type": file.content_type
            }
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
            
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.delete("/api/files/{file_id}")  # Changed to match your working frontend
async def delete_file(file_id: int):
    """Delete a file using ParadigmClient"""
    try:
        # Use ParadigmClient to delete the file
        await paradigm_client.delete_file(file_id)
        
        # Remove from local storage if exists
        if file_id in uploaded_documents:
            del uploaded_documents[file_id]
        
        return {"success": True, "message": f"File {file_id} deleted successfully"}
        
    except Exception as e:
        logger.error(f"Delete failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

@app.post("/api/screen")
async def screen_investment(document_ids: List[int]):
    """Process investment screening for uploaded documents"""
    try:
        logger.info(f"Starting investment screening for documents: {document_ids}")
        
        # Execute the investment screening workflow
        user_input = "Analyze the attached investment opportunity documents"
        result = await execute_workflow(user_input, document_ids)
        
        logger.info("Investment screening completed successfully")
        
        return {
            "success": True,
            "document_ids": document_ids,
            "screening_result": result,
            "message": "Investment screening completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Screening failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Screening failed: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test ParadigmClient connectivity
        # You can add a simple API call here to test connectivity
        return {
            "status": "healthy",
            "service": "Investment Screening API",
            "version": "1.0.0",
            "paradigm_client": "configured"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "Investment Screening API", 
            "version": "1.0.0",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")