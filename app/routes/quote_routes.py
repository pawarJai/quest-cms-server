from fastapi import APIRouter, HTTPException, Depends
from typing import List

from app.schemas.quote_schema import QuoteCreate, QuoteResponse
from app.repository.quote_repository import QuoteRepository
from app.services.auth_dependency import verify_user

router = APIRouter(prefix="/quotes", tags=["Quotes"])


# ---------------- POST (Public) ----------------
@router.post("/", response_model=dict)
async def create_quote(payload: QuoteCreate):
    quote_id = await QuoteRepository.create_quote(payload.dict())
    return {
        "message": "Quote request submitted successfully",
        "quote_id": quote_id
    }


# ---------------- GET ALL (Admin) ----------------
@router.get("/", dependencies=[Depends(verify_user)])
async def get_all_quotes():
    quotes = await QuoteRepository.get_all_quotes()
    return {
        "count": len(quotes),
        "quotes": quotes
    }


# ---------------- GET BY ID (Admin) ----------------
@router.get("/{quote_id}", dependencies=[Depends(verify_user)])
async def get_quote(quote_id: str):
    quote = await QuoteRepository.get_quote_by_id(quote_id)
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    return quote
