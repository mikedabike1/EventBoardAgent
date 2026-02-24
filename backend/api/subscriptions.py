from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import databridge, schemas
from ..database import get_db

# ---------------------------------------------------------------------------
# Subscriptions
# ---------------------------------------------------------------------------

router = APIRouter()


@router.post(
    "/subscribe", response_model=schemas.SubscribeOut, status_code=201, tags=["subscriptions"]
)
def subscribe(payload: schemas.SubscribeIn, db: Session = Depends(get_db)):
    sub = databridge.create_or_update_subscriber(
        db, str(payload.email), payload.location_ids, payload.game_system_ids
    )
    db.commit()
    db.refresh(sub)
    return sub
