from database import get_db

def get_all_rooms():
    conn = get_db()
    rooms = conn.execute("""
        SELECT r.*, 
               COUNT(s.id) as current_occupancy,
               GROUP_CONCAT(s.name, ', ') as student_names
        FROM rooms r
        LEFT JOIN students s ON r.id = s.room_id AND s.status='Active'
        GROUP BY r.id ORDER BY r.floor, r.room_number
    """).fetchall()
    conn.close()
    return rooms

def get_vacant_rooms():
    conn = get_db()
    rooms = conn.execute("SELECT * FROM rooms WHERE status='Vacant' ORDER BY floor, room_number").fetchall()
    conn.close()
    return rooms

def get_room_by_id(room_id):
    conn = get_db()
    room = conn.execute("""
        SELECT r.*, COUNT(s.id) as current_occupancy
        FROM rooms r
        LEFT JOIN students s ON r.id = s.room_id AND s.status='Active'
        WHERE r.id=? GROUP BY r.id
    """, (room_id,)).fetchone()
    conn.close()
    return room

def add_room(data):
    conn = get_db()
    try:
        # Removed amenities from INSERT statement columns and values
        conn.execute("""
            INSERT INTO rooms (room_number, capacity, room_type, floor, status)
            VALUES (?, ?, ?, ?, ?)
        """, (data['room_number'], data['capacity'], data['room_type'], data['floor'], 'Vacant'))
        # Original query backup:
        # INSERT INTO rooms (room_number, capacity, room_type, floor, status, amenities) VALUES (?, ?, ?, ?, ?, ?)
        # Tuple backup: (data['room_number'], data['capacity'], data['room_type'], data['floor'], 'Vacant', data.get('amenities', ''))
        
        conn.commit()
        return True, "Room added successfully."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def update_room(room_id, data):
    conn = get_db()
    try:
        # Removed amenities=? from UPDATE statement
        conn.execute("""
            UPDATE rooms SET room_number=?, capacity=?, room_type=?, floor=? WHERE id=?
        """, (data['room_number'], data['capacity'], data['room_type'], data['floor'], room_id))
        # Original query backup:
        # UPDATE rooms SET room_number=?, capacity=?, room_type=?, floor=?, amenities=? WHERE id=?
        # Tuple backup: (data['room_number'], data['capacity'], data['room_type'], data['floor'], data.get('amenities', ''), room_id)
        
        conn.commit()
        return True, "Room updated."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def delete_room(room_id):
    conn = get_db()
    try:
        occupants = conn.execute("SELECT COUNT(*) FROM students WHERE room_id=? AND status='Active'", (room_id,)).fetchone()[0]
        if occupants > 0:
            return False, "Cannot delete room with active students."
        conn.execute("DELETE FROM rooms WHERE id=?", (room_id,))
        conn.commit()
        return True, "Room deleted."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def get_room_students(room_id):
    conn = get_db()
    students = conn.execute("""
        SELECT * FROM students WHERE room_id=? AND status='Active'
    """, (room_id,)).fetchall()
    conn.close()
    return students

def get_room_stats():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM rooms").fetchone()[0]
    occupied = conn.execute("SELECT COUNT(*) FROM rooms WHERE status='Occupied'").fetchone()[0]
    vacant = total - occupied
    conn.close()
    return {'total': total, 'occupied': occupied, 'vacant': vacant}