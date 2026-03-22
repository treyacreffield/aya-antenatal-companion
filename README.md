# aya-antenatal-companion
## Problem
Nigeria faces one of the highest maternal mortality rates in the world, with many deaths caused not only by lack of medical treatment, but by delays in deciding to seek care. In rural and low-resource communities, pregnant women may not recognise early danger signs such as headache, blurred vision, swelling or bleeding. These symptoms are often dismissed as normal pregnancy discomfort, malaria, or non-medical causes, which can delay urgent intervention. 

This challenge is made worse by limited access to smartphones, low digital literacy, and language barriers. Many digital health solutions assume reliable internet access and smartphone ownership, but these assumptions exclude a large proportion of women at risk.

## Solution
Aya is a zero-rated SMS-based maternal health triage platform designed to help pregnant women in Nigeria recognise danger signs early and seek care sooner. Using simpple text messaging, women can register on the system, recieve regular check-in prompts throughout pregnancy, and complete a guided symptom assessment in their preferred language: English, Pidgin, Hausa, Yoruba, or Lgbo.

The plaform uses a clinically informed weighted triage algorithm to assess risk and classify responses into low, medium or high urgency. Based on the result, the user recieves clear next-step advice, while the clinic recieves the relevant patient details, symptoms, and required response level. This enables faster follow-up for medium-risk cases and urgent escalation for high-risk cases.

By using SMS rather than a smartphone app, Aya is designed for accesibility, scale and real-world deployment in low-connectivity settings. Its goal is to reduce preventable maternal deaths by addressing the first delay: the delay in recognising danger and deciding to seek care.


## Features
SMS-Based Maternal Triage
-low cost accesible SMS interface (no internet required)
-users respond using numeric inputs only for simplicity and inclusivity
-supports multiple local languages (English, Pidgin, Hausa, Yoruba, Lgbo)

Risk Assessment Engine
-structured 11-question triage flow based on key maternal danger signs
-real-time scoring system that classifies patients as high/medium/low risk
-early exit logic for critical symptoms

Emergency Response
-patient recieves clear instructions to dial emergency services immediately (112)
-system simulates clinic alert escalation
-optional location sharing for emergency coordination (demo feature)

Community Health Worker Allocation
-medium risk cases assigned to an available community health worker
-evenly distributed across online workers
-workers recieve structured patient summary: phone number, symptoms, risk level
-patient is informed that a health worker will call them shortly

Clinic Dashboard
-real time patient monitoring dashboard
-displays risk levels (red/yellow/green), symptoms and risk factors, required response (emergency/call/monitor)
-includes patient lookup, live updates and risk distribution stats

Community Health Worker Panel
-displays available workers and status (online/busy)

SMS Simulation Environment
-built in phone simulator UI for demo without Twilio setup
-fully mirrors real SMS flow: send/recieve messages, track patient journey

Patient Lifecycle Management
-registration flow: language->age->pregnancy week
-ongoing features: text 'HELP' to restart assessment, scheduled follow-ups (every 14 days)
Designed for Low-Rescource Settings

-works on basic mobile phones (SMS only)
-no reliance on smartphones, apps, internet
-built around constraints like limited transport access

## Tech Stack
This prototype is built with:
-Python + Flask for the backend logic and routing
-HTML, CSS and Vanilla JavaScript for the patient simulator and clinic dashboard
-Twilio SMS webhook handling for inbound and outbound messaging logic
-In-memory data storage for rapid hackathon prototyping without a database

The app is currently designed as a single-file Flask prototype, making it fast to run, demo and iterate on during the hackathon.


## How to run
1. Clone this repository
2. Install Python 3
3. Install the dependecies listed in the requirements.txt
4. Add your SMS API credentials: e.g Twilio
5. Run the application
6. Expose local server if needed using tunneling service e.g CloudFlared
7. Test the SMS flow

## Team
Treya Creffield, Benjamin Cook, Leong Hoy Kit, Yvonne Cho

## Demo
-demo link here
