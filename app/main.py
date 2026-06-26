from fastapi import FastAPI
from app.routers import quotations

app = FastAPI(
    title="AL ROUF Quotation Engine",
    description="Offline-friendly Quotation Engine microservice for AL ROUF LED Assessment.",
    version="0.1.0"
)

# Register routes
app.include_router(quotations.router, tags=["Quotations"])

@app.get("/")
def read_root():
    """
    Health-check endpoint to verify if the API is online.
    """
    return {
        "status": "healthy",
        "service": "AL ROUF Quotation Engine",
        "version": "0.1.0"
    }
