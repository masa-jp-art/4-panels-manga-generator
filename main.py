"""Main FastAPI application."""

import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from google.genai import types

from config import get_settings
from models import FileListResponse, ImageGenerationRequest, ImageGenerationResponse
from utils import get_files_in_directory, validate_api_key, load_image_bytes
from prompt_builder import build_manga_prompt
from gemini_client import GeminiImageGenerator

# Initialize FastAPI app
app = FastAPI(
    title="4-Panel Manga Generator",
    description="Generate 4-panel manga using Google Gemini API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


@app.get("/")
async def root():
    """Root endpoint redirects to the UI."""
    return {"message": "4-Panel Manga Generator API", "docs": "/docs"}


@app.get("/api/files/layout", response_model=FileListResponse)
async def get_layout_files():
    """Get list of layout reference images.

    Returns:
        FileListResponse: List of layout reference image filenames

    Raises:
        HTTPException: If directory cannot be read
    """
    try:
        files = get_files_in_directory("static/layout_refs")
        return FileListResponse(files=files)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/files/characters", response_model=FileListResponse)
async def get_character_files():
    """Get list of character reference images.

    Returns:
        FileListResponse: List of character reference image filenames

    Raises:
        HTTPException: If directory cannot be read
    """
    try:
        files = get_files_in_directory("static/char_refs")
        return FileListResponse(files=files)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate", response_model=ImageGenerationResponse)
async def generate_image(request: ImageGenerationRequest):
    """Generate manga panel images based on input.

    Args:
        request: Image generation request with scenes and references

    Returns:
        ImageGenerationResponse: Generation result with image URL or error

    Raises:
        HTTPException: If generation fails
    """
    try:
        settings = get_settings()
        validate_api_key(settings.gemini_api_key)

        # Build prompt
        prompt_text = build_manga_prompt(
            characters=request.characters,
            scenes=request.scenes,
            has_layout_ref=bool(request.layout_ref_image)
        )

        # Build image parts list
        image_parts = []

        # Add layout reference image if provided
        if request.layout_ref_image:
            layout_path = f"static/layout_refs/{request.layout_ref_image}"
            if Path(layout_path).exists():
                image_data, mime_type = load_image_bytes(layout_path)
                image_parts.append(
                    types.Part.from_bytes(data=image_data, mime_type=mime_type)
                )

        # Add character reference images
        for char in request.characters:
            if char.ref_image:
                char_path = f"static/char_refs/{char.ref_image}"
                if Path(char_path).exists():
                    image_data, mime_type = load_image_bytes(char_path)
                    image_parts.append(
                        types.Part.from_bytes(data=image_data, mime_type=mime_type)
                    )

        # Initialize Gemini client and generate
        generator = GeminiImageGenerator(api_key=settings.gemini_api_key)
        thought_process, image_url = generator.generate_manga(
            prompt=prompt_text,
            aspect_ratio=request.aspect_ratio,
            image_parts=image_parts
        )

        return ImageGenerationResponse(
            success=True,
            thought_process=thought_process,
            image_url=image_url,
            error=None
        )

    except ValueError as e:
        return ImageGenerationResponse(
            success=False,
            thought_process="",
            image_url=None,
            error=str(e)
        )
    except FileNotFoundError as e:
        return ImageGenerationResponse(
            success=False,
            thought_process="",
            image_url=None,
            error=f"Reference image not found: {str(e)}"
        )
    except Exception as e:
        return ImageGenerationResponse(
            success=False,
            thought_process="",
            image_url=None,
            error=f"Image generation failed: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint.

    Returns:
        Health status
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
