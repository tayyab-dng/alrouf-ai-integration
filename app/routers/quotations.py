from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List
import json
from pathlib import Path

router = APIRouter()

MOCK_FILE_PATH = Path(__file__).parent.parent / "mocks" / "mock_quotes.json"

class QuoteItem(BaseModel):
    item_id: str = Field(..., description="Unique identifier for the item")
    description: str = Field(..., description="Description of the item")
    quantity: int = Field(..., gt=0, description="Quantity of the item (must be greater than 0)")
    unit_price: float = Field(..., ge=0.0, description="Unit price of the item (must be non-negative)")

class CreateQuoteRequest(BaseModel):
    rfq_id: str = Field(..., description="Reference RFQ ID")
    items: List[QuoteItem] = Field(..., min_items=1, description="List of items in the RFQ")
    currency: str = Field("USD", description="Currency of the quote")

class Quotation(BaseModel):
    rfq_id: str
    items: List[QuoteItem]
    total_cost: float
    currency: str
    status: str = "pending"

def read_mock_quotes() -> List[dict]:
    if not MOCK_FILE_PATH.exists():
        return []
    try:
        with open(MOCK_FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error reading mock quotes database file."
        )

def write_mock_quotes(quotes: List[dict]):
    try:
        with open(MOCK_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(quotes, f, indent=2)
    except IOError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error writing to mock quotes database file."
        )

@router.get("/quotations", response_model=List[Quotation])
def get_quotations():
    """
    Read and return all mock quotations from the database.
    """
    return read_mock_quotes()

@router.post("/quotations", response_model=Quotation, status_code=status.HTTP_201_CREATED)
def create_quotation(payload: CreateQuoteRequest):
    """
    Accept an RFQ payload, calculate total cost, save it, and return the created quotation.
    """
    # 1. Read existing quotes
    quotes = read_mock_quotes()

    # 2. Check if RFQ ID already exists
    if any(q.get("rfq_id") == payload.rfq_id for q in quotes):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Quotation with RFQ ID '{payload.rfq_id}' already exists."
        )

    # 3. Calculate total cost
    total_cost = sum(item.quantity * item.unit_price for item in payload.items)

    # 4. Form the quotation object
    new_quote = Quotation(
        rfq_id=payload.rfq_id,
        items=payload.items,
        total_cost=total_cost,
        currency=payload.currency,
        status="pending"
    )

    # 5. Save/Append
    quotes.append(new_quote.dict())
    write_mock_quotes(quotes)

    return new_quote
