# app.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from schemas import FactCheckRequest, FactCheckResponse
from factcheck_engine import fact_check
import pytesseract
from PIL import Image
import io

app = FastAPI(
    title="TEJAS Fact Checking API",
    description="Evidence-based, multi-source fact checking system",
    version="4.1"
)

# --- CRITICAL: ALLOW FRONTEND TO COMMUNICATE ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any URL (Ngrok, Localhost, etc.)
    allow_credentials=True,
    allow_methods=["*"],  # Allows POST, GET, OPTIONS
    allow_headers=["*"],
)
# -----------------------------------------------

@app.get("/")
def health_check():
    return {"status": "TEJAS fact-checking service running"}

# --- NEW: IMAGE TEXT EXTRACTION ENDPOINT ---
@app.post("/extract-text")
async def extract_text_from_image(file: UploadFile = File(...)):
    """
    Receives an image, performs OCR using Tesseract, and returns the text.
    """
    try:
        # 1. Read image file into memory
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # 2. Perform OCR (Image to String)
        # Note: Tesseract must be installed in the Docker container
        text = pytesseract.image_to_string(image)
        
        # 3. Clean text (replace multiple newlines with spaces)
        clean_text = " ".join(text.split())
        
        if not clean_text:
            return {"text": "", "message": "No text detected in image."}
            
        return {"text": clean_text}
        
    except Exception as e:
        print(f"OCR Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Image processing failed: {str(e)}")
# -------------------------------------------

@app.post("/factcheck", response_model=FactCheckResponse)
def check_fact(request: FactCheckRequest):
    return fact_check(request.text)