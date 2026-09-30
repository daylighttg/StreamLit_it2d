# Clinic Appointment System (Streamlit)
# data is only saved in st.session_state, no database

from abc import ABC, abstractmethod
from datetime import datetime, date, time, timedelta
from enum import Enum
import re
import streamlit as st


# custom exceptions (exception handling)
class ClinicException(Exception):
    pass


class PatientNotFoundError(ClinicException):
    pass


class AppointmentNotFoundError(ClinicException):
    pass


class AppointmentConflictError(ClinicException):
    pass


class InvalidInputError(ClinicException):
    pass


def clean_phone(value: str) -> str:
    return re.sub(r"[\s\-]", "", value or "")


# abstraction: abstract class, Patient and Doctor inherit from this
class Person(ABC):

    # constructor
    def __init__(self, name: str, phone: str) -> None:
        # encapsulation: _ means protected, use the property to get it
        self._name = name
        self.phone = phone

    @property
    def name(self) -> str:
        return self._name

    @property
    def phone(self) -> str:
        return self._phone

    # setter with validation
    @phone.setter
    def phone(self, value: str) -> None:
        value = clean_phone(value)
        if not value:
            raise InvalidInputError("Phone number cannot be empty.")
        if not value.isdigit():
            raise InvalidInputError("Phone number must contain digits only.")
        self._phone = value

    # abstract methods, the child classes must override these
    @abstractmethod
    def get_role(self) -> str:
        ...

    @abstractmethod
    def get_summary(self) -> str:
        ...


# inheritance
class Patient(Person):

    def __init__(self, patient_id: int, name: str, phone: str,
                 date_of_birth: date) -> None:
        super().__init__(name, phone)
        self._patient_id = patient_id
        self._date_of_birth = date_of_birth

    @property
    def patient_id(self) -> int:
        return self._patient_id

    @property
    def date_of_birth(self) -> date:
        return self._date_of_birth

    # method overriding
    def get_role(self) -> str:
        return "Patient"

    def get_summary(self) -> str:
        return f"Patient #{self._patient_id}: {self._name} (DOB: {self._date_of_birth})"


class Doctor(Person):

    def __init__(self, name: str, phone: str, specialty: str) -> None:
        super().__init__(name, phone)
        self._specialty = specialty

    @property
    def specialty(self) -> str:
        return self._specialty

    # overriding again, same method but different output (polymorphism)
    def get_role(self) -> str:
        return "Doctor"

    def get_summary(self) -> str:
        return f"Dr. {self._name} — {self._specialty}"


class AppointmentStatus(Enum):
    SCHEDULED = "Scheduled"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"


# class and objects
class Appointment:

    def __init__(self, appointment_id: int, patient: Patient, doctor: Doctor,
                 date_time: datetime, reason: str) -> None:
        self._appointment_id = appointment_id
        self._patient = patient
        self._doctor = doctor
        self._date_time = date_time
        self._reason = reason
        self._status = AppointmentStatus.SCHEDULED

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
        if self._status == AppointmentStatus.CANCELLED:
            raise ClinicException("This appointment is already cancelled.")
        if self._status == AppointmentStatus.COMPLETED:
            raise ClinicException("Cannot cancel a completed appointment.")
        self._status = AppointmentStatus.CANCELLED

    def complete(self) -> None:
        if self._status != AppointmentStatus.SCHEDULED:
            raise ClinicException(
                f"Cannot complete an appointment with status '{self._status.value}'."
            )
        self._status = AppointmentStatus.COMPLETED


class ClinicScheduler:

    def __init__(self) -> None:
        self._patients: list[Patient] = []
        self._appointments: list[Appointment] = []
        self._doctors: list[Doctor] = [
            Doctor("Alice Smith", "5550101", "General Practice"),
            Doctor("Bob Johnson", "5550102", "Pediatrics"),
            Doctor("Carol Williams", "5550103", "Cardiology"),
            Doctor("David Lee", "5550104", "Dermatology"),
        ]
        self._next_patient_id: int = 1
        self._next_appointment_id: int = 1

    @property
    def patients(self) -> list[Patient]:
        return list(self._patients)

    @property
    def doctors(self) -> list[Doctor]:
        return list(self._doctors)

    @property
    def appointments(self) -> list[Appointment]:
        return list(self._appointments)

    def register_patient(self, name: str, phone: str,
                         date_of_birth: date) -> Patient:
        if not name.strip():
            raise InvalidInputError("Patient name is required.")
        phone = clean_phone(phone)
        if not phone:
            raise InvalidInputError("Phone number is required.")
        if not phone.isdigit():
            raise InvalidInputError("Phone number must contain digits only.")
        if date_of_birth > date.today():
            raise InvalidInputError("Date of birth cannot be in the future.")

        patient = Patient(
            self._next_patient_id, name.strip(), phone, date_of_birth
        )
        self._patients.append(patient)
        self._next_patient_id += 1
        return patient

    def find_patient(self, patient_id: int) -> Patient:
        for p in self._patients:
            if p.patient_id == patient_id:
                return p
        raise PatientNotFoundError(f"No patient found with ID #{patient_id}.")

    def schedule_appointment(self, patient_id: int, doctor_name: str,
                             appt_date: date, appt_time: time,
                             reason: str) -> Appointment:
        patient = self.find_patient(patient_id)
        doctor = self._find_doctor_by_name(doctor_name)

        if not reason.strip():
            raise InvalidInputError("Reason for visit is required.")

        appt_datetime = datetime.combine(appt_date, appt_time)
        if appt_datetime <= datetime.now():
            raise InvalidInputError("Appointment must be scheduled in the future.")

        # check if the doctor already has an appointment at that time
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
        appt.cancel()
        return appt

    def complete_appointment(self, appointment_id: int) -> Appointment:
        appt = self._find_appointment(appointment_id)
        appt.complete()
        return appt

    def search_appointments(self, patient_name: str = "",
                            doctor_name: str = "All",
                            status_filter: str = "All") -> list[Appointment]:
        results = self._appointments
        if patient_name:
            results = [a for a in results
                       if patient_name.lower() in a.patient.name.lower()]
        if doctor_name and doctor_name != "All":
            results = [a for a in results if a.doctor.name == doctor_name]
        if status_filter and status_filter != "All":
            results = [a for a in results if a.status.value == status_filter]
        return results

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


# polymorphism: works for both Patient and Doctor
def display_person_summary(person: Person) -> str:
    return f"[{person.get_role()}] {person.get_summary()}"


def get_scheduler() -> ClinicScheduler:
    if "scheduler" not in st.session_state:
        # creating the object
        st.session_state.scheduler = ClinicScheduler()
    else:
        _rebind_to_current_classes(st.session_state.scheduler)
    return st.session_state.scheduler


def _rebind_to_current_classes(sch) -> None:
    # streamlit reruns the file every click, so the saved objects still use the old classes
    # this reattaches them to the current ones
    sch.__class__ = ClinicScheduler
    for p in sch._patients:
        p.__class__ = Patient
    for d in sch._doctors:
        d.__class__ = Doctor
    for a in sch._appointments:
        a.__class__ = Appointment
        a._status = AppointmentStatus(a._status.value)


# pages
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
        try:
            # if the input is invalid it raises an exception
            patient = scheduler.register_patient(name, phone, dob)
            st.success(f"✅ Registered successfully — {patient.get_summary()}")
        except ClinicException as e:
            st.error(f"❌ {e}")

    if scheduler.patients:
        st.subheader("Registered Patients")
        for p in scheduler.patients:
            st.write(display_person_summary(p))


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
        default_date = date.today() + timedelta(days=1)
        appt_date = st.date_input("Date", value=default_date, min_value=date.today())
        appt_time = st.time_input("Time", value=time(9, 0))
        reason = st.text_area("Reason for Visit")
        submitted = st.form_submit_button("Schedule Appointment")

    if submitted:
        try:
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
                st.toast(f"✅ Appointment #{selected_id} has been cancelled.")
                st.rerun()
            except ClinicException as e:
                st.error(f"❌ {e}")
    with col2:
        if st.button("✅ Mark as Completed"):
            try:
                scheduler.complete_appointment(selected_id)
                st.toast(f"✅ Appointment #{selected_id} marked as completed.")
                st.rerun()
            except ClinicException as e:
                st.error(f"❌ {e}")


# additional feature: search and filter
def page_search_filter(scheduler: ClinicScheduler) -> None:
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


def main() -> None:
    st.set_page_config(
        page_title="Clinic Appointment System", page_icon="🏥", layout="wide"
    )
    st.title("🏥 Clinic Appointment System")

    scheduler = get_scheduler()

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

    st.sidebar.markdown("---")
    st.sidebar.subheader("📌 Staff Directory")
    for doc in scheduler.doctors:
        st.sidebar.caption(display_person_summary(doc))

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