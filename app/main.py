from functools import partial

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.csrf import csrf_protect
from app.routers import authentication, user
import uvicorn

app = FastAPI()

origins = [
    "http://localhost:5173"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Uključivanje rutera
app.include_router(authentication.router,tags=["authentication"])
app.include_router(user.router,tags=["user"])

#zastita od csrf napada kroz generisanje csrf tokena
app.middleware("http")(partial(csrf_protect,exclude =["/login"]))

# Pokretanje aplikacije sa uvicorn serverom
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)