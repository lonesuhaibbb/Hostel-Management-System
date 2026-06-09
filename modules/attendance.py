from database import get_db
from datetime import date, timedelta

def get_attendance_by_date(att_date=None):
    if not att_date:
        att_date = date.today().isoformat()
    conn = get_db()
    records = conn.execute("""
        SELECT a.*, s.name, s.student_id as sid, s.department, r.room_number
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        LEFT JOIN rooms r ON s.room_id = r.id
        WHERE a.date = ? ORDER BY s.name
    """, (att_date,)).fetchall()
    conn.close()
    return records

def get_students_not_marked(att_date=None):
    if not att_date:
        att_date = date.today().isoformat()
    conn = get_db()
    students = conn.execute("""
        SELECT s.*, r.room_number FROM students s
        LEFT JOIN rooms r ON s.room_id = r.id
        WHERE s.status='Active' AND s.id NOT IN (
            SELECT student_id FROM attendance WHERE date=?
        ) ORDER BY s.name
    """, (att_date,)).fetchall()
    conn.close()
    return students

def mark_attendance(student_id, att_date, status, remarks=''):
    conn = get_db()
    try:
        conn.execute("""
            INSERT INTO attendance (student_id, date, status, remarks)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(student_id, date) DO UPDATE SET status=excluded.status, remarks=excluded.remarks
        """, (student_id, att_date, status, remarks))
        conn.commit()
        return True, "Attendance marked."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def mark_bulk_attendance(records):
    conn = get_db()
    try:
        for r in records:
            conn.execute("""
                INSERT INTO attendance (student_id, date, status, remarks)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(student_id, date) DO UPDATE SET status=excluded.status
            """, (r['student_id'], r['date'], r['status'], r.get('remarks', '')))
        conn.commit()
        return True, f"{len(records)} attendance records saved."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def get_attendance_summary(student_id):
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM attendance WHERE student_id=?", (student_id,)).fetchone()[0]
    present = conn.execute("SELECT COUNT(*) FROM attendance WHERE student_id=? AND status='Present'", (student_id,)).fetchone()[0]
    absent = conn.execute("SELECT COUNT(*) FROM attendance WHERE student_id=? AND status='Absent'", (student_id,)).fetchone()[0]
    conn.close()
    percentage = round((present / total * 100), 2) if total > 0 else 0
    return {'total': total, 'present': present, 'absent': absent, 'percentage': percentage}

def get_defaulters(threshold=75):
    conn = get_db()
    students = conn.execute("SELECT id, name, student_id, department FROM students WHERE status='Active'").fetchall()
    defaulters = []
    for s in students:
        summary = get_attendance_summary(s['id'])
        if summary['total'] > 0 and summary['percentage'] < threshold:
            defaulters.append({**dict(s), **summary})
    conn.close()
    return defaulters

def get_today_present_count():
    conn = get_db()
    today = date.today().isoformat()
    count = conn.execute("SELECT COUNT(*) FROM attendance WHERE date=? AND status='Present'", (today,)).fetchone()[0]
    conn.close()
    return count

def get_attendance_history(student_id, limit=30):
    conn = get_db()
    records = conn.execute("""
        SELECT * FROM attendance WHERE student_id=? ORDER BY date DESC LIMIT ?
    """, (student_id, limit)).fetchall()
    conn.close()
    return records

def get_monthly_stats():
    conn = get_db()
    stats = conn.execute("""
        SELECT date, 
               SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END) as present_count,
               SUM(CASE WHEN status='Absent' THEN 1 ELSE 0 END) as absent_count
        FROM attendance
        GROUP BY date ORDER BY date DESC LIMIT 30
    """).fetchall()
    conn.close()
    return stats