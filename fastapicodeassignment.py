from fastapi import FastAPI, HTTPException, status
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

app = FastAPI()

# Define models

class Patient(BaseModel):
    id: int = Field(..., gt=0, description="Unique identifier for the patient")
    name: str = Field(..., description="Patient's name")
    age: int = Field(..., gt=0, description="Patient's age")
    sex: str = Field(..., description="Patient's gender")
    weight: float = Field(..., gt=0, description="Patient's weight")
    height: float = Field(..., gt=0, description="Patient's height")
    phone: str = Field(..., description="Patient's phone number")

class Doctor(BaseModel):
    id: int = Field(..., gt=0, description="Unique identifier for the doctor")
    name: str = Field(..., description="Doctor's name")
    specialization: str = Field(..., description="Doctor's specialization")
    phone: str = Field(..., description="Doctor's phone number")
    is_available: bool = Field(True, description="Availability status of the doctor")

class Appointment(BaseModel):
    id: int = Field(..., gt=0, description="Unique identifier for the appointment")
    patient_id: int = Field(..., gt=0, description="ID of the patient")
    doctor_id: int = Field(..., gt=0, description="ID of the doctor")
    date: datetime = Field(..., description="Appointment date and time")

# In-memory data structures
patients: List[Patient] = []
doctors: List[Doctor] = []
appointments: List[Appointment] = []

# CRUD endpoints for Patients

@app.post("/patients", response_model=Patient)
def create_patient(patient: Patient):
    patients.append(patient)
    return patient

@app.get("/patients", response_model=List[Patient])
def get_patients():
    return patients

@app.get("/patients/{patient_id}", response_model=Optional[Patient])
def get_patient(patient_id: int):
    for patient in patients:
        if patient.id == patient_id:
            return patient
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

@app.put("/patients/{patient_id}", response_model=Patient)
def update_patient(patient_id: int, patient: Patient):
    for idx, p in enumerate(patients):
        if p.id == patient_id:
            patients[idx] = patient
            return patient
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

@app.delete("/patients/{patient_id}")
def delete_patient(patient_id: int):
    for idx, patient in enumerate(patients):
        if patient.id == patient_id:
            del patients[idx]
            return {"message": "Patient deleted successfully"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

# CRUD endpoints for Doctors

@app.post("/doctors", response_model=Doctor)
def create_doctor(doctor: Doctor):
    doctors.append(doctor)
    return doctor

@app.get("/doctors", response_model=List[Doctor])
def get_doctors():
    return doctors

@app.get("/doctors/{doctor_id}", response_model=Optional[Doctor])
def get_doctor(doctor_id: int):
    for doctor in doctors:
        if doctor.id == doctor_id:
            return doctor
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")

@app.put("/doctors/{doctor_id}", response_model=Doctor)
def update_doctor(doctor_id: int, doctor: Doctor):
    for idx, d in enumerate(doctors):
        if d.id == doctor_id:
            doctors[idx] = doctor
            return doctor
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")

@app.delete("/doctors/{doctor_id}")
def delete_doctor(doctor_id: int):
    for idx, doctor in enumerate(doctors):
        if doctor.id == doctor_id:
            del doctors[idx]
            return {"message": "Doctor deleted successfully"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")

# Create an appointment

@app.post("/appointments", response_model=Appointment)
def create_appointment(appointment: Appointment):
    available_doctors = [doctor for doctor in doctors if doctor.is_available]
    if not available_doctors:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No available doctors")
    # Assign the first available doctor to the appointment
    appointment.doctor_id = available_doctors[0].id
    appointments.append(appointment)
    return appointment

# Complete an appointment

@app.put("/appointments/{appointment_id}/complete")
def complete_appointment(appointment_id: int):
    for appointment in appointments:
        if appointment.id == appointment_id:
            appointment.completed = True
            for doctor in doctors:
                if doctor.id == appointment.doctor_id:
                    doctor.is_available = True
            return {"message": "Appointment completed successfully"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")

# Cancel an appointment

@app.delete("/appointments/{appointment_id}")
def cancel_appointment(appointment_id: int):
    for idx, appointment in enumerate(appointments):
        if appointment.id == appointment_id:
            del appointments[idx]
            for doctor in doctors:
                if doctor.id == appointment.doctor_id:
                    doctor.is_available = True
            return {"message": "Appointment canceled successfully"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")

# Set availability status

@app.put("/doctors/{doctor_id}/set_availability")
def set_availability(doctor_id: int, is_available: bool):
    for doctor in doctors:
        if doctor.id == doctor_id:
            doctor.is_available = is_available
            return {"message": "Availability status updated successfully"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
