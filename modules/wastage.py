from database import get_db
from datetime import date

FINE_PER_WASTAGE = 20.0

def add_wastage(data):
    conn = get_db()
    try:
        conn.execute("""
            INSERT INTO food_wastage (student_id, date, meal_type, wastage_level, remarks, fine_amount)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (data['student_id'], data['date'], data['meal_type'], data['wastage_level'], data.get('remarks', ''), FINE_PER_WASTAGE))
        conn.commit()
        return True, "Wastage record added."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def get_all_wastage(date_filter=None, student_filter=None):
    conn = get_db()
    query = """
        SELECT fw.*, s.name, s.student_id as sid, r.room_number
        FROM food_wastage fw
        JOIN students s ON fw.student_id = s.id
        LEFT JOIN rooms r ON s.room_id = r.id
        WHERE 1=1
    """
    params = []
    if date_filter:
        query += " AND fw.date=?"
        params.append(date_filter)
    if student_filter:
        query += " AND (s.name LIKE ? OR s.student_id LIKE ?)"
        params += [f'%{student_filter}%', f'%{student_filter}%']
    query += " ORDER BY fw.recorded_at DESC"
    records = conn.execute(query, params).fetchall()
    conn.close()
    return records

def get_monthly_wastage(student_id, year=None, month=None):
    if not year:
        year = date.today().year
    if not month:
        month = date.today().month
    conn = get_db()
    records = conn.execute("""
        SELECT * FROM food_wastage
        WHERE student_id=? AND strftime('%Y', date)=? AND strftime('%m', date)=?
        ORDER BY date
    """, (student_id, str(year), f'{month:02d}')).fetchall()
    total_fine = len(records) * FINE_PER_WASTAGE
    conn.close()
    return records, total_fine

def get_wastage_fine_for_fee(student_id):
    conn = get_db()
    # Count wastage records not yet converted to fee
    count = conn.execute("""
        SELECT COUNT(*) FROM food_wastage fw
        WHERE fw.student_id=? AND fw.fine_applied=1
        AND fw.id NOT IN (
            SELECT CAST(remarks AS INTEGER) FROM fees 
            WHERE student_id=? AND fee_type='Food Wastage Fine' AND remarks LIKE 'wastage_%'
        )
    """, (student_id, student_id)).fetchone()[0]
    conn.close()
    return count * FINE_PER_WASTAGE

def get_wastage_summary_by_student():
    conn = get_db()
    summary = conn.execute("""
        SELECT s.id, s.name, s.student_id as sid, s.department,
               COUNT(fw.id) as total_wastage,
               SUM(fw.fine_amount) as total_fine,
               MAX(fw.date) as last_wastage
        FROM students s
        LEFT JOIN food_wastage fw ON s.id = fw.student_id
        WHERE s.status='Active'
        GROUP BY s.id ORDER BY total_wastage DESC
    """).fetchall()
    conn.close()
    return summary

def get_today_wastage_count():
    conn = get_db()
    today = date.today().isoformat()
    count = conn.execute("SELECT COUNT(*) FROM food_wastage WHERE date=?", (today,)).fetchone()[0]
    conn.close()
    return count

def get_wastage_chart_data():
    conn = get_db()
    data = conn.execute("""
        SELECT date, COUNT(*) as count FROM food_wastage
        GROUP BY date ORDER BY date DESC LIMIT 14
    """).fetchall()
    conn.close()
    return data

def delete_wastage(wastage_id):
    conn = get_db()
    try:
        conn.execute("DELETE FROM food_wastage WHERE id=?", (wastage_id,))
        conn.commit()
        return True, "Record deleted."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()