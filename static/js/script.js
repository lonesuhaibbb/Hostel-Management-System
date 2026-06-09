/* ═══════════════════════════════════════════════
   HOSTEL MANAGEMENT SYSTEM — MAIN SCRIPT
   ═══════════════════════════════════════════════ */

'use strict';

/* ── Sidebar Toggle ── */
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('sidebarOverlay');
const toggleBtn = document.getElementById('sidebarToggle');

function openSidebar() {
  sidebar?.classList.add('open');
  overlay?.classList.add('show');
  document.body.style.overflow = 'hidden';
}
function closeSidebar() {
  sidebar?.classList.remove('open');
  overlay?.classList.remove('show');
  document.body.style.overflow = '';
}
toggleBtn?.addEventListener('click', openSidebar);
overlay?.addEventListener('click', closeSidebar);

/* ── Flash Alert Auto-dismiss ── */
function initFlashAlerts() {
  const alerts = document.querySelectorAll('.flash-alert');
  alerts.forEach((alert, i) => {
    setTimeout(() => {
      alert.style.animation = 'slideInRight .3s ease reverse';
      setTimeout(() => alert.remove(), 300);
    }, 4000 + i * 500);

    const closeBtn = alert.querySelector('.btn-close');
    closeBtn?.addEventListener('click', () => {
      alert.style.animation = 'slideInRight .3s ease reverse';
      setTimeout(() => alert.remove(), 300);
    });
  });
}

/* ── Active Nav Link ── */
function setActiveNav() {
  const path = window.location.pathname;
  document.querySelectorAll('.nav-link').forEach(link => {
    const href = link.getAttribute('href');
    if (href && path.startsWith(href) && href !== '/') {
      link.classList.add('active');
    } else if (path === '/' && href === '/') {
      link.classList.add('active');
    }
  });
}

/* ── Confirm Delete ── */
function confirmDelete(formEl, msg = 'Are you sure you want to delete this record?') {
  formEl.addEventListener('submit', function(e) {
    if (!confirm(msg)) e.preventDefault();
  });
}
document.querySelectorAll('.delete-form').forEach(f => confirmDelete(f));

/* ── Edit Modal Population ── */
function populateEditModal(modalId, data) {
  const modal = document.getElementById(modalId);
  if (!modal) return;
  Object.entries(data).forEach(([key, val]) => {
    const el = modal.querySelector(`[name="${key}"]`);
    if (el) el.value = val ?? '';
  });
}

/* ── Password Toggle ── */
function initPasswordToggle() {
  document.querySelectorAll('.toggle-icon').forEach(icon => {
    icon.addEventListener('click', function() {
      const input = this.closest('.pass-toggle').querySelector('input');
      if (input.type === 'password') {
        input.type = 'text';
        this.classList.replace('bi-eye-slash', 'bi-eye');
      } else {
        input.type = 'password';
        this.classList.replace('bi-eye', 'bi-eye-slash');
      }
    });
  });
}

/* ═══════════════════════════════════════════════
   CHARTS
   ═══════════════════════════════════════════════ */

const CHART_COLORS = {
  primary:  'rgba(99,102,241,1)',
  primaryA: 'rgba(99,102,241,0.12)',
  success:  'rgba(16,185,129,1)',
  successA: 'rgba(16,185,129,0.12)',
  danger:   'rgba(239,68,68,1)',
  dangerA:  'rgba(239,68,68,0.12)',
  warning:  'rgba(245,158,11,1)',
  warningA: 'rgba(245,158,11,0.12)',
  info:     'rgba(6,182,212,1)',
  purple:   'rgba(139,92,246,1)',
  purpleA:  'rgba(139,92,246,0.12)',
};

const baseChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: '#0f172a',
      titleColor: '#e2e8f0',
      bodyColor: '#94a3b8',
      borderColor: '#1e293b',
      borderWidth: 1,
      cornerRadius: 8,
      padding: 10,
    }
  },
  scales: {
    x: {
      grid: { display: false },
      ticks: { color: '#94a3b8', font: { size: 11, family: "'Plus Jakarta Sans', sans-serif" } },
      border: { display: false }
    },
    y: {
      grid: { color: '#f1f5f9' },
      ticks: { color: '#94a3b8', font: { size: 11 } },
      border: { display: false }
    }
  }
};

/* ── Attendance Line Chart ── */
function initAttendanceChart(labels, presentData, absentData) {
  const canvas = document.getElementById('attendanceChart');
  if (!canvas) return;
  new Chart(canvas, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Present',
          data: presentData,
          borderColor: CHART_COLORS.success,
          backgroundColor: CHART_COLORS.successA,
          fill: true,
          tension: 0.45,
          pointRadius: 4,
          pointBackgroundColor: CHART_COLORS.success,
          borderWidth: 2.5,
        },
        {
          label: 'Absent',
          data: absentData,
          borderColor: CHART_COLORS.danger,
          backgroundColor: CHART_COLORS.dangerA,
          fill: true,
          tension: 0.45,
          pointRadius: 4,
          pointBackgroundColor: CHART_COLORS.danger,
          borderWidth: 2.5,
        }
      ]
    },
    options: {
      ...baseChartOptions,
      plugins: {
        ...baseChartOptions.plugins,
        legend: {
          display: true,
          position: 'top',
          align: 'end',
          labels: {
            color: '#64748b',
            font: { size: 12, family: "'Plus Jakarta Sans',sans-serif" },
            boxWidth: 10,
            boxHeight: 10,
            usePointStyle: true,
            pointStyle: 'circle',
            padding: 16,
          }
        }
      }
    }
  });
}

/* ── Wastage Bar Chart ── */
function initWastageChart(labels, data) {
  const canvas = document.getElementById('wastageChart');
  if (!canvas) return;
  new Chart(canvas, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Wastage Events',
        data,
        backgroundColor: 'rgba(245,158,11,0.8)',
        borderColor: CHART_COLORS.warning,
        borderWidth: 0,
        borderRadius: 6,
        borderSkipped: false,
      }]
    },
    options: baseChartOptions,
  });
}

/* ── Donut Chart ── */
function initDonutChart(canvasId, labels, data, colors) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  return new Chart(canvas, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: colors,
        borderWidth: 3,
        borderColor: '#fff',
        hoverOffset: 6,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '72%',
      plugins: {
        legend: {
          display: true,
          position: 'bottom',
          labels: {
            color: '#64748b',
            font: { size: 12, family: "'Plus Jakarta Sans',sans-serif" },
            boxWidth: 10,
            boxHeight: 10,
            usePointStyle: true,
            pointStyle: 'circle',
            padding: 14,
          }
        },
        tooltip: baseChartOptions.plugins.tooltip
      }
    }
  });
}

/* ── Room Occupancy Mini Chart ── */
function initRoomChart(occupied, vacant) {
  initDonutChart(
    'roomChart',
    ['Occupied', 'Vacant'],
    [occupied, vacant],
    [CHART_COLORS.primary, '#e2e8f0']
  );
}

/* ── Fee Status Chart ── */
function initFeeChart(paid, pending, overdue) {
  initDonutChart(
    'feeChart',
    ['Paid', 'Pending', 'Overdue'],
    [paid, pending, overdue],
    [CHART_COLORS.success, CHART_COLORS.warning, CHART_COLORS.danger]
  );
}

/* ── Complaint Status Chart ── */
function initComplaintChart(open, inProg, resolved) {
  initDonutChart(
    'complaintChart',
    ['Open', 'In Progress', 'Resolved'],
    [open, inProg, resolved],
    [CHART_COLORS.danger, CHART_COLORS.warning, CHART_COLORS.success]
  );
}

/* ── Attendance Percentage Bar (student detail) ── */
function animateProgressBars() {
  document.querySelectorAll('.progress-bar-modern[data-width]').forEach(bar => {
    const w = bar.getAttribute('data-width');
    setTimeout(() => bar.style.width = w + '%', 200);
  });
}

/* ── Attendance Mark All ── */
function initAttendanceMarkAll() {
  const presentAll = document.getElementById('markAllPresent');
  const absentAll  = document.getElementById('markAllAbsent');

  presentAll?.addEventListener('click', () => {
    document.querySelectorAll('input[type=radio][value=Present]').forEach(r => r.checked = true);
  });
  absentAll?.addEventListener('click', () => {
    document.querySelectorAll('input[type=radio][value=Absent]').forEach(r => r.checked = true);
  });
}

/* ── Edit Button ── */
function initEditButtons() {
  document.querySelectorAll('[data-edit]').forEach(btn => {
    btn.addEventListener('click', function() {
      const raw = this.getAttribute('data-edit');
      try {
        const data = JSON.parse(raw);
        const targetId = this.getAttribute('data-target');
        populateEditModal(targetId, data);
        const modal = new bootstrap.Modal(document.getElementById(targetId));
        modal.show();
      } catch(e) { console.error('Edit parse error:', e); }
    });
  });
}

/* ── Toast-style table row highlight ── */
function highlightNewRows() {
  const hash = window.location.hash;
  if (hash) {
    const el = document.querySelector(hash);
    if (el) {
      el.style.background = '#eef2ff';
      setTimeout(() => el.style.background = '', 2500);
    }
  }
}

/* ── Number Counter Animation ── */
function animateCounters() {
  document.querySelectorAll('.stat-value[data-target]').forEach(el => {
    const target = parseInt(el.getAttribute('data-target'), 10);
    const duration = 1000;
    const step = target / (duration / 16);
    let current = 0;
    const timer = setInterval(() => {
      current = Math.min(current + step, target);
      el.textContent = Math.floor(current).toLocaleString();
      if (current >= target) clearInterval(timer);
    }, 16);
  });
}

/* ── Filter pill clicks ── */
function initFilterPills() {
  document.querySelectorAll('.filter-pill[data-param]').forEach(pill => {
    pill.addEventListener('click', function(e) {
      e.preventDefault();
      const param = this.dataset.param;
      const value = this.dataset.value;
      const url = new URL(window.location.href);
      if (value) url.searchParams.set(param, value);
      else url.searchParams.delete(param);
      window.location.href = url.toString();
    });
  });
}

/* ── Init ── */
document.addEventListener('DOMContentLoaded', () => {
  initFlashAlerts();
  setActiveNav();
  initPasswordToggle();
  initAttendanceMarkAll();
  initEditButtons();
  highlightNewRows();
  animateProgressBars();
  initFilterPills();
  setTimeout(animateCounters, 100);
});