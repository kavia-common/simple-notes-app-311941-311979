from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from datetime import datetime

from src.api.schemas import NoteCreate, NoteUpdate, NoteResponse
from src.api.db import get_db_connection, dict_from_row

# OpenAPI metadata
tags_metadata = [
    {
        "name": "health",
        "description": "Health check endpoint to verify the API is running."
    },
    {
        "name": "notes",
        "description": "Operations for managing notes. Create, read, update, and delete notes."
    }
]

app = FastAPI(
    title="Notes API",
    description="A REST API for managing notes with CRUD operations. This API allows you to create, read, update, and delete notes with title and content.",
    version="1.0.0",
    openapi_tags=tags_metadata
)

# CORS middleware to allow frontend on port 3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["health"], summary="Health Check", response_description="Returns health status")
def health_check():
    """
    PUBLIC_INTERFACE
    Health check endpoint.
    
    Returns:
        dict: A message indicating the API is healthy
    """
    return {"message": "Healthy"}


@app.get(
    "/notes",
    response_model=List[NoteResponse],
    tags=["notes"],
    summary="List all notes",
    description="Retrieve a list of all notes in the database.",
    response_description="List of notes with their details"
)
def list_notes():
    """
    PUBLIC_INTERFACE
    Retrieve all notes from the database.
    
    Returns:
        List[NoteResponse]: List of all notes
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, content, created_at, updated_at
            FROM notes
            ORDER BY updated_at DESC
        """)
        rows = cursor.fetchall()
        notes = [dict_from_row(row) for row in rows]
    return notes


@app.post(
    "/notes",
    response_model=NoteResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["notes"],
    summary="Create a new note",
    description="Create a new note with a title and optional content.",
    response_description="The created note with its assigned ID and timestamps"
)
def create_note(note: NoteCreate):
    """
    PUBLIC_INTERFACE
    Create a new note.
    
    Args:
        note: The note data (title and content)
        
    Returns:
        NoteResponse: The created note with ID and timestamps
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO notes (title, content)
            VALUES (?, ?)
        """, (note.title, note.content))
        note_id = cursor.lastrowid
        
        # Fetch the created note with timestamps
        cursor.execute("""
            SELECT id, title, content, created_at, updated_at
            FROM notes
            WHERE id = ?
        """, (note_id,))
        row = cursor.fetchone()
        
    return dict_from_row(row)


@app.get(
    "/notes/{id}",
    response_model=NoteResponse,
    tags=["notes"],
    summary="Get a specific note",
    description="Retrieve a single note by its ID.",
    response_description="The note with the specified ID",
    responses={
        200: {"description": "Note found and returned"},
        404: {"description": "Note not found"}
    }
)
def get_note(id: int):
    """
    PUBLIC_INTERFACE
    Retrieve a single note by ID.
    
    Args:
        id: The ID of the note to retrieve
        
    Returns:
        NoteResponse: The note with the specified ID
        
    Raises:
        HTTPException: 404 if note not found
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, content, created_at, updated_at
            FROM notes
            WHERE id = ?
        """, (id,))
        row = cursor.fetchone()
        
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {id} not found"
        )
    
    return dict_from_row(row)


@app.put(
    "/notes/{id}",
    response_model=NoteResponse,
    tags=["notes"],
    summary="Update a note",
    description="Update an existing note's title and/or content. Only provided fields will be updated.",
    response_description="The updated note",
    responses={
        200: {"description": "Note updated successfully"},
        404: {"description": "Note not found"}
    }
)
def update_note(id: int, note: NoteUpdate):
    """
    PUBLIC_INTERFACE
    Update an existing note.
    
    Args:
        id: The ID of the note to update
        note: The updated note data (title and/or content)
        
    Returns:
        NoteResponse: The updated note
        
    Raises:
        HTTPException: 404 if note not found
    """
    # Check if note exists
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM notes WHERE id = ?", (id,))
        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Note with id {id} not found"
            )
        
        # Build dynamic update query based on provided fields
        update_fields = []
        values = []
        
        if note.title is not None:
            update_fields.append("title = ?")
            values.append(note.title)
        
        if note.content is not None:
            update_fields.append("content = ?")
            values.append(note.content)
        
        # Always update the updated_at timestamp
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        
        if not update_fields:
            # No fields to update, just return the current note
            cursor.execute("""
                SELECT id, title, content, created_at, updated_at
                FROM notes
                WHERE id = ?
            """, (id,))
            row = cursor.fetchone()
            return dict_from_row(row)
        
        # Perform the update
        values.append(id)
        query = f"UPDATE notes SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, values)
        
        # Fetch and return the updated note
        cursor.execute("""
            SELECT id, title, content, created_at, updated_at
            FROM notes
            WHERE id = ?
        """, (id,))
        row = cursor.fetchone()
        
    return dict_from_row(row)


@app.delete(
    "/notes/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["notes"],
    summary="Delete a note",
    description="Delete a note by its ID.",
    response_description="No content returned on successful deletion",
    responses={
        204: {"description": "Note deleted successfully"},
        404: {"description": "Note not found"}
    }
)
def delete_note(id: int):
    """
    PUBLIC_INTERFACE
    Delete a note by ID.
    
    Args:
        id: The ID of the note to delete
        
    Raises:
        HTTPException: 404 if note not found
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check if note exists
        cursor.execute("SELECT id FROM notes WHERE id = ?", (id,))
        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Note with id {id} not found"
            )
        
        # Delete the note
        cursor.execute("DELETE FROM notes WHERE id = ?", (id,))
    
    return None
