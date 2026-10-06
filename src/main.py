from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.logger_config import logger
from src.routers import users, comments, files

app = FastAPI(title="File Manager")


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    policy = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:;"
    response.headers["Content-Security-Policy"] = policy
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception on %s", request.url, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "We are sorry, something went wrong."},
    )


@app.get("/cause_error")
def cause_error():
    raise ZeroDivisionError("test error")


app.include_router(users.router)
app.include_router(comments.router)
app.include_router(files.router)
