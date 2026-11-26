/**
 * AttendSynth AI — Analytics Dashboard Controller
 */

document.addEventListener('DOMContentLoaded', async () => {
  const deptSelect = document.getElementById('deptSelect');
  const kpiStudents = document.getElementById('kpiStudents');
  const kpiAttendance = document.getElementById('kpiAttendance');
  const kpiEngagement = document.getElementById('kpiEngagement');
  const kpiAcademic = document.getElementById('kpiAcademic');
  const kpiHighRisk = document.getElementById('kpiHighRisk');
  const insightsRow = document.getElementById('insightsRow');

  let charts = {};

  function destroyChart(name) {
    if (charts[name]) {
      charts[name].destroy();
      charts[name] = null;
    }
  }

  async function loadAnalytics(dept = 'All') {
    try {
      const data = await window.API.getAnalytics(dept);
      if (!data.has_cohort) {
        window.App.showToast('No active cohort found. Generate a dataset first.', 'warning');
        return;
      }

      // Populate Department Dropdown if not yet done
      if (data.available_departments && !deptSelect.dataset.populated) {
        deptSelect.innerHTML = data.available_departments.map((d) => `<option value="${d}">${d}</option>`).join('');
        deptSelect.value = dept;
        deptSelect.dataset.populated = 'true';
      }

      // KPIs
      const k = data.kpis;
      kpiStudents.textContent = (k.total_students || 0).toLocaleString();
      kpiAttendance.textContent = `${k.avg_attendance}%`;
      kpiEngagement.textContent = `${k.avg_engagement}/100`;
      kpiAcademic.textContent = `${k.avg_academic}/100`;
      kpiHighRisk.textContent = `${k.high_risk_count} (${k.high_risk_pct}%)`;

      // Insights
      if (data.insights && data.insights.length > 0) {
        insightsRow.innerHTML = data.insights.map((ins) => `
          <div class="col-12 col-md-6">
            <div class="insight-box">${ins.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')}</div>
          </div>
        `).join('');
      } else {
        insightsRow.innerHTML = '<div class="col-12 text-muted">No insights generated.</div>';
      }

      const c = data.charts;

      // 1. Attendance Distribution Histogram
      destroyChart('attendance');
      if (c.attendance_histogram) {
        charts['attendance'] = new Chart(document.getElementById('chartAttendance'), {
          type: 'bar',
          data: {
            labels: c.attendance_histogram.labels,
            datasets: [{
              label: 'Students',
              data: c.attendance_histogram.counts,
              backgroundColor: 'rgba(37, 99, 235, 0.8)',
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

      // 2. Engagement Histogram
      destroyChart('engagement');
      if (c.engagement_histogram) {
        charts['engagement'] = new Chart(document.getElementById('chartEngagement'), {
          type: 'bar',
          data: {
            labels: c.engagement_histogram.labels,
            datasets: [{
              label: 'Students',
              data: c.engagement_histogram.counts,
              backgroundColor: 'rgba(13, 148, 136, 0.8)',
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

      // 3. Academic Histogram
      destroyChart('academic');
      if (c.academic_histogram) {
        charts['academic'] = new Chart(document.getElementById('chartAcademic'), {
          type: 'bar',
          data: {
            labels: c.academic_histogram.labels,
            datasets: [{
              label: 'Students',
              data: c.academic_histogram.counts,
              backgroundColor: 'rgba(96, 165, 250, 0.8)',
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

      // 4. Department Attendance Bar
      destroyChart('deptAttendance');
      if (c.department_attendance) {
        charts['deptAttendance'] = new Chart(document.getElementById('chartDeptAttendance'), {
          type: 'bar',
          data: {
            labels: c.department_attendance.departments,
            datasets: [{
              label: 'Avg Attendance (%)',
              data: c.department_attendance.averages,
              backgroundColor: 'rgba(59, 130, 246, 0.75)',
              borderRadius: 4,
            }],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: { legend: { display: false } },
            scales: {
              x: { min: 0, max: 100, grid: { color: '#f1f5f9' } },
              y: { grid: { display: false } },
            },
          },
        });
      }

      // 5. Risk Donut
      destroyChart('riskDonut');
      if (c.risk_distribution) {
        charts['riskDonut'] = new Chart(document.getElementById('chartRiskDonut'), {
          type: 'doughnut',
          data: {
            labels: c.risk_distribution.labels,
            datasets: [{
              data: c.risk_distribution.counts,
              backgroundColor: c.risk_distribution.colors,
              borderWidth: 2,
              borderColor: '#ffffff',
            }],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { position: 'bottom', labels: { boxWidth: 12 } },
            },
            cutout: '65%',
          },
        });
      }

      // 6. Scatter Plot
      destroyChart('scatter');
      if (c.attendance_vs_engagement) {
        const scatterData = c.attendance_vs_engagement.map((p) => ({
          x: p.x,
          y: p.y,
          student_id: p.student_id,
          risk: p.risk_category,
        }));

        charts['scatter'] = new Chart(document.getElementById('chartScatter'), {
          type: 'scatter',
          data: {
            datasets: [{
              label: 'Students',
              data: scatterData,
              backgroundColor: c.attendance_vs_engagement.map((p) => p.color),
              pointRadius: 4,
              pointHoverRadius: 6,
            }],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { display: false },
              tooltip: {
                callbacks: {
                  label: (ctx) => {
                    const raw = ctx.raw;
                    return `${raw.student_id}: Attendance ${raw.x}%, Engagement ${raw.y} (${raw.risk})`;
                  },
                },
              },
            },
            scales: {
              x: { title: { display: true, text: 'Attendance (%)' }, min: 0, max: 100, grid: { color: '#f1f5f9' } },
              y: { title: { display: true, text: 'Engagement Score (0–100)' }, min: 0, max: 100, grid: { color: '#f1f5f9' } },
            },
          },
        });
      }

      // 7. Engagement Bands Stacked Bar
      destroyChart('engagementBands');
      if (c.engagement_bands) {
        charts['engagementBands'] = new Chart(document.getElementById('chartEngagementBands'), {
          type: 'bar',
          data: {
            labels: c.engagement_bands.departments,
            datasets: [
              {
                label: 'Low (0-40)',
                data: c.engagement_bands.low,
                backgroundColor: '#EF4444',
                borderRadius: 2,
              },
              {
                label: 'Medium (40-70)',
                data: c.engagement_bands.medium,
                backgroundColor: '#F59E0B',
                borderRadius: 2,
              },
              {
                label: 'High (70-100)',
                data: c.engagement_bands.high,
                backgroundColor: '#10B981',
                borderRadius: 2,
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { position: 'bottom', labels: { boxWidth: 12 } },
            },
            scales: {
              x: { stacked: true, grid: { display: false } },
              y: { stacked: true, beginAtZero: true, grid: { color: '#f1f5f9' } },
            },
          },
        });
      }
    } catch (err) {
      window.App.showToast(`Failed to load analytics: ${err.message}`, 'danger');
    }
  }

  deptSelect.addEventListener('change', (e) => {
    loadAnalytics(e.target.value);
  });

  await loadAnalytics();
});
