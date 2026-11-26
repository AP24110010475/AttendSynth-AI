/**
 * AttendSynth AI — Data Quality Audit Controller
 */

document.addEventListener('DOMContentLoaded', async () => {
  const qTotal = document.getElementById('qTotal');
  const qValid = document.getElementById('qValid');
  const qInvalid = document.getElementById('qInvalid');
  const qMissing = document.getElementById('qMissing');
  const qDupes = document.getElementById('qDupes');

  const qualityScoreBanner = document.getElementById('qualityScoreBanner');
  const qualityScoreHeading = document.getElementById('qualityScoreHeading');
  const qualityScoreDesc = document.getElementById('qualityScoreDesc');

  const validationChecksBody = document.getElementById('validationChecksBody');
  const completenessBody = document.getElementById('completenessBody');

  try {
    const data = await window.API.getDataQuality();
    if (!data.has_cohort) {
      window.App.showToast('No active dataset found. Please generate a cohort first.', 'warning');
      return;
    }

    const s = data.summary;
    qTotal.textContent = (s.total_records || 0).toLocaleString();
    qValid.textContent = (s.valid_records || 0).toLocaleString();
    qInvalid.textContent = (s.invalid_records || 0).toLocaleString();
    qMissing.textContent = (s.missing_values || 0).toLocaleString();
    qDupes.textContent = (s.duplicate_ids || 0).toLocaleString();

    // Banner status
    const qpct = data.quality_pct;
    if (qpct === 100) {
      qualityScoreBanner.className = 'alert alert-success border d-flex align-items-center gap-3 mb-4';
      qualityScoreHeading.textContent = `Data Quality Score: ${qpct}% (Perfect)`;
      qualityScoreDesc.textContent = `All ${data.checks.length} deterministic validation checks passed with zero integrity anomalies.`;
    } else if (qpct >= 95) {
      qualityScoreBanner.className = 'alert alert-warning border d-flex align-items-center gap-3 mb-4';
      qualityScoreHeading.textContent = `Data Quality Score: ${qpct}% (Minor Flags)`;
      qualityScoreDesc.textContent = 'Minor validation inconsistencies detected. Review table below for affected records.';
    } else {
      qualityScoreBanner.className = 'alert alert-danger border d-flex align-items-center gap-3 mb-4';
      qualityScoreHeading.textContent = `Data Quality Score: ${qpct}% (Critical)`;
      qualityScoreDesc.textContent = 'Significant anomalies detected in bounds or physical calculations.';
    }

    // 11 Checks Table
    validationChecksBody.innerHTML = data.checks.map((c) => {
      const badge = c.passed
        ? '<span class="badge bg-success-subtle text-success border border-success-subtle px-2 py-1"><i class="bi bi-check-circle-fill me-1"></i> Passed</span>'
        : '<span class="badge bg-danger-subtle text-danger border border-danger-subtle px-2 py-1"><i class="bi bi-x-circle-fill me-1"></i> Failed</span>';

      return `
        <tr>
          <td class="fw-semibold text-dark">${c.check}</td>
          <td>${badge}</td>
          <td class="${c.count > 0 ? 'text-danger fw-bold' : 'text-muted'}">${c.count}</td>
          <td class="small font-monospace text-muted">${c.detail}</td>
        </tr>
      `;
    }).join('');

    // Attribute Completeness Table
    completenessBody.innerHTML = data.attribute_completeness.map((col) => {
      const statusBadge = col.status === 'OK'
        ? '<span class="badge bg-light text-success border"><i class="bi bi-check-lg me-1"></i> 100% Complete</span>'
        : `<span class="badge bg-danger">${col.missing_count} Null</span>`;

      return `
        <tr>
          <td class="font-monospace fw-semibold text-primary">${col.column}</td>
          <td>${col.missing_count}</td>
          <td>${col.missing_percentage}%</td>
          <td>${statusBadge}</td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    window.App.showToast(`Failed to audit data quality: ${err.message}`, 'danger');
  }
});
