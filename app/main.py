from functools import partial
from datetime import datetime

import pytz
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.csrf import csrf_protect
from app.db import permission
from app.routers import authentication, user, project, task, status, taskCategory, role
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

# @app.middleware("http")
# async def convert_dates_to_utc(request: Request, call_next):
#     # Function to convert date strings to UTC
#     def convert_to_utc(date_str, timezone_str):
#         local_tz = pytz.timezone(timezone_str)
#         local_dt = local_tz.localize(datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S"))
#         utc_dt = local_dt.astimezone(pytz.utc)
#         #Get the name of my timezone
#         return utc_dt
# # body[key] = datetime.fromisoformat(value).replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Europe/Belgrade')).isoformat()
#
#     # Process the request body and convert date strings to UTC
#     if request.method in ["POST", "PUT", "PATCH"]:
#         print("Usao sam u if")
#         body = await request.json()
#         timezone_str = "Europe/Belgrade"  # Adjust this to your timezone
#         for key, value in body.items():
#             if isinstance(value, str) and "T" in value:  # Simple check for datetime strings
#                 print("Usao sam u if 2")
#                 print("Key: ", body[key])
#                 try:
#                     body[key] = convert_to_utc(value, timezone_str).isoformat()
#                 except ValueError:
#                     pass  # Ignore values that are not valid date strings
#         request._body = body
#
#     response = await call_next(request)
#     return response

# Your existing routes and other configurations

@app.get("/openapi.json")
def get_openapi_spec():
    return app.openapi()

# Uključivanje rutera
app.include_router(authentication.router,tags=["authentication"])
app.include_router(user.router,tags=["user"])
app.include_router(project.router,tags=["project"])
app.include_router(task.router,tags=["task"])
app.include_router(status.router,tags=["status"])
app.include_router(taskCategory.router,tags=["taskCategory"])
app.include_router(role.router,tags=["role"])

#zastita od csrf napada kroz generisanje csrf tokena
# app.middleware("http")(partial(csrf_protect,exclude =["/login"]))


# Pokretanje aplikacije sa uvicorn serverom
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)