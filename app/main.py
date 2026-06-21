import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, OperationalError

from app.api.v1.router import router
from app.core.scheduler import setup_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = setup_scheduler()
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(title="Agrobot Weather Alerts", lifespan=lifespan)
app.include_router(router)


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    detail = str(exc.orig).split("\n")[0] if exc.orig else "Integrity constraint violated"
    logger.warning("IntegrityError on %s %s — %s", request.method, request.url.path, detail)
    return JSONResponse(status_code=409, content={"detail": detail})


@app.exception_handler(OperationalError)
async def operational_error_handler(request: Request, exc: OperationalError) -> JSONResponse:
    logger.error("Database unavailable on %s %s", request.method, request.url.path, exc_info=exc)
    return JSONResponse(status_code=503, content={"detail": "Database unavailable"})
