from database import get_db
from datetime import datetime

def get_all_complaints(status=None):
    conn = get_db()
    query = """
        SELECT c.*, s.name, s.student_id as sid FROM complaints c
        JOIN students s ON c.student_id = s.id WHERE 1=1
    """
    params = []
    if status:
        query += " AND c.status=?"
        params.append(status)
    query += " ORDER BY c.created_at DESC"
    records = conn.execute(query, params).fetchall()
    conn.close()
    return records

def add_complaint(data):
    conn = get_db()
    try:
        conn.execute("""
            INSERT INTO complaints (student_id, category, subject, description, priority)
            VALUES (?, ?, ?, ?, ?)
        """, (data['student_id'], data['category'], data['subject'], data['description'], data.get('priority', 'Medium')))
        conn.commit()
        return True, "Complaint registered."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def update_complaint(complaint_id, status, response=''):
    conn = get_db()
    try:
        resolved_at = datetime.now().isoformat() if status in ('Resolved', 'Closed') else None
        conn.execute("""
            UPDATE complaints SET status=?, admin_response=?, resolved_at=? WHERE id=?
        """, (status, response, resolved_at, complaint_id))
        conn.commit()
        return True, "Complaint updated."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def delete_complaint(complaint_id):
    conn = get_db()
    try:
        conn.execute("DELETE FROM complaints WHERE id=?", (complaint_id,))
        conn.commit()
        return True, "Complaint deleted."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def get_complaint_stats():
    conn = get_db()
    stats = {
        'open': conn.execute("SELECT COUNT(*) FROM complaints WHERE status='Open'").fetchone()[0],
        'in_progress': conn.execute("SELECT COUNT(*) FROM complaints WHERE status='In Progress'").fetchone()[0],
        'resolved': conn.execute("SELECT COUNT(*) FROM complaints WHERE status='Resolved'").fetchone()[0],
        'total': conn.execute("SELECT COUNT(*) FROM complaints").fetchone()[0],
    }
    conn.close()
    return stats