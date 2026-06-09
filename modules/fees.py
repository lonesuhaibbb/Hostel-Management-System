from database import get_db
from datetime import date

def get_all_fees(status=None, student_filter=None):
    conn = get_db()
    query = """
        SELECT f.*, s.name, s.student_id as sid FROM fees f
        JOIN students s ON f.student_id = s.id WHERE 1=1
    """
    params = []
    if status:
        query += " AND f.status=?"
        params.append(status)
    if student_filter:
        query += " AND (s.name LIKE ? OR s.student_id LIKE ?)"
        params += [f'%{student_filter}%', f'%{student_filter}%']
    query += " ORDER BY f.created_at DESC"
    records = conn.execute(query, params).fetchall()
    conn.close()
    return records

def add_fee(data):
    conn = get_db()
    try:
        conn.execute("""
            INSERT INTO fees (student_id, fee_type, amount, due_date, status, wastage_fine, remarks)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data['student_id'], data['fee_type'], data['amount'],
            data.get('due_date'), data.get('status', 'Pending'),
            data.get('wastage_fine', 0), data.get('remarks', '')
        ))
        conn.commit()
        return True, "Fee record added."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def update_fee_status(fee_id, status):
    conn = get_db()
    try:
        paid_date = date.today().isoformat() if status == 'Paid' else None
        conn.execute("UPDATE fees SET status=?, paid_date=? WHERE id=?", (status, paid_date, fee_id))
        conn.commit()
        return True, "Fee status updated."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def delete_fee(fee_id):
    conn = get_db()
    try:
        conn.execute("DELETE FROM fees WHERE id=?", (fee_id,))
        conn.commit()
        return True, "Fee deleted."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def apply_wastage_fine(student_id):
    from modules.wastage import get_monthly_wastage
    records, total_fine = get_monthly_wastage(student_id)
    if total_fine <= 0:
        return False, "No wastage fine to apply."
    today = date.today()
    data = {
        'student_id': student_id,
        'fee_type': 'Food Wastage Fine',
        'amount': total_fine,
        'due_date': today.isoformat(),
        'status': 'Pending',
        'wastage_fine': total_fine,
        'remarks': f'Auto-generated for {today.strftime("%B %Y")}'
    }
    return add_fee(data)

def get_fee_stats():
    conn = get_db()
    total_collected = conn.execute("SELECT COALESCE(SUM(amount),0) FROM fees WHERE status='Paid'").fetchone()[0]
    total_pending = conn.execute("SELECT COALESCE(SUM(amount),0) FROM fees WHERE status='Pending'").fetchone()[0]
    total_overdue = conn.execute("SELECT COALESCE(SUM(amount),0) FROM fees WHERE status='Overdue'").fetchone()[0]
    conn.close()
    return {
        'collected': round(total_collected, 2),
        'pending': round(total_pending, 2),
        'overdue': round(total_overdue, 2)
    }

def get_student_fees(student_id):
    conn = get_db()
    fees = conn.execute("SELECT * FROM fees WHERE student_id=? ORDER BY created_at DESC", (student_id,)).fetchall()
    conn.close()
    return fees