
# ============================================================
# 1. IMPORTS (Required libraries ko import karna)
# ============================================================

from pathlib import Path
# Path: File aur folder ke paths ko easily handle karne ke liye.
# Example: templates folder, static folder ka path banana.

import traceback
# Error aane par complete error details (line number ke saath)
# terminal mein print karne ke liye.

import uvicorn
# Uvicorn: FastAPI application ko run karne wala server.


from fastapi import FastAPI, Request
# FastAPI: API application create karne ke liye.
# Request: Browser se aane wali request ko handle karne ke liye.

from fastapi.responses import HTMLResponse, JSONResponse
# HTMLResponse: Browser ko HTML page return karne ke liye.
# JSONResponse: API se JSON format mein response bhejne ke liye.

from fastapi.staticfiles import StaticFiles
# StaticFiles: CSS, JavaScript, images jaise static files serve karne ke liye.

from fastapi.templating import Jinja2Templates
# Jinja2Templates: HTML templates (index.html) ko render karne ke liye.

from pydantic import BaseModel
# BaseModel: Request data ka structure aur validation define karne ke liye.


from backend import run_travel_agent
# Apne backend.py se travel agent function import kar rahe hain.
# Ye function LangGraph / AI agent ko run karega.
# Input: User ka travel question
# Output: Travel planning ka result


# ============================================================
# 2. BASE DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

# __file__ = Current Python file (app.py) ka path.
# resolve() = Complete / absolute path nikalta hai.
# parent = Jis folder mein app.py rakhi hai, woh folder.
#
# Example:
# Project/
# ├── app.py
# ├── static/
# └── templates/
#
# BASE_DIR = Project folder ka absolute path.
#
# Isse hum static aur templates folder ko locate kar sakte hain.


# ============================================================
# 3. FASTAPI APPLICATION CREATE KARNA
# ============================================================

app = FastAPI(
    title="TripMate AI",
    description="LangGraph Multi-Agent Travel Planner with FastAPI Frontend",
    version="1.0.0"
)

# FastAPI() ek application object create karta hai.
# Isi 'app' object ke andar hum API routes define karenge.
#
# title, description, version:
# API documentation (Swagger UI) mein information dikhane ke liye.
#
# Swagger UI:
# http://127.0.0.1:8000/docs


# ============================================================
# 4. STATIC FILES CONFIGURATION
# ============================================================

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static"
)

# Static files = CSS, JavaScript, images etc.
#
# BASE_DIR / "static":
# Project ke andar static folder ka path banata hai.
#
# str():
# Path object ko string mein convert karta hai.
#
# "/static":
# Browser jab /static/... URL access karega,
# FastAPI static folder se file serve karega.
#
# Example:
# static/style.css
#
# Browser URL:
# http://127.0.0.1:8000/static/style.css
#
# name="static":
# Static files mount ko ek naam deta hai.


# ============================================================
# 5. HTML TEMPLATES CONFIGURATION
# ============================================================

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)

# templates folder ke andar HTML files rakhi hongi.
#
# Example:
# templates/
# └── index.html
#
# Jinja2Templates ka use HTML page ko browser mein render
# karne ke liye kiya jata hai.
#
# directory = Jahan HTML templates stored hain.


# ============================================================
# 6. REQUEST DATA MODEL (PYDANTIC)
# ============================================================

class TravelRequest(BaseModel):

    message: str
    thread_id: str | None = None

# Ye class frontend se aane wale JSON data ka jstructure define karti hai.
#
# BaseModel:
# Pydantic automatically request data ko validate karta hai.
#
# message: str
# User ka travel question string format mein hona chahiye.
#
# thread_id: str | None = None
# thread_id ek string ho sakti hai ya None.
# None ka matlab: User ne thread_id provide nahi ki.
#
# Example JSON:
# {
#     "message": "Plan a 3 day trip to Goa",
#     "thread_id": "user-123"
# }
#
# Agar thread_id nahi bheji:
# {
#     "message": "Plan a trip to Goa"
# }
#
# Toh thread_id ka value None ho sakta hai.


# ============================================================
# 7. HOME PAGE ROUTE
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )

# @app.get("/")
# Ye ek GET API route define karta hai.
#
# Jab user browser mein open karega:
# http://127.0.0.1:8000/
#
# Toh home() function execute hoga.
#
# async def:
# Asynchronous function. FastAPI async functions ko support karta hai.
#
# request: Request
# Browser ki incoming request ka object.
#
# TemplateResponse:
# templates folder se index.html load karke browser ko return karta hai.
#
# name="index.html":
# Kaunsi HTML file render karni hai.
#
# context={}:
# HTML template ko additional data bhejne ke liye.
# Abhi koi extra data nahi bhej rahe hain.


# ============================================================
# 8. TRAVEL PLANNER API ROUTE
# ============================================================

@app.post("/api/travel")
async def travel_planner(request_data: TravelRequest):

    # @app.post():
    # POST request handle karne ke liye.
    #
    # Frontend user ka travel question bhejega.
    #
    # Example URL:
    # http://127.0.0.1:8000/api/travel
    #
    # request_data: TravelRequest
    # FastAPI incoming JSON ko TravelRequest model ke through
    # validate karega aur object mein convert karega.
    #
    # Example:
    # request_data.message
    # request_data.thread_id

    try:

        # ----------------------------------------------------
        # 8.1 USER MESSAGE CLEAN KARNA
        # ----------------------------------------------------

        user_message = request_data.message.strip()

        # strip():
        # Message ke starting aur ending ke extra spaces remove karta hai.
        #
        # Example:
        # "   Plan a Goa trip   "
        # Result:
        # "Plan a Goa trip"


        # ----------------------------------------------------
        # 8.2 EMPTY MESSAGE VALIDATION
        # ----------------------------------------------------

        if not user_message:

            # Agar user ne empty message bheja,
            # toh AI agent ko run nahi karna.
            #
            # Empty string = False condition ke andar chali jayegi.

            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "Message cannot be empty."
                }
            )

        # status_code=400:
        # Bad Request. Client ne invalid data bheja.
        #
        # success=False:
        # Frontend ko batata hai ki request successful nahi hui.
        #
        # error:
        # Error ka reason frontend ko return karta hai.


        # ----------------------------------------------------
        # 8.3 BACKEND TRAVEL AGENT RUN KARNA
        # ----------------------------------------------------

        result = run_travel_agent(
            user_input=user_message,
            thread_id=request_data.thread_id
        )

        # Ab actual AI travel agent ko call kar rahe hain.
        #
        # user_input:
        # User ka cleaned travel question.
        #
        # thread_id:
        # Conversation ko identify / maintain karne ke liye.
        #
        # run_travel_agent() backend.py mein defined hai.
        #
        # Expected result example:
        #
        # result = {
        #     "thread_id": "user-123",
        #     "answer": "Here is your travel plan...",
        #     "flight_results": [...],
        #     "hotel_results": [...],
        #     "itinerary": [...],
        #     "llm_calls": 3
        # }


        # ----------------------------------------------------
        # 8.4 SUCCESS RESPONSE FRONTEND KO BHEJNA
        # ----------------------------------------------------

        return JSONResponse(
            content={
                "success": True,

                "thread_id": result["thread_id"],

                "answer": result["answer"],

                "flight_results": result["flight_results"],

                "hotel_results": result["hotel_results"],

                "itinerary": result["itinerary"],

                "llm_calls": result["llm_calls"],
            }
        )

        # JSONResponse:
        # Python dictionary ko JSON response ke form mein bhejta hai.
        #
        # success=True:
        # Request successfully complete hui.
        #
        # result["answer"]:
        # AI ka final travel planning answer.
        #
        # result["flight_results"]:
        # Flight search se aane wale results.
        #
        # result["hotel_results"]:
        # Hotel search ke results.
        #
        # result["itinerary"]:
        # Complete travel itinerary.
        #
        # result["llm_calls"]:
        # Kitni baar LLM call hui, uski information.
        #
        # NOTE:
        # result mein ye saare keys available hone chahiye,
        # warna KeyError aa sakta hai.


    # ========================================================
    # 8.5 ERROR HANDLING
    # ========================================================

    except Exception as e:

        # Agar try block ke andar koi bhi unexpected error aata hai,
        # toh control except block mein aa jayega.
        #
        # Example errors:
        # - Backend agent fail hona
        # - API error
        # - Missing dictionary key
        # - Network issue

        print("ERROR:", e)

        # Short error message terminal mein print karta hai.

        traceback.print_exc()

        # Complete error traceback terminal mein print karta hai.
        # Isse pata chalta hai ki error kis line par aaya.


        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )

        # status_code=500:
        # Internal Server Error.
        # Server ke andar unexpected problem hui.
        #
        # str(e):
        # Error object ko string mein convert karke frontend ko bhejna.
        #
        # Production application mein detailed internal errors
        # directly client ko expose karne se bachna chahiye.


# ============================================================
# 9. HEALTH CHECK API
# ============================================================

@app.get("/health")
async def health_check():

    return {
        "status": "ok",
        "message": "AI Travel Planner API is running"
    }

# Health check endpoint:
# Server chal raha hai ya nahi, check karne ke liye.
#
# Browser mein open karo:
# http://127.0.0.1:8000/health
#
# Expected response:
# {
#     "status": "ok",
#     "message": "AI Travel Planner API is running"
# }
#
# Iska use monitoring aur deployment mein hota hai.


# ============================================================
# 10. FAVICON ROUTE
# ============================================================

@app.get("/favicon.ico")
async def favicon():

    return JSONResponse(content={})

# Browser aksar website ka favicon automatically request karta hai.
#
# Ye route favicon request ko handle karta hai.
# Abhi empty JSON return kar raha hai.
#
# Isse favicon ke liye alag error avoid karne mein help ho sakti hai.
# Actual favicon serve karna ho toh static files se icon provide kar sakte hain.


# ============================================================
# 11. APPLICATION RUN KARNA
# ============================================================

if __name__ == "__main__":

    # Ye condition tab True hoti hai jab file ko directly run karte hain.
    #
    # Example:
    # python app.py
    #
    # Agar file kisi aur module mein import hoti hai,
    # toh ye block automatically execute nahi hota.

    uvicorn.run(
        "app:app",

        # "app:app" ka meaning:
        # Pehla app = Python file ka naam (app.py)
        # Dusra app = FastAPI object ka naam
        #
        # Format:
        # "filename:FastAPI_object"

        host="127.0.0.1",

        # Server sirf local machine par accessible hoga.
        # 127.0.0.1 = localhost

        port=8000,

        # Application port number.
        # Browser URL:
        # http://127.0.0.1:8000

        reload=True

        # Development mode mein:
        # Code change hone par server automatically restart hota hai.
        #
        # Production mein reload=True use nahi karna chahiye.
    )