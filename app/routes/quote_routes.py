from fastapi import APIRouter, HTTPException, Depends
from typing import List

from app.schemas.quote_schema import QuoteCreate, QuoteResponse
from app.repository.quote_repository import QuoteRepository
from app.services.auth_dependency import verify_user

router = APIRouter(prefix="/contact-us", tags=["Contact-us"])


# ---------------- POST (Public) ----------------
@router.post("/", response_model=dict, summary="Create Contact Us", description="Submit a new Contact Us request")
async def create_quote(payload: QuoteCreate):
    quote_id = await QuoteRepository.create_contact(payload.dict())
    return {
        "message": "Contact-us request submitted successfully",
        "contact_us_id": quote_id
    }


# ---------------- GET ALL (Admin) ----------------
@router.get("/", summary="Get all Contact Us requests", description="Returns all Contact Us submissions with count and data")
async def get_all_quotes():
    quotes = await QuoteRepository.get_all_contacts()
    return {
        "count": len(quotes),
        "contact_data": quotes
    }


# ---------------- GET BY ID (Admin) ----------------
@router.get("/{quote_id}", summary="Get Contact Us by ID", description="Fetch a single Contact Us submission by its ID")
async def get_quote(quote_id: str):
    quote = await QuoteRepository.get_contact_by_id(quote_id)
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    return quote
