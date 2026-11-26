/**
 * AttendSynth AI — Early Warning Analysis Controller
 */

document.addEventListener('DOMContentLoaded', async () => {
  const riskTotal = document.getElementById('riskTotal');
  const riskLowVal = document.getElementById('riskLowVal');
  const riskLowSub = document.getElementById('riskLowSub');
  const riskMedVal = document.getElementById('riskMedVal');
  const riskMedSub = document.getElementById('riskMedSub');
  const riskHighVal = document.getElementById('riskHighVal');
  const riskHighSub = document.getElementById('riskHighSub');
  const highRiskBadge = document.getElementById('highRiskBadge');
  const highRiskTableBody = document.getElementById('highRiskTableBody');

  // Modal
  const modalEl = document.getElementById('riskStudentModal');
  const modal = new bootstrap.Modal(modalEl);
  const modalTitle = document.getElementById('riskModalTitle');
  const modalBody = document.getElementById('riskModalBody');
  const modalAskAiBtn = document.getElementById('riskModalAskAiBtn');
  let selectedStudentId = null;

  let propChart = null;
  let histChart = null;

  async function loadRiskData() {
    try {
      const data = await window.API.getRiskAnalysis();
      if (!data.has_cohort) {
        window.App.showToast('No active cohort available. Generate a dataset first.', 'warning');
        return;
      }

      const dist = data.distribution;
      const pcts = dist.percentages || {};

      riskTotal.textContent = (data.total_evaluated || 0).toLocaleString();
      riskLowVal.textContent = (dist.low_risk_count || 0).toLocaleString();
      riskLowSub.textContent = `${pcts.Low || 0}% of cohort (Score < 35)`;

      riskMedVal.textContent = (dist.medium_risk_count || 0).toLocaleString();
      riskMedSub.textContent = `${pcts.Medium || 0}% of cohort (Score 35–59)`;

      riskHighVal.textContent = (dist.high_risk_count || 0).toLocaleString();
      riskHighSub.textContent = `${pcts.High || 0}% of cohort (Score ≥ 60)`;

      highRiskBadge.textContent = `${dist.high_risk_count} Students`;

      // 1. Proportions Bar Chart
      if (propChart) propChart.destroy();
      propChart = new Chart(document.getElementById('chartRiskProportions'), {
        type: 'bar',
        data: {
          labels: ['Low Risk', 'Medium Risk', 'High Risk'],
          datasets: [{
            label: '% of Cohort',
            data: [pcts.Low || 0, pcts.Medium || 0, pcts.High || 0],
            backgroundColor: ['#10B981', '#F59E0B', '#EF4444'],
            borderRadius: 6,
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { grid: { display: false } },
            y: { title: { display: true, text: '% of Students' }, beginAtZero: true, grid: { color: '#f1f5f9' } },
          },
        },
      });

      // 2. Risk Score Histogram
      if (histChart) histChart.destroy();
      const scoreHist = data.risk_score_histogram;
      if (scoreHist) {
        histChart = new Chart(document.getElementById('chartRiskHistogram'), {
          type: 'bar',
          data: {
            labels: scoreHist.labels,
            datasets: [{
              label: 'Student Count',
              data: scoreHist.counts,
              backgroundColor: 'rgba(239, 68, 68, 0.75)',
              borderRadius: 4,
            }],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
              x: { grid: { display: false } },
              y: { beginAtZero: true, grid: { color: '#f1f5f9' } },
            },
          },
        });
      }

      // High Risk Table
      const highRisk = data.high_risk_students || [];
      if (highRisk.length === 0) {
        highRiskTableBody.innerHTML = '<tr><td colspan="10" class="text-center py-4 text-success fw-semibold"><i class="bi bi-check-circle me-1"></i> No students are currently in the High-Risk category.</td></tr>';
      } else {
        highRiskTableBody.innerHTML = highRisk.map((s) => {
          const topFactor = s.primary_factors && s.primary_factors.length > 0 ? s.primary_factors[0] : 'High risk index';
          return `
            <tr>
              <td class="fw-bold font-monospace text-primary">${s.student_id}</td>
              <td>${s.department}</td>
              <td>${s.year_of_study}</td>
              <td class="text-danger fw-semibold">${s.attendance_percentage}%</td>
              <td>${s.engagement_score}</td>
              <td>${s.assignment_completion_percentage}%</td>
              <td>${s.academic_performance_score}</td>
              <td class="fw-bold text-danger">${s.risk_score}</td>
              <td class="small text-muted">${topFactor}</td>
              <td class="text-end">
                <button class="btn btn-sm btn-outline-danger py-0 px-2 btn-audit-student" data-id="${s.student_id}">
                  Audit
                </button>
              </td>
            </tr>
          `;
        }).join('');

        document.querySelectorAll('.btn-audit-student').forEach((btn) => {
          btn.addEventListener('click', () => openStudentModal(btn.dataset.id));
        });
      }
    } catch (err) {
      window.App.showToast(`Failed to load risk analysis: ${err.message}`, 'danger');
    }
  }

  async function openStudentModal(studentId) {
    selectedStudentId = studentId;
    modalTitle.textContent = `Student Vulnerability Audit: ${studentId}`;
    modalBody.innerHTML = '<div class="text-center py-4"><span class="spinner-border spinner-border-sm me-2"></span>Loading audit...</div>';
    modal.show();

    try {
      const res = await window.API.getStudentRisk(studentId);
      const s = res.student;
      const b = res.formula_breakdown;

      modalBody.innerHTML = `
        <div class="row g-3 mb-4">
          <div class="col-6 col-md-3">
            <div class="p-2 border rounded bg-light">
              <div class="small text-muted">Department</div>
              <div class="fw-semibold">${s.department}</div>
            </div>
          </div>
          <div class="col-6 col-md-3">
            <div class="p-2 border rounded bg-light">
              <div class="small text-muted">Study Term</div>
              <div class="fw-semibold">${s.year_of_study} (${s.semester})</div>
            </div>
          </div>
          <div class="col-6 col-md-3">
            <div class="p-2 border rounded bg-light">
              <div class="small text-muted">Attendance Rate</div>
              <div class="fw-semibold text-danger">${s.attendance_percentage}% (${s.classes_attended}/${s.total_classes} classes)</div>
            </div>
          </div>
          <div class="col-6 col-md-3">
            <div class="p-2 border rounded bg-light">
              <div class="small text-muted">Risk Score</div>
              <div class="fw-bold text-danger fs-5">${s.risk_score} / 100</div>
            </div>
          </div>
        </div>

        <h6 class="fw-bold mb-2">Primary Risk Drivers</h6>
        <div class="mb-4">
          ${res.contributing_factors.map(f => `<div class="p-2 mb-1 border-start border-3 border-danger bg-light small">${f}</div>`).join('')}
        </div>

        <h6 class="fw-bold mb-2">Deterministic Scoring Math</h6>
        <div class="p-3 border rounded font-monospace small bg-light">
          <div>Positive Component = 0.35×(${s.attendance_percentage}) + 0.25×(${s.engagement_score}) + 0.25×(${s.assignment_completion_percentage}) + 0.15×(${s.academic_performance_score})</div>
          <div>Positive Component = ${b.attendance_contribution} + ${b.engagement_contribution} + ${b.assignment_contribution} + ${b.academic_contribution} = <strong>${b.positive_index}</strong></div>
          <div class="mt-2 text-danger fw-bold">Calculated Risk Score = 100 − ${b.positive_index} = ${b.risk_score} (${b.risk_category} Risk)</div>
        </div>
      `;
    } catch (err) {
      modalBody.innerHTML = `<div class="alert alert-danger">Error: ${err.message}</div>`;
    }
  }

  modalAskAiBtn.addEventListener('click', () => {
    if (!selectedStudentId) return;
    modal.hide();
    window.location.href = `/pages/ai-assistant.html?student_id=${encodeURIComponent(selectedStudentId)}`;
  });

  await loadRiskData();
});
