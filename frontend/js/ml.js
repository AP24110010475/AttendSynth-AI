/**
 * AttendSynth AI — Machine Learning Demonstration Controller
 */

document.addEventListener('DOMContentLoaded', () => {
  const nTreesInput = document.getElementById('nTreesInput');
  const testSplitInput = document.getElementById('testSplitInput');
  const mlSeedInput = document.getElementById('mlSeedInput');
  const trainModelBtn = document.getElementById('trainModelBtn');

  const mlResultsContainer = document.getElementById('mlResultsContainer');
  const mlPlaceholderState = document.getElementById('mlPlaceholderState');

  const kpiAccuracy = document.getElementById('kpiAccuracy');
  const kpiSplitInfo = document.getElementById('kpiSplitInfo');
  const kpiPrecision = document.getElementById('kpiPrecision');
  const kpiRecall = document.getElementById('kpiRecall');
  const kpiF1 = document.getElementById('kpiF1');

  const confusionMatrixTable = document.getElementById('confusionMatrixTable');
  const classificationReportBody = document.getElementById('classificationReportBody');

  let fiChart = null;

  trainModelBtn.addEventListener('click', async () => {
    const payload = {
      n_estimators: parseInt(nTreesInput.value) || 100,
      test_size: (parseInt(testSplitInput.value) || 25) / 100,
      random_state: parseInt(mlSeedInput.value) || 42,
    };

    window.App.setLoading(trainModelBtn, true, 'Training Random Forest...');

    try {
      const res = await window.API.trainML(payload);

      mlPlaceholderState.classList.add('d-none');
      mlResultsContainer.classList.remove('d-none');

      // KPIs
      kpiAccuracy.textContent = `${res.accuracy}%`;
      kpiSplitInfo.textContent = `Trained on ${res.train_size} · Tested on ${res.test_size}`;
      kpiPrecision.textContent = `${res.precision_macro}%`;
      kpiRecall.textContent = `${res.recall_macro}%`;
      kpiF1.textContent = `${res.f1_macro}%`;

      // Confusion Matrix Table
      const cm = res.confusion_matrix;
      const classes = res.class_names;

      let cmHtml = `
        <thead>
          <tr>
            <th class="bg-light text-muted small" rowspan="2" style="vertical-align: middle;">Actual Risk</th>
            <th class="bg-light text-muted small" colspan="${classes.length}">Predicted Risk Category</th>
          </tr>
          <tr>
            ${classes.map(c => `<th class="small fw-semibold">${c}</th>`).join('')}
          </tr>
        </thead>
        <tbody>
      `;

      for (let i = 0; i < classes.length; i++) {
        cmHtml += `<tr><td class="fw-semibold bg-light text-start">${classes[i]}</td>`;
        for (let j = 0; j < classes.length; j++) {
          const val = cm[i][j];
          const isDiagonal = (i === j);
          const cellBg = isDiagonal ? 'rgba(37, 99, 235, 0.12)' : (val > 0 ? 'rgba(239, 68, 68, 0.12)' : 'transparent');
          const cellColor = isDiagonal ? 'text-primary fw-bold' : (val > 0 ? 'text-danger fw-semibold' : 'text-muted');
          cmHtml += `<td style="background-color:${cellBg};" class="${cellColor} fs-6">${val}</td>`;
        }
        cmHtml += `</tr>`;
      }
      cmHtml += `</tbody>`;
      confusionMatrixTable.innerHTML = cmHtml;

      // Feature Importance Chart
      if (fiChart) fiChart.destroy();
      const fiData = res.feature_importance.slice().reverse();
      fiChart = new Chart(document.getElementById('chartFeatureImportance'), {
        type: 'bar',
        data: {
          labels: fiData.map(f => f.feature.replace(/_/g, ' ')),
          datasets: [{
            label: 'Relative Gini Importance',
            data: fiData.map(f => f.importance),
            backgroundColor: 'rgba(37, 99, 235, 0.8)',
            borderRadius: 4,
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          indexAxis: 'y',
          plugins: { legend: { display: false } },
          scales: {
            x: { beginAtZero: true, grid: { color: '#f1f5f9' } },
            y: { grid: { display: false } },
          },
        },
      });

      // Classification Report Table
      const report = res.classification_report;
      const reportRows = classes.map((c) => {
        const row = report[c] || {};
        return `
          <tr>
            <td class="fw-bold">${c}</td>
            <td>${((row.precision || 0) * 100).toFixed(1)}%</td>
            <td>${((row.recall || 0) * 100).toFixed(1)}%</td>
            <td>${((row['f1-score'] || 0) * 100).toFixed(1)}%</td>
            <td>${row.support || 0}</td>
          </tr>
        `;
      });

      // Add macro average row
      const macro = report['macro avg'] || {};
      reportRows.push(`
        <tr class="table-light fw-bold">
          <td>Macro Average</td>
          <td>${((macro.precision || 0) * 100).toFixed(1)}%</td>
          <td>${((macro.recall || 0) * 100).toFixed(1)}%</td>
          <td>${((macro['f1-score'] || 0) * 100).toFixed(1)}%</td>
          <td>${macro.support || 0}</td>
        </tr>
      `);
      classificationReportBody.innerHTML = reportRows.join('');

      window.App.showToast('Model training and evaluation benchmark complete!', 'success');
      mlResultsContainer.scrollIntoView({ behavior: 'smooth' });
    } catch (err) {
      window.App.showToast(`Training failed: ${err.message}`, 'danger');
    } finally {
      window.App.setLoading(trainModelBtn, false);
    }
  });
});
