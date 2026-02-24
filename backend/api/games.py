from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import databridge, schemas
from ..database import get_db

# ---------------------------------------------------------------------------
# Game Systems
# ---------------------------------------------------------------------------

router = APIRouter()


@router.get("/games", response_model=list[schemas.GameSystemOut], tags=["games"])
def list_game_systems(db: Session = Depends(get_db)):
    return databridge.get_game_systems(db)

