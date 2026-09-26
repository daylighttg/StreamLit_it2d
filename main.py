"""
Clinic Appointment System — Streamlit Application
==================================================
A single-session appointment management app demonstrating OOP principles.
Persistence: st.session_state only (no database, no file I/O).
Additional feature: Search & Filter Appointments.
"""

import streamlit as st
from abc import ABC, abstractmethod
from datetime import datetime, date, time
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════════
#  OOP 8: Exception Handling — Custom exception hierarchy
# ═══════════════════════════════════════════════════════════════════════════

class ClinicException(Exception):                    # Custom exception base class
    """Base exception for all clinic-related errors."""
    pass


class PatientNotFoundError(ClinicException):         # Custom exception subclass
    """Raised when a patient lookup fails."""
    pass


class AppointmentNotFoundError(ClinicException):
    """Raised when an appointment lookup fails."""
    pass


class AppointmentConflictError(ClinicException):
    """Raised when a scheduling conflict is detected."""
    pass


class InvalidInputError(ClinicException):
    """Raised when user-supplied data fails validation."""
    pass


# ═══════════════════════════════════════════════════════════════════════════
#  OOP 7: Abstraction — Abstract base class using abc.ABC
# ═══════════════════════════════════════════════════════════════════════════

class Person(ABC):                                   # Abstraction: abstract base class
    """Abstract representation of a person in the clinic system."""

    # OOP 2: Constructor (__init__)
    def __init__(self, name: str, phone: str) -> None:
        # OOP 3: Encapsulation — protected attributes prefixed with _
        self._name = name
        self._phone = phone

    # OOP 3: Encapsulation — property getters / setters
    @property
    def name(self) -> str:
        return self._name

    @property
    def phone(self) -> str:
        return self._phone

    @phone.setter                                    # Encapsulation: setter with validation
    def phone(self, value: str) -> None:
        if not value.strip():
            raise InvalidInputError("Phone number cannot be empty.")
        self._phone = value

    # OOP 7: Abstraction — abstract methods (must be overridden)
    @abstractmethod
    def get_role(self) -> str:
        """Return the role label for this person."""
        ...

    @abstractmethod
    def get_summary(self) -> str:
        """Return a human-readable summary string."""
        ...


# ═══════════════════════════════════════════════════════════════════════════
#  OOP 4: Inheritance — Patient and Doctor extend Person
# ═══════════════════════════════════════════════════════════════════════════

class Patient(Person):                               # Inheritance: Patient extends Person
    """A registered patient in the clinic."""

    # OOP 2: Constructor
    def __init__(self, patient_id: int, name: str, phone: str,
                 date_of_birth: date) -> None:
        super().__init__(name, phone)
        self._patient_id = patient_id                # Encapsulation: private-by-convention
        self._date_of_birth = date_of_birth

    @property
    def patient_id(self) -> int:
        return self._patient_id

    @property
    def date_of_birth(self) -> date:
        return self._date_of_birth

    # OOP 5: Method Overriding — overrides abstract Person.get_role()
    def get_role(self) -> str:
        return "Patient"

    # OOP 5: Method Overriding — overrides abstract Person.get_summary()
    def get_summary(self) -> str:
        return f"Patient #{self._patient_id}: {self._name} (DOB: {self._date_of_birth})"


class Doctor(Person):                                # Inheritance: Doctor extends Person
    """A doctor on staff at the clinic."""

    def __init__(self, name: str, phone: str, specialty: str) -> None:
        super().__init__(name, phone)
        self._specialty = specialty

    @property
    def specialty(self) -> str:
        return self._specialty

    # OOP 5 & 6: Method Overriding + Polymorphism — same interface, different output
    def get_role(self) -> str:
        return "Doctor"

    def get_summary(self) -> str:
        return f"Dr. {self._name} — {self._specialty}"


# ═══════════════════════════════════════════════════════════════════════════
#  OOP 1: Classes & Objects — Appointment and ClinicScheduler
# ═══════════════════════════════════════════════════════════════════════════

class AppointmentStatus(Enum):
    SCHEDULED = "Scheduled"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"


class Appointment:                                   # Classes & Objects
    """Represents a scheduled appointment between a patient and a doctor."""

    # OOP 2: Constructor
    def __init__(self, appointment_id: int, patient: Patient, doctor: Doctor,
                 date_time: datetime, reason: str) -> None:
        self._appointment_id = appointment_id
        self._patient = patient
        self._doctor = doctor
        self._date_time = date_time
        self._reason = reason
        self._status = AppointmentStatus.SCHEDULED   # Encapsulation: managed via methods

    # OOP 3: Encapsulation — read-only properties
    @property
    def appointment_id(self) -> int:
        return self._appointment_id

    @property
    def patient(self) -> Patient:
        return self._patient

    @property
    def doctor(self) -> Doctor:
        return self._doctor

    @property
    def date_time(self) -> datetime:
        return self._date_time

    @property
    def reason(self) -> str:
        return self._reason

    @property
    def status(self) -> AppointmentStatus:
        return self._status

    def cancel(self) -> None:
        """Cancel this appointment, enforcing business rules."""
        if self._status == AppointmentStatus.CANCELLED:
            raise ClinicException("This appointment is already cancelled.")
        if self._status == AppointmentStatus.COMPLETED:
            raise ClinicException("Cannot cancel a completed appointment.")
        self._status = AppointmentStatus.CANCELLED

    def complete(self) -> None:
        """Mark this appointment as completed."""
        if self._status != AppointmentStatus.SCHEDULED:
            raise ClinicException(
                f"Cannot complete an appointment with status '{self._status.value}'."
            )
        self._status = AppointmentStatus.COMPLETED


class ClinicScheduler:                               # Classes & Objects
    """Central coordinator managing patients, doctors, and appointments."""

    def __init__(self) -> None:
        self._patients: list[Patient] = []           # Persistence via Python lists
        self._appointments: list[Appointment] = []
        self._doctors: list[Doctor] = [
            Doctor("Alice Smith", "555-0101", "General Practice"),
            Doctor("Bob Johnson", "555-0102", "Pediatrics"),
            Doctor("Carol Williams", "555-0103", "Cardiology"),
            Doctor("David Lee", "555-0104", "Dermatology"),
        ]
        self._next_patient_id: int = 1
        self._next_appointment_id: int = 1

    # ── Public read-only accessors ──────────────────────────────
    @property
    def patients(self) -> list[Patient]:
        return list(self._patients)

    @property
    def doctors(self) -> list[Doctor]:
        return list(self._doctors)

    @property
    def appointments(self) -> list[Appointment]:
        return list(self._appointments)

    # ── Patient management ──────────────────────────────────────
    def register_patient(self, name: str, phone: str,
                         date_of_birth: date) -> Patient:
        """Validate inputs and register a new patient."""
        if not name.strip():
            raise InvalidInputError("Patient name is required.")
        if not phone.strip():
            raise InvalidInputError("Phone number is required.")
        if date_of_birth >= date.today():
            raise InvalidInputError("Date of birth must be in the past.")

        patient = Patient(
            self._next_patient_id, name.strip(), phone.strip(), date_of_birth
        )
        self._patients.append(patient)
        self._next_patient_id += 1
        return patient

    def find_patient(self, patient_id: int) -> Patient:
        for p in self._patients:
            if p.patient_id == patient_id:
                return p
        raise PatientNotFoundError(f"No patient found with ID #{patient_id}.")

    # ── Appointment management ──────────────────────────────────
    def schedule_appointment(self, patient_id: int, doctor_name: str,
                             appt_date: date, appt_time: time,
                             reason: str) -> Appointment:
        """Validate, check conflicts, and create a new appointment."""
        patient = self.find_patient(patient_id)
        doctor = self._find_doctor_by_name(doctor_name)

        if not reason.strip():
            raise InvalidInputError("Reason for visit is required.")

        appt_datetime = datetime.combine(appt_date, appt_time)
        if appt_datetime <= datetime.now():
            raise InvalidInputError("Appointment must be scheduled in the future.")

        # Conflict check: same doctor at the same date-time
        for existing in self._appointments:
            if (existing.doctor.name == doctor.name
                    and existing.date_time == appt_datetime
                    and existing.status == AppointmentStatus.SCHEDULED):
                raise AppointmentConflictError(
                    f"Dr. {doctor.name} already has an appointment at "
                    f"{appt_datetime:%Y-%m-%d %H:%M}."
                )

        appointment = Appointment(
            self._next_appointment_id, patient, doctor, appt_datetime, reason.strip()
        )
        self._appointments.append(appointment)
        self._next_appointment_id += 1
        return appointment

    def cancel_appointment(self, appointment_id: int) -> Appointment:
        appt = self._find_appointment(appointment_id)
        appt.cancel()                               # OOP 8: may raise ClinicException
        return appt

    def complete_appointment(self, appointment_id: int) -> Appointment:
        appt = self._find_appointment(appointment_id)
        appt.complete()
        return appt

    # ── Additional Feature: Search & Filter ─────────────────────
    def search_appointments(self, patient_name: str = "",
                            doctor_name: str = "All",
                            status_filter: str = "All") -> list[Appointment]:
        """Filter appointments by patient name, doctor, and/or status."""
        results = self._appointments
        if patient_name:
            results = [a for a in results
                       if patient_name.lower() in a.patient.name.lower()]
        if doctor_name and doctor_name != "All":
            results = [a for a in results if a.doctor.name == doctor_name]
        if status_filter and status_filter != "All":
            results = [a for a in results if a.status.value == status_filter]
        return results

    # ── Private helpers ─────────────────────────────────────────
    def _find_doctor_by_name(self, name: str) -> Doctor:
        for d in self._doctors:
            if d.name == name:
                return d
        raise ClinicException(f"Doctor '{name}' not found.")

    def _find_appointment(self, appointment_id: int) -> Appointment:
        for a in self._appointments:
            if a.appointment_id == appointment_id:
                return a
        raise AppointmentNotFoundError(
            f"No appointment found with ID #{appointment_id}."
        )


# ═══════════════════════════════════════════════════════════════════════════
#  OOP 6: Polymorphism — a single function handles any Person subclass
# ═══════════════════════════════════════════════════════════════════════════

def display_person_summary(person: Person) -> str:   # Polymorphism: same call, different result
    """Accepts any Person; output varies for Patient vs Doctor."""
    return f"[{person.get_role()}] {person.get_summary()}"


# ═══════════════════════════════════════════════════════════════════════════
#  Streamlit UI
# ═══════════════════════════════════════════════════════════════════════════

def get_scheduler() -> ClinicScheduler:
    """Retrieve or initialize the ClinicScheduler stored in session state."""
    if "scheduler" not in st.session_state:
        # OOP 1: Creating an object from a class
        st.session_state.scheduler = ClinicScheduler()
    return st.session_state.scheduler


# ── Page: Register Patient ──────────────────────────────────────────────

def page_register_patient(scheduler: ClinicScheduler) -> None:
    st.header("📋 Register Patient")

    with st.form("register_form", clear_on_submit=True):
        name = st.text_input("Full Name")
        phone = st.text_input("Phone Number")
        dob = st.date_input(
            "Date of Birth",
            value=date(2000, 1, 1),
            min_value=date(1900, 1, 1),
            max_value=date.today(),
        )
        submitted = st.form_submit_button("Register Patient")

    if submitted:
        try:                                         # OOP 8: Exception handling around user input
            patient = scheduler.register_patient(name, phone, dob)
            st.success(f"✅ Registered successfully — {patient.get_summary()}")
        except ClinicException as e:
            st.error(f"❌ {e}")

    # Show registered patients
    if scheduler.patients:
        st.subheader("Registered Patients")
        for p in scheduler.patients:
            # Polymorphism in action: display_person_summary works on Patient
            st.write(display_person_summary(p))


# ── Page: Schedule Appointment ──────────────────────────────────────────

def page_schedule_appointment(scheduler: ClinicScheduler) -> None:
    st.header("📅 Schedule Appointment")

    if not scheduler.patients:
        st.warning("No patients registered yet. Please register a patient first.")
        return

    patient_options = {
        f"#{p.patient_id} — {p.name}": p.patient_id
        for p in scheduler.patients
    }
    doctor_names = [d.name for d in scheduler.doctors]

    with st.form("schedule_form"):
        patient_choice = st.selectbox("Patient", list(patient_options.keys()))
        doctor_choice = st.selectbox(
            "Doctor",
            doctor_names,
            format_func=lambda n: (
                f"Dr. {n} — "
                f"{next(d.specialty for d in scheduler.doctors if d.name == n)}"
            ),
        )
        appt_date = st.date_input("Date", min_value=date.today())
        appt_time = st.time_input("Time", value=time(9, 0))
        reason = st.text_area("Reason for Visit")
        submitted = st.form_submit_button("Schedule Appointment")

    if submitted:
        try:                                         # OOP 8: Exception handling
            patient_id = patient_options[patient_choice]
            appt = scheduler.schedule_appointment(
                patient_id, doctor_choice, appt_date, appt_time, reason
            )
            st.success(
                f"✅ Appointment #{appt.appointment_id} scheduled — "
                f"{appt.patient.name} with Dr. {appt.doctor.name} on "
                f"{appt.date_time:%Y-%m-%d at %H:%M}."
            )
        except ClinicException as e:
            st.error(f"❌ {e}")


# ── Page: View Appointments ─────────────────────────────────────────────

def page_view_appointments(scheduler: ClinicScheduler) -> None:
    st.header("👁️ View Appointments")

    if not scheduler.appointments:
        st.info("No appointments have been scheduled yet.")
        return

    status_icons = {"Scheduled": "🟢", "Cancelled": "🔴", "Completed": "✅"}

    for appt in scheduler.appointments:
        icon = status_icons.get(appt.status.value, "⚪")
        with st.expander(
            f"{icon} Appt #{appt.appointment_id} — {appt.patient.name} "
            f"({appt.status.value})"
        ):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Patient:** {appt.patient.name}")
                st.markdown(
                    f"**Doctor:** Dr. {appt.doctor.name} ({appt.doctor.specialty})"
                )
                st.markdown(f"**Reason:** {appt.reason}")
            with col2:
                st.markdown(f"**Date/Time:** {appt.date_time:%Y-%m-%d %H:%M}")
                st.markdown(f"**Status:** {appt.status.value}")


# ── Page: Manage / Cancel Appointments ──────────────────────────────────

def page_manage_appointments(scheduler: ClinicScheduler) -> None:
    st.header("⚙️ Manage Appointments")

    active = [
        a for a in scheduler.appointments
        if a.status == AppointmentStatus.SCHEDULED
    ]

    if not active:
        st.info("No active (scheduled) appointments to manage.")
        return

    appt_options = {
        (
            f"#{a.appointment_id} — {a.patient.name} → "
            f"Dr. {a.doctor.name} ({a.date_time:%Y-%m-%d %H:%M})"
        ): a.appointment_id
        for a in active
    }

    selected_label = st.selectbox("Select Appointment", list(appt_options.keys()))
    selected_id = appt_options[selected_label]

    col1, col2 = st.columns(2)
    with col1:
        if st.button("❌ Cancel Appointment", type="primary"):
            try:
                scheduler.cancel_appointment(selected_id)
                st.success(f"Appointment #{selected_id} has been cancelled.")
                st.rerun()
            except ClinicException as e:
                st.error(f"❌ {e}")
    with col2:
        if st.button("✅ Mark as Completed"):
            try:
                scheduler.complete_appointment(selected_id)
                st.success(f"Appointment #{selected_id} marked as completed.")
                st.rerun()
            except ClinicException as e:
                st.error(f"❌ {e}")


# ── Page: Search & Filter (Additional Feature) ─────────────────────────

def page_search_filter(scheduler: ClinicScheduler) -> None:
    """Additional Feature: Search & Filter appointments by multiple criteria."""
    st.header("🔎 Search & Filter Appointments")

    if not scheduler.appointments:
        st.info("No appointments to search. Schedule some first!")
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        search_name = st.text_input("Patient Name", placeholder="e.g. John")
    with col2:
        doctor_filter = st.selectbox(
            "Doctor", ["All"] + [d.name for d in scheduler.doctors]
        )
    with col3:
        status_filter = st.selectbox(
            "Status", ["All"] + [s.value for s in AppointmentStatus]
        )

    results = scheduler.search_appointments(search_name, doctor_filter, status_filter)

    status_icons = {"Scheduled": "🟢", "Cancelled": "🔴", "Completed": "✅"}

    if results:
        st.markdown(f"**{len(results)} result(s) found:**")
        for appt in results:
            icon = status_icons.get(appt.status.value, "⚪")
            st.markdown(
                f"{icon} **Appt #{appt.appointment_id}** — "
                f"{appt.patient.name} → Dr. {appt.doctor.name} | "
                f"{appt.date_time:%Y-%m-%d %H:%M} | _{appt.status.value}_"
            )
    else:
        st.warning("No appointments match the selected filters.")


# ═══════════════════════════════════════════════════════════════════════════
#  Main entry point
# ═══════════════════════════════════════════════════════════════════════════

def main() -> None:
    st.set_page_config(
        page_title="Clinic Appointment System", page_icon="🏥", layout="wide"
    )
    st.title("🏥 Clinic Appointment System")

    scheduler = get_scheduler()

    # Sidebar navigation
    page = st.sidebar.radio(
        "Navigation",
        [
            "Register Patient",
            "Schedule Appointment",
            "View Appointments",
            "Manage Appointments",
            "Search & Filter",
        ],
    )

    # Staff directory in sidebar — demonstrates Polymorphism on Doctor objects
    st.sidebar.markdown("---")
    st.sidebar.subheader("📌 Staff Directory")
    for doc in scheduler.doctors:
        # Polymorphism: display_person_summary handles Doctor just like Patient
        st.sidebar.caption(display_person_summary(doc))

    # Route to the selected page
    match page:
        case "Register Patient":
            page_register_patient(scheduler)
        case "Schedule Appointment":
            page_schedule_appointment(scheduler)
        case "View Appointments":
            page_view_appointments(scheduler)
        case "Manage Appointments":
            page_manage_appointments(scheduler)
        case "Search & Filter":
            page_search_filter(scheduler)


if __name__ == "__main__":
    main()


# ═══════════════════════════════════════════════════════════════════════════
#  OOP Concept Map — exact locations
# ═══════════════════════════════════════════════════════════════════════════
#
#  1. Classes & Objects
#     → class Appointment, class ClinicScheduler, instantiation in get_scheduler()
#
#  2. Constructor (__init__)
#     → Person.__init__, Patient.__init__, Doctor.__init__,
#       Appointment.__init__, ClinicScheduler.__init__
#
#  3. Encapsulation (private/protected attrs + properties)
#     → Person._name, Person._phone with @property getters and @phone.setter
#     → Patient._patient_id, Appointment._status (read-only property)
#
#  4. Inheritance
#     → Patient(Person), Doctor(Person) — both extend the abstract base class
#
#  5. Method Overriding
#     → Patient.get_role() and Patient.get_summary() override Person's abstract methods
#     → Doctor.get_role() and Doctor.get_summary() override Person's abstract methods
#
#  6. Polymorphism
#     → display_person_summary(person: Person) — same function call produces
#       different output for Patient vs Doctor instances
#     → Used in page_register_patient (Patient) and sidebar (Doctor)
#
#  7. Abstraction
#     → class Person(ABC) with @abstractmethod get_role() and get_summary()
#
#  8. Exception Handling
#     → Custom hierarchy: ClinicException → PatientNotFoundError,
#       AppointmentNotFoundError, AppointmentConflictError, InvalidInputError
#     → try/except blocks in every page function (register, schedule, manage)
#
# ═══════════════════════════════════════════════════════════════════════════
