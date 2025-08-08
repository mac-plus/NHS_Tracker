from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# Allow CORS for all origins (for frontend testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/hospitals")
def get_hospitals():
    url = "https://aeinfo.nhs.wales/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
    except Exception as e:
        return {"error": str(e)}

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
        except Exception:
            continue

    return {"hospitals": hospital_data}
