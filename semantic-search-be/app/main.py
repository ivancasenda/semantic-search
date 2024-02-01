import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from search import router as search

# Imports the Cloud Logging client library
import google.cloud.logging

# Instantiates a logging at INFO level and higher
google.cloud.logging.Client().setup_logging()


app = FastAPI()

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the search router
app.include_router(search.router)


@app.get("/")
async def root():
    """Get Cloud Run environment variables."""
    service = os.environ.get("K_SERVICE", "Unknown service")
    revision = os.environ.get("K_REVISION", "Unknown revision")

    return {"service": service, "revision": revision}


if __name__ == "__main__":
    # Run the FastAPI app using Uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="debug")
