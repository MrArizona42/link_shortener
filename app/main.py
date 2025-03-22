# app/main.py
import uvicorn
from fastapi import FastAPI

# from app.auth.routes import router as auth_router
# from app.db import db  # our Database instance

app = FastAPI(title="ShortLinks App")


@app.get("/")
async def root():
    return {"message": "Hello from FastAPI!"}


# Include the auth routes (similar setup can be done for links)
# app.include_router(auth_router, prefix="/auth", tags=["auth"])

# @app.on_event("startup")
# async def startup():
#     await db.connect()  # Initializes the connection pool

# @app.on_event("shutdown")
# async def shutdown():
#     await db.disconnect()  # Closes the connection pool

if __name__ == "main":
    uvicorn.run(app, host="0.0.0.0", port=8000)
