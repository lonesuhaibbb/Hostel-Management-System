import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'hostel.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    c = conn.cursor()

    c.executescript("""
        CREATE TABLE IF not exists admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT UNIQUE NOT NULL,
            capacity INTEGER DEFAULT 1,
            room_type TEXT DEFAULT 'Single',
            floor INTEGER DEFAULT 1,
            status TEXT DEFAULT 'Vacant',
            amenities TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            phone TEXT NOT NULL,
            room_id INTEGER,
            address TEXT,
            joining_date DATE NOT NULL,
            email TEXT,
            emergency_contact TEXT,
            status TEXT DEFAULT 'Active',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            date DATE NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('Present','Absent','Leave')),
            marked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            remarks TEXT,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            UNIQUE(student_id, date)
        );

        CREATE TABLE IF NOT EXISTS food_wastage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            date DATE NOT NULL,
            meal_type TEXT NOT NULL CHECK(meal_type IN ('Breakfast','Lunch','Dinner')),
            wastage_level TEXT NOT NULL CHECK(wastage_level IN ('Low','Medium','High')),
            remarks TEXT,
            fine_amount REAL DEFAULT 20.0,
            fine_applied INTEGER DEFAULT 1,
            recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS fees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            fee_type TEXT NOT NULL,
            amount REAL NOT NULL,
            due_date DATE,
            paid_date DATE,
            status TEXT DEFAULT 'Pending' CHECK(status IN ('Paid','Pending','Overdue')),
            wastage_fine REAL DEFAULT 0.0,
            remarks TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            subject TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT DEFAULT 'Open' CHECK(status IN ('Open','In Progress','Resolved','Closed')),
            priority TEXT DEFAULT 'Medium' CHECK(priority IN ('Low','Medium','High','Urgent')),
            admin_response TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            resolved_at DATETIME,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS visitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            visitor_name TEXT NOT NULL,
            visitor_phone TEXT,
            visitor_address TEXT,
            purpose TEXT NOT NULL,
            student_id INTEGER NOT NULL,
            id_proof_type TEXT,
            id_proof_number TEXT,
            check_in DATETIME DEFAULT CURRENT_TIMESTAMP,
            check_out DATETIME,
            status TEXT DEFAULT 'Checked In' CHECK(status IN ('Checked In','Checked Out')),
            remarks TEXT,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        );
    """)

    # Insert default admin
    existing = c.execute("SELECT id FROM admin WHERE username='admin'").fetchone()
    if not existing:
        c.execute(
            "INSERT INTO admin (username, password) VALUES (?, ?)",
            ('admin', generate_password_hash('admin123'))
        )

    # Insert default rooms
    existing_rooms = c.execute("SELECT COUNT(*) FROM rooms").fetchone()[0]
    if existing_rooms == 0:
        rooms_data = []
        for floor in range(1, 3):
            for num in range(1, 11):
                room_num = f"{floor}0{num}" if num < 10 else f"{floor}{num}"
                room_type = 'Single' if num % 3 == 0 else ('Double' if num % 3 == 1 else 'Triple')
                capacity = 1 if room_type == 'Single' else (2 if room_type == 'Double' else 3)
                rooms_data.append((room_num, capacity, room_type, floor, 'Vacant', 'WiFi, AC'))
        c.executemany(
            "INSERT INTO rooms (room_number, capacity, room_type, floor, status, amenities) VALUES (?,?,?,?,?,?)",
            rooms_data
        )

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully.")
