/**
 * AttendSynth AI — Dataset Explorer Controller
 */

document.addEventListener('DOMContentLoaded', async () => {
  let currentPage = 1;
  let currentPageSize = 25;
  let totalPages = 1;
  let currentStudentId = null;

  // DOM Elements
  const searchIdInput = document.getElementById('searchIdInput');
  const deptFilterSelect = document.getElementById('deptFilterSelect');
  const yearFilterSelect = document.getElementById('yearFilterSelect');
  const semFilterSelect = document.getElementById('semFilterSelect');
  const riskFilterSelect = document.getElementById('riskFilterSelect');
  const clearFiltersBtn = document.getElementById('clearFiltersBtn');

  const metricMatching = document.getElementById('metricMatching');
  const metricTotal = document.getElementById('metricTotal');
  const metricFilteredOut = document.getElementById('metricFilteredOut');

  const pageSizeSelect = document.getElementById('pageSizeSelect');
  const pageIndicator = document.getElementById('pageIndicator');
  const prevPageBtn = document.getElementById('prevPageBtn');
  const nextPageBtn = document.getElementById('nextPageBtn');

  const tableHead = document.getElementById('explorerTableHead');
  const tableBody = document.getElementById('explorerTableBody');
  const descStatsBody = document.getElementById('descStatsBody');

  // Modal elements
  const studentModalEl = document.getElementById('studentDetailModal');
  const studentModal = new bootstrap.Modal(studentModalEl);
  const studentDetailTitle = document.getElementById('studentDetailTitle');
  const studentDetailBody = document.getElementById('studentDetailBody');
  const modalAskAiBtn = document.getElementById('modalAskAiBtn');

  async function loadData() {
    tableBody.innerHTML = '<tr><td colspan="10" class="text-center py-4 text-muted">Fetching records...</td></tr>';

    const params = {
      search_id: searchIdInput.value.trim(),
      department: deptFilterSelect.value,
      year_of_study: yearFilterSelect.value,
      semester: semFilterSelect.value,
      risk_category: riskFilterSelect.value,
      page: currentPage,
      page_size: currentPageSize,
    };

    try {
      const data = await window.API.getDataset(params);

      // Populate filter dropdowns on first load
      if (data.filter_options) {
        populateSelect(deptFilterSelect, data.filter_options.departments, 'All Departments');
        populateSelect(yearFilterSelect, data.filter_options.years_of_study, 'All Years');
        populateSelect(semFilterSelect, data.filter_options.semesters, 'All Semesters');
      }

      metricMatching.textContent = (data.filtered_records || 0).toLocaleString();
      metricTotal.textContent = (data.total_cohort || 0).toLocaleString();
      metricFilteredOut.textContent = (data.filtered_out || 0).toLocaleString();

      totalPages = data.total_pages || 1;
      currentPage = data.page || 1;
      pageIndicator.textContent = `Page ${currentPage} of ${totalPages} (${data.filtered_records} records)`;

      prevPageBtn.disabled = (currentPage <= 1);
      nextPageBtn.disabled = (currentPage >= totalPages);

      // Render Table Headers
      tableHead.innerHTML = `
        <tr>
          <th>Student ID</th>
          <th>Age</th>
          <th>Department</th>
          <th>Year</th>
          <th>Semester</th>
          <th>Attendance %</th>
          <th>Engagement</th>
          <th>Academic Score</th>
          <th>Risk Score</th>
          <th>Risk Category</th>
          <th class="text-end">Actions</th>
        </tr>
      `;

      // Render Rows
      if (!data.records || data.records.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="11" class="text-center py-4 text-muted">No student records match the active criteria.</td></tr>';
      } else {
        tableBody.innerHTML = data.records.map((r) => {
          let badgeClass = 'badge-risk-low';
          if (r.risk_category === 'Medium') badgeClass = 'badge-risk-medium';
          if (r.risk_category === 'High') badgeClass = 'badge-risk-high';

          return `
            <tr>
              <td class="fw-bold font-monospace text-primary">${r.student_id}</td>
              <td>${r.age}</td>
              <td>${r.department}</td>
              <td>${r.year_of_study}</td>
              <td>${r.semester}</td>
              <td>${r.attendance_percentage}%</td>
              <td>${r.engagement_score}</td>
              <td>${r.academic_performance_score}</td>
              <td class="fw-bold">${r.risk_score}</td>
              <td><span class="badge-risk ${badgeClass}">${r.risk_category}</span></td>
              <td class="text-end">
                <button class="btn btn-sm btn-outline-primary py-0 px-2 btn-view-student" data-id="${r.student_id}">
                  <i class="bi bi-eye me-1"></i> Inspect
                </button>
              </td>
            </tr>
          `;
        }).join('');

        // Attach modal triggers
        document.querySelectorAll('.btn-view-student').forEach((btn) => {
          btn.addEventListener('click', () => openStudentModal(btn.dataset.id));
        });
      }

      // Descriptive Stats
      if (data.descriptive_stats && Object.keys(data.descriptive_stats).length > 0) {
        const stats = data.descriptive_stats;
        const metrics = ['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max'];
        descStatsBody.innerHTML = metrics.map((m) => `
          <tr>
            <td class="fw-semibold text-uppercase small text-muted">${m}</td>
            <td>${stats.attendance_percentage ? stats.attendance_percentage[m] ?? '—' : '—'}</td>
            <td>${stats.engagement_score ? stats.engagement_score[m] ?? '—' : '—'}</td>
            <td>${stats.assignment_completion_percentage ? stats.assignment_completion_percentage[m] ?? '—' : '—'}</td>
            <td>${stats.academic_performance_score ? stats.academic_performance_score[m] ?? '—' : '—'}</td>
            <td>${stats.risk_score ? stats.risk_score[m] ?? '—' : '—'}</td>
          </tr>
        `).join('');
      } else {
        descStatsBody.innerHTML = '<tr><td colspan="6" class="text-center py-2 text-muted">No statistics available.</td></tr>';
      }
    } catch (err) {
      tableBody.innerHTML = `<tr><td colspan="11" class="text-center py-4 text-danger">Failed to load dataset: ${err.message}</td></tr>`;
    }
  }

  function populateSelect(selectEl, items, allLabel) {
    if (!items || selectEl.dataset.populated) return;
    const currentVal = selectEl.value;
    selectEl.innerHTML = `<option value="All">${allLabel}</option>` +
      items.map((it) => `<option value="${it}">${it}</option>`).join('');
    if (items.includes(currentVal)) selectEl.value = currentVal;
    selectEl.dataset.populated = 'true';
  }

  // Individual Student Modal
  async function openStudentModal(studentId) {
    currentStudentId = studentId;
    studentDetailTitle.textContent = `Student Evaluation: ${studentId}`;
    studentDetailBody.innerHTML = '<div class="text-center py-4"><span class="spinner-border spinner-border-sm me-2"></span>Loading factor breakdown...</div>';
    studentModal.show();

    try {
      const res = await window.API.getStudentRisk(studentId);
      const s = res.student;
      const b = res.formula_breakdown;

      let badgeClass = 'badge-risk-low';
      if (s.risk_category === 'Medium') badgeClass = 'badge-risk-medium';
      if (s.risk_category === 'High') badgeClass = 'badge-risk-high';

      studentDetailBody.innerHTML = `
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
              <div class="fw-semibold">${s.attendance_percentage}% (${s.classes_attended}/${s.total_classes} classes)</div>
            </div>
          </div>
          <div class="col-6 col-md-3">
            <div class="p-2 border rounded bg-light">
              <div class="small text-muted">Risk Classification</div>
              <div><span class="badge-risk ${badgeClass}">${s.risk_category} (Score: ${s.risk_score})</span></div>
            </div>
          </div>
        </div>

        <h6 class="fw-bold mb-2">Rule-Based Contributing Factors</h6>
        <div class="mb-4">
          ${res.contributing_factors.map(f => `<div class="p-2 mb-1 border-start border-3 border-warning bg-light small">${f}</div>`).join('')}
        </div>

        <h6 class="fw-bold mb-2">Deterministic Formula Calculation</h6>
        <div class="p-3 border rounded font-monospace small bg-light">
          <div>Positive Component = 0.35×(${s.attendance_percentage}%) + 0.25×(${s.engagement_score}) + 0.25×(${s.assignment_completion_percentage}%) + 0.15×(${s.academic_performance_score})</div>
          <div>Positive Index = ${b.attendance_contribution} + ${b.engagement_contribution} + ${b.assignment_contribution} + ${b.academic_contribution} = <strong>${b.positive_index}</strong></div>
          <div class="mt-2 text-danger fw-bold">Risk Score = 100 − ${b.positive_index} = ${b.risk_score} (${b.risk_category} Risk)</div>
        </div>
      `;
    } catch (err) {
      studentDetailBody.innerHTML = `<div class="alert alert-danger">Failed to load student factors: ${err.message}</div>`;
    }
  }

  modalAskAiBtn.addEventListener('click', () => {
    if (!currentStudentId) return;
    studentModal.hide();
    window.location.href = `/pages/ai-assistant.html?student_id=${encodeURIComponent(currentStudentId)}`;
  });

  // Filter Listeners
  let debounceTimer;
  searchIdInput.addEventListener('input', () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      currentPage = 1;
      loadData();
    }, 350);
  });

  [deptFilterSelect, yearFilterSelect, semFilterSelect, riskFilterSelect].forEach((sel) => {
    sel.addEventListener('change', () => {
      currentPage = 1;
      loadData();
    });
  });

  clearFiltersBtn.addEventListener('click', () => {
    searchIdInput.value = '';
    deptFilterSelect.value = 'All';
    yearFilterSelect.value = 'All';
    semFilterSelect.value = 'All';
    riskFilterSelect.value = 'All';
    currentPage = 1;
    loadData();
  });

  pageSizeSelect.addEventListener('change', (e) => {
    currentPageSize = parseInt(e.target.value) || 25;
    currentPage = 1;
    loadData();
  });

  prevPageBtn.addEventListener('click', () => {
    if (currentPage > 1) {
      currentPage--;
      loadData();
    }
  });

  nextPageBtn.addEventListener('click', () => {
    if (currentPage < totalPages) {
      currentPage++;
      loadData();
    }
  });

  await loadData();
});
