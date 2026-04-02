from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routers import router

app = FastAPI(
    title="Candidate Management API",
    description=(
        "A recruitment system API for managing candidates through their hiring pipeline. "
        "Supports creating candidates, listing them (with optional status filtering), "
        "and updating candidate status."
    ),
    version="1.0.0",
)

# ── Custom validation error handler ──────────────────────────────────────────
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"] if loc != "body")
        errors.append({"field": field, "message": error["msg"]})
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation failed", "errors": errors},
    )


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(router)


@app.get("/", tags=["Health"])
def root():
    return {
        "message": "Candidate Management API is running 🚀",
        "docs": "/docs",
        "redoc": "/redoc",
    }
