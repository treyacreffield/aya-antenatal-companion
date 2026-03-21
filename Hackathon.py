from flask import Flask, request, Response, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)

APP_NAME = "Aya"
APP_SUBTITLE = "Antenatal Companion"

# ---------------------------------
# In-memory patient store
# ---------------------------------
patients = {}

# ---------------------------------
# Question flow configuration
# ---------------------------------
QUESTION_TEXT = {
    "registration_age": "Welcome to Aya. Please reply with your age in years using numbers only.",
    "registration_week": "Please reply with your pregnancy week using numbers only. If you do not know, reply 0.",
    "q1": (
        "Q1. Are you experiencing any of these danger signs: heavy bleeding, fits/seizures, or blurred vision?\n"
        "Reply:\n1. Yes\n2. No"
    ),
    "q2": (
        "Q2. Are you having a severe constant headache?\n"
        "Reply:\n1. Yes\n2. No"
    ),
    "q3": (
        "Q3. Do you have fever or chills?\n"
        "Reply:\n1. Yes\n2. No"
    ),
    "q4": (
        "Q4. Is water leaking or has your fluid broken?\n"
        "Reply:\n1. Yes\n2. No"
    ),
    "q5": (
        "Q5. Have you noticed reduced fetal movement?\n"
        "Reply:\n1. Yes\n2. No"
    ),
    "q6": (
        "Q6. Do you have itchy hands or feet?\n"
        "Reply:\n1. Yes\n2. No"
    ),
    "q7": (
        "Q7. Do you have severe pelvic or abdominal pain?\n"
        "Reply:\n1. Yes\n2. No"
    ),
    "q8": (
        "Q8. Have you previously had pre-eclampsia or stillbirth?\n"
        "Reply:\n1. Yes\n2. No"
    ),
    "q9": (
        "Q9. Do you have a history of hypertension (high blood pressure)?\n"
        "Reply:\n1. Yes\n2. No"
    ),
    "q10": (
        "Q10. Do you have a history of diabetes?\n"
        "Reply:\n1. Yes\n2. No"
    ),
    "q11": (
        "Q11. Are you younger than 18 or older than 35?\n"
        "Reply:\n1. Yes\n2. No"
    ),
}

QUESTION_SEQUENCE = [
    "q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "q10", "q11"
]

QUESTION_POINTS = {
    "q1": 5,
    "q2": 3,
    "q3": 3,
    "q4": 3,
    "q5": 3,
    "q6": 2,
    "q7": 2,
    "q8": 2,
    "q9": 1,
    "q10": 1,
    "q11": 1,
}

QUESTION_LABELS = {
    "q1": "Danger signs: heavy bleeding / fits / blurred vision",
    "q2": "Severe constant headache",
    "q3": "Fever or chills",
    "q4": "Water leaking / fluid breaking",
    "q5": "Reduced fetal movement",
    "q6": "Itchy hands/feet",
    "q7": "Severe pelvic/abdominal pain",
    "q8": "Previous pre-eclampsia or stillbirth",
    "q9": "Hypertension history",
    "q10": "Diabetes history",
    "q11": "Age under 18 or over 35",
}

# ---------------------------------
# Helpers
# ---------------------------------
def now_iso():
    return datetime.utcnow().isoformat()

def twiml_message(text: str) -> Response:
    safe_text = (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
    )
    xml = f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{safe_text}</Message></Response>'
    return Response(xml, mimetype="application/xml")

def normalise_text(text: str) -> str:
    return (text or "").strip().lower()

def risk_from_score(score: int) -> str:
    if score >= 5:
        return "red"
    if score >= 3:
        return "yellow"
    return "green"

def required_response_from_risk(risk: str) -> str:
    if risk == "red":
        return "Emergency pickup"
    if risk == "yellow":
        return "Phone call"
    return "Routine monitoring"

def patient_message_from_risk(risk: str) -> str:
    if risk == "red":
        return (
            "Aya has flagged your assessment as urgent. "
            "Please go to the nearest hospital or dial your local emergency number now. "
            "A clinic has also been alerted."
        )
    if risk == "yellow":
        return (
            "Aya has completed your assessment. "
            "A clinic will phone you soon to follow up. "
            "If your symptoms worsen before then, go to the nearest hospital."
        )
    return (
        "Aya has completed your assessment. "
        "You can continue routine antenatal care and monitor for new symptoms. "
        "If new warning signs appear, seek medical help."
    )

def create_patient(phone: str) -> dict:
    patient = {
        "phone": phone,
        "age": None,
        "pregnancy_week": None,
        "status": "registering_age",
        "current_question": "registration_age",
        "score": 0,
        "risk": "green",
        "required_response": "Routine monitoring",
        "patient_message": None,
        "symptoms": [],
        "risk_factors": [],
        "answers": {},
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "last_message": None,
        "completed": False,
    }
    patients[phone] = patient
    return patient

def get_or_create_patient(phone: str) -> dict:
    return patients.get(phone) or create_patient(phone)

def delete_patient(phone: str) -> bool:
    if phone in patients:
        del patients[phone]
        return True
    return False

def clinic_row(patient: dict) -> dict:
    return {
        "phone": patient["phone"],
        "age": patient["age"],
        "pregnancy_week": patient["pregnancy_week"],
        "score": patient["score"],
        "risk": patient["risk"],
        "symptoms": patient["symptoms"],
        "risk_factors": patient["risk_factors"],
        "required_response": patient["required_response"],
        "patient_message": patient["patient_message"],
        "status": patient["status"],
        "completed": patient["completed"],
        "updated_at": patient["updated_at"],
        "answers": patient["answers"],
    }

def parse_yes_no_number(text: str):
    if text.strip() == "1":
        return True
    if text.strip() == "2":
        return False
    return None

def parse_age(text: str):
    cleaned = text.strip()
    if not cleaned.isdigit():
        return None
    age = int(cleaned)
    if 10 <= age <= 60:
        return age
    return None

def parse_week(text: str):
    cleaned = text.strip()
    if not cleaned.isdigit():
        return None
    week = int(cleaned)
    if 0 <= week <= 45:
        return week
    return None

def next_question_after(qid: str):
    idx = QUESTION_SEQUENCE.index(qid)
    return QUESTION_SEQUENCE[idx + 1] if idx + 1 < len(QUESTION_SEQUENCE) else None

def update_risk(patient: dict):
    patient["risk"] = risk_from_score(patient["score"])
    patient["required_response"] = required_response_from_risk(patient["risk"])
    patient["patient_message"] = patient_message_from_risk(patient["risk"])

def restart_assessment(patient: dict):
    patient["status"] = "registering_age"
    patient["current_question"] = "registration_age"
    patient["score"] = 0
    patient["risk"] = "green"
    patient["required_response"] = "Routine monitoring"
    patient["patient_message"] = None
    patient["symptoms"] = []
    patient["risk_factors"] = []
    patient["answers"] = {}
    patient["completed"] = False
    patient["updated_at"] = now_iso()

def apply_question_answer(patient: dict, qid: str, yes: bool):
    patient["answers"][qid] = yes

    if yes:
        patient["score"] += QUESTION_POINTS[qid]
        label = QUESTION_LABELS[qid]
        if qid in {"q1", "q2", "q3", "q4", "q5", "q6", "q7"}:
            patient["symptoms"].append(label)
        else:
            patient["risk_factors"].append(label)

    update_risk(patient)

def complete_assessment(patient: dict):
    patient["completed"] = True
    patient["status"] = "completed"
    patient["current_question"] = None
    patient["updated_at"] = now_iso()
    update_risk(patient)

def process_message(patient: dict, incoming_text: str) -> str:
    text = normalise_text(incoming_text)
    patient["last_message"] = incoming_text
    patient["updated_at"] = now_iso()

    if text == "delete me":
        delete_patient(patient["phone"])
        return "Your data has been removed from Aya. If you message again, a new record will be created."

    if text == "restart":
        restart_assessment(patient)
        return QUESTION_TEXT["registration_age"]

    if text == "status":
        if patient["completed"]:
            return patient["patient_message"]
        return "Your assessment is still in progress. Please continue answering the questions with numbers only."

    if patient["status"] == "registering_age":
        age = parse_age(text)
        if age is None:
            return "Please reply with your age using numbers only, for example: 24"
        patient["age"] = age
        patient["status"] = "registering_week"
        patient["current_question"] = "registration_week"
        patient["updated_at"] = now_iso()
        return QUESTION_TEXT["registration_week"]

    if patient["status"] == "registering_week":
        week = parse_week(text)
        if week is None:
            return "Please reply with your pregnancy week using numbers only. If unknown, reply 0."
        patient["pregnancy_week"] = None if week == 0 else week
        patient["status"] = "triage"
        patient["current_question"] = "q1"
        patient["updated_at"] = now_iso()
        return QUESTION_TEXT["q1"]

    if patient["completed"]:
        return patient["patient_message"] + "\n\nReply RESTART for a new assessment or DELETE ME to remove your data."

    if patient["status"] == "triage":
        qid = patient["current_question"]
        yes = parse_yes_no_number(text)
        if yes is None:
            return "Please reply with 1 for Yes or 2 for No."

        apply_question_answer(patient, qid, yes)

        if qid == "q1" and yes:
            complete_assessment(patient)
            patient["risk"] = "red"
            patient["score"] = max(patient["score"], 5)
            patient["required_response"] = "Emergency pickup"
            patient["patient_message"] = (
                "Aya has flagged your assessment as urgent. "
                "Please go to the nearest hospital or dial your local emergency number now. "
                "A clinic has also been alerted."
            )
            return patient["patient_message"]

        if patient["score"] >= 5:
            complete_assessment(patient)
            return patient["patient_message"]

        next_q = next_question_after(qid)
        if next_q is None:
            complete_assessment(patient)
            return patient["patient_message"]

        patient["current_question"] = next_q
        patient["updated_at"] = now_iso()
        return QUESTION_TEXT[next_q]

    return "Something went wrong. Reply RESTART to begin again."

# ---------------------------------
# Demo HTML: patient phone simulator
# ---------------------------------
DEMO_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Aya - Antenatal Companion</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f5f2fb;
            margin: 0;
            padding: 24px;
            display: flex;
            justify-content: center;
        }
        .page {
            display: flex;
            gap: 24px;
            flex-wrap: wrap;
            align-items: flex-start;
        }
        .phone {
            width: 370px;
            background: #fff;
            border-radius: 28px;
            border: 8px solid #222;
            overflow: hidden;
            box-shadow: 0 12px 32px rgba(0,0,0,0.14);
        }
        .header {
            background: #6d35b1;
            color: white;
            padding: 16px;
            text-align: center;
            font-weight: bold;
        }
        .chat {
            height: 520px;
            overflow-y: auto;
            background: #f7f7fb;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .bubble {
            max-width: 80%;
            padding: 10px 14px;
            border-radius: 18px;
            line-height: 1.4;
            font-size: 14px;
            white-space: pre-wrap;
        }
        .bot {
            align-self: flex-start;
            background: #ffffff;
            border: 1px solid #ddd;
        }
        .user {
            align-self: flex-end;
            background: #ddd0f4;
        }
        .input-row {
            display: flex;
            gap: 8px;
            padding: 12px;
            border-top: 1px solid #ddd;
        }
        .input-row input {
            flex: 1;
            padding: 12px;
            border-radius: 12px;
            border: 1px solid #ccc;
            font-size: 14px;
        }
        .input-row button, .controls button {
            padding: 12px 14px;
            border-radius: 12px;
            border: none;
            background: #6d35b1;
            color: white;
            cursor: pointer;
            font-weight: bold;
        }
        .panel {
            width: 390px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 12px 32px rgba(0,0,0,0.14);
            padding: 20px;
        }
        .panel h3 {
            margin-top: 0;
        }
        .state {
            margin-top: 16px;
            padding: 14px;
            border-radius: 12px;
            background: #f5f2fb;
            line-height: 1.6;
            font-size: 14px;
        }
        .controls input {
            width: 100%;
            box-sizing: border-box;
            padding: 10px;
            margin: 6px 0 10px;
            border-radius: 10px;
            border: 1px solid #ccc;
        }
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 999px;
            background: #eee;
            font-size: 12px;
            margin: 4px 4px 0 0;
        }
    </style>
</head>
<body>
    <div class="page">
        <div class="phone">
            <div class="header">Aya - Antenatal Companion</div>
            <div id="chat" class="chat">
                <div class="bubble bot">Welcome to Aya. Reply with your age in numbers only to begin.</div>
            </div>
            <div class="input-row">
                <input id="messageInput" type="text" placeholder="Type message..." />
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>

        <div class="panel">
            <h3>Simulation Controls</h3>
            <div class="controls">
                <label><strong>Patient phone number</strong></label>
                <input id="phoneInput" type="text" value="+447700900123" />
                <button onclick="quickSend('24')">Send age 24</button>
                <button onclick="quickSend('30')">Send week 30</button>
                <button onclick="quickSend('1')">Send 1</button>
                <button onclick="quickSend('2')">Send 2</button>
                <button onclick="quickSend('restart')">Restart</button>
                <button onclick="quickSend('delete me')">Delete Me</button>
            </div>
            <div id="state" class="state">No patient state loaded yet.</div>
        </div>
    </div>

    <script>
        function addBubble(text, cls) {
            const chat = document.getElementById("chat");
            const bubble = document.createElement("div");
            bubble.className = "bubble " + cls;
            bubble.textContent = text;
            chat.appendChild(bubble);
            chat.scrollTop = chat.scrollHeight;
        }

        function renderState(patient) {
            const state = document.getElementById("state");
            if (!patient) {
                state.innerHTML = "Patient not found.";
                return;
            }

            const symptoms = (patient.symptoms || []).map(s => `<span class="badge">${s}</span>`).join("");
            const riskFactors = (patient.risk_factors || []).map(s => `<span class="badge">${s}</span>`).join("");

            state.innerHTML = `
                <strong>Phone:</strong> ${patient.phone}<br>
                <strong>Age:</strong> ${patient.age ?? "Not set"}<br>
                <strong>Pregnancy week:</strong> ${patient.pregnancy_week ?? "Unknown"}<br>
                <strong>Status:</strong> ${patient.status}<br>
                <strong>Current question:</strong> ${patient.current_question ?? "None"}<br>
                <strong>Score:</strong> ${patient.score}<br>
                <strong>Risk:</strong> ${patient.risk.toUpperCase()}<br>
                <strong>Required response:</strong> ${patient.required_response}<br><br>
                <strong>Symptoms:</strong><br>${symptoms || "None"}<br><br>
                <strong>Risk factors:</strong><br>${riskFactors || "None"}
            `;
        }

        async function sendMessage(customText = null) {
            const phone = document.getElementById("phoneInput").value.trim();
            const input = document.getElementById("messageInput");
            const text = customText || input.value.trim();

            if (!text) return;

            addBubble(text, "user");
            input.value = "";

            const response = await fetch("/simulate-sms", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({ phone: phone, body: text })
            });

            const data = await response.json();
            addBubble(data.reply, "bot");
            renderState(data.patient);
        }

        function quickSend(text) {
            sendMessage(text);
        }

        document.getElementById("messageInput").addEventListener("keypress", function(e) {
            if (e.key === "Enter") sendMessage();
        });
    </script>
</body>
</html>
"""

# ---------------------------------
# Simple built-in clinic dashboard
# Your friend can replace this later
# ---------------------------------
CLINIC_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Aya Clinic Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>
        body { font-family: Arial, sans-serif; margin: 0; background: #f7f7fb; }
        .wrap { max-width: 1200px; margin: 0 auto; padding: 24px; }
        h1 { margin-bottom: 8px; }
        .sub { color: #555; margin-bottom: 20px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }
        .card {
            background: white; border-radius: 16px; padding: 16px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.08);
        }
        .red { border-left: 6px solid #d62828; }
        .yellow { border-left: 6px solid #e9b100; }
        .green { border-left: 6px solid #2a9d55; }
        .pill {
            display: inline-block; padding: 4px 8px; border-radius: 999px;
            background: #eee; font-size: 12px; margin: 4px 4px 0 0;
        }
        .muted { color: #555; font-size: 14px; }
        button {
            background: #6d35b1; color: white; border: none; border-radius: 10px;
            padding: 10px 14px; cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="wrap">
        <h1>Aya Clinic Dashboard</h1>
        <div class="sub">View-only clinic dashboard showing patients, risk, symptoms, and required response.</div>
        <button onclick="loadPatients()">Refresh</button>
        <div style="height:16px;"></div>
        <div id="grid" class="grid"></div>
    </div>

    <script>
        function cardClass(risk) {
            if (risk === "red") return "card red";
            if (risk === "yellow") return "card yellow";
            return "card green";
        }

        function pillList(items) {
            if (!items || items.length === 0) return "None";
            return items.map(x => `<span class="pill">${x}</span>`).join("");
        }

        async function loadPatients() {
            const res = await fetch("/api/patients");
            const data = await res.json();
            const grid = document.getElementById("grid");

            if (!data.patients || data.patients.length === 0) {
                grid.innerHTML = '<div class="card">No patients yet.</div>';
                return;
            }

            grid.innerHTML = data.patients.map(p => `
                <div class="${cardClass(p.risk)}">
                    <h3>${(p.risk || "").toUpperCase()} risk</h3>
                    <div><strong>Phone:</strong> ${p.phone}</div>
                    <div><strong>Age:</strong> ${p.age ?? "Not set"}</div>
                    <div><strong>Pregnancy week:</strong> ${p.pregnancy_week ?? "Unknown"}</div>
                    <div><strong>Score:</strong> ${p.score}</div>
                    <div><strong>Required response:</strong> ${p.required_response}</div>
                    <div><strong>Status:</strong> ${p.status}</div>
                    <div class="muted"><strong>Updated:</strong> ${p.updated_at}</div>
                    <div style="margin-top:10px;"><strong>Symptoms:</strong><br>${pillList(p.symptoms)}</div>
                    <div style="margin-top:10px;"><strong>Risk factors:</strong><br>${pillList(p.risk_factors)}</div>
                </div>
            `).join("");
        }

        loadPatients();
    </script>
</body>
</html>
"""

# ---------------------------------
# Routes
# ---------------------------------
@app.route("/")
def home():
    return (
        f"{APP_NAME} ({APP_SUBTITLE}) server is live.<br>"
        "Available routes:<br>"
        "/demo - patient phone simulation<br>"
        "/clinic-dashboard - clinic-facing dashboard<br>"
        "/api/patients - patient JSON for clinic dashboard<br>"
        "/api/patient/&lt;phone&gt; - single patient JSON<br>"
        "/sms - Twilio webhook<br>"
        "/health - health check"
    )

@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "app": APP_NAME,
        "subtitle": APP_SUBTITLE,
        "patient_count": len(patients),
        "time": now_iso(),
    })

@app.route("/demo")
def demo():
    return render_template_string(DEMO_HTML)

@app.route("/clinic-dashboard")
def clinic_dashboard():
    return render_template_string(CLINIC_HTML)

@app.route("/api/patients")
def api_patients():
    rows = [clinic_row(p) for p in patients.values()]
    risk_order = {"red": 0, "yellow": 1, "green": 2}
    rows.sort(key=lambda x: (risk_order.get(x["risk"], 3), x["updated_at"]))
    return jsonify({
        "app": APP_NAME,
        "patient_count": len(rows),
        "patients": rows,
    })

@app.route("/api/patient/<path:phone>")
def api_patient(phone):
    phone_key = phone if phone.startswith("+") else f"+{phone}" if phone.isdigit() else phone
    patient = patients.get(phone_key)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
    return jsonify(clinic_row(patient))

@app.route("/simulate-sms", methods=["POST"])
def simulate_sms():
    data = request.get_json() or {}
    phone = str(data.get("phone", "+447700900123"))
    body = str(data.get("body", ""))

    patient = patients.get(phone) or create_patient(phone)
    reply = process_message(patient, body)
    current_patient = patients.get(phone)

    return jsonify({
        "reply": reply,
        "patient": clinic_row(current_patient) if current_patient else None
    })

@app.route("/sms", methods=["POST"])
def sms_reply():
    incoming_msg = request.form.get("Body", "")
    from_number = request.form.get("From", "unknown")

    patient = get_or_create_patient(from_number)
    reply = process_message(patient, incoming_msg)

    print("From:", from_number)
    print("Received:", incoming_msg)
    print("Reply:", reply)

    return twiml_message(reply)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)