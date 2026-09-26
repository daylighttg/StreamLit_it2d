# 🏥 Clinic Appointment System

A single-session **Streamlit** application that demonstrates core Object-Oriented Programming (OOP) principles through a practical clinic appointment scheduler. Built as an IT2D coursework project.

> **Persistence:** In-memory only via `st.session_state` — no database, no file I/O. Data resets when the app restarts.

## Features

- **Register Patients** — capture name, phone number, and date of birth with input validation
- **Schedule Appointments** — book a patient with a doctor, with automatic conflict detection (no double-booking a doctor at the same date/time)
- **View Appointments** — browse all appointments with status indicators (🟢 Scheduled, 🔴 Cancelled, ✅ Completed)
- **Manage Appointments** — cancel or mark appointments as completed
- **Search & Filter** *(bonus feature)* — filter appointments by patient name, doctor, and/or status

## OOP Concepts Demonstrated

| # | Concept | Where |
|---|---------|-------|
| 1 | Classes & Objects | `Appointment`, `ClinicScheduler` |
| 2 | Constructors | `__init__` in `Person`, `Patient`, `Doctor`, `Appointment`, `ClinicScheduler` |
| 3 | Encapsulation | Protected attributes (`_name`, `_phone`) with `@property` getters/setters |
| 4 | Inheritance | `Patient(Person)`, `Doctor(Person)` |
| 5 | Method Overriding | `get_role()` / `get_summary()` overridden in `Patient` and `Doctor` |
| 6 | Polymorphism | `display_person_summary(person: Person)` behaves differently per subclass |
| 7 | Abstraction | `Person(ABC)` with abstract methods `get_role()`, `get_summary()` |
| 8 | Exception Handling | Custom exception hierarchy (`ClinicException` and subclasses) |

## Tech Stack

- [Streamlit](https://streamlit.io/) — UI framework
- Python standard library: `abc`, `datetime`, `enum`

## Getting Started

### Prerequisites

- Python 3.10+ (uses `match` statements)

### Installation

```bash
git clone https://github.com/daylighttg/StreamLit_it2d.git
cd StreamLit_it2d
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run main.py
```

The app will open in your browser at `http://localhost:8501`.

## Project Structure

```
StreamLit_it2d/
├── main.py             # Application source (models, scheduler logic, Streamlit UI)
├── requirements.txt    # Python dependencies
├── .gitignore
└── README.md
```

## Usage Notes

- A few sample doctors (General Practice, Pediatrics, Cardiology, Dermatology) are pre-loaded on startup.
- All data lives in `st.session_state` for the duration of the browser session — refreshing the page resets everything.
- Appointments must be scheduled in the future, and a doctor cannot be double-booked for the same date and time.

## License

No license specified.