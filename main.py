from fastapi import FastAPI

from routes.home import router as home_router
from routes.v1 import api as v1
from routes.v2 import api as v2

app = FastAPI(title="ChocoMax Shop API")

# Home (non-versioned)
app.include_router(home_router)

# Versioned API
app.mount("/api/v1", v1)
app.mount("/api/v2", v2)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True)
