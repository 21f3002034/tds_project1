# /// script
# requires-python = ">=3.13"
# dependencies = [
#      "fastapi",
#      "uvicorn", 
#      "requests",    
#
#
# ]
# ///

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Working"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
