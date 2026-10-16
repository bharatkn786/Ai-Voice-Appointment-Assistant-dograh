# 🏥 AI Voice Appointment Assistant (Dograh)

An AI voice assistant that answers inbound hospital phone calls and handles **doctor search, appointment booking and cancellation** in natural, multilingual conversation. Built on the [Dograh](https://github.com/dograh-hq/dograh) voice-agent platform with a FastAPI backend, Supabase Postgres and Google Calendar.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📞 Inbound call handling | Answers hospital calls via Plivo telephony |
| 🗣️ Multilingual | Replies in the caller's language (English, Hindi, Marathi and more) |
| 🔍 Doctor search | Search by name, specialty or location with typo-tolerant matching |
| 📅 Availability check | Live slot lookup from each doctor's Google Calendar |
| ✅ Booking | Books the slot after explicit caller confirmation |
| ❌ Cancellation | Finds the caller's upcoming appointments by phone number and cancels only after a "yes" |
| 📱 Caller ID capture | Phone number is picked up automatically, so the caller is never asked for it |
| 🚨 Emergency handling | Detects emergencies, tells the caller to dial **108 / 112**, and ends the call |

---

## 🧠 Call Flow (Dograh Workflow)


<img width="1535" height="470" alt="Screenshot 2026-10-14 154503" src="https://github.com/user-attachments/assets/28214f01-032a-4192-9b0e-2be9bc4af8a2" />


| Node | Purpose |
|---|---|
| **Global Node** | Persona ("Sam"), language rules, truth rules, emergency rule |
| **Start Call** | Greets the caller, asks the name, runs `extract_caller` |
| **Main Agenda** | Routes to booking, doctor search or cancellation |
| **Book Appointment** | Collects doctor/date/time, confirms, then books |
| **Doctor Search / Availability** | Finds doctors and checks open slots |
| **Cancel Appointment** | Fetches upcoming bookings, confirms, cancels |
| **End Call** | Short polite goodbye |

The importable workflow lives in the repo as a Dograh JSON export.

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Voice agent platform | Dograh |
| Telephony | Plivo (inbound) |
| LLM / speech | Gemini Live (speech-to-speech) |
| Backend API | FastAPI (Python) |
| Database | Supabase Postgres (SQLAlchemy) |
| Doctor matching | `pg_trgm` + `fuzzystrmatch` |
| Scheduling | Google Calendar API (service account, one calendar per doctor) |

---

## 🔧 Agent Tools

Dograh calls these HTTP tools on the FastAPI backend:

| Tool | Used in | What it does |
|---|---|---|
| `extract_caller` | Start, Main Agenda | Reads the caller's phone number from call context |
| `search_doctors` | Doctor Search, Booking | Finds doctors by name, specialty or location |
| `get_all_doctors` | Doctor Search | Lists all doctors |
| `get_available_slots` | Doctor Search, Booking | Returns free slots for a doctor and date |
| `book_appointment` | Booking | Creates the calendar event and saves the booking |
| `get_my_bookings` | Cancellation | Lists the caller's upcoming appointments |
| `cancel_booking` | Cancellation | Cancels the confirmed appointment |

---

## 🗄️ Data Model

**`doctors`**: `id`, `name`, `specialty`, `location`, `available`, `calendar_id`
**`bookings`**: doctor, patient name, caller phone, date/time, status

Seed doctors with:

```bash
python -m app.database.seed
```

---

## 🚀 Getting Started

### 1. Clone

```bash
git clone https://github.com/bharatkn786/Ai-Voice-Appointment-Assistant-dograh.git
cd Ai-Voice-Appointment-Assistant-dograh
```

### 2. Install

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure `.env`

```env
DATABASE_URL=postgresql://user:password@host:5432/postgres
GOOGLE_SERVICE_ACCOUNT_FILE=service-account.json
```

The repo includes **`sa.example.json`**, a template showing the structure of the Google service-account key. Copy it and fill in your real values:

```bash
cp sa.example.json service-account.json
```

Then edit `service-account.json` with the credentials from your Google Cloud service account (`project_id`, `private_key`, `client_email`, etc.).

> ⚠️ Never commit `.env` or the real `service-account.json`. Only `sa.example.json` (with placeholder values) belongs in the repo. Make sure `service-account.json` is in your `.gitignore`.

### 4. Enable Postgres extensions (Supabase SQL editor)

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
```

### 5. Google Calendar setup

1. Create a Google Cloud service account and download its JSON key. Use it to fill in your `service-account.json` (see `sa.example.json` for the expected format).
2. Create one calendar per doctor and share each with the service-account email (make changes to events).
3. Save each `calendar_id` in `doctors.json`.

### 6. Run the backend

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

Expose it publicly (e.g. ngrok) so Dograh can reach it.

### 7. Connect Dograh

1. Import the workflow JSON into Dograh.
2. Create the HTTP tools above, pointing to your backend URL.
3. Attach tools to nodes as shown in the call flow.
4. Add your Plivo credentials and Gemini API key, then assign the number to the workflow.

---

## ⏱️ Performance

| Step | Latency |
|---|---|
| Availability check | ~1226 ms |
| Booking | ~1575 ms |
| Spoken confirmation | ~545 ms |

Target: under 2 s per turn.

---

## 💰 Cost per Minute

| Setup | ₹ / min |
|---|---|
| Dograh cloud + paid services | 7.64 |
| Self-hosted Dograh | 6.69 |
| Own keys (Gemini free tier + Plivo) | ~1.33 |

---



