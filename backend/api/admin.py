
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..importer import run_import
from ..newsletter import run_newsletter

# ---------------------------------------------------------------------------
# Admin (no auth in MVP — protect via network/reverse proxy in production)
# ---------------------------------------------------------------------------

router = APIRouter()


@router.post("/admin/import", tags=["admin"])
def trigger_import(db: Session = Depends(get_db)):
    return run_import(db)


@router.post("/admin/newsletter", tags=["admin"])
def trigger_newsletter(db: Session = Depends(get_db)):
    return run_newsletter(db)


@router.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}
