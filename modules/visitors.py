from database import get_db
from datetime import datetime

def get_all_visitors(status=None):
    conn = get_db()
    query = """
        SELECT v.*, s.name as student_name, s.student_id as sid FROM visitors v
        JOIN students s ON v.student_id = s.id WHERE 1=1
    """
    params = []
    if status:
        query += " AND v.status=?"
        params.append(status)
    query += " ORDER BY v.check_in DESC"
    records = conn.execute(query, params).fetchall()
    conn.close()
    return records

def add_visitor(data):
    conn = get_db()
    try:
        conn.execute("""
            INSERT INTO visitors (visitor_name, visitor_phone, visitor_address, purpose,
            student_id, id_proof_type, id_proof_number, remarks)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['visitor_name'], data.get('visitor_phone', ''), data.get('visitor_address', ''),
            data['purpose'], data['student_id'], data.get('id_proof_type', ''),
            data.get('id_proof_number', ''), data.get('remarks', '')
        ))
        conn.commit()
        return True, "Visitor checked in."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def checkout_visitor(visitor_id):
    conn = get_db()
    try:
        conn.execute("""
            UPDATE visitors SET check_out=?, status='Checked Out' WHERE id=?
        """, (datetime.now().isoformat(), visitor_id))
        conn.commit()
        return True, "Visitor checked out."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def delete_visitor(visitor_id):
    conn = get_db()
    try:
        conn.execute("DELETE FROM visitors WHERE id=?", (visitor_id,))
        conn.commit()
        return True, "Record deleted."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def get_visitor_stats():
    conn = get_db()
    stats = {
        'checked_in': conn.execute("SELECT COUNT(*) FROM visitors WHERE status='Checked In'").fetchone()[0],
        'today': conn.execute("SELECT COUNT(*) FROM visitors WHERE DATE(check_in)=DATE('now')").fetchone()[0],
        'total': conn.execute("SELECT COUNT(*) FROM visitors").fetchone()[0],
    }
    conn.close()
    return stats