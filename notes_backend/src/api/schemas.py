from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    """
    PUBLIC_INTERFACE
    Schema for creating a new note.
    """
    title: str = Field(..., description="The title of the note", min_length=1, max_length=255)
    content: Optional[str] = Field(None, description="The content of the note")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "My First Note",
                    "content": "This is the content of my first note."
                }
            ]
        }
    }


class NoteUpdate(BaseModel):
    """
    PUBLIC_INTERFACE
    Schema for updating an existing note.
    All fields are optional to allow partial updates.
    """
    title: Optional[str] = Field(None, description="The updated title of the note", min_length=1, max_length=255)
    content: Optional[str] = Field(None, description="The updated content of the note")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Updated Note Title",
                    "content": "Updated content for the note."
                }
            ]
        }
    }


class NoteResponse(BaseModel):
    """
    PUBLIC_INTERFACE
    Schema for note response.
    """
    id: int = Field(..., description="The unique identifier of the note")
    title: str = Field(..., description="The title of the note")
    content: Optional[str] = Field(None, description="The content of the note")
    created_at: str = Field(..., description="The timestamp when the note was created")
    updated_at: str = Field(..., description="The timestamp when the note was last updated")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "title": "My First Note",
                    "content": "This is the content of my first note.",
                    "created_at": "2024-01-15 10:30:00",
                    "updated_at": "2024-01-15 10:30:00"
                }
            ]
        }
    }
