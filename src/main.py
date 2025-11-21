from fastapi import FastAPI

from src.routers.admin import router as admin_router
from src.routers.vendors import router as vendor_router

app = FastAPI()

app.include_router(vendor_router)
app.include_router(admin_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}