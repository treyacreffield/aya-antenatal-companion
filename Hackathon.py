from flask import Flask, request, Response, jsonify, render_template_string
from datetime import datetime, timedelta

app = Flask(__name__)

APP_NAME = "Aya"
APP_SUBTITLE = "Antenatal Companion"

# ---------------------------------
# In-memory patient store
# ---------------------------------
patients = {}

# ---------------------------------
# Language config
# Demo translations - should be reviewed by native speakers for production use
# ---------------------------------
LANGUAGES = {
    "1": "en",
    "2": "pidgin",
    "3": "ha",
    "4": "yo",
    "5": "ig",
}

LANGUAGE_NAMES = {
    "en": "English",
    "pidgin": "Pidgin",
    "ha": "Hausa",
    "yo": "Yoruba",
    "ig": "Igbo",
}

TEXT = {
    "en": {
        "language_prompt": (
            "Welcome to Aya.\n"
            "Choose your language:\n"
            "1. English\n"
            "2. Pidgin\n"
            "3. Hausa\n"
            "4. Yoruba\n"
            "5. Igbo"
        ),
        "language_invalid": "Please reply with 1, 2, 3, 4, or 5 to choose a language.",
        "registration_age": "Please reply with your age in years using numbers only.",
        "registration_week": "Please reply with your pregnancy week using numbers only. If you do not know, reply 0.",
        "invalid_age": "Please reply with your age using numbers only, for example: 24",
        "invalid_week": "Please reply with your pregnancy week using numbers only. If unknown, reply 0.",
        "invalid_yes_no": "Please reply with 1 for Yes or 2 for No.",
        "deleted": "Your data has been removed from Aya. If you message again, a new record will be created.",
        "status_incomplete": "Your assessment is still in progress. Please continue answering the questions with numbers only.",
        "q1": (
            "Q1. Are you experiencing any of these danger signs: heavy bleeding, fits/seizures, or blurred vision?\n"
            "Reply:\n1. Yes\n2. No"
        ),
        "q2": "Q2. Are you having a severe constant headache?\nReply:\n1. Yes\n2. No",
        "q3": "Q3. Do you have fever or chills?\nReply:\n1. Yes\n2. No",
        "q4": "Q4. Is water leaking or has your fluid broken?\nReply:\n1. Yes\n2. No",
        "q5": "Q5. Have you noticed reduced fetal movement?\nReply:\n1. Yes\n2. No",
        "q6": "Q6. Do you have itchy hands or feet?\nReply:\n1. Yes\n2. No",
        "q7": "Q7. Do you have severe pelvic or abdominal pain?\nReply:\n1. Yes\n2. No",
        "q8": "Q8. Have you previously had pre-eclampsia or stillbirth?\nReply:\n1. Yes\n2. No",
        "q9": "Q9. Do you have a history of hypertension (high blood pressure)?\nReply:\n1. Yes\n2. No",
        "q10": "Q10. Do you have a history of diabetes?\nReply:\n1. Yes\n2. No",
        "q11": "Q11. Are you younger than 18 or older than 35?\nReply:\n1. Yes\n2. No",
        "patient_red": (
            "Aya has flagged your assessment as urgent. Please go to the nearest hospital or dial your local emergency number now. "
            "A clinic has also been alerted."
        ),
        "patient_yellow": (
            "Aya has completed your assessment. A clinic will phone you soon to follow up. "
            "If your symptoms worsen before then, go to the nearest hospital."
        ),
        "patient_green": (
            "Aya has completed your assessment. You can continue routine antenatal care and monitor for new symptoms. "
            "If new warning signs appear, seek medical help."
        ),
        "reassess_prompt": "Reply HELP at any time to take another assessment.",
        "next_due": "Your next routine assessment is due on {date}.",
        "help_complete": "Reply HELP to start a new assessment.",
        "location_saved": "Your location has been shared with the clinic.",
        "location_failed": "Aya could not save your location.",
    },
    "pidgin": {
        "language_prompt": (
            "Welcome to Aya.\n"
            "Choose your language:\n"
            "1. English\n"
            "2. Pidgin\n"
            "3. Hausa\n"
            "4. Yoruba\n"
            "5. Igbo"
        ),
        "language_invalid": "Abeg reply 1, 2, 3, 4, or 5 to choose language.",
        "registration_age": "Abeg reply your age for years with number only.",
        "registration_week": "Abeg reply your pregnancy week with number only. If you no know am, reply 0.",
        "invalid_age": "Abeg reply your age with number only, example: 24",
        "invalid_week": "Abeg reply your pregnancy week with number only. If you no know am, reply 0.",
        "invalid_yes_no": "Abeg reply 1 for Yes or 2 for No.",
        "deleted": "Aya don remove your data. If you message again, we go create new record.",
        "status_incomplete": "Your assessment still dey go on. Abeg continue to answer with number only.",
        "q1": "Q1. You dey get any danger sign like heavy bleeding, fits/seizures, or blurred vision?\nReply:\n1. Yes\n2. No",
        "q2": "Q2. You get strong constant headache?\nReply:\n1. Yes\n2. No",
        "q3": "Q3. You get fever or chills?\nReply:\n1. Yes\n2. No",
        "q4": "Q4. Water dey leak or your fluid don break?\nReply:\n1. Yes\n2. No",
        "q5": "Q5. You notice reduced fetal movement?\nReply:\n1. Yes\n2. No",
        "q6": "Q6. Your hands or feet dey itch?\nReply:\n1. Yes\n2. No",
        "q7": "Q7. You get serious pelvic or abdominal pain?\nReply:\n1. Yes\n2. No",
        "q8": "Q8. You don get pre-eclampsia or stillbirth before?\nReply:\n1. Yes\n2. No",
        "q9": "Q9. You get history of hypertension/high blood pressure?\nReply:\n1. Yes\n2. No",
        "q10": "Q10. You get history of diabetes?\nReply:\n1. Yes\n2. No",
        "q11": "Q11. You dey under 18 or over 35?\nReply:\n1. Yes\n2. No",
        "patient_red": "Aya don flag your assessment as urgent. Abeg go nearest hospital or call emergency number now. Clinic don receive alert too.",
        "patient_yellow": "Aya don complete your assessment. Clinic go call you soon. If your symptoms worsen before then, go nearest hospital.",
        "patient_green": "Aya don complete your assessment. Continue routine antenatal care and watch for new symptoms. If warning signs show, look for medical help.",
        "reassess_prompt": "Reply HELP anytime to take another assessment.",
        "next_due": "Your next routine assessment dey due on {date}.",
        "help_complete": "Reply HELP to start another assessment.",
        "location_saved": "Clinic don receive your location.",
        "location_failed": "Aya no fit save your location.",
    },
    "ha": {
        "language_prompt": (
            "Barka da zuwa Aya.\n"
            "Zaɓi harshe:\n"
            "1. English\n"
            "2. Pidgin\n"
            "3. Hausa\n"
            "4. Yoruba\n"
            "5. Igbo"
        ),
        "language_invalid": "Da fatan a amsa da 1, 2, 3, 4, ko 5 domin zaɓar harshe.",
        "registration_age": "Da fatan a turo shekarunki da lambobi kaɗai.",
        "registration_week": "Da fatan a turo makon ciki da lambobi kaɗai. Idan ba ki sani ba, ki turo 0.",
        "invalid_age": "Da fatan a turo shekarunki da lambobi kaɗai, misali: 24",
        "invalid_week": "Da fatan a turo makon ciki da lambobi kaɗai. Idan ba ki sani ba, ki turo 0.",
        "invalid_yes_no": "Da fatan a amsa da 1 don Eh ko 2 don A'a.",
        "deleted": "An cire bayananki daga Aya. Idan kika sake yin saƙo, za a ƙirƙiri sabon bayaninki.",
        "status_incomplete": "Tantancewarki na gudana. Da fatan ki ci gaba da amsawa da lambobi kaɗai.",
        "q1": "Q1. Kina da wata alamar haɗari kamar zubar jini mai yawa, farfaɗiya, ko gani ya dusashe?\nAmsa:\n1. Eh\n2. A'a",
        "q2": "Q2. Kina da matsanancin ciwon kai mai dorewa?\nAmsa:\n1. Eh\n2. A'a",
        "q3": "Q3. Kina da zazzabi ko sanyi?\nAmsa:\n1. Eh\n2. A'a",
        "q4": "Q4. Ruwa na fita ko ruwan ciki ya fashe?\nAmsa:\n1. Eh\n2. A'a",
        "q5": "Q5. Kin lura motsin jariri ya ragu?\nAmsa:\n1. Eh\n2. A'a",
        "q6": "Q6. Hannaye ko ƙafafunki na kaikayi?\nAmsa:\n1. Eh\n2. A'a",
        "q7": "Q7. Kina da matsanancin ciwon ƙugu ko ciki?\nAmsa:\n1. Eh\n2. A'a",
        "q8": "Q8. Kina da tarihin pre-eclampsia ko haihuwar gawa?\nAmsa:\n1. Eh\n2. A'a",
        "q9": "Q9. Kina da tarihin hawan jini?\nAmsa:\n1. Eh\n2. A'a",
        "q10": "Q10. Kina da tarihin ciwon sukari?\nAmsa:\n1. Eh\n2. A'a",
        "q11": "Q11. Shekarunki kasa da 18 ne ko sama da 35?\nAmsa:\n1. Eh\n2. A'a",
        "patient_red": "Aya ta gano gaggawa. Ki je asibiti mafi kusa ko ki kira lambar gaggawa yanzu. An kuma sanar da asibitin yankinku.",
        "patient_yellow": "Aya ta kammala tantancewa. Asibiti zai kira ki nan ba da jimawa ba. Idan alamunki suka tsananta kafin lokacin, ki je asibiti mafi kusa.",
        "patient_green": "Aya ta kammala tantancewa. Ki ci gaba da kula da ciki kamar kullum kuma ki lura da sababbin alamomi. Idan alamar haɗari ta bayyana, ki nemi taimakon lafiya.",
        "reassess_prompt": "A turo HELP a kowane lokaci don sake yin tantancewa.",
        "next_due": "Lokacin tantancewa ta gaba zai yi ranar {date}.",
        "help_complete": "A turo HELP don fara sabon tantancewa.",
        "location_saved": "An aika wurin da kike zuwa asibiti.",
        "location_failed": "Aya ba ta iya adana wurin da kike ba.",
    },
    "yo": {
        "language_prompt": (
            "Kaabo si Aya.\n"
            "Yan ede re:\n"
            "1. English\n"
            "2. Pidgin\n"
            "3. Hausa\n"
            "4. Yoruba\n"
            "5. Igbo"
        ),
        "language_invalid": "Jowo fi 1, 2, 3, 4, tabi 5 ranse lati yan ede.",
        "registration_age": "Jowo fi ori re ranse pelu nomba nikan.",
        "registration_week": "Jowo fi ose oyun re ranse pelu nomba nikan. Ti o ko ba mo, fi 0 ranse.",
        "invalid_age": "Jowo fi ori re ranse pelu nomba nikan, apere: 24",
        "invalid_week": "Jowo fi ose oyun re ranse pelu nomba nikan. Ti o ko ba mo, fi 0 ranse.",
        "invalid_yes_no": "Jowo fi 1 fun Beni tabi 2 fun Beeko.",
        "deleted": "A ti pa data re nu kuro ninu Aya. Ti o ba tun fi ifiranse ranse, a o da akosile tuntun sile.",
        "status_incomplete": "Ayewo re n lo lowo. Jowo tesiwaju lati dahun pelu nomba nikan.",
        "q1": "Q1. Se o n ni eyikeyi awon ami ewu wonyi: eje pupo, seizure, tabi iran to dinku?\nDahun:\n1. Beni\n2. Beeko",
        "q2": "Q2. Se o n ni efori to lagbara ti ko n lo?\nDahun:\n1. Beni\n2. Beeko",
        "q3": "Q3. Se o ni iba tabi otutu inu ara?\nDahun:\n1. Beni\n2. Beeko",
        "q4": "Q4. Se omi n jo tabi fluid re ti fo?\nDahun:\n1. Beni\n2. Beeko",
        "q5": "Q5. Se o ti se akiyesi pe gbigbe omo inu dinku?\nDahun:\n1. Beni\n2. Beeko",
        "q6": "Q6. Se owo tabi ese re n yun?\nDahun:\n1. Beni\n2. Beeko",
        "q7": "Q7. Se o n ni irora nla ni ikun tabi ibadi?\nDahun:\n1. Beni\n2. Beeko",
        "q8": "Q8. Se o ti ni pre-eclampsia tabi stillbirth tele?\nDahun:\n1. Beni\n2. Beeko",
        "q9": "Q9. Se o ni itan hypertension/tabi high blood pressure?\nDahun:\n1. Beni\n2. Beeko",
        "q10": "Q10. Se o ni itan diabetes?\nDahun:\n1. Beni\n2. Beeko",
        "q11": "Q11. Se ori re kere ju 18 tabi ju 35 lo?\nDahun:\n1. Beni\n2. Beeko",
        "patient_red": "Aya ti fi ayewo re han gege bi pajawiri. Jowo lo si ile-iwosan to sunmo re tabi pe nomba emergency bayii. A tun ti kilo fun ile-iwosan agbegbe re.",
        "patient_yellow": "Aya ti pari ayewo re. Ile-iwosan yoo pe e laipe. Ti aami aisan ba buru si, lo si ile-iwosan to sunmo re.",
        "patient_green": "Aya ti pari ayewo re. O le tesiwaju pelu itoju oyun deede ki o si maa wo awon aami tuntun. Ti aami ewu ba farahan, wa iranlowo ilera.",
        "reassess_prompt": "Fi HELP ranse nigbakugba lati tun se ayewo.",
        "next_due": "Ayewo deede to tele ye ni ojo {date}.",
        "help_complete": "Fi HELP ranse lati bere ayewo tuntun.",
        "location_saved": "A ti fi ipo re ranse si ile-iwosan.",
        "location_failed": "Aya ko le fi ipo re pamọ.",
    },
    "ig": {
        "language_prompt": (
            "Nnọọ na Aya.\n"
            "Họrọ asụsụ gị:\n"
            "1. English\n"
            "2. Pidgin\n"
            "3. Hausa\n"
            "4. Yoruba\n"
            "5. Igbo"
        ),
        "language_invalid": "Biko zaa 1, 2, 3, 4, ma ọ bụ 5 iji họrọ asụsụ.",
        "registration_age": "Biko ziga afọ gị site na nọmba naanị.",
        "registration_week": "Biko ziga izu ime gị site na nọmba naanị. Ọ bụrụ na ị maghị, ziga 0.",
        "invalid_age": "Biko ziga afọ gị site na nọmba naanị, dịka: 24",
        "invalid_week": "Biko ziga izu ime gị site na nọmba naanị. Ọ bụrụ na ị maghị, ziga 0.",
        "invalid_yes_no": "Biko zaa 1 maka Ee ma ọ bụ 2 maka Mba.",
        "deleted": "E wepụrụ data gị na Aya. Ọ bụrụ na ị ziga ozi ọzọ, a ga-emepụta ndekọ ọhụrụ.",
        "status_incomplete": "Nyocha gị ka na-aga. Biko gaa n'ihu na-aza site na nọmba naanị.",
        "q1": "Q1. Ị na-enwe otu n'ime ihe ize ndụ ndị a: ọbara ọgbụgba ukwuu, seizure, ma ọ bụ anya na-adịghị ahụ nke ọma?\nZaa:\n1. Ee\n2. Mba",
        "q2": "Q2. Ị na-enwe isi ọwụwa siri ike na-adịgide?\nZaa:\n1. Ee\n2. Mba",
        "q3": "Q3. Ị nwere fever ma ọ bụ chills?\nZaa:\n1. Ee\n2. Mba",
        "q4": "Q4. Mmiri na-apụta ma ọ bụ fluid agbajiela?\nZaa:\n1. Ee\n2. Mba",
        "q5": "Q5. Ị chọpụtara na mmegharị nwa ebu n’afọ belatara?\nZaa:\n1. Ee\n2. Mba",
        "q6": "Q6. Aka ma ọ bụ ụkwụ gị na-akọwa?\nZaa:\n1. Ee\n2. Mba",
        "q7": "Q7. Ị na-enwe mgbu siri ike n’afọ ma ọ bụ n’akụkụ ikpere/ukwu?\nZaa:\n1. Ee\n2. Mba",
        "q8": "Q8. Ị nwere akụkọ pre-eclampsia ma ọ bụ stillbirth tupu a?\nZaa:\n1. Ee\n2. Mba",
        "q9": "Q9. Ị nwere akụkọ hypertension / high blood pressure?\nZaa:\n1. Ee\n2. Mba",
        "q10": "Q10. Ị nwere akụkọ diabetes?\nZaa:\n1. Ee\n2. Mba",
        "q11": "Q11. Afọ gị dị n'okpuru 18 ma ọ bụ karịa 35?\nZaa:\n1. Ee\n2. Mba",
        "patient_red": "Aya achọpụtala na ọnọdụ a dị ngwa. Biko gaa ụlọ ọgwụ kacha nso ma ọ bụ kpọọ nọmba mberede ugbu a. A gwala ụlọ ọgwụ mpaghara gị kwa.",
        "patient_yellow": "Aya emechala nyocha gị. Ụlọ ọgwụ ga-akpọ gị n’oge na-adịghị anya. Ọ bụrụ na mgbaàmà gị ka njọ tupu ahụ, gaa ụlọ ọgwụ kacha nso.",
        "patient_green": "Aya emechala nyocha gị. Ị nwere ike ịga n’ihu na nlekọta ime nkịtị ma leba anya na mgbaàmà ọhụrụ. Ọ bụrụ na ihe ize ndụ pụta, chọọ enyemaka ahụike.",
        "reassess_prompt": "Zipu HELP oge ọ bụla iji mee nyocha ọzọ.",
        "next_due": "Nyocha nkịtị na-esote gị ga-abụ na {date}.",
        "help_complete": "Zipu HELP iji malite nyocha ọhụrụ.",
        "location_saved": "Ekesara ụlọ ọgwụ ọnọdụ gị.",
        "location_failed": "Aya enweghị ike ịchekwa ọnọdụ gị.",
    },
}

QUESTION_SEQUENCE = ["q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "q10", "q11"]

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

def format_due_date(dt_str):
    if not dt_str:
        return "Not set"
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime("%d %b %Y")
    except Exception:
        return dt_str

def tr(patient, key, **kwargs):
    lang = patient.get("language", "en")
    template = TEXT.get(lang, TEXT["en"]).get(key, TEXT["en"].get(key, key))
    return template.format(**kwargs)

def qtext(patient, qid):
    lang = patient.get("language", "en")
    return TEXT.get(lang, TEXT["en"]).get(qid, TEXT["en"][qid])

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

def patient_message_from_risk(patient, risk: str) -> str:
    if risk == "red":
        return tr(patient, "patient_red")
    if risk == "yellow":
        return tr(patient, "patient_yellow")
    return tr(patient, "patient_green")

def next_due_date():
    return (datetime.utcnow() + timedelta(days=14)).isoformat()

def create_patient(phone: str) -> dict:
    patient = {
        "phone": phone,
        "language": None,
        "age": None,
        "pregnancy_week": None,
        "status": "awaiting_language",
        "current_question": "language",
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
        "last_completed_at": None,
        "next_assessment_due": None,
        "location": None,
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
        "language": LANGUAGE_NAMES.get(patient.get("language"), "Not set"),
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
        "last_completed_at": patient["last_completed_at"],
        "next_assessment_due": patient["next_assessment_due"],
        "answers": patient["answers"],
        "location": patient["location"],
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
    patient["patient_message"] = patient_message_from_risk(patient, patient["risk"])

def restart_assessment(patient: dict, keep_registration=True):
    patient["status"] = "triage" if keep_registration and patient.get("language") and patient.get("age") is not None else "awaiting_language"
    patient["current_question"] = "q1" if patient["status"] == "triage" else "language"
    patient["score"] = 0
    patient["risk"] = "green"
    patient["required_response"] = "Routine monitoring"
    patient["patient_message"] = None
    patient["symptoms"] = []
    patient["risk_factors"] = []
    patient["answers"] = {}
    patient["completed"] = False
    patient["updated_at"] = now_iso()
    patient["location"] = None
    if not keep_registration:
        patient["language"] = None
        patient["age"] = None
        patient["pregnancy_week"] = None

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
    patient["last_completed_at"] = now_iso()
    patient["next_assessment_due"] = next_due_date()
    update_risk(patient)

def assessment_complete_reply(patient):
    due_text = tr(patient, "next_due", date=format_due_date(patient["next_assessment_due"]))
    return f"{patient['patient_message']}\n\n{due_text}\n{tr(patient, 'help_complete')}"

def patient_message_deleted(patient):
    lang = patient.get("language", "en") if patient else "en"
    return TEXT.get(lang, TEXT["en"]).get("deleted", TEXT["en"]["deleted"])

# ---------------------------------
# Main processing
# ---------------------------------
def process_message(patient: dict, incoming_text: str) -> str:
    text = normalise_text(incoming_text)
    patient["last_message"] = incoming_text
    patient["updated_at"] = now_iso()

    if text == "delete me":
        delete_patient(patient["phone"])
        return patient_message_deleted(patient)

    # first patient message triggers language prompt
    if patient["status"] == "awaiting_language" and patient["current_question"] == "language":
        if patient["language"] is None:
            if text in LANGUAGES:
                patient["language"] = LANGUAGES[text]
                patient["status"] = "registering_age"
                patient["current_question"] = "registration_age"
                patient["updated_at"] = now_iso()
                return tr(patient, "registration_age")
            return TEXT["en"]["language_prompt"]

    if text == "help":
        if patient.get("language") is None:
            patient["status"] = "awaiting_language"
            patient["current_question"] = "language"
            return TEXT["en"]["language_prompt"]

        if patient.get("age") is None:
            patient["status"] = "registering_age"
            patient["current_question"] = "registration_age"
            return tr(patient, "registration_age")

        if patient.get("pregnancy_week") is None and patient.get("status") == "registering_week":
            return tr(patient, "registration_week")

        restart_assessment(patient, keep_registration=True)
        return qtext(patient, "q1")

    if text == "restart":
        if patient.get("language") and patient.get("age") is not None:
            restart_assessment(patient, keep_registration=True)
            return qtext(patient, "q1")
        patient["status"] = "awaiting_language"
        patient["current_question"] = "language"
        return TEXT["en"]["language_prompt"]

    if text == "status":
        if patient["completed"]:
            return assessment_complete_reply(patient)
        return tr(patient, "status_incomplete")

    if patient["status"] == "awaiting_language":
        if text not in LANGUAGES:
            return TEXT["en"]["language_invalid"]
        patient["language"] = LANGUAGES[text]
        patient["status"] = "registering_age"
        patient["current_question"] = "registration_age"
        patient["updated_at"] = now_iso()
        return tr(patient, "registration_age")

    if patient["status"] == "registering_age":
        age = parse_age(text)
        if age is None:
            return tr(patient, "invalid_age")
        patient["age"] = age
        patient["status"] = "registering_week"
        patient["current_question"] = "registration_week"
        patient["updated_at"] = now_iso()
        return tr(patient, "registration_week")

    if patient["status"] == "registering_week":
        week = parse_week(text)
        if week is None:
            return tr(patient, "invalid_week")
        patient["pregnancy_week"] = None if week == 0 else week
        patient["status"] = "triage"
        patient["current_question"] = "q1"
        patient["updated_at"] = now_iso()
        return qtext(patient, "q1")

    if patient["completed"]:
        return assessment_complete_reply(patient)

    if patient["status"] == "triage":
        qid = patient["current_question"]
        yes = parse_yes_no_number(text)
        if yes is None:
            return tr(patient, "invalid_yes_no")

        apply_question_answer(patient, qid, yes)

        if qid == "q1" and yes:
            complete_assessment(patient)
            patient["risk"] = "red"
            patient["score"] = max(patient["score"], 5)
            patient["required_response"] = "Emergency pickup"
            patient["patient_message"] = patient_message_from_risk(patient, "red")
            return assessment_complete_reply(patient)

        if patient["score"] >= 5:
            complete_assessment(patient)
            return assessment_complete_reply(patient)

        next_q = next_question_after(qid)
        if next_q is None:
            complete_assessment(patient)
            return assessment_complete_reply(patient)

        patient["current_question"] = next_q
        patient["updated_at"] = now_iso()
        return qtext(patient, next_q)

    return "Something went wrong. Reply HELP to begin again."

# ---------------------------------
# Demo HTML
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
        .share-location {
            background: #d62828 !important;
            width: 100%;
        }
        .panel {
            width: 430px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 12px 32px rgba(0,0,0,0.14);
            padding: 20px;
        }
        .controls input {
            width: 100%;
            box-sizing: border-box;
            padding: 10px;
            margin: 6px 0 10px;
            border-radius: 10px;
            border: 1px solid #ccc;
        }
        .state {
            margin-top: 16px;
            padding: 14px;
            border-radius: 12px;
            background: #f5f2fb;
            line-height: 1.6;
            font-size: 14px;
        }
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 999px;
            background: #eee;
            font-size: 12px;
            margin: 4px 4px 0 0;
        }
        #locationBox {
            margin-top: 16px;
            display: none;
        }
        .muted {
            color: #666;
            font-size: 13px;
        }
    </style>
</head>
<body>
    <div class="page">
        <div class="phone">
            <div class="header">Aya - Antenatal Companion</div>
            <div id="chat" class="chat">
                <div class="bubble bot">Patient sends the first message to begin.</div>
            </div>
            <div class="input-row">
                <input id="messageInput" type="text" placeholder="Type message..." />
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>

        <div class="panel">
            <div class="controls">
                <label><strong>Patient phone number</strong></label>
                <input id="phoneInput" type="text" value="+447700900123" />
            </div>

            <div id="state" class="state">No patient state loaded yet.</div>

            <div id="locationBox">
                <button class="share-location" onclick="shareLocation()">Share Emergency Location</button>
                <div class="muted" style="margin-top:8px;">
                    This only appears for completed emergency cases.
                </div>
            </div>
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
            const locationBox = document.getElementById("locationBox");

            if (!patient) {
                state.innerHTML = "Patient not found.";
                locationBox.style.display = "none";
                return;
            }

            const symptoms = (patient.symptoms || []).map(s => `<span class="badge">${s}</span>`).join("");
            const riskFactors = (patient.risk_factors || []).map(s => `<span class="badge">${s}</span>`).join("");
            const location = patient.location
                ? `${patient.location.latitude}, ${patient.location.longitude} (${patient.location.timestamp})`
                : "Not shared";

            state.innerHTML = `
                <strong>Phone:</strong> ${patient.phone}<br>
                <strong>Language:</strong> ${patient.language ?? "Not set"}<br>
                <strong>Age:</strong> ${patient.age ?? "Not set"}<br>
                <strong>Pregnancy week:</strong> ${patient.pregnancy_week ?? "Unknown"}<br>
                <strong>Status:</strong> ${patient.status}<br>
                <strong>Current question:</strong> ${patient.current_question ?? "None"}<br>
                <strong>Score:</strong> ${patient.score}<br>
                <strong>Risk:</strong> ${patient.risk.toUpperCase()}<br>
                <strong>Required response:</strong> ${patient.required_response}<br>
                <strong>Next due:</strong> ${patient.next_assessment_due ?? "Not set"}<br>
                <strong>Location:</strong> ${location}<br><br>
                <strong>Symptoms:</strong><br>${symptoms || "None"}<br><br>
                <strong>Risk factors:</strong><br>${riskFactors || "None"}
            `;

            if (patient.risk === "red" && patient.completed) {
                locationBox.style.display = "block";
            } else {
                locationBox.style.display = "none";
            }
        }

        async function sendMessage() {
            const phone = document.getElementById("phoneInput").value.trim();
            const input = document.getElementById("messageInput");
            const text = input.value.trim();

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

        async function shareLocation() {
            const phone = document.getElementById("phoneInput").value.trim();

            if (!navigator.geolocation) {
                addBubble("This browser does not support location sharing.", "bot");
                return;
            }

            navigator.geolocation.getCurrentPosition(
                async (position) => {
                    const response = await fetch("/api/share-location", {
                        method: "POST",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify({
                            phone: phone,
                            latitude: position.coords.latitude,
                            longitude: position.coords.longitude
                        })
                    });

                    const data = await response.json();

                    if (data.message) {
                        addBubble(data.message, "bot");
                    } else if (data.error) {
                        addBubble(data.error, "bot");
                    }

                    renderState(data.patient || null);
                },
                () => {
                    addBubble("Location permission was denied or unavailable.", "bot");
                }
            );
        }

        document.getElementById("messageInput").addEventListener("keypress", function(e) {
            if (e.key === "Enter") sendMessage();
        });
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
        "/api/share-location - POST emergency location from simulation<br>"
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

@app.route("/api/share-location", methods=["POST"])
def api_share_location():
    data = request.get_json() or {}
    phone = str(data.get("phone", ""))
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    patient = patients.get(phone)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    if patient.get("risk") != "red" or not patient.get("completed"):
        return jsonify({
            "error": "Location sharing is only enabled for completed red-risk cases in the simulation."
        }), 400

    try:
        lat = float(latitude)
        lon = float(longitude)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid coordinates"}), 400

    patient["location"] = {
        "latitude": lat,
        "longitude": lon,
        "timestamp": now_iso(),
    }
    patient["updated_at"] = now_iso()

    return jsonify({
        "message": tr(patient, "location_saved"),
        "patient": clinic_row(patient),
    })

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
