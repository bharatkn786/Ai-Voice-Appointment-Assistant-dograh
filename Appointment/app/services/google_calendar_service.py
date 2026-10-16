from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo
from google.oauth2 import service_account
from googleapiclient.discovery import build
from pathlib import Path
from googleapiclient.errors import HttpError

TZ = ZoneInfo("Asia/Kolkata")
BASE_DIR = Path(__file__).resolve().parent
SA_FILE = BASE_DIR / "sa.json"

creds = service_account.Credentials.from_service_account_file(
    str(SA_FILE),
    scopes=["https://www.googleapis.com/auth/calendar"]
)

cal = build("calendar", "v3", credentials=creds)

# doctor name (lowercase) -> calendar id. Move to DB later.
# DOCTOR_CALENDARS = {
#     "doc_001": "1baa8e4c54e975d8470e51793a5bd317655d9b02dd5ebdb1f189a78b7a2298fa@group.calendar.google.com",
# }

def get_slots(calendar_id, day, slot_min=30, start_h=10, end_h=18):
    start = datetime.combine(day, time(start_h), TZ)
    end = datetime.combine(day, time(end_h), TZ)
    fb = cal.freebusy().query(body={
        "timeMin": start.isoformat(), "timeMax": end.isoformat(),
        "timeZone": "Asia/Kolkata", "items": [{"id": calendar_id}]}).execute()
    busy = [(datetime.fromisoformat(b["start"]), datetime.fromisoformat(b["end"]))
            for b in fb["calendars"][calendar_id]["busy"]]
    slots, t = [], start
    while t + timedelta(minutes=slot_min) <= end:
        e = t + timedelta(minutes=slot_min)
        if t > datetime.now(TZ) and not any(t < be and e > bs for bs, be in busy):
            slots.append(t.strftime("%H:%M"))
        t = e
    return slots

def book(calendar_id, day, hhmm, patient, phone=None, slot_min=30):
    if hhmm not in get_slots(calendar_id, day, slot_min):
        return {"ok": False, "error": "slot_taken"}
    h, m = map(int, hhmm.split(":"))
    start = datetime.combine(day, time(h, m), TZ)
    ev = cal.events().insert(calendarId=calendar_id, body={
        "summary": f"Appointment - {patient}",
        "description": f"Phone: {phone or 'not provided'}\nBooked by voice assistant",
        "start": {"dateTime": start.isoformat(), "timeZone": "Asia/Kolkata"},
        "end": {"dateTime": (start + timedelta(minutes=slot_min)).isoformat(),
                "timeZone": "Asia/Kolkata"},
    }).execute()
    return {"ok": True, "event_id": ev["id"]}




def cancel(calendar_id, event_id):
    try:
        cal.events().delete(calendarId=calendar_id, eventId=event_id).execute()
    except HttpError as e:
        if e.resp.status in (404, 410):      # already deleted
            return {"ok": True}
        return {"ok": False, "error": "calendar_error"}
    return {"ok": True}
    