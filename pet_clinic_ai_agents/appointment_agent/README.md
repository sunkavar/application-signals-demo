# Appointment Booking Agent

A simple appointment booking system using Strands Agents that runs locally.

## Features

- Book new appointments
- List existing appointments
- Cancel appointments
- In-memory storage (resets on restart)
- AWS Bedrock integration for natural language processing

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure AWS credentials (for Bedrock access):
```bash
aws configure
```

3. Run the agent:
```bash
python appointment_agent.py
```

## Usage Examples

- "Book an appointment for John Doe tomorrow at 2 PM for a checkup"
- "Show me all appointments for today"
- "List appointments for 2025-11-04"
- "Cancel the appointment on 2025-11-04 at 14:00"

## Functions

- `book_appointment(date, time, patient_name, reason)` - Book new appointment
- `list_appointments(date)` - List appointments (optional date filter)
- `cancel_appointment(date, time)` - Cancel existing appointment

The agent uses natural language processing to understand your requests and call the appropriate functions.