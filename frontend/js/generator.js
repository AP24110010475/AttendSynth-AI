/**
 * AttendSynth AI — Data Generator Controller
 */

document.addEventListener('DOMContentLoaded', async () => {
  const form = document.getElementById('generatorForm');
  const nStudentsInput = document.getElementById('nStudentsInput');
  const academicYearSelect = document.getElementById('academicYearSelect');
  const semesterSelect = document.getElementById('semesterSelect');
  const departmentsTextarea = document.getElementById('departmentsTextarea');
  const seedInput = document.getElementById('seedInput');
  const autoValidateCheck = document.getElementById('autoValidateCheck');
  const generateBtn = document.getElementById('generateBtn');
  const resetBtn = document.getElementById('resetBtn');

  // Sliders
  const sliderRegular = document.getElementById('sliderRegular');
  const sliderModerate = document.getElementById('sliderModerate');
  const sliderIrregular = document.getElementById('sliderIrregular');
  const sliderLow = document.getElementById('sliderLow');
  const valRegular = document.getElementById('valRegular');
  const valModerate = document.getElementById('valModerate');
  const valIrregular = document.getElementById('valIrregular');
  const valLow = document.getElementById('valLow');
  const totalWeightBadge = document.getElementById('totalWeightBadge');

  // Results Section
  const resultCard = document.getElementById('generationResultCard');
  const genResultSubtitle = document.getElementById('genResultSubtitle');
  const genKpiRow = document.getElementById('genKpiRow');
  const sampleRecordsBody = document.getElementById('sampleRecordsBody');

  function updateSliderDisplay() {
    const r = parseInt(sliderRegular.value) || 0;
    const m = parseInt(sliderModerate.value) || 0;
    const i = parseInt(sliderIrregular.value) || 0;
    const l = parseInt(sliderLow.value) || 0;

    valRegular.textContent = `${r}%`;
    valModerate.textContent = `${m}%`;
    valIrregular.textContent = `${i}%`;
    valLow.textContent = `${l}%`;

    const total = r + m + i + l;
    totalWeightBadge.textContent = `Total: ${total}%`;
    totalWeightBadge.className = `badge ${total === 100 ? 'bg-success' : 'bg-primary'}`;
  }

  [sliderRegular, sliderModerate, sliderIrregular, sliderLow].forEach((sl) => {
    sl.addEventListener('input', updateSliderDisplay);
  });

  // Load defaults from backend
  async function loadDefaults() {
    try {
      const defs = await window.API.getGeneratorDefaults();
      nStudentsInput.value = defs.default_n_students;
      seedInput.value = defs.default_seed;
      academicYearSelect.value = defs.default_academic_year;
      semesterSelect.value = defs.default_semester;
      departmentsTextarea.value = defs.default_departments.join('\n');

      sliderRegular.value = defs.default_attendance_distribution.Regular || 40;
      sliderModerate.value = defs.default_attendance_distribution.Moderate || 30;
      sliderIrregular.value = defs.default_attendance_distribution.Irregular || 20;
      sliderLow.value = defs.default_attendance_distribution.Low || 10;
      updateSliderDisplay();
    } catch (err) {
      console.warn('Could not load generator defaults, using client fallback.', err);
      departmentsTextarea.value = [
        'Computer Science',
        'Electronics',
        'Mechanical',
        'Civil',
        'Business Administration',
      ].join('\n');
      updateSliderDisplay();
    }
  }

  resetBtn.addEventListener('click', loadDefaults);
  await loadDefaults();

  // Form Submission
  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const depts = departmentsTextarea.value
      .split('\n')
      .map((d) => d.trim())
      .filter((d) => d.length > 0);

    if (depts.length === 0) {
      window.App.showToast('Please enter at least one academic department.', 'warning');
      return;
    }

    const attDist = {
      Regular: parseInt(sliderRegular.value) || 0,
      Moderate: parseInt(sliderModerate.value) || 0,
      Irregular: parseInt(sliderIrregular.value) || 0,
      Low: parseInt(sliderLow.value) || 0,
    };

    const payload = {
      n_students: parseInt(nStudentsInput.value) || 300,
      academic_year: academicYearSelect.value,
      semester: semesterSelect.value,
      departments: depts,
      attendance_distribution: attDist,
      seed: parseInt(seedInput.value) || 42,
      auto_validate: autoValidateCheck.checked,
    };

    window.App.setLoading(generateBtn, true, 'Synthesizing Cohort...');

    try {
      const res = await window.API.generateCohort(payload);
      window.App.showToast(res.message, 'success');

      // Update sidebar status
      window.App.refreshCohortStatus();

      // Display result summary card
      resultCard.classList.remove('d-none');
      genResultSubtitle.textContent = `Generated ${res.metadata.n_students} students for Academic Year ${res.metadata.academic_year} (${res.metadata.semester} Sem) with Seed ${res.metadata.seed}.`;

      const kpis = res.kpis;
      genKpiRow.innerHTML = `
        <div class="col-6 col-md-3">
          <div class="p-3 bg-light rounded text-center border">
            <div class="text-muted small">Total Students</div>
            <div class="fs-4 fw-bold text-primary">${kpis.total_students.toLocaleString()}</div>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="p-3 bg-light rounded text-center border">
            <div class="text-muted small">Avg Attendance</div>
            <div class="fs-4 fw-bold text-success">${kpis.avg_attendance}%</div>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="p-3 bg-light rounded text-center border">
            <div class="text-muted small">Avg Engagement</div>
            <div class="fs-4 fw-bold text-info">${kpis.avg_engagement}/100</div>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="p-3 bg-light rounded text-center border">
            <div class="text-muted small">High Risk Count</div>
            <div class="fs-4 fw-bold text-danger">${kpis.high_risk_count} (${kpis.high_risk_pct}%)</div>
          </div>
        </div>
      `;

      // Sample records table
      sampleRecordsBody.innerHTML = res.sample_records.map((r) => {
        let riskClass = 'badge-risk-low';
        if (r.risk_category === 'Medium') riskClass = 'badge-risk-medium';
        if (r.risk_category === 'High') riskClass = 'badge-risk-high';

        return `
          <tr>
            <td class="fw-bold font-monospace">${r.student_id}</td>
            <td>${r.department}</td>
            <td>${r.year_of_study}</td>
            <td>${r.attendance_percentage}%</td>
            <td>${r.engagement_score}</td>
            <td>${r.academic_performance_score}</td>
            <td><span class="badge-risk ${riskClass}">${r.risk_category}</span></td>
          </tr>
        `;
      }).join('');

      resultCard.scrollIntoView({ behavior: 'smooth' });
    } catch (err) {
      window.App.showToast(`Generation failed: ${err.message}`, 'danger');
    } finally {
      window.App.setLoading(generateBtn, false);
    }
  });
});
