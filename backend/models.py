from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class Visual(BaseModel):
    kind: Literal["image", "shapes", "text-only"] = "text-only"
    imagePrompt: Optional[str] = None
    imageFile: Optional[str] = None
    kenBurns: Optional[Literal["zoom-in", "zoom-out", "pan-left", "pan-right", "none"]] = "zoom-in"


class Scene(BaseModel):
    id: str
    type: Literal["title", "content", "diagram", "outro"] = "content"
    durationSec: float = Field(ge=2, le=60)
    transition: Literal["fade", "slide", "zoom", "none"] = "fade"
    narration: str
    audioFile: Optional[str] = None
    visual: Visual = Field(default_factory=Visual)
    headline: Optional[str] = None
    bullets: List[str] = Field(default_factory=list)
    caption: Optional[str] = None


class Storyboard(BaseModel):
    jobId: str
    title: str
    fps: int = 30
    width: int = 1920
    height: int = 1080
    totalDurationSec: float
    music: Optional[str] = None
    scenes: List[Scene]


class JobStatus(BaseModel):
    jobId: str
    prompt: str
    stage: str = "queued"  # queued, storyboard, tts, images, render, done, error
    percent: int = 0
    message: str = ""
    error: Optional[str] = None
    outputUrl: Optional[str] = None
    createdAt: float
    updatedAt: float
