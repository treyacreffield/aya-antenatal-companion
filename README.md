## Aya - antenatal companion
### Aya is a zero-cost SMS platform that helps pregnant women recognise danger signs early and triggers real-world clinical response, without requiring internet or smartphones

## Inspiration
Nigeria faces one of the highest maternal mortality rates in the world, with many deaths caused not only by lack of medical treatment, but by delays in deciding to seek care. 

In rural and low-resource communities, pregnant women may not recognise early danger signs such as headache, blurred vision, swelling or bleeding. These symptoms are often dismissed as normal pregnancy discomfort, malaria, or non-medical causes, which can delay urgent intervention. 

At the same time, most digital health solutions assume:
-Smartphone access
-Internet connectivity
-High digital literacy

These assumptions exclude the very populations most at risk.

**We were inspired to build a solution that works within real-world constraints - not ideal ones.**

## Our Solution
Aya is a zero-rated SMS-based maternal health triage platform designed to help pregnant women in Nigeria recognise danger signs early and seek care sooner. Using simple text messaging, women can register on the system, receive regular check-in prompts throughout pregnancy, and complete a guided symptom assessment in their preferred language: English, Pidgin, Hausa, Yoruba, or Lgbo.

The platform uses a clinically informed weighted triage algorithm to assess risk and classify responses into low, medium or high urgency. Based on the result, the user receives clear next-step advice, while the clinic receives the relevant patient details, symptoms, and required response level. This enables faster follow-up for medium-risk cases and urgent escalation for high-risk cases.

By using SMS rather than a smartphone app, Aya is designed for accesibility, scale and real-world deployment in low-connectivity settings. Its goal is to reduce preventable maternal deaths by addressing the first delay: the delay in recognising danger and deciding to seek care.

## How it works
1. User sends SMS to Aya
2. System registers user (language, age, pregnancy stage)
3. User completes 11-question triage via numeric inputs
4. Backend calculates risk score in real-time
5. Patient is classified: Green / Amber / Red
6. Action is triggered:
- Red -> emergency SMS + clinic alert
- Amber -> assigned to CHW
- Green -> routine monitoring
7. Clinic dashboard updates live with patient data

## Features
**SMS-Based Maternal Triage**
-low cost accesible SMS interface (no internet required)
-users respond using numeric inputs only for simplicity and inclusivity
-supports multiple local languages (English, Pidgin, Hausa, Yoruba, Lgbo)

**Risk Assessment Engine**
-structured 11-question triage flow based on key maternal danger signs
-real-time scoring system that classifies patients as high/medium/low risk
-early exit logic for critical symptoms

**Emergency Response**
-patient recieves clear instructions to dial emergency services immediately (112)
-system simulates clinic alert escalation
-optional location sharing for emergency coordination (demo feature)

**Community Health Worker Allocation**
-medium risk cases assigned to an available community health worker
-evenly distributed across online workers
-workers recieve structured patient summary: phone number, symptoms, risk level
-patient is informed that a health worker will call them shortly

**Clinic Dashboard**
-real time patient monitoring dashboard
-displays risk levels (red/yellow/green), symptoms and risk factors, required response (emergency/call/monitor)
-includes patient lookup, live updates and risk distribution stats

**Community Health Worker Panel**
-displays available workers and status (online/busy)

**SMS Simulation Environment**
-built in phone simulator UI for demo without Twilio setup
-fully mirrors real SMS flow: send/recieve messages, track patient journey

**Patient Lifecycle Management**
-registration flow: language->age->pregnancy week
-ongoing features: text 'HELP' to restart assessment, scheduled follow-ups (every 14 days)

**Designed for Low-Rescource Settings**
-works on basic mobile phones (SMS only)
-no reliance on smartphones, apps, internet
-built around constraints like limited transport access

## How we built it
**Tech Stack**
- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, Vanilla JavaScript  
- **Messaging:** Twilio SMS API  
- **Data:** In-memory storage (hackathon prototype)  
- **Deployment:** Local + tunnelling (e.g. Cloudflare)  
The app is currently designed as a single-file Flask prototype, making it fast to run, demo and iterate on during the hackathon.

## How to run
1. Clone the GitHub repository
2. Install Python 3
3. Install the dependencies listed in the requirements.txt in GitHub
4. Add your SMS API credentials: e.g Twilio
5. Run the application
6. Expose local server if needed using tunnelling service e.g CloudFlared
7. Test the SMS flow

## Real-world Impact
Aya directly addresses the first delay in maternal mortality:

**Delay #1: recognising danger and deciding to seek care**

By:
- Simplifying symptom recognition
- Providing immediate guidance
- Triggering real-world follow-up

## Challenges we faced
One of our biggest challenges was implementing real two-way SMS communication. 
During development we planned to use Twilio for live messaging. However, Twilio requires regulatory approval for two-way SMS in Nigeria, and without this, only limited one-way messaging is supported. This made it difficult to fully test real-user interaction within the hackathon timeframe.
Our solution was to build a fully functional SMS simulation environment within the web interface, allowing us to: replicate real-user journeys, test triage logic end-to-end, and demonstrate full system behaviour without live SMS.
For deployment we would integrate with providers such as Africa's Talking, which supports: Nigerian phone numbers, two-way SMS at scale and local infrastructure compatibility.

Another challenge we faced was understanding financial impact in a non-profit model.
Unlike traditional tech products, Aya is not designed as a direct profit-generating platform. This created a challenge in how we evaluate financial viability and long-term sustainability.
Most standard models focus on revenue generation or loss minimisation, but in our case, the value is created through:
-Prevented medical complications
-Reduced emergency care costs
-Improved maternal health outcomes
We had to rethink how to measure success and justify investment without relying on conventional profit metrics.
We adapted a cost-benefit and social return on investment (SROI) model, where value is derived from:
-avoided emergency and late-stage treatment costs through earlier intervention
-reduced strain on healthcare systems by identifying and prioritising high-risk patients sooner
-more efficient allocation of community health workers through targeted follow-up
-improved maternal health outcomes, reducing preventable complications and deaths

This reframes Aya as:
-A cost-saving intervention for healthcare systems
-A high-impact, low-cost scalable solution for governments and NGOs

## Accomplishments we are proud of
We are proud to have built a fully functional, end-to-end maternal health triage system in a hackathon timeframe. Aya integrates SMS-based user interaction, real-time risk assessment, a live clinic dashboard, and community health worker allocation, all designed for low-resource settings. Rather than just a concept, we focused on creating a solution that is practical, scalable, and ready for real-world deployment.

## What we learned
We learned that impactful solutions in global health must be built around real-world constraints, not ideal scenarios. This pushed us to prioritise accessibility, simplicity, and reliability, while considering factors like connectivity, language, and infrastructure. We also developed a deeper understanding of how to translate a technical prototype into a scalable public health solution, including partnerships, deployment, and long-term sustainability.


## Team
Treya Creffield, Benjamin Cook, Leong Hoy Kit, Yvonne Cho
