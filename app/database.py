import uuid
from typing import Dict, List, Optional
from app.models import CandidateCreate, CandidateStatus


# In-memory store: {id: candidate_dict}
_store: Dict[str, dict] = {}


def create_candidate(data: CandidateCreate) -> dict:
    candidate_id = str(uuid.uuid4())
    candidate = {
        "id": candidate_id,
        "name": data.name,
        "email": data.email,
        "skill": data.skill,
        "status": data.status,
    }
    _store[candidate_id] = candidate
    return candidate


def get_candidates(status: Optional[CandidateStatus] = None) -> List[dict]:
    candidates = list(_store.values())
    if status is not None:
        candidates = [c for c in candidates if c["status"] == status]
    return candidates


def update_candidate_status(candidate_id: str, status: CandidateStatus) -> Optional[dict]:
    candidate = _store.get(candidate_id)
    if candidate is None:
        return None
    candidate["status"] = status
    _store[candidate_id] = candidate
    return candidate
