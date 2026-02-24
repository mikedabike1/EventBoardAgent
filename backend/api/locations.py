
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import databridge, schemas
from ..database import get_db

# ---------------------------------------------------------------------------
# Locations
# ---------------------------------------------------------------------------

router = APIRouter()


@router.get("/locations", response_model=list[schemas.LocationOut], tags=["locations"])
def list_locations(db: Session = Depends(get_db)):
    return databridge.get_locations(db)
