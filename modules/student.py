from database import get_db

def get_all_students(search=None):
    conn = get_db()
    if search:
        students = conn.execute("""
            SELECT s.*, r.room_number FROM students s
            LEFT JOIN rooms r ON s.room_id = r.id
            WHERE s.name LIKE ? OR s.student_id LIKE ? OR s.department LIKE ?
            ORDER BY s.created_at DESC
        """, (f'%{search}%', f'%{search}%', f'%{search}%')).fetchall()
    else:
        students = conn.execute("""
            SELECT s.*, r.room_number FROM students s
            LEFT JOIN rooms r ON s.room_id = r.id
            ORDER BY s.created_at DESC
        """).fetchall()
    conn.close()
    return students

def get_student_by_id(student_id):
    conn = get_db()
    student = conn.execute("""
        SELECT s.*, r.room_number FROM students s
        LEFT JOIN rooms r ON s.room_id = r.id
        WHERE s.id = ?
    """, (student_id,)).fetchone()
    conn.close()
    return student

def add_student(data):
    conn = get_db()
    try:
        conn.execute("""
            INSERT INTO students (student_id, name, department, phone, room_id, address, joining_date, email, emergency_contact)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['student_id'], data['name'], data['department'],
            data['phone'], data.get('room_id') or None, data['address'],
            data['joining_date'], data.get('email', ''), data.get('emergency_contact', '')
        ))
        if data.get('room_id'):
            conn.execute("UPDATE rooms SET status='Occupied' WHERE id=?", (data['room_id'],))
        conn.commit()
        return True, "Student added successfully."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def update_student(student_id, data):
    conn = get_db()
    try:
        old = conn.execute("SELECT room_id FROM students WHERE id=?", (student_id,)).fetchone()
        conn.execute("""
            UPDATE students SET name=?, department=?, phone=?, room_id=?, address=?,
            joining_date=?, email=?, emergency_contact=?, status=? WHERE id=?
        """, (
            data['name'], data['department'], data['phone'],
            data.get('room_id') or None, data['address'], data['joining_date'],
            data.get('email', ''), data.get('emergency_contact', ''),
            data.get('status', 'Active'), student_id
        ))
        # Update room statuses
        new_room_id = data.get('room_id') or None
        old_room_id = old['room_id'] if old else None
        if old_room_id and old_room_id != new_room_id:
            conn.execute("UPDATE rooms SET status='Vacant' WHERE id=?", (old_room_id,))
        if new_room_id and old_room_id != new_room_id:
            conn.execute("UPDATE rooms SET status='Occupied' WHERE id=?", (new_room_id,))
        conn.commit()
        return True, "Student updated successfully."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def delete_student(student_id):
    conn = get_db()
    try:
        student = conn.execute("SELECT room_id FROM students WHERE id=?", (student_id,)).fetchone()
        if student and student['room_id']:
            conn.execute("UPDATE rooms SET status='Vacant' WHERE id=?", (student['room_id'],))
        conn.execute("DELETE FROM students WHERE id=?", (student_id,))
        conn.commit()
        return True, "Student deleted successfully."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def get_student_count():
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) FROM students WHERE status='Active'").fetchone()[0]
    conn.close()
    return count