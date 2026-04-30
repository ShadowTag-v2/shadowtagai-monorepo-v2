from fastapi import FastAPI
from starlette.responses import JSONResponse

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health")
async def health_check():
    return JSONResponse(content={"status": "healthy"}, status_code=200)
