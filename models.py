"""Data models for the application."""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator


class CharacterInput(BaseModel):
    """Character input model."""

    name: str = Field(..., min_length=1, max_length=100)
    ref_image: str = Field(..., min_length=1)
    description: Optional[str] = Field(None, max_length=500)


class SceneInput(BaseModel):
    """Scene input model for each panel."""

    scene_description: str = Field(..., min_length=1, max_length=1000)
    character_states: dict[str, str] = Field(default_factory=dict)
    objects_background: str = Field(default="", max_length=1000)


class ImageGenerationRequest(BaseModel):
    """Request model for image generation."""

    # Aspect ratio is fixed to 3:4 (portrait) to avoid interference with layout reference
    aspect_ratio: Literal["3:4"] = "3:4"
    layout_ref_image: Optional[str] = None
    characters: List[CharacterInput] = Field(default_factory=list)
    scenes: List[SceneInput] = Field(..., min_items=4, max_items=4)

    @field_validator('scenes')
    @classmethod
    def validate_scenes_count(cls, v):
        """Validate that exactly 4 scenes are provided."""
        if len(v) != 4:
            raise ValueError('Exactly 4 scenes must be provided')
        return v


class ImageGenerationResponse(BaseModel):
    """Response model for image generation."""

    success: bool
    thought_process: str = ""
    image_url: Optional[str] = None
    error: Optional[str] = None


class FileListResponse(BaseModel):
    """Response model for file list."""

    files: List[str]
