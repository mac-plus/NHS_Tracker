
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# Allow all origins for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock hospital data as fallback
mock_data = [
    {
        "name": "Cardiff Royal Infirmary",
        "wait_minutes": 35,
        "current_patients": 30,
        "paediatric": True,
        "open_24_7": True,
        "note": "General A&E with paediatrics",
        "hours": "Open 24/7"
    },
    {
        "name": "Ysbyty Ystrad Fawr",
        "wait_minutes": 25,
        "current_patients": 15,
        "paediatric": True,
        "open_24_7": False,
        "note": "Minor Injuries, no overnight",
        "hours": "08:00–20:00"
    },
    {
        "name": "Royal Glamorgan Hospital",
        "wait_minutes": 45,
        "current_patients": 40,
        "paediatric": False,
        "open_24_7": True,
        "note": "Adult A&E only",
        "hours": "Open 24/7"
    }
]

@app.get("/hospitals")
def get_hospitals():
    url = "https://aeinfo.nhs.wales/"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")

        hospital_data = []
        for h in soup.select(".ae-department"):
            try:
                name = h.select_one("h3").text.strip()
                wait_text = h.select_one(".wait-time__current span").text.strip()
                wait = int(wait_text.split()[0])
                patients = int(h.select_one(".patients__current span").text.strip())
                note = h.select_one(".ae-department__note").text.strip().lower()
                hours = h.select_one(".ae-department__hours").text.strip().lower()

                hospital_data.append({
                    "name": name,
                    "wait_minutes": wait,
                    "current_patients": patients,
                    "paediatric": "no paediatric" not in note,
                    "open_24_7": "24" in hours or "open all day" in hours,
                    "note": note,
                    "hours": hours
                })
            except:
                continue

        if not hospital_data:
            return {"hospitals": mock_data, "source": "mock"}
        return {"hospitals": hospital_data, "source": "live"}

    except Exception as e:
        return {"hospitals": mock_data, "source": "mock", "error": str(e)}
