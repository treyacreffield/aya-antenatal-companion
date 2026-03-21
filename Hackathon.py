from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Simple temporary storage
patients = {}

# Each patient record looks like:
# {
#     "phone": "+441234567890",
#     "state": "awaiting_age",
#     "age": None,
#     "pregnancy_week": None,
#     "bleeding": None
# }


def get_or_create_patient(phone):
    if phone not in patients:
        patients[phone] = {
            "phone": phone,
            "state": "new",
            "age": None,
            "pregnancy_week": None,
            "bleeding": None
        }
    return patients[phone]


@app.route("/sms", methods=["POST"])
def sms_reply():
    incoming_msg = request.form.get("Body", "").strip()
    from_number = request.form.get("From", "").strip()

    response = MessagingResponse()
    msg = response.message()

    patient = get_or_create_patient(from_number)
    state = patient["state"]

    # Step 1: welcome
    if state == "new":
        patient["state"] = "awaiting_age"
        msg.body(
            "Welcome to MamiCare.\n"
            "Please reply with your age."
        )
        return str(response)

    # Step 2: collect age
    if state == "awaiting_age":
        try:
            age = int(incoming_msg)
            patient["age"] = age
            patient["state"] = "awaiting_pregnancy_week"
            msg.body(
                "Thank you.\n"
                "Please reply with your pregnancy week."
            )
        except ValueError:
            msg.body("Please enter your age as a number.")
        return str(response)

    # Step 3: collect pregnancy week
    if state == "awaiting_pregnancy_week":
        try:
            week = int(incoming_msg)
            patient["pregnancy_week"] = week
            patient["state"] = "awaiting_bleeding"
            msg.body(
                "Assessment Q1:\n"
                "Are you bleeding?\n"
                "Reply YES or NO."
            )
        except ValueError:
            msg.body("Please enter your pregnancy week as a number.")
        return str(response)

    # Step 4: collect one symptom
    if state == "awaiting_bleeding":
        answer = incoming_msg.lower()

        if answer == "yes":
            patient["bleeding"] = "Yes"
        elif answer == "no":
            patient["bleeding"] = "No"
        else:
            msg.body("Please reply YES or NO.")
            return str(response)

        patient["state"] = "complete"
        msg.body(
            "Thank you. Your response has been recorded."
        )
        return str(response)

    # Step 5: already completed
    if state == "complete":
        msg.body(
            "You have already completed registration and assessment."
        )
        return str(response)

    msg.body("Something went wrong. Please try again.")
    return str(response)


@app.route("/clinic", methods=["GET"])
def clinic_dashboard():
    html = """
    <html>
    <head>
        <title>MamiCare Clinic Dashboard</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 40px;
            }
            h1 {
                color: #c2185b;
            }
            .card {
                border: 1px solid #ccc;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 15px;
            }
        </style>
    </head>
    <body>
        <h1>MamiCare Clinic Dashboard</h1>
    """

    if not patients:
        html += "<p>No patients registered yet.</p>"
    else:
        for patient in patients.values():
            html += f"""
            <div class="card">
                <p><strong>Phone:</strong> {patient['phone']}</p>
                <p><strong>Age:</strong> {patient['age']}</p>
                <p><strong>Pregnancy Week:</strong> {patient['pregnancy_week']}</p>
                <p><strong>Bleeding:</strong> {patient['bleeding']}</p>
            </div>
            """

    html += """
    </body>
    </html>
    """
    return html


if __name__ == "__main__":
    app.run(debug=True, port=8080)