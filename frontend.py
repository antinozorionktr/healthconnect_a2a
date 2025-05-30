# hospital_a2a_frontend.py
import streamlit as st
import httpx
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import asyncio
import time

# Configuration
AGENT_URLS = {
    "coordinator": "http://localhost:8000",
    "patient": "http://localhost:8001",
    "doctor": "http://localhost:8002",
    "booking": "http://localhost:8003"
}

# Helper Functions
async def get_agent_card(agent_type: str) -> Optional[Dict]:
    """Get agent card for discovery"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{AGENT_URLS[agent_type]}/.well-known/agent.json", timeout=5.0)
            return response.json()
    except Exception as e:
        st.error(f"Error getting agent card for {agent_type}: {str(e)}")
        return None

async def send_message(agent_type: str, message_text: str) -> Dict:
    """Send message to agent using A2A protocol"""
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "message/send",
            "params": {
                "message": {
                    "role": "user",
                    "parts": [{"kind": "text", "text": message_text}],
                    "messageId": str(uuid.uuid4())
                }
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{AGENT_URLS[agent_type]}/a2a/v1", json=payload, timeout=10.0)
            return response.json()
    except Exception as e:
        return {"error": {"message": str(e)}}

def display_response(response: Dict):
    """Display A2A response in a user-friendly way"""
    if "error" in response:
        st.error(f"Error: {response['error']['message']}")
        return
    
    result = response.get("result", {})
    status = result.get("status", {})
    
    if status.get("state"):
        st.success(f"Status: {status['state']}")
    
    if "message" in status:
        message = status["message"]
        for part in message.get("parts", []):
            if part["kind"] == "text":
                st.info(part["text"])
            elif part["kind"] == "data":
                st.json(part["data"])

# Async helper to run coroutines in Streamlit
def run_async(coro):
    """Run async coroutine in Streamlit context"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    finally:
        loop.close()

# Page Layout
st.set_page_config(
    page_title="Hospital A2A System",
    page_icon="🏥",
    layout="wide"
)

# Sidebar - System Status
st.sidebar.title("System Status")
status_cols = st.sidebar.columns(2)

# Check all agents status
for i, agent_type in enumerate(AGENT_URLS.keys()):
    with status_cols[i % 2]:
        try:
            card = run_async(get_agent_card(agent_type))
            if card:
                st.success(f"✅ {agent_type.capitalize()}")
            else:
                st.error(f"❌ {agent_type.capitalize()}")
        except:
            st.error(f"❌ {agent_type.capitalize()}")

# Main App
st.title("🏥 Hospital Appointment Booking System")
st.markdown("""
This interface connects to the Hospital A2A (Agent-to-Agent) system that implements a distributed 
appointment booking system using specialized agents communicating via the A2A protocol.
""")

# Tabs for different functionalities
tab1, tab2, tab3, tab4 = st.tabs([
    "Patient Registration", 
    "Doctor Search", 
    "Appointment Booking", 
    "Coordinator Workflow"
])

# Patient Registration Tab
with tab1:
    st.header("Patient Registration")
    st.markdown("Register new patients or look up existing patient records.")
    
    reg_option = st.radio("Action:", ["Register New Patient", "Lookup Existing Patient"], key="reg_option")
    
    if reg_option == "Register New Patient":
        with st.form("patient_registration"):
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone Number")
            
            submitted = st.form_submit_button("Register Patient")
            if submitted:
                if not all([name, email, phone]):
                    st.error("Please fill in all fields")
                else:
                    message = f"""Register new patient:
                    Name: {name}
                    Email: {email}
                    Phone: {phone}"""
                    
                    with st.spinner("Registering patient..."):
                        response = run_async(send_message("patient", message))
                        display_response(response)
    
    else:  # Lookup
        with st.form("patient_lookup"):
            lookup_by = st.radio("Lookup by:", ["Email", "Medical Record Number"], key="lookup_by")
            
            if lookup_by == "Email":
                email = st.text_input("Patient Email", key="patient_email")
                submitted = st.form_submit_button("Find Patient")
                if submitted:
                    if not email:
                        st.error("Please enter an email address")
                    else:
                        with st.spinner("Searching for patient..."):
                            response = run_async(send_message("patient", f"lookup patient by email: {email}"))
                            display_response(response)
            else:
                mrn = st.text_input("Medical Record Number (e.g., MR123456)", key="patient_mrn")
                submitted = st.form_submit_button("Find Patient")
                if submitted:
                    if not mrn:
                        st.error("Please enter a medical record number")
                    else:
                        with st.spinner("Searching for patient..."):
                            response = run_async(send_message("patient", f"lookup patient by medical record number: {mrn}"))
                            display_response(response)

# Doctor Search Tab
with tab2:
    st.header("Doctor Search & Availability")
    st.markdown("Find doctors by specialty or check their availability.")
    
    search_option = st.radio("Action:", ["Search Doctors", "Check Availability"], key="search_option")
    
    if search_option == "Search Doctors":
        with st.form("doctor_search"):
            specialty = st.selectbox(
                "Specialty",
                ["Cardiology", "Dermatology", "Pediatrics", "Orthopedics", "Emergency Medicine", "All"],
                key="doctor_specialty"
            )
            
            submitted = st.form_submit_button("Find Doctors")
            if submitted:
                query = "Find all doctors" if specialty == "All" else f"Find {specialty.lower()} specialists"
                with st.spinner("Searching for doctors..."):
                    response = run_async(send_message("doctor", query))
                    display_response(response)
    
    else:  # Check Availability
        with st.form("availability_check"):
            doctor_name = st.text_input("Doctor Name (optional)", key="doctor_name")
            department = st.selectbox(
                "Department (optional)",
                ["", "Cardiology", "Dermatology", "Pediatrics", "Orthopedics", "Emergency Medicine"],
                key="doctor_dept"
            )
            date_range = st.selectbox(
                "Date Range",
                ["Next 3 days", "This week", "Next 2 weeks"],
                key="date_range"
            )
            
            submitted = st.form_submit_button("Check Availability")
            if submitted:
                query_parts = []
                if doctor_name:
                    query_parts.append(f"Find {doctor_name}'s availability")
                if department:
                    query_parts.append(f"in {department}")
                query_parts.append(f"for {date_range.lower()}")
                
                with st.spinner("Checking availability..."):
                    response = run_async(send_message("doctor", " ".join(query_parts)))
                    display_response(response)

# Appointment Booking Tab
with tab3:
    st.header("Appointment Booking")
    st.markdown("Book, view, or cancel appointments.")
    
    booking_option = st.radio("Action:", ["Book Appointment", "View Appointments", "Cancel Appointment"], key="booking_option")
    
    if booking_option == "Book Appointment":
        with st.form("book_appointment"):
            patient_id = st.text_input("Patient ID or Medical Record Number", key="book_patient_id")
            doctor_id = st.text_input("Doctor ID (optional)", key="book_doctor_id")
            department = st.selectbox(
                "Department",
                ["Cardiology", "Dermatology", "Pediatrics", "Orthopedics", "Emergency Medicine"],
                key="book_dept"
            )
            preferred_date = st.date_input("Preferred Date", min_value=datetime.now().date(), key="book_date")
            preferred_time = st.time_input("Preferred Time", key="book_time")
            
            submitted = st.form_submit_button("Book Appointment")
            if submitted:
                if not patient_id:
                    st.error("Please provide patient information")
                else:
                    datetime_str = f"{preferred_date}T{preferred_time.hour:02d}:00:00"
                    message = f"""Book appointment:
                    Patient: {patient_id}
                    {"Doctor: " + doctor_id if doctor_id else "Department: " + department}
                    Time: {datetime_str}"""
                    
                    with st.spinner("Booking appointment..."):
                        response = run_async(send_message("booking", message))
                        display_response(response)
    
    elif booking_option == "View Appointments":
        with st.form("view_appointments"):
            patient_id = st.text_input("Patient ID or Medical Record Number", key="view_patient_id")
            
            submitted = st.form_submit_button("View Appointments")
            if submitted:
                if not patient_id:
                    st.error("Please provide patient information")
                else:
                    with st.spinner("Retrieving appointments..."):
                        response = run_async(send_message("booking", f"view appointments for patient {patient_id}"))
                        display_response(response)
    
    else:  # Cancel Appointment
        with st.form("cancel_appointment"):
            appointment_id = st.text_input("Appointment ID", key="cancel_appt_id")
            
            submitted = st.form_submit_button("Cancel Appointment")
            if submitted:
                if not appointment_id:
                    st.error("Please provide an appointment ID")
                else:
                    with st.spinner("Canceling appointment..."):
                        response = run_async(send_message("booking", f"cancel appointment {appointment_id}"))
                        display_response(response)

# Coordinator Workflow Tab
with tab4:
    st.header("Complete Appointment Workflow")
    st.markdown("""
    Use the coordinator agent to handle the complete appointment booking workflow:
    1. Patient registration/lookup
    2. Doctor search
    3. Availability check
    4. Appointment booking
    """)
    
    with st.form("coordinator_workflow"):
        patient_info = st.text_area("Patient Information", 
                                  placeholder="e.g., 'John Doe with email john@example.com'",
                                  key="coord_patient")
        doctor_preference = st.text_input("Doctor/Department Preference", 
                                        placeholder="e.g., 'Dr. Smith' or 'Cardiology department'",
                                        key="coord_doctor")
        time_preference = st.text_input("Time Preference (optional)", 
                                      placeholder="e.g., 'next Monday' or 'this week'",
                                      key="coord_time")
        
        submitted = st.form_submit_button("Run Complete Workflow")
        if submitted:
            if not patient_info:
                st.error("Please provide patient information")
            else:
                message = f"Book appointment for {patient_info}"
                if doctor_preference:
                    message += f" with {doctor_preference}"
                if time_preference:
                    message += f" for {time_preference}"
                
                with st.spinner("Running complete workflow..."):
                    response = run_async(send_message("coordinator", message))
                    display_response(response)

# About Section
st.sidebar.markdown("---")
st.sidebar.header("About")
st.sidebar.markdown("""
This is a frontend for the **Hospital A2A System** that demonstrates:

- **Agent-to-Agent (A2A) communication**
- **Distributed hospital services**
- **Appointment booking workflow**

The backend system consists of specialized agents:
- Coordinator (Port 8000)
- Patient Registration (Port 8001)
- Doctor Availability (Port 8002)
- Appointment Booking (Port 8003)
""")