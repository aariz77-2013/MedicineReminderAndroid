
import sqlite3
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder

DB_FILE = "medicines.db"

KV = """
BoxLayout:
    orientation: "vertical"
    padding: 12
    spacing: 8

    Label:
        text: "Medicine Reminder"
        font_size: "24sp"
        size_hint_y: None
        height: "50dp"

    TextInput:
        id: patient
        hint_text: "Patient name"
        multiline: False
        size_hint_y: None
        height: "45dp"

    TextInput:
        id: medicine
        hint_text: "Medicine name"
        multiline: False
        size_hint_y: None
        height: "45dp"

    TextInput:
        id: dosage
        hint_text: "Dosage as prescribed"
        multiline: False
        size_hint_y: None
        height: "45dp"

    TextInput:
        id: time
        hint_text: "Reminder time (HH:MM, 24-hour)"
        multiline: False
        size_hint_y: None
        height: "45dp"

    Button:
        text: "Save medicine"
        size_hint_y: None
        height: "48dp"
        on_release: app.save_medicine()

    Button:
        text: "Refresh medicine list"
        size_hint_y: None
        height: "48dp"
        on_release: app.refresh_list()

    Label:
        id: status
        text: "Enter medicine details."
        size_hint_y: None
        height: "45dp"

    Label:
        id: medicines
        text: ""
        halign: "left"
        valign: "top"
        text_size: self.width, None
"""

class MedicineReminderApp(App):
    def build(self):
        self.conn = sqlite3.connect(DB_FILE)
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS medicines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient TEXT NOT NULL,
                name TEXT NOT NULL,
                dosage TEXT NOT NULL,
                time TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

        self.root = Builder.load_string(KV)
        Clock.schedule_interval(self.check_reminders, 15)
        self.refresh_list()
        return self.root

    def save_medicine(self):
        ids = self.root.ids
        patient = ids.patient.text.strip()
        name = ids.medicine.text.strip()
        dosage = ids.dosage.text.strip()
        time = ids.time.text.strip()

        if not all([patient, name, dosage, time]):
            ids.status.text = "Please fill in every field."
            return

        try:
            datetime.strptime(time, "%H:%M")
        except ValueError:
            ids.status.text = "Use 24-hour time, e.g. 08:30."
            return

        self.conn.execute(
            "INSERT INTO medicines (patient, name, dosage, time) "
            "VALUES (?, ?, ?, ?)",
            (patient, name, dosage, time)
        )
        self.conn.commit()
        ids.status.text = "Medicine saved!"
        self.refresh_list()

    def refresh_list(self):
        rows = self.conn.execute(
            "SELECT patient, name, dosage, time "
            "FROM medicines ORDER BY time"
        ).fetchall()

        self.root.ids.medicines.text = "\n".join(
            f"{p} | {m} | {d} | {t}"
            for p, m, d, t in rows
        ) or "No medicines saved yet."

    def check_reminders(self, _dt):
        now = datetime.now().strftime("%H:%M")
        rows = self.conn.execute(
            "SELECT patient, name, dosage "
            "FROM medicines WHERE time = ?",
            (now,)
        ).fetchall()

        if rows:
            messages = [
                f"Reminder: {p}, take {m} ({d}) as prescribed."
                for p, m, d in rows
            ]
            self.root.ids.status.text = "\n".join(messages)

    def on_stop(self):
        if hasattr(self, "conn"):
            self.conn.close()


if __name__ == "__main__":
    MedicineReminderApp().run()
