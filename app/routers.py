from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional

from app.models import (
    CandidateCreate,
    CandidateResponse,
    CandidateStatus,
    StatusUpdate,
)
from app import database

router = APIRouter(prefix="/candidates", tags=["Candidates"])


@router.post(
    "",
    response_model=CandidateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new candidate",
)
def create_candidate(payload: CandidateCreate):
    """
    Add a new candidate to the recruitment pipeline.

    - **name**: Full name of the candidate (required, non-empty)
    - **email**: Valid email address (required)
    - **skill**: Primary skill / technology (required, non-empty)
    - **status**: One of `applied`, `interview`, `selected`, `rejected` (default: `applied`)
    """
    candidate = database.create_candidate(payload)
    return candidate


@router.get(
    "",
    response_model=List[CandidateResponse],
    summary="List all candidates",
)
def list_candidates(
    status: Optional[CandidateStatus] = Query(
        default=None,
        description="Filter candidates by status",
    )
):
    """
    Retrieve all candidates. Optionally filter by **status**.

    Example: `GET /candidates?status=interview`
    """
    return database.get_candidates(status=status)


@router.put(
    "/{candidate_id}/status",
    response_model=CandidateResponse,
    summary="Update candidate status",
)
def update_status(candidate_id: str, payload: StatusUpdate):
    """
    Update the recruitment status of a specific candidate.

    - **candidate_id**: UUID of the candidate
    - **status**: New status — one of `applied`, `interview`, `selected`, `rejected`
    """
    candidate = database.update_candidate_status(candidate_id, payload.status)
    if candidate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with id '{candidate_id}' not found.",
        )
    return candidate
