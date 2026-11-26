/**
 * AttendSynth AI — Export Center Controller
 */

document.addEventListener('DOMContentLoaded', async () => {
  const headline = document.getElementById('exportCohortHeadline');
  const sub = document.getElementById('exportCohortSub');

  try {
    const health = await window.API.getHealth();
    const c = health.active_cohort;

    if (c && c.loaded && c.student_count > 0) {
      headline.textContent = `Active Cohort: ${c.student_count.toLocaleString()} Students Ready for Export`;
      sub.textContent = `Academic Year: ${c.academic_year || '—'} · Seed: ${c.seed ?? '—'}. All export files are dynamically generated from active SQLite storage.`;
    } else {
      headline.textContent = 'No Active Dataset Loaded';
      sub.textContent = 'Generate a synthetic student cohort to unlock CSV and JSON exports.';
    }
  } catch (err) {
    headline.textContent = 'Active Cohort Status Unavailable';
    sub.textContent = 'Could not verify database records.';
  }
});
