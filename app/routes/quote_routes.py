from fastapi import APIRouter, HTTPException, Depends
from typing import List

from app.schemas.quote_schema import QuoteCreate, QuoteResponse
from app.repository.quote_repository import QuoteRepository
from app.services.auth_dependency import verify_user

router = APIRouter(prefix="/contact-us", tags=["Contact-us"])


# ---------------- POST (Public) ----------------
@router.post("/", response_model=dict)
async def create_quote(payload: QuoteCreate):
    quote_id = await QuoteRepository.create_contact(payload.dict())
    return {
        "message": "Contact-us request submitted successfully",
        "quote_id": quote_id
    }


# ---------------- GET ALL (Admin) ----------------
@router.get("/")
async def get_all_quotes():
    quotes = await QuoteRepository.get_all_contacts()
    return {
        "count": len(quotes),
        "quotes": quotes
    }


# ---------------- GET BY ID (Admin) ----------------
@router.get("/{quote_id}")
async def get_quote(quote_id: str):
    quote = await QuoteRepository.get_contact_by_id(quote_id)
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    return quote
