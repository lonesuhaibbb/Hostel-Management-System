import os
import sys
import json
sys.path.insert(0, os.path.dirname(__file__))

from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash, jsonify)
from werkzeug.security import check_password_hash
from functools import wraps
from datetime import date, datetime

from database import get_db, init_db
from modules.student import (
    get_all_students, get_student_by_id, add_student,
    update_student, delete_student, get_student_count,
)
from modules.attendance import (
    get_attendance_by_date, get_students_not_marked, mark_bulk_attendance,
    get_defaulters, get_today_present_count, get_attendance_history,
    get_monthly_stats, get_attendance_summary,
)
from modules.rooms import (
    get_all_rooms, get_vacant_rooms, get_room_by_id, add_room,
    update_room, delete_room, get_room_students, get_room_stats,
)
from modules.wastage import (
    add_wastage, get_all_wastage, get_wastage_summary_by_student,
    get_today_wastage_count, get_wastage_chart_data, delete_wastage,
)
from modules.fees import (
    get_all_fees, add_fee, update_fee_status, delete_fee,
    apply_wastage_fine, get_fee_stats, get_student_fees,
)
from modules.complaints import (
    get_all_complaints, add_complaint, update_complaint,
    delete_complaint, get_complaint_stats,
)
from modules.visitors import (
    get_all_visitors, add_visitor, checkout_visitor,
    delete_visitor, get_visitor_stats,
)

# ─────────────────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = 'hostel_mgmt_super_secret_key_2024'


# ── helpers ──────────────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin' not in session:
            flash('Please login to continue.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def _rows_to_dicts(rows):
    """Convert sqlite3.Row list → plain dicts (JSON-serialisable)."""
    return [dict(r) for r in rows]


def _get_student_360_data(sid):
    """
    Fetch and aggregate ALL data for a student's 360° profile.
    Returns a dict of context variables ready to be unpacked into render_template.
    """
    conn = get_db()

    # ── attendance history for chart (last 30 days, ordered oldest→newest) ──
    att_rows = conn.execute("""
        SELECT date, status FROM attendance
        WHERE student_id=? ORDER BY date ASC LIMIT 30
    """, (sid,)).fetchall()

    att_chart_labels  = [r['date']   for r in att_rows]
    att_chart_present = [1 if r['status'] == 'Present' else 0 for r in att_rows]
    att_chart_absent  = [1 if r['status'] == 'Absent'  else 0 for r in att_rows]

    # ── wastage records for this student ──
    wastage_rows = conn.execute("""
        SELECT * FROM food_wastage WHERE student_id=? ORDER BY date DESC
    """, (sid,)).fetchall()
    wastage_records = _rows_to_dicts(wastage_rows)

    # wastage chart — count per date, oldest→newest (last 12 months)
    w_chart_rows = conn.execute("""
        SELECT date, COUNT(*) as cnt FROM food_wastage
        WHERE student_id=? GROUP BY date ORDER BY date ASC LIMIT 20
    """, (sid,)).fetchall()
    wastage_chart_labels = [r['date'] for r in w_chart_rows]
    wastage_chart_data   = [r['cnt']  for r in w_chart_rows]

    # wastage summary
    total_w = len(wastage_records)
    high_w  = sum(1 for w in wastage_records if w['wastage_level'] == 'High')
    total_fine = sum(w['fine_amount'] for w in wastage_records)
    wastage_summary = {
        'total_count': total_w,
        'high_count':  high_w,
        'total_fine':  total_fine,
    }

    # ── fees ──
    fee_rows = conn.execute("""
        SELECT * FROM fees WHERE student_id=? ORDER BY created_at DESC
    """, (sid,)).fetchall()
    fees = _rows_to_dicts(fee_rows)

    paid_amount    = sum(f['amount'] for f in fees if f['status'] == 'Paid')
    pending_amount = sum(f['amount'] for f in fees if f['status'] == 'Pending')
    overdue_amount = sum(f['amount'] for f in fees if f['status'] == 'Overdue')
    fine_amount    = sum(f.get('wastage_fine', 0) or 0 for f in fees)
    pending_count  = sum(1 for f in fees if f['status'] == 'Pending')
    fees_summary = {
        'paid_amount':    paid_amount,
        'pending_amount': pending_amount,
        'overdue_amount': overdue_amount,
        'fine_amount':    fine_amount,
        'pending_count':  pending_count,
        'total':          len(fees),
    }

    # ── complaints ──
    complaint_rows = conn.execute("""
        SELECT * FROM complaints WHERE student_id=? ORDER BY created_at DESC
    """, (sid,)).fetchall()
    student_complaints = _rows_to_dicts(complaint_rows)
    open_c     = sum(1 for c in student_complaints if c['status'] == 'Open')
    resolved_c = sum(1 for c in student_complaints if c['status'] == 'Resolved')
    complaints_summary = {
        'total':    len(student_complaints),
        'open':     open_c,
        'resolved': resolved_c,
    }

    # ── visitors ──
    visitor_rows = conn.execute("""
        SELECT * FROM visitors WHERE student_id=? ORDER BY check_in DESC
    """, (sid,)).fetchall()
    visitor_records = _rows_to_dicts(visitor_rows)

    conn.close()

    return dict(
        wastage_records=wastage_records,
        wastage_summary=wastage_summary,
        wastage_chart_labels=wastage_chart_labels,
        wastage_chart_data=wastage_chart_data,
        fees=fees,
        fees_summary=fees_summary,
        student_complaints=student_complaints,
        complaints_summary=complaints_summary,
        visitor_records=visitor_records,
        att_chart_labels=att_chart_labels,
        att_chart_present=att_chart_present,
        att_chart_absent=att_chart_absent,
    )


# ── Auth ─────────────────────────────────────────────────────────────────────

@app.route('/', methods=['GET', 'POST'])
def login():
    if 'admin' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        conn = get_db()
        admin = conn.execute(
            'SELECT * FROM admin WHERE username=?', (username,)
        ).fetchone()
        conn.close()
        if admin and check_password_hash(admin['password'], password):
            session['admin'] = username
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid credentials. Please try again.', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('admin', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))


# ── Dashboard ────────────────────────────────────────────────────────────────

@app.route('/dashboard')
@login_required
def dashboard():
    now             = datetime.now()
    today_str       = date.today().strftime('%A, %d %B %Y')

    students        = get_student_count()
    present         = get_today_present_count()
    room_stats      = get_room_stats()
    complaint_stats = get_complaint_stats()
    wastage_today   = get_today_wastage_count()
    fee_stats       = get_fee_stats()
    visitor_stats   = get_visitor_stats()

    wastage_chart = _rows_to_dicts(get_wastage_chart_data())[::-1]
    monthly_att   = _rows_to_dicts(get_monthly_stats())[::-1]

    return render_template(
        'dashboard.html',
        now=now,
        today=today_str,
        students=students,
        present=present,
        room_stats=room_stats,
        complaint_stats=complaint_stats,
        wastage_today=wastage_today,
        fee_stats=fee_stats,
        visitor_stats=visitor_stats,
        wastage_chart=wastage_chart,
        monthly_att=monthly_att,
    )


# ── Students ─────────────────────────────────────────────────────────────────

@app.route('/students')
@login_required
def students():
    search       = request.args.get('search', '')
    all_students = get_all_students(search if search else None)
    all_rooms    = get_all_rooms()
    vacant_rooms = get_vacant_rooms()
    return render_template(
        'students.html',
        students=all_students,
        rooms=all_rooms,
        vacant_rooms=vacant_rooms,
        search=search,
    )


@app.route('/students/add', methods=['POST'])
@login_required
def add_student_route():
    ok, msg = add_student(request.form)
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('students'))


@app.route('/students/edit/<int:sid>', methods=['POST'])
@login_required
def edit_student_route(sid):
    ok, msg = update_student(sid, request.form)
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('students'))


@app.route('/students/delete/<int:sid>', methods=['POST'])
@login_required
def delete_student_route(sid):
    ok, msg = delete_student(sid)
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('students'))


# ── Student 360° Profile ─────────────────────────────────────────────────────

@app.route('/students/<int:sid>/360')
@login_required
def student_360_profile(sid):
    student = get_student_by_id(sid)
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('students'))

    att_summary = get_attendance_summary(sid)
    att_history = get_attendance_history(sid, limit=60)

    extra = _get_student_360_data(sid)

    return render_template(
        'student_profile.html',
        student=student,
        att_summary=att_summary,
        att_history=att_history,
        **extra,
    )


# ── Attendance ───────────────────────────────────────────────────────────────

@app.route('/attendance')
@login_required
def attendance():
    sel_date   = request.args.get('date', date.today().isoformat())
    marked     = get_attendance_by_date(sel_date)
    unmarked   = get_students_not_marked(sel_date)
    defaulters = get_defaulters()
    return render_template(
        'attendance.html',
        marked=marked,
        unmarked=unmarked,
        sel_date=sel_date,
        defaulters=defaulters,
    )


@app.route('/attendance/mark', methods=['POST'])
@login_required
def mark_attendance_route():
    sel_date    = request.form.get('date', date.today().isoformat())
    student_ids = request.form.getlist('student_ids')

    records = []
    for sid in student_ids:
        status = request.form.get(f'status_{sid}', 'Present')
        records.append({'student_id': sid, 'date': sel_date, 'status': status})

    if not records:
        flash('No students to mark.', 'warning')
        return redirect(url_for('attendance', date=sel_date))

    ok, msg = mark_bulk_attendance(records)
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('attendance', date=sel_date))


# ── Rooms ────────────────────────────────────────────────────────────────────

@app.route('/rooms')
@login_required
def rooms():
    all_rooms = get_all_rooms()
    stats     = get_room_stats()
    return render_template('rooms.html', rooms=all_rooms, stats=stats)


@app.route('/rooms/add', methods=['POST'])
@login_required
def add_room_route():
    ok, msg = add_room(request.form)
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('rooms'))


@app.route('/rooms/edit/<int:rid>', methods=['POST'])
@login_required
def edit_room_route(rid):
    ok, msg = update_room(rid, request.form)
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('rooms'))


@app.route('/rooms/delete/<int:rid>', methods=['POST'])
@login_required
def delete_room_route(rid):
    ok, msg = delete_room(rid)
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('rooms'))


@app.route('/rooms/<int:rid>/students')
@login_required
def room_students(rid):
    room     = get_room_by_id(rid)
    students = get_room_students(rid)
    return jsonify({
        'room':     dict(room) if room else {},
        'students': _rows_to_dicts(students),
    })


# ── Wastage ──────────────────────────────────────────────────────────────────

@app.route('/wastage')
@login_required
def wastage():
    date_filter    = request.args.get('date', '')
    student_filter = request.args.get('student', '')

    records      = get_all_wastage(date_filter or None, student_filter or None)
    summary      = get_wastage_summary_by_student()
    all_students = get_all_students()

    chart_rows           = _rows_to_dicts(get_wastage_chart_data())[::-1]
    wastage_chart_labels = [r['date']  for r in chart_rows]
    wastage_chart_data   = [r['count'] for r in chart_rows]

    return render_template(
        'wastage.html',
        records=records,
        summary=summary,
        all_students=all_students,
        date_filter=date_filter,
        student_filter=student_filter,
        wastage_chart_labels=wastage_chart_labels,
        wastage_chart_data=wastage_chart_data,
        now_date=date.today().isoformat(),
    )


@app.route('/wastage/add', methods=['POST'])
@login_required
def add_wastage_route():
    ok, msg = add_wastage(request.form)
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('wastage'))


@app.route('/wastage/delete/<int:wid>', methods=['POST'])
@login_required
def delete_wastage_route(wid):
    ok, msg = delete_wastage(wid)
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('wastage'))


@app.route('/wastage/apply-fine/<int:sid>', methods=['POST'])
@login_required
def apply_fine_route(sid):
    ok, msg = apply_wastage_fine(sid)
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('fees'))


# ── Fees ─────────────────────────────────────────────────────────────────────

@app.route('/fees')
@login_required
def fees():
    status_filter  = request.args.get('status', '')
    student_filter = request.args.get('student', '')
    all_fees       = get_all_fees(status_filter or None, student_filter or None)
    stats          = get_fee_stats()
    all_students   = get_all_students()
    return render_template(
        'fees.html',
        fees=all_fees,
        stats=stats,
        all_students=all_students,
        status_filter=status_filter,
        student_filter=student_filter,
    )


@app.route('/fees/add', methods=['POST'])
@login_required
def add_fee_route():
    ok, msg = add_fee(request.form)
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('fees'))


@app.route('/fees/update/<int:fid>', methods=['POST'])
@login_required
def update_fee_route(fid):
    status = request.form.get('status', 'Paid')
    ok, msg = update_fee_status(fid, status)
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('fees'))


@app.route('/fees/delete/<int:fid>', methods=['POST'])
@login_required
def delete_fee_route(fid):
    ok, msg = delete_fee(fid)
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('fees'))


# ── Complaints ───────────────────────────────────────────────────────────────

@app.route('/complaints')
@login_required
def complaints():
    status_filter  = request.args.get('status', '')
    all_complaints = get_all_complaints(status_filter or None)
    stats          = get_complaint_stats()
    all_students   = get_all_students()
    return render_template(
        'complaints.html',
        complaints=all_complaints,
        stats=stats,
        all_students=all_students,
        status_filter=status_filter,
    )


@app.route('/complaints/add', methods=['POST'])
@login_required
def add_complaint_route():
    ok, msg = add_complaint(request.form)
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('complaints'))


@app.route('/complaints/update/<int:cid>', methods=['POST'])
@login_required
def update_complaint_route(cid):
    status   = request.form.get('status', 'Open')
    response = request.form.get('admin_response', '')
    ok, msg  = update_complaint(cid, status, response)
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('complaints'))


@app.route('/complaints/delete/<int:cid>', methods=['POST'])
@login_required
def delete_complaint_route(cid):
    ok, msg = delete_complaint(cid)
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('complaints'))


# ── Visitors ─────────────────────────────────────────────────────────────────

@app.route('/visitors')
@login_required
def visitors():
    status_filter = request.args.get('status', '')
    all_visitors  = get_all_visitors(status_filter or None)
    stats         = get_visitor_stats()
    all_students  = get_all_students()
    return render_template(
        'visitors.html',
        visitors=all_visitors,
        stats=stats,
        all_students=all_students,
        status_filter=status_filter,
    )


@app.route('/visitors/add', methods=['POST'])
@login_required
def add_visitor_route():
    ok, msg = add_visitor(request.form)
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('visitors'))


@app.route('/visitors/checkout/<int:vid>', methods=['POST'])
@login_required
def checkout_visitor_route(vid):
    ok, msg = checkout_visitor(vid)
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('visitors'))


@app.route('/visitors/delete/<int:vid>', methods=['POST'])
@login_required
def delete_visitor_route(vid):
    ok, msg = delete_visitor(vid)
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('visitors'))


# ── Error handlers ───────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return render_template('login.html'), 404


@app.errorhandler(500)
def server_error(e):
    return f'<h2>500 — Internal Server Error</h2><pre>{e}</pre>', 500


# ── Run ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)