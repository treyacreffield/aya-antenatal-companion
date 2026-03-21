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
# Community health workers
# ---------------------------------
community_workers = [
    {
        "name": "Nurse Adaeze",
        "zone": "Zone A",
        "city": "Lagos",
        "phone": "+2348012345601",
        "status": "Online",
    },
    {
        "name": "Midwife Kemi",
        "zone": "Zone B",
        "city": "Kano",
        "phone": "+2348012345602",
        "status": "Online",
    },
    {
        "name": "Dr. Emeka",
        "zone": "Zone C",
        "city": "Abuja",
        "phone": "+2348012345603",
        "status": "Busy",
    },
    {
        "name": "CHW Tola",
        "zone": "Zone A",
        "city": "Ibadan",
        "phone": "+2348012345604",
        "status": "Online",
    },
]

# ---------------------------------
# Language config
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
            "Choose your language by replying with a number only:\n"
            "1. English\n"
            "2. Pidgin\n"
            "3. Hausa\n"
            "4. Yoruba\n"
            "5. Igbo"
        ),
        "language_invalid": "Please reply with a number only: 1, 2, 3, 4, or 5.",
        "registration_age": "Please reply with your age in years using numbers only. Do not type words.",
        "registration_week": "Please reply with your pregnancy week using numbers only. If you do not know, reply 0. Do not type words.",
        "invalid_age": "Please reply with your age using numbers only, for example: 24",
        "invalid_week": "Please reply with your pregnancy week using numbers only. If unknown, reply 0.",
        "invalid_yes_no": "Please reply with numbers only: 1 for Yes or 2 for No.",
        "deleted": "Your data has been removed from Aya. If you message again, a new record will be created.",
        "status_incomplete": "Your assessment is still in progress. Please continue answering with numbers only.",
        "q1": (
            "Q1. Are you experiencing any of these danger signs: heavy bleeding, fits or seizures, or blurred vision?\n"
            "Reply with a number only:\n1. Yes\n2. No"
        ),
        "q2": "Q2. Are you having a severe constant headache?\nReply with a number only:\n1. Yes\n2. No",
        "q3": "Q3. Do you have fever or chills?\nReply with a number only:\n1. Yes\n2. No",
        "q4": "Q4. Is water leaking or has your fluid broken?\nReply with a number only:\n1. Yes\n2. No",
        "q5": "Q5. Have you noticed reduced fetal movement?\nReply with a number only:\n1. Yes\n2. No",
        "q6": "Q6. Do you have itchy hands or feet?\nReply with a number only:\n1. Yes\n2. No",
        "q7": "Q7. Do you have severe pelvic or abdominal pain?\nReply with a number only:\n1. Yes\n2. No",
        "q8": "Q8. Have you previously had pre-eclampsia or stillbirth?\nReply with a number only:\n1. Yes\n2. No",
        "q9": "Q9. Do you have a history of hypertension (high blood pressure)?\nReply with a number only:\n1. Yes\n2. No",
        "q10": "Q10. Do you have a history of diabetes?\nReply with a number only:\n1. Yes\n2. No",
        "q11": "Q11. Are you younger than 18 or older than 35?\nReply with a number only:\n1. Yes\n2. No",
        "patient_red": (
            "Aya has flagged your assessment as urgent. Dial 112 now for emergency help. "
            "A clinic has also been alerted."
        ),
        "patient_yellow": (
            "Aya has completed your assessment. A community health worker has been alerted and will phone you to assess your risk. "
            "If your symptoms get worse, reply HELP for a new assessment."
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
            "Choose your language by replying with number only:\n"
            "1. English\n"
            "2. Pidgin\n"
            "3. Hausa\n"
            "4. Yoruba\n"
            "5. Igbo"
        ),
        "language_invalid": "Abeg reply with number only: 1, 2, 3, 4, or 5.",
        "registration_age": "Abeg reply your age for years with number only. No type words.",
        "registration_week": "Abeg reply your pregnancy week with number only. If you no know am, reply 0. No type words.",
        "invalid_age": "Abeg reply your age with number only, example: 24",
        "invalid_week": "Abeg reply your pregnancy week with number only. If you no know am, reply 0.",
        "invalid_yes_no": "Abeg reply with number only: 1 for Yes or 2 for No.",
        "deleted": "Aya don remove your data. If you message again, we go create new record.",
        "status_incomplete": "Your assessment still dey go on. Abeg continue to answer with number only.",
        "q1": "Q1. You dey get any danger sign like heavy bleeding, fits or seizures, or blurred vision?\nReply with number only:\n1. Yes\n2. No",
        "q2": "Q2. You get strong constant headache?\nReply with number only:\n1. Yes\n2. No",
        "q3": "Q3. You get fever or chills?\nReply with number only:\n1. Yes\n2. No",
        "q4": "Q4. Water dey leak or your fluid don break?\nReply with number only:\n1. Yes\n2. No",
        "q5": "Q5. You notice reduced fetal movement?\nReply with number only:\n1. Yes\n2. No",
        "q6": "Q6. Your hands or feet dey itch?\nReply with number only:\n1. Yes\n2. No",
        "q7": "Q7. You get serious pelvic or abdominal pain?\nReply with number only:\n1. Yes\n2. No",
        "q8": "Q8. You don get pre-eclampsia or stillbirth before?\nReply with number only:\n1. Yes\n2. No",
        "q9": "Q9. You get history of hypertension or high blood pressure?\nReply with number only:\n1. Yes\n2. No",
        "q10": "Q10. You get history of diabetes?\nReply with number only:\n1. Yes\n2. No",
        "q11": "Q11. You dey under 18 or over 35?\nReply with number only:\n1. Yes\n2. No",
        "patient_red": "Aya don flag your assessment as urgent. Dial 112 now for emergency help. Clinic don receive alert too.",
        "patient_yellow": "Aya don complete your assessment. Community health worker don receive alert and dem go call you to assess your risk. If your symptoms worse, reply HELP for new assessment.",
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
            "Zaɓi harshe ta hanyar amsawa da lamba kawai:\n"
            "1. English\n"
            "2. Pidgin\n"
            "3. Hausa\n"
            "4. Yoruba\n"
            "5. Igbo"
        ),
        "language_invalid": "Da fatan a amsa da lamba kawai: 1, 2, 3, 4, ko 5.",
        "registration_age": "Da fatan a turo shekarunki da lambobi kaɗai. Kada ki rubuta kalmomi.",
        "registration_week": "Da fatan a turo makon ciki da lambobi kaɗai. Idan ba ki sani ba, ki turo 0. Kada ki rubuta kalmomi.",
        "invalid_age": "Da fatan a turo shekarunki da lambobi kaɗai, misali: 24",
        "invalid_week": "Da fatan a turo makon ciki da lambobi kaɗai. Idan ba ki sani ba, ki turo 0.",
        "invalid_yes_no": "Da fatan a amsa da lambobi kaɗai: 1 don Eh ko 2 don A'a.",
        "deleted": "An cire bayananki daga Aya. Idan kika sake yin saƙo, za a ƙirƙiri sabon bayaninki.",
        "status_incomplete": "Tantancewarki na gudana. Da fatan ki ci gaba da amsawa da lambobi kaɗai.",
        "q1": "Q1. Kina da wata alamar haɗari kamar zubar jini mai yawa, farfaɗiya, ko gani ya dusashe?\nAmsa da lamba kawai:\n1. Eh\n2. A'a",
        "q2": "Q2. Kina da matsanancin ciwon kai mai dorewa?\nAmsa da lamba kawai:\n1. Eh\n2. A'a",
        "q3": "Q3. Kina da zazzabi ko sanyi?\nAmsa da lamba kawai:\n1. Eh\n2. A'a",
        "q4": "Q4. Ruwa na fita ko ruwan ciki ya fashe?\nAmsa da lamba kawai:\n1. Eh\n2. A'a",
        "q5": "Q5. Kin lura motsin jariri ya ragu?\nAmsa da lamba kawai:\n1. Eh\n2. A'a",
        "q6": "Q6. Hannaye ko ƙafafunki na kaikayi?\nAmsa da lamba kawai:\n1. Eh\n2. A'a",
        "q7": "Q7. Kina da matsanancin ciwon ƙugu ko ciki?\nAmsa da lamba kawai:\n1. Eh\n2. A'a",
        "q8": "Q8. Kina da tarihin pre-eclampsia ko haihuwar gawa?\nAmsa da lamba kawai:\n1. Eh\n2. A'a",
        "q9": "Q9. Kina da tarihin hawan jini?\nAmsa da lamba kawai:\n1. Eh\n2. A'a",
        "q10": "Q10. Kina da tarihin ciwon sukari?\nAmsa da lamba kawai:\n1. Eh\n2. A'a",
        "q11": "Q11. Shekarunki kasa da 18 ne ko sama da 35?\nAmsa da lamba kawai:\n1. Eh\n2. A'a",
        "patient_red": "Aya ta gano gaggawa. Ki kira 112 yanzu don taimakon gaggawa. An kuma sanar da asibitin yankinku.",
        "patient_yellow": "Aya ta kammala tantancewa. An sanar da ma'aikaciyar lafiyar al'umma kuma za ta kira ki don tantance haɗarinki. Idan alamunki suka tsananta, ki turo HELP don sabon tantancewa.",
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
            "Yan ede re nipa fifi nomba nikan ranse:\n"
            "1. English\n"
            "2. Pidgin\n"
            "3. Hausa\n"
            "4. Yoruba\n"
            "5. Igbo"
        ),
        "language_invalid": "Jowo fi nomba nikan ranse: 1, 2, 3, 4, tabi 5.",
        "registration_age": "Jowo fi ori re ranse pelu nomba nikan. Ma ko oro.",
        "registration_week": "Jowo fi ose oyun re ranse pelu nomba nikan. Ti o ko ba mo, fi 0 ranse. Ma ko oro.",
        "invalid_age": "Jowo fi ori re ranse pelu nomba nikan, apere: 24",
        "invalid_week": "Jowo fi ose oyun re ranse pelu nomba nikan. Ti o ko ba mo, fi 0 ranse.",
        "invalid_yes_no": "Jowo fi nomba nikan ranse: 1 fun Beni tabi 2 fun Beeko.",
        "deleted": "A ti pa data re nu kuro ninu Aya. Ti o ba tun fi ifiranse ranse, a o da akosile tuntun sile.",
        "status_incomplete": "Ayewo re n lo lowo. Jowo tesiwaju lati dahun pelu nomba nikan.",
        "q1": "Q1. Se o n ni eyikeyi awon ami ewu wonyi: eje pupo, seizure, tabi iran to dinku?\nDahun pelu nomba nikan:\n1. Beni\n2. Beeko",
        "q2": "Q2. Se o n ni efori to lagbara ti ko n lo?\nDahun pelu nomba nikan:\n1. Beni\n2. Beeko",
        "q3": "Q3. Se o ni iba tabi otutu inu ara?\nDahun pelu nomba nikan:\n1. Beni\n2. Beeko",
        "q4": "Q4. Se omi n jo tabi fluid re ti fo?\nDahun pelu nomba nikan:\n1. Beni\n2. Beeko",
        "q5": "Q5. Se o ti se akiyesi pe gbigbe omo inu dinku?\nDahun pelu nomba nikan:\n1. Beni\n2. Beeko",
        "q6": "Q6. Se owo tabi ese re n yun?\nDahun pelu nomba nikan:\n1. Beni\n2. Beeko",
        "q7": "Q7. Se o n ni irora nla ni ikun tabi ibadi?\nDahun pelu nomba nikan:\n1. Beni\n2. Beeko",
        "q8": "Q8. Se o ti ni pre-eclampsia tabi stillbirth tele?\nDahun pelu nomba nikan:\n1. Beni\n2. Beeko",
        "q9": "Q9. Se o ni itan hypertension tabi high blood pressure?\nDahun pelu nomba nikan:\n1. Beni\n2. Beeko",
        "q10": "Q10. Se o ni itan diabetes?\nDahun pelu nomba nikan:\n1. Beni\n2. Beeko",
        "q11": "Q11. Se ori re kere ju 18 tabi ju 35 lo?\nDahun pelu nomba nikan:\n1. Beni\n2. Beeko",
        "patient_red": "Aya ti fi ayewo re han gege bi pajawiri. Jowo pe 112 bayii fun iranlowo pajawiri. A tun ti kilo fun ile-iwosan agbegbe re.",
        "patient_yellow": "Aya ti pari ayewo re. A ti fi to community health worker leti, won a si pe e lati se ayewo ewu kikun. Ti aami aisan ba buru si, fi HELP ranse fun ayewo tuntun.",
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
            "Họrọ asụsụ gị site n'iji nọmba naanị zaa:\n"
            "1. English\n"
            "2. Pidgin\n"
            "3. Hausa\n"
            "4. Yoruba\n"
            "5. Igbo"
        ),
        "language_invalid": "Biko zaa na nọmba naanị: 1, 2, 3, 4, ma ọ bụ 5.",
        "registration_age": "Biko ziga afọ gị site na nọmba naanị. Ederela okwu.",
        "registration_week": "Biko ziga izu ime gị site na nọmba naanị. Ọ bụrụ na ị maghị, ziga 0. Ederela okwu.",
        "invalid_age": "Biko ziga afọ gị site na nọmba naanị, dịka: 24",
        "invalid_week": "Biko ziga izu ime gị site na nọmba naanị. Ọ bụrụ na ị maghị, ziga 0.",
        "invalid_yes_no": "Biko zaa na nọmba naanị: 1 maka Ee ma ọ bụ 2 maka Mba.",
        "deleted": "E wepụrụ data gị na Aya. Ọ bụrụ na ị ziga ozi ọzọ, a ga-emepụta ndekọ ọhụrụ.",
        "status_incomplete": "Nyocha gị ka na-aga. Biko gaa n'ihu na-aza site na nọmba naanị.",
        "q1": "Q1. Ị na-enwe otu n'ime ihe ize ndụ ndị a: ọbara ọgbụgba ukwuu, seizure, ma ọ bụ anya na-adịghị ahụ nke ọma?\nZaa site na nọmba naanị:\n1. Ee\n2. Mba",
        "q2": "Q2. Ị na-enwe isi ọwụwa siri ike na-adịgide?\nZaa site na nọmba naanị:\n1. Ee\n2. Mba",
        "q3": "Q3. Ị nwere fever ma ọ bụ chills?\nZaa site na nọmba naanị:\n1. Ee\n2. Mba",
        "q4": "Q4. Mmiri na-apụta ma ọ bụ fluid agbajiela?\nZaa site na nọmba naanị:\n1. Ee\n2. Mba",
        "q5": "Q5. Ị chọpụtara na mmegharị nwa ebu n’afọ belatara?\nZaa site na nọmba naanị:\n1. Ee\n2. Mba",
        "q6": "Q6. Aka ma ọ bụ ụkwụ gị na-akọwa?\nZaa site na nọmba naanị:\n1. Ee\n2. Mba",
        "q7": "Q7. Ị na-enwe mgbu siri ike n’afọ ma ọ bụ n’akụkụ ikpere/ukwu?\nZaa site na nọmba naanị:\n1. Ee\n2. Mba",
        "q8": "Q8. Ị nwere akụkọ pre-eclampsia ma ọ bụ stillbirth tupu a?\nZaa site na nọmba naanị:\n1. Ee\n2. Mba",
        "q9": "Q9. Ị nwere akụkọ hypertension ma ọ bụ high blood pressure?\nZaa site na nọmba naanị:\n1. Ee\n2. Mba",
        "q10": "Q10. Ị nwere akụkọ diabetes?\nZaa site na nọmba naanị:\n1. Ee\n2. Mba",
        "q11": "Q11. Afọ gị dị n'okpuru 18 ma ọ bụ karịa 35?\nZaa site na nọmba naanị:\n1. Ee\n2. Mba",
        "patient_red": "Aya achọpụtala na ọnọdụ a dị ngwa. Biko kpọọ 112 ugbu a maka enyemaka mberede. A gwala ụlọ ọgwụ mpaghara gị kwa.",
        "patient_yellow": "Aya emechala nyocha gị. A gwaala onye ọrụ ahụike obodo, ọ ga-akpọkwa gị iji nyochaa ihe ize ndụ gị nke ọma. Ọ bụrụ na mgbaàmà gị ka njọ, zipu HELP maka nyocha ọhụrụ.",
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
        return "Emergency response"
    if risk == "yellow":
        return "CHW phone assessment"
    return "Routine monitoring"


def patient_message_from_risk(patient, risk: str) -> str:
    if risk == "red":
        return tr(patient, "patient_red")
    if risk == "yellow":
        return tr(patient, "patient_yellow")
    return tr(patient, "patient_green")


def next_due_date():
    return (datetime.utcnow() + timedelta(days=14)).isoformat()


def choose_chw(patient: dict):
    online_workers = [w for w in community_workers if w["status"].lower() == "online"]
    if online_workers:
        return online_workers[0]
    return community_workers[0] if community_workers else None


def build_chw_alert_message(patient: dict) -> str:
    symptoms = ", ".join(patient.get("symptoms", [])) or "None recorded"
    risk_factors = ", ".join(patient.get("risk_factors", [])) or "None recorded"

    return (
        f"AYA ALERT: Medium-risk antenatal patient requires follow-up.\n"
        f"Phone: {patient['phone']}\n"
        f"Age: {patient.get('age', 'Not set')}\n"
        f"Pregnancy week: {patient.get('pregnancy_week') if patient.get('pregnancy_week') is not None else 'Unknown'}\n"
        f"Risk: {patient.get('risk', '').upper()}\n"
        f"Symptoms: {symptoms}\n"
        f"Risk factors: {risk_factors}\n"
        f"Action: Please phone the patient and complete a fuller risk assessment."
    )


def apply_chw_alert(patient: dict):
    if patient.get("risk") != "yellow":
        patient["assigned_chw"] = None
        patient["chw_alert_message"] = None
        patient["chw_alert_sent_at"] = None
        return

    chw = choose_chw(patient)
    if not chw:
        patient["assigned_chw"] = None
        patient["chw_alert_message"] = None
        patient["chw_alert_sent_at"] = None
        return

    patient["assigned_chw"] = chw
    patient["chw_alert_message"] = build_chw_alert_message(patient)
    patient["chw_alert_sent_at"] = now_iso()


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
        "assigned_chw": None,
        "chw_alert_message": None,
        "chw_alert_sent_at": None,
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
        "assigned_chw": patient["assigned_chw"],
        "chw_alert_message": patient["chw_alert_message"],
        "chw_alert_sent_at": patient["chw_alert_sent_at"],
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
    patient["assigned_chw"] = None
    patient["chw_alert_message"] = None
    patient["chw_alert_sent_at"] = None
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
            if label not in patient["symptoms"]:
                patient["symptoms"].append(label)
        else:
            if label not in patient["risk_factors"]:
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
    apply_chw_alert(patient)


def assessment_complete_reply(patient):
    due_text = tr(patient, "next_due", date=format_due_date(patient["next_assessment_due"]))

    extra = ""
    if patient.get("risk") == "yellow" and patient.get("assigned_chw") and patient.get("chw_alert_message"):
        chw = patient["assigned_chw"]
        extra = (
            f"\n\nAlert sent to community health worker:\n"
            f"{chw['name']} ({chw['phone']})\n\n"
            f"Message sent:\n{patient['chw_alert_message']}"
        )

    return f"{patient['patient_message']}{extra}\n\n{due_text}\n{tr(patient, 'help_complete')}"


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
            patient["required_response"] = "Emergency response"
            patient["patient_message"] = patient_message_from_risk(patient, "red")
            patient["assigned_chw"] = None
            patient["chw_alert_message"] = None
            patient["chw_alert_sent_at"] = None
            return assessment_complete_reply(patient)

        if patient["score"] >= 5:
            complete_assessment(patient)
            patient["risk"] = "red"
            patient["required_response"] = "Emergency response"
            patient["patient_message"] = patient_message_from_risk(patient, "red")
            patient["assigned_chw"] = None
            patient["chw_alert_message"] = None
            patient["chw_alert_sent_at"] = None
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
# Seed 10 hardcoded patients
# ---------------------------------
def seed_patient(
    phone,
    language="en",
    age=None,
    pregnancy_week=None,
    status="awaiting_language",
    score=0,
    symptoms=None,
    risk_factors=None,
    answers=None,
    completed=False,
    location=None,
):
    patient = create_patient(phone)
    patient["language"] = language
    patient["age"] = age
    patient["pregnancy_week"] = pregnancy_week
    patient["status"] = status
    patient["score"] = score
    patient["symptoms"] = symptoms or []
    patient["risk_factors"] = risk_factors or []
    patient["answers"] = answers or {}
    patient["completed"] = completed
    patient["location"] = location
    patient["created_at"] = now_iso()
    patient["updated_at"] = now_iso()
    patient["last_completed_at"] = now_iso() if completed else None
    patient["next_assessment_due"] = next_due_date() if completed else None

    if completed:
        patient["current_question"] = None
    elif status == "triage":
        patient["current_question"] = "q1"
    elif status == "registering_week":
        patient["current_question"] = "registration_week"
    elif status == "registering_age":
        patient["current_question"] = "registration_age"
    else:
        patient["current_question"] = "language"

    update_risk(patient)
    if completed:
        apply_chw_alert(patient)
        if patient["risk"] == "red":
            patient["assigned_chw"] = None
            patient["chw_alert_message"] = None
            patient["chw_alert_sent_at"] = None
    return patient


def seed_demo_patients():
    patients.clear()

    seed_patient("+2347000000001")
    seed_patient("+2347000000002", language="pidgin", status="registering_age")
    seed_patient("+2347000000003", language="ha", age=22, status="registering_week")
    seed_patient(
        "+2347000000004",
        language="en",
        age=31,
        pregnancy_week=24,
        status="triage",
        score=3,
        symptoms=["Severe constant headache"],
        answers={"q2": True},
    )

    seed_patient(
        "+2347000000005",
        language="en",
        age=27,
        pregnancy_week=32,
        status="completed",
        score=2,
        symptoms=["Itchy hands/feet"],
        completed=True,
    )
    seed_patient(
        "+2347000000006",
        language="pidgin",
        age=19,
        pregnancy_week=16,
        status="completed",
        score=4,
        symptoms=["Fever or chills"],
        risk_factors=["Age under 18 or over 35"],
        completed=True,
    )
    seed_patient(
        "+2347000000007",
        language="ha",
        age=36,
        pregnancy_week=28,
        status="completed",
        score=6,
        symptoms=["Reduced fetal movement"],
        risk_factors=["Age under 18 or over 35", "Hypertension history"],
        completed=True,
    )
    seed_patient(
        "+2347000000008",
        language="yo",
        age=24,
        pregnancy_week=38,
        status="completed",
        score=1,
        risk_factors=["Previous pre-eclampsia or stillbirth"],
        completed=True,
    )
    seed_patient(
        "+2347000000009",
        language="ig",
        age=41,
        pregnancy_week=20,
        status="completed",
        score=5,
        symptoms=["Water leaking / fluid breaking"],
        risk_factors=["Age under 18 or over 35"],
        completed=True,
        location={
            "latitude": 6.5244,
            "longitude": 3.3792,
            "timestamp": now_iso(),
        },
    )
    seed_patient(
        "+2347000000010",
        language="en",
        age=29,
        pregnancy_week=12,
        status="completed",
        score=3,
        symptoms=["Severe pelvic/abdominal pain"],
        risk_factors=["Diabetes history"],
        completed=True,
    )


seed_demo_patients()


# ---------------------------------
# Integrated stripped HTML
# ---------------------------------
CLINIC_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
    <title>Aya Antenatal Companion</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        :root {
            --primary: #153d36;
            --primary-dark: #0d2820;
            --primary-light: #2a6b5e;
            --primary-pale: #e8f2f0;
            --red: #c0392b;
            --red-pale: #fdecea;
            --yellow: #c9880a;
            --yellow-pale: #fef6e4;
            --green: #153d36;
            --green-pale: #e8f2f0;
            --bg: #f4f8f7;
            --card: #fff;
            --border: #c8dbd8;
            --text: #0d2820;
            --muted: #4a7a70;
            --phone-frame: #0d2820;
        }

        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
        }

        header {
            background: var(--primary-dark);
            color: #fff;
            padding: 14px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        header h1 {
            font-size: 1rem;
            font-weight: 800;
        }

        header p {
            font-size: 0.75rem;
            opacity: 0.75;
            margin-top: 4px;
        }

        .clock {
            font-size: 0.8rem;
            opacity: 0.8;
        }

        .main {
            display: grid;
            grid-template-columns: 380px 1fr;
            gap: 16px;
            padding: 16px;
        }

        .phone-wrap {
            background: var(--phone-frame);
            border-radius: 24px;
            padding: 14px;
        }

        .phone-label {
            color: rgba(255,255,255,0.6);
            font-size: 0.7rem;
            text-align: center;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 0.8px;
        }

        .phone-frame {
            background: #0d1f1c;
            border-radius: 28px;
            border: 4px solid #1e4a42;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0,0,0,0.35);
        }

        .phone-status, .phone-contact, .progress-wrap, .chat-input {
            padding: 10px 12px;
        }

        .phone-status {
            display: flex;
            justify-content: space-between;
            background: #08110f;
            color: #cdd;
            font-size: 0.7rem;
        }

        .phone-contact {
            background: #122b26;
            border-bottom: 1px solid #1e4a42;
        }

        .phone-contact .name {
            color: #fff;
            font-weight: 700;
            font-size: 0.82rem;
        }

        .phone-contact .sub {
            color: #86b5ad;
            font-size: 0.66rem;
            margin-top: 2px;
        }

        .progress-wrap {
            background: #0d1f1c;
            border-bottom: 1px solid #1e4a42;
        }

        .progress-line {
            height: 4px;
            background: #1e4a42;
            border-radius: 999px;
            overflow: hidden;
            margin-top: 6px;
        }

        .progress-fill {
            height: 100%;
            width: 0%;
            background: var(--primary-light);
        }

        .chat {
            height: 520px;
            overflow-y: auto;
            background: #091510;
            padding: 12px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .bubble {
            max-width: 85%;
            padding: 10px 12px;
            border-radius: 16px;
            font-size: 0.78rem;
            line-height: 1.5;
            white-space: pre-wrap;
            word-break: break-word;
        }

        .bubble.user {
            align-self: flex-end;
            background: var(--primary);
            color: #fff;
            border-bottom-right-radius: 4px;
        }

        .bubble.bot {
            align-self: flex-start;
            background: #d8ede9;
            color: var(--text);
            border-bottom-left-radius: 4px;
        }

        .chat-input {
            display: flex;
            gap: 8px;
            background: #0d1f1c;
            border-top: 1px solid #1e4a42;
        }

        .chat-input input, .toolbar input {
            flex: 1;
            border: 1px solid #2a6b5e;
            border-radius: 16px;
            padding: 10px 12px;
            font-size: 0.8rem;
            outline: none;
        }

        .chat-input input {
            background: #122b26;
            color: #fff;
        }

        .chat-input input::placeholder {
            color: #79a49b;
        }

        button {
            border: none;
            border-radius: 12px;
            padding: 10px 12px;
            cursor: pointer;
            font-weight: 700;
        }

        .send-btn, .primary-btn {
            background: var(--primary);
            color: white;
        }

        .danger-btn {
            background: var(--red);
            color: white;
        }

        .ghost-btn {
            background: #edf3f2;
            color: var(--primary-dark);
            border: 1px solid var(--border);
        }

        .dashboard {
            display: flex;
            flex-direction: column;
            gap: 14px;
        }

        .toolbar, .card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 14px;
        }

        .toolbar {
            display: flex;
            gap: 10px;
            align-items: center;
            flex-wrap: wrap;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
        }

        .stat {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 14px;
        }

        .stat .label {
            font-size: 0.68rem;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .stat .value {
            font-size: 1.8rem;
            font-weight: 900;
            margin-top: 8px;
        }

        .red { color: var(--red); }
        .yellow { color: var(--yellow); }
        .green { color: var(--green); }

        .card h3 {
            font-size: 0.9rem;
            margin-bottom: 10px;
            color: var(--primary-dark);
        }

        .state-box {
            font-size: 0.8rem;
            line-height: 1.65;
            background: #f8fbfa;
            border-radius: 12px;
            padding: 12px;
        }

        .badge {
            display: inline-block;
            font-size: 0.7rem;
            padding: 4px 8px;
            border-radius: 999px;
            margin: 3px 6px 3px 0;
            background: #eef3f2;
        }

        .badge.red {
            background: var(--red-pale);
            color: var(--red);
        }

        .badge.yellow {
            background: var(--yellow-pale);
            color: var(--yellow);
        }

        .badge.green {
            background: var(--green-pale);
            color: var(--green);
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.78rem;
        }

        th, td {
            text-align: left;
            padding: 10px 8px;
            border-bottom: 1px solid var(--border);
            vertical-align: top;
        }

        th {
            color: var(--muted);
            font-size: 0.68rem;
            text-transform: uppercase;
            letter-spacing: 0.4px;
        }

        tr:hover {
            background: #fafdfc;
        }

        .pill {
            display: inline-block;
            border-radius: 999px;
            padding: 4px 8px;
            font-size: 0.68rem;
            font-weight: 700;
        }

        .pill.red {
            background: var(--red-pale);
            color: var(--red);
        }

        .pill.yellow {
            background: var(--yellow-pale);
            color: var(--yellow);
        }

        .pill.green {
            background: var(--green-pale);
            color: var(--green);
        }

        .muted {
            color: var(--muted);
        }

        .row-actions {
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
        }

        .row-actions button {
            font-size: 0.7rem;
            padding: 6px 8px;
        }

        pre.alert-box {
            background: #f8fbfa;
            border: 1px solid var(--border);
            padding: 10px;
            border-radius: 10px;
            white-space: pre-wrap;
            word-break: break-word;
            font-family: inherit;
            font-size: 0.75rem;
            line-height: 1.5;
        }

        @media (max-width: 1000px) {
            .main {
                grid-template-columns: 1fr;
            }
            .stats {
                grid-template-columns: 1fr 1fr;
            }
        }
    </style>
</head>
<body>
    <header>
        <div>
            <h1>Aya Antenatal Companion</h1>
            <p>Patient SMS simulator and clinic response dashboard</p>
        </div>
        <div class="clock" id="clock">--:--:--</div>
    </header>

    <div class="main">
        <div class="phone-wrap">
            <div class="phone-label">Patient SMS Simulator</div>
            <div class="phone-frame">
                <div class="phone-status">
                    <span>Aya</span>
                    <span>SMS Triage</span>
                    <span id="phoneClock">--:--</span>
                </div>
                <div class="phone-contact">
                    <div class="name">Aya Antenatal Companion</div>
                    <div class="sub" id="patientTag">Enter a Nigerian phone number</div>
                </div>
                <div class="progress-wrap">
                    <div style="font-size:0.68rem;color:#86b5ad;">Assessment Progress <span id="progressText" style="float:right;">0%</span></div>
                    <div class="progress-line">
                        <div class="progress-fill" id="progressFill"></div>
                    </div>
                </div>
                <div id="chat" class="chat">
                    <div class="bubble bot">Type any message to start. Reply using numbers only for all multiple-choice questions.</div>
                </div>
                <div class="chat-input">
                    <input id="phoneInput" value="+2347000000001" placeholder="+2348012345678" />
                </div>
                <div class="chat-input">
                    <input id="messageInput" placeholder="Type message... use numbers only for multiple choice" />
                    <button class="send-btn" onclick="sendMessage()">Send</button>
                </div>
                <div class="chat-input">
                    <button class="danger-btn" style="width:100%;" onclick="shareLocation()">Share emergency location</button>
                </div>
            </div>
        </div>

        <div class="dashboard">
            <div class="toolbar">
                <input id="lookupPhone" value="+2347000000001" placeholder="+2348012345678" />
                <button class="primary-btn" onclick="loadSinglePatient()">Load patient</button>
                <button class="ghost-btn" onclick="refreshPatients()">Refresh dashboard</button>
            </div>

            <div class="stats">
                <div class="stat">
                    <div class="label">Patients</div>
                    <div class="value" id="statTotal">0</div>
                </div>
                <div class="stat">
                    <div class="label">High Risk</div>
                    <div class="value red" id="statRed">0</div>
                </div>
                <div class="stat">
                    <div class="label">Medium Risk</div>
                    <div class="value yellow" id="statYellow">0</div>
                </div>
                <div class="stat">
                    <div class="label">Low Risk</div>
                    <div class="value green" id="statGreen">0</div>
                </div>
            </div>

            <div class="card">
                <h3>Selected Patient State</h3>
                <div id="stateBox" class="state-box">No patient loaded.</div>
            </div>

            <div class="card">
                <h3>Patients</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Phone</th>
                            <th>Age / Week</th>
                            <th>Risk</th>
                            <th>Status</th>
                            <th>Response</th>
                        </tr>
                    </thead>
                    <tbody id="patientsTable"></tbody>
                </table>
            </div>

            <div class="card">
                <h3>Available Community Health Workers</h3>
                <div style="display:flex;flex-direction:column;gap:10px;">
                    <div style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;border:1px solid var(--border);border-radius:12px;background:#f8fbfa;">
                        <div>
                            <div style="font-weight:700;">Nurse Adaeze</div>
                            <div class="muted" style="font-size:0.72rem;">Zone A · Lagos · +2348012345601</div>
                        </div>
                        <span class="pill green">Online</span>
                    </div>

                    <div style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;border:1px solid var(--border);border-radius:12px;background:#f8fbfa;">
                        <div>
                            <div style="font-weight:700;">Midwife Kemi</div>
                            <div class="muted" style="font-size:0.72rem;">Zone B · Kano · +2348012345602</div>
                        </div>
                        <span class="pill green">Online</span>
                    </div>

                    <div style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;border:1px solid var(--border);border-radius:12px;background:#f8fbfa;">
                        <div>
                            <div style="font-weight:700;">Dr. Emeka</div>
                            <div class="muted" style="font-size:0.72rem;">Zone C · Abuja · +2348012345603</div>
                        </div>
                        <span class="pill yellow">Busy</span>
                    </div>

                    <div style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;border:1px solid var(--border);border-radius:12px;background:#f8fbfa;">
                        <div>
                            <div style="font-weight:700;">CHW Tola</div>
                            <div class="muted" style="font-size:0.72rem;">Zone A · Ibadan · +2348012345604</div>
                        </div>
                        <span class="pill green">Online</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let selectedPatient = null;

        function nowTime() {
            return new Date().toLocaleTimeString('en-GB', {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
        }

        function tick() {
            document.getElementById('clock').textContent = nowTime();
            document.getElementById('phoneClock').textContent = new Date().toLocaleTimeString('en-GB', {
                hour: '2-digit',
                minute: '2-digit'
            });
        }
        setInterval(tick, 1000);
        tick();

        function addBubble(text, cls) {
            const chat = document.getElementById("chat");
            const bubble = document.createElement("div");
            bubble.className = "bubble " + cls;
            bubble.textContent = text;
            chat.appendChild(bubble);
            chat.scrollTop = chat.scrollHeight;
        }

        function riskClass(risk) {
            if (risk === "red") return "red";
            if (risk === "yellow") return "yellow";
            return "green";
        }

        function riskPill(risk) {
            const cls = riskClass(risk);
            return `<span class="pill ${cls}">${risk.toUpperCase()}</span>`;
        }

        function progressPercent(patient) {
            if (!patient) return 0;
            if (patient.completed) return 100;
            if (patient.status === "awaiting_language") return 5;
            if (patient.status === "registering_age") return 15;
            if (patient.status === "registering_week") return 25;
            if (patient.status === "triage") {
                const map = {
                    q1: 35, q2: 42, q3: 49, q4: 56, q5: 63,
                    q6: 70, q7: 77, q8: 84, q9: 90, q10: 95, q11: 98
                };
                return map[patient.current_question] || 30;
            }
            return 0;
        }

        function renderState(patient) {
            const state = document.getElementById("stateBox");
            const progress = progressPercent(patient);
            document.getElementById("progressFill").style.width = progress + "%";
            document.getElementById("progressText").textContent = progress + "%";

            if (!patient) {
                state.innerHTML = "Patient not found.";
                document.getElementById("patientTag").textContent = "No active patient";
                return;
            }

            selectedPatient = patient;
            document.getElementById("patientTag").textContent = patient.phone + " · " + (patient.language || "Not set");

            const symptoms = (patient.symptoms || []).map(s => `<span class="badge">${s}</span>`).join("");
            const riskFactors = (patient.risk_factors || []).map(s => `<span class="badge">${s}</span>`).join("");
            const location = patient.location
                ? `${patient.location.latitude}, ${patient.location.longitude} (${patient.location.timestamp})`
                : "Not shared";

            const chwAssigned = patient.assigned_chw
                ? `${patient.assigned_chw.name} · ${patient.assigned_chw.phone} · ${patient.assigned_chw.status}`
                : "None";

            const chwMessage = patient.chw_alert_message
                ? patient.chw_alert_message.replaceAll("\\n", "<br>")
                : "None";

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
                <strong>Location:</strong> ${location}<br>
                <strong>Assigned CHW:</strong> ${chwAssigned}<br>
                <strong>CHW alert sent:</strong> ${patient.chw_alert_sent_at ?? "Not sent"}<br><br>
                <strong>Symptoms:</strong><br>${symptoms || '<span class="muted">None</span>'}<br><br>
                <strong>Risk factors:</strong><br>${riskFactors || '<span class="muted">None</span>'}<br><br>
                <strong>CHW message:</strong><br>${chwMessage}
            `;
        }

        function buildResponseInfo(patient) {
            const phoneLine = `<div><strong>Phone:</strong> ${patient.phone}</div>`;

            if (patient.risk === "red") {
                const loc = patient.location
                    ? `${patient.location.latitude}, ${patient.location.longitude}`
                    : "Location not shared";

                return `
                    <div style="font-size:0.74rem;line-height:1.5;">
                        ${phoneLine}
                        <div><span class="pill red">Emergency</span></div>
                        <div><strong>Action:</strong> Patient told to dial 112</div>
                        <div><strong>Clinic alerted:</strong> Yes</div>
                        <div><strong>Location:</strong> ${loc}</div>
                        <div class="row-actions" style="margin-top:6px;">
                           <button class="ghost-btn" onclick="selectPatient('${patient.phone}')">Open</button>
                        </div>
                    </div>
                `;
            }

            if (patient.risk === "yellow") {
                const chwText = patient.assigned_chw
                    ? `${patient.assigned_chw.name} (${patient.assigned_chw.phone})`
                    : "Not assigned";

                return `
                    <div style="font-size:0.74rem;line-height:1.5;">
                        ${phoneLine}
                        <div><span class="pill yellow">Medium risk</span></div>
                        <div><strong>Action:</strong> CHW text sent</div>
                        <div><strong>Assigned:</strong> ${chwText}</div>
                        <div class="row-actions" style="margin-top:6px;">
                            <button class="ghost-btn" onclick="selectPatient('${patient.phone}')">Open</button>
                        </div>
                    </div>
                `;
            }

            return `
                <div style="font-size:0.74rem;line-height:1.5;">
                    ${phoneLine}
                    <div><span class="pill green">Routine monitoring</span></div>
                    <div><strong>Action:</strong> Routine follow-up</div>
                    <div class="row-actions" style="margin-top:6px;">
                       <button class="ghost-btn" onclick="selectPatient('${patient.phone}')">Open</button>
                    </div>
                </div>
            `;
        }

        async function refreshPatients() {
            const response = await fetch("/api/patients");
            const data = await response.json();

            const patients = data.patients || [];
            document.getElementById("statTotal").textContent = patients.length;
            document.getElementById("statRed").textContent = patients.filter(p => p.risk === "red").length;
            document.getElementById("statYellow").textContent = patients.filter(p => p.risk === "yellow").length;
            document.getElementById("statGreen").textContent = patients.filter(p => p.risk === "green").length;

            const tbody = document.getElementById("patientsTable");
            tbody.innerHTML = "";

            patients.forEach(patient => {
                const tr = document.createElement("tr");
                const responseInfo = buildResponseInfo(patient);

                tr.innerHTML = `
                    <td>${patient.phone}</td>
                    <td>${patient.age ?? "—"} / ${patient.pregnancy_week ?? "—"}</td>
                    <td>${riskPill(patient.risk)}</td>
                    <td>${patient.status}</td>
                    <td>${responseInfo}</td>
                `;
                tbody.appendChild(tr);
            });
        }

        async function selectPatient(phone) {
            document.getElementById("phoneInput").value = phone;
            document.getElementById("lookupPhone").value = phone;
            await loadSinglePatient();
        }

        async function loadSinglePatient() {
            const phone = document.getElementById("lookupPhone").value.trim();
            if (!phone) return;

            const response = await fetch("/api/patient/" + encodeURIComponent(phone));
            if (!response.ok) {
                renderState(null);
                return;
            }

            const patient = await response.json();
            renderState(patient);
        }

        async function sendMessage() {
            const phone = document.getElementById("phoneInput").value.trim();
            const input = document.getElementById("messageInput");
            const text = input.value.trim();

            if (!phone || !text) return;

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
            await refreshPatients();
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
                    await refreshPatients();
                },
                () => {
                    addBubble("Location permission was denied or unavailable.", "bot");
                }
            );
        }

        document.getElementById("messageInput").addEventListener("keypress", function(e) {
            if (e.key === "Enter") sendMessage();
        });

        refreshPatients();
        loadSinglePatient();
    </script>
</body>
</html>
"""


# ---------------------------------
# Routes
# ---------------------------------
@app.route("/")
def home():
    return render_template_string(CLINIC_HTML)


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
    return render_template_string(CLINIC_HTML)


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


@app.route("/api/reset-demo", methods=["POST"])
def api_reset_demo():
    seed_demo_patients()
    return jsonify({
        "message": "Demo patients reset.",
        "patient_count": len(patients),
    })


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
    phone = str(data.get("phone", "+2347000000001")).strip()
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
    app.run(host="0.0.0.0", port=8080, debug=True)
