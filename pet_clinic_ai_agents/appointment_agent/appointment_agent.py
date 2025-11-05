#!/usr/bin/env python3
from strands import Agent, tool
from strands.models import BedrockModel
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Configure the strands logger
strands_logger = logging.getLogger("strands")
strands_logger.setLevel(logging.INFO)

# Simple in-memory storage for appointments
appointments_db = {}
next_appointment_id = 1

@tool
def book_appointment(date: str, time: str, patient_name: str, reason: str = "General consultation") -> Dict[str, Any]:
    """
    Book an appointment for a patient.
    
    Args:
        date: Date in YYYY-MM-DD format
        time: Time in HH:MM format (24-hour)
        patient_name: Name of the patient
        reason: Reason for the appointment
    
    Returns:
        Dictionary with booking confirmation or error
    """
    global next_appointment_id
    
    try:
        # Validate date format
        appointment_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        
        # Check if appointment is in the future
        if appointment_datetime <= datetime.now():
            return {"success": False, "error": "Appointment must be in the future"}
        
        # Check if slot is available (simple check - no double booking same time)
        slot_key = f"{date}_{time}"
        if slot_key in appointments_db:
            return {"success": False, "error": "Time slot already booked"}
        
        # Book the appointment
        appointment = {
            "id": next_appointment_id,
            "date": date,
            "time": time,
            "patient_name": patient_name,
            "reason": reason,
            "status": "confirmed",
            "created_at": datetime.now().isoformat()
        }
        
        appointments_db[slot_key] = appointment
        next_appointment_id += 1
        
        return {
            "success": True,
            "appointment": appointment,
            "message": f"Appointment booked successfully for {patient_name} on {date} at {time}"
        }
        
    except ValueError as e:
        return {"success": False, "error": f"Invalid date/time format: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Booking failed: {str(e)}"}

@tool
def list_appointments(date: str = None) -> Dict[str, Any]:
    """
    List appointments for a specific date or all appointments.
    
    Args:
        date: Optional date in YYYY-MM-DD format. If None, lists all appointments.
    
    Returns:
        Dictionary with list of appointments
    """
    try:
        if date:
            # List appointments for specific date
            filtered_appointments = [
                apt for slot_key, apt in appointments_db.items() 
                if apt["date"] == date
            ]
            return {
                "success": True,
                "appointments": filtered_appointments,
                "date": date,
                "count": len(filtered_appointments)
            }
        else:
            # List all appointments
            all_appointments = list(appointments_db.values())
            return {
                "success": True,
                "appointments": all_appointments,
                "count": len(all_appointments)
            }
    except Exception as e:
        return {"success": False, "error": f"Failed to list appointments: {str(e)}"}

@tool
def cancel_appointment(date: str, time: str) -> Dict[str, Any]:
    """
    Cancel an appointment by date and time.
    
    Args:
        date: Date in YYYY-MM-DD format
        time: Time in HH:MM format
    
    Returns:
        Dictionary with cancellation confirmation or error
    """
    try:
        slot_key = f"{date}_{time}"
        
        if slot_key not in appointments_db:
            return {"success": False, "error": "No appointment found for this date and time"}
        
        cancelled_appointment = appointments_db.pop(slot_key)
        cancelled_appointment["status"] = "cancelled"
        
        return {
            "success": True,
            "message": f"Appointment cancelled for {cancelled_appointment['patient_name']} on {date} at {time}",
            "cancelled_appointment": cancelled_appointment
        }
        
    except Exception as e:
        return {"success": False, "error": f"Cancellation failed: {str(e)}"}

# Define appointment system prompt
APPOINTMENT_SYSTEM_PROMPT = """You are an appointment booking assistant. You can help patients:

1. Book new appointments
2. List existing appointments
3. Cancel appointments

Available functions:
- book_appointment(date, time, patient_name, reason): Book a new appointment
- list_appointments(date): List appointments (optional date filter)
- cancel_appointment(date, time): Cancel an existing appointment

Guidelines:
- Always use YYYY-MM-DD format for dates
- Always use HH:MM format for times (24-hour format)
- Be helpful and confirm all booking details
- Handle errors gracefully and suggest alternatives
- Ask for missing information when needed

When booking appointments:
- Confirm the patient name, date, time, and reason
- Check that the appointment is in the future
- Provide clear confirmation with appointment details

When listing appointments:
- Format the information clearly
- Show date, time, patient name, and reason
- If no appointments exist, suggest booking one

Be friendly, professional, and efficient in your responses."""

# Create a Bedrock model
bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
    region_name="us-west-2"
)

# Create an agent with appointment booking capabilities
appointment_agent = Agent(
    model=bedrock_model,
    system_prompt=APPOINTMENT_SYSTEM_PROMPT,
    tools=[book_appointment, list_appointments, cancel_appointment],
    trace_attributes={
        "session.id": "appointment-session-001",
        "user.id": "clinic@example.com",
        "tags": ["Appointment-Agent", "Healthcare", "Booking-System"]
    }
)

# Example usage
if __name__ == "__main__":
    session_id = "appointment-session-001"
    print(f"\nAppointment Booking Agent (Session: {session_id})\n")
    print("This appointment agent can help you:")
    print("  • Book new appointments")
    print("  • List existing appointments") 
    print("  • Cancel appointments")
    print("\nExample commands:")
    print("  'Book an appointment for John Doe tomorrow at 2 PM'")
    print("  'Show me all appointments for today'")
    print("  'Cancel the appointment on 2025-11-04 at 14:00'")
    print("  'exit' - Exit the program")
    
    # Interactive loop
    while True:
        try:
            user_input = input("\n> ")
            
            if user_input.lower() == "exit":
                print("\nGoodbye! Have a great day! 👋")
                break
            
            # Call the appointment agent
            response = appointment_agent(user_input)
            
            # Display the response
            print(str(response))
            
            # Log for tracing
            strands_logger.info(str(response))
            
        except KeyboardInterrupt:
            print("\n\nExecution interrupted. Exiting...")
            break
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
            print("Please try a different request.")