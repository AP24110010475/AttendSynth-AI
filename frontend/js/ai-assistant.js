/**
 * AttendSynth AI — AI Academic Insights Assistant Controller
 */

document.addEventListener('DOMContentLoaded', async () => {
  const md = window.markdownit ? window.markdownit({ html: true, linkify: true, typographer: true }) : null;

  // AI Status
  const aiConfigBadge = document.getElementById('aiConfigBadge');
  const aiKeyAlert = document.getElementById('aiKeyAlert');

  // Chatbot
  const chatForm = document.getElementById('chatForm');
  const chatInput = document.getElementById('chatInput');
  const chatHistory = document.getElementById('chatHistory');
  const sendChatBtn = document.getElementById('sendChatBtn');
  const clearChatBtn = document.getElementById('clearChatBtn');
  const promptChips = document.querySelectorAll('.chip-btn');
  let historyTurns = [];

  // Analysis, Recommendations, Report
  const runAnalysisBtn = document.getElementById('runAnalysisBtn');
  const analysisResultArea = document.getElementById('analysisResultArea');

  const runRecommendationsBtn = document.getElementById('runRecommendationsBtn');
  const recommendationsResultArea = document.getElementById('recommendationsResultArea');

  const runReportBtn = document.getElementById('runReportBtn');
  const reportResultArea = document.getElementById('reportResultArea');
  const copyReportBtn = document.getElementById('copyReportBtn');
  let lastReportText = '';

  // Student Explanation
  const studentExplainForm = document.getElementById('studentExplainForm');
  const studentIdInput = document.getElementById('studentIdInput');
  const explainStudentBtn = document.getElementById('explainStudentBtn');
  const studentExplainResultArea = document.getElementById('studentExplainResultArea');
  const tabStudentBtn = document.getElementById('tabStudentBtn');

  // 1. Check AI Configuration Status
  async function checkStatus() {
    try {
      const status = await window.API.getAiStatus();
      if (status.is_configured) {
        aiConfigBadge.className = 'badge bg-success-subtle text-success border border-success-subtle px-2 py-1';
        aiConfigBadge.innerHTML = `<i class="bi bi-check-circle-fill me-1"></i> Gemini Ready (${status.model})`;
        aiKeyAlert.classList.add('d-none');
      } else {
        aiConfigBadge.className = 'badge bg-warning-subtle text-warning border border-warning-subtle px-2 py-1';
        aiConfigBadge.innerHTML = '<i class="bi bi-exclamation-triangle-fill me-1"></i> API Key Missing';
        aiKeyAlert.classList.remove('d-none');
      }
    } catch (err) {
      aiConfigBadge.className = 'badge bg-danger-subtle text-danger border border-danger-subtle px-2 py-1';
      aiConfigBadge.textContent = 'AI Offline';
    }
  }
  await checkStatus();

  function renderMarkdown(content) {
    if (md) {
      return md.render(content);
    }
    return `<div style="white-space: pre-wrap;">${content}</div>`;
  }

  // 2. Chatbot Logic
  function appendMessage(role, text) {
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble chat-bubble-${role === 'user' ? 'user' : 'assistant'}`;

    if (role === 'assistant') {
      bubble.innerHTML = renderMarkdown(text);
    } else {
      bubble.textContent = text;
    }

    chatHistory.appendChild(bubble);
    chatHistory.scrollTop = chatHistory.scrollHeight;
  }

  async function handleChatSubmit(queryText) {
    const q = queryText || chatInput.value.trim();
    if (!q) return;

    appendMessage('user', q);
    chatInput.value = '';
    window.App.setLoading(sendChatBtn, true, 'Thinking...');

    try {
      const res = await window.API.chatWithAi(q, historyTurns);
      if (res.status === 'unconfigured') {
        appendMessage('assistant', `⚠️ **Gemini API Key Required**\n\n${res.message}`);
      } else if (res.status === 'success') {
        appendMessage('assistant', res.reply);
        historyTurns.push({ role: 'user', content: q });
        historyTurns.push({ role: 'assistant', content: res.reply });
      } else {
        appendMessage('assistant', `❌ Error: ${res.message || 'Failed to generate response.'}`);
      }
    } catch (err) {
      appendMessage('assistant', `❌ Connection error: ${err.message}`);
    } finally {
      window.App.setLoading(sendChatBtn, false);
      chatInput.focus();
    }
  }

  chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    handleChatSubmit();
  });

  promptChips.forEach((chip) => {
    chip.addEventListener('click', () => {
      handleChatSubmit(chip.textContent.trim());
    });
  });

  clearChatBtn.addEventListener('click', () => {
    historyTurns = [];
    chatHistory.innerHTML = `
      <div class="chat-bubble chat-bubble-assistant">
        <strong>AttendSynth AI Assistant</strong><br />
        Chat session reset. What else would you like to investigate about the student dataset?
      </div>
    `;
    window.App.showToast('Chat history cleared.', 'info');
  });

  // 3. AI Dataset Analysis
  runAnalysisBtn.addEventListener('click', async () => {
    window.App.setLoading(runAnalysisBtn, true, 'Generating Analysis...');
    analysisResultArea.innerHTML = `
      <div class="text-center py-5">
        <div class="spinner-border text-primary mb-3" role="status"></div>
        <p class="text-muted fw-semibold">Analyzing attendance, engagement, and risk distributions with Gemini 3.8 Flash...</p>
      </div>
    `;

    try {
      const res = await window.API.analyzeWithAi();
      if (res.status === 'unconfigured') {
        analysisResultArea.innerHTML = `
          <div class="alert alert-warning">
            <h6 class="fw-bold"><i class="bi bi-key-fill me-1"></i> Gemini API Key Required</h6>
            <p class="mb-0 small">${res.message}</p>
          </div>
        `;
      } else if (res.status === 'success') {
        analysisResultArea.innerHTML = `
          <div class="p-3 bg-white rounded border">
            ${renderMarkdown(res.analysis)}
          </div>
        `;
        window.App.showToast('AI Dataset Analysis generated successfully!', 'success');
      } else {
        analysisResultArea.innerHTML = `<div class="alert alert-danger">${res.message}</div>`;
      }
    } catch (err) {
      analysisResultArea.innerHTML = `<div class="alert alert-danger">Error: ${err.message}</div>`;
    } finally {
      window.App.setLoading(runAnalysisBtn, false);
    }
  });

  // 4. AI Support Recommendations
  runRecommendationsBtn.addEventListener('click', async () => {
    window.App.setLoading(runRecommendationsBtn, true, 'Synthesizing Strategies...');
    recommendationsResultArea.innerHTML = `
      <div class="text-center py-5">
        <div class="spinner-border text-primary mb-3" role="status"></div>
        <p class="text-muted fw-semibold">Consulting educational support models with Gemini...</p>
      </div>
    `;

    try {
      const res = await window.API.getAiRecommendations();
      if (res.status === 'unconfigured') {
        recommendationsResultArea.innerHTML = `
          <div class="alert alert-warning">
            <h6 class="fw-bold"><i class="bi bi-key-fill me-1"></i> Gemini API Key Required</h6>
            <p class="mb-0 small">${res.message}</p>
          </div>
        `;
      } else if (res.status === 'success') {
        recommendationsResultArea.innerHTML = `
          <div class="p-3 bg-white rounded border">
            ${renderMarkdown(res.recommendations)}
          </div>
        `;
        window.App.showToast('Support recommendations generated!', 'success');
      } else {
        recommendationsResultArea.innerHTML = `<div class="alert alert-danger">${res.message}</div>`;
      }
    } catch (err) {
      recommendationsResultArea.innerHTML = `<div class="alert alert-danger">Error: ${err.message}</div>`;
    } finally {
      window.App.setLoading(runRecommendationsBtn, false);
    }
  });

  // 5. AI Cohort Report
  runReportBtn.addEventListener('click', async () => {
    window.App.setLoading(runReportBtn, true, 'Drafting Formal Report...');
    reportResultArea.innerHTML = `
      <div class="text-center py-5">
        <div class="spinner-border text-primary mb-3" role="status"></div>
        <p class="text-muted fw-semibold">Compiling comprehensive academic institutional evaluation report...</p>
      </div>
    `;

    try {
      const res = await window.API.generateAiReport();
      if (res.status === 'unconfigured') {
        reportResultArea.innerHTML = `
          <div class="alert alert-warning">
            <h6 class="fw-bold"><i class="bi bi-key-fill me-1"></i> Gemini API Key Required</h6>
            <p class="mb-0 small">${res.message}</p>
          </div>
        `;
      } else if (res.status === 'success') {
        lastReportText = res.report;
        reportResultArea.innerHTML = `
          <div class="p-4 bg-white rounded border">
            ${renderMarkdown(res.report)}
          </div>
        `;
        copyReportBtn.disabled = false;
        window.App.showToast('AI Institutional Report ready!', 'success');
      } else {
        reportResultArea.innerHTML = `<div class="alert alert-danger">${res.message}</div>`;
      }
    } catch (err) {
      reportResultArea.innerHTML = `<div class="alert alert-danger">Error: ${err.message}</div>`;
    } finally {
      window.App.setLoading(runReportBtn, false);
    }
  });

  copyReportBtn.addEventListener('click', () => {
    if (!lastReportText) return;
    navigator.clipboard.writeText(lastReportText).then(() => {
      window.App.showToast('Report copied to clipboard!', 'success');
    }).catch(() => {
      window.App.showToast('Failed to copy report to clipboard.', 'warning');
    });
  });

  // 6. Student Explanation Form
  async function runStudentExplanation(id) {
    const studentId = (id || studentIdInput.value).trim();
    if (!studentId) return;

    studentIdInput.value = studentId;
    window.App.setLoading(explainStudentBtn, true, 'Analyzing Student Profile...');
    studentExplainResultArea.innerHTML = `
      <div class="text-center py-4">
        <div class="spinner-border text-primary mb-2" role="status"></div>
        <p class="text-muted small">Generating counselor risk audit for ${studentId}...</p>
      </div>
    `;

    try {
      const res = await window.API.explainStudentWithAi(studentId);
      if (res.status === 'unconfigured') {
        studentExplainResultArea.innerHTML = `
          <div class="alert alert-warning">
            <h6 class="fw-bold"><i class="bi bi-key-fill me-1"></i> Gemini API Key Required</h6>
            <p class="mb-2 small">${res.message}</p>
            <div class="p-2 bg-white rounded border small">
              <strong>Calculated Contributing Factors for ${res.student_id}:</strong>
              <ul class="mb-0 ps-3">
                ${res.calculated_factors.map(f => `<li>${f}</li>`).join('')}
              </ul>
            </div>
          </div>
        `;
      } else if (res.status === 'success') {
        studentExplainResultArea.innerHTML = `
          <div class="p-3 bg-white rounded border">
            <div class="mb-3 p-2 bg-light rounded border small">
              <strong>Verified Deterministic Flags (${res.student_id}):</strong>
              <ul class="mb-0 ps-3">
                ${res.calculated_factors.map(f => `<li>${f}</li>`).join('')}
              </ul>
            </div>
            ${renderMarkdown(res.explanation)}
          </div>
        `;
        window.App.showToast(`AI Counseling Plan generated for ${studentId}!`, 'success');
      } else {
        studentExplainResultArea.innerHTML = `<div class="alert alert-danger">${res.message}</div>`;
      }
    } catch (err) {
      studentExplainResultArea.innerHTML = `<div class="alert alert-danger">Error: ${err.message}</div>`;
    } finally {
      window.App.setLoading(explainStudentBtn, false);
    }
  }

  studentExplainForm.addEventListener('submit', (e) => {
    e.preventDefault();
    runStudentExplanation();
  });

  // Check URL query parameters for ?student_id=...
  const urlParams = new URLSearchParams(window.location.search);
  const paramStudentId = urlParams.get('student_id');
  if (paramStudentId) {
    // Switch to Student Explanation tab
    const tabTrigger = new bootstrap.Tab(tabStudentBtn);
    tabTrigger.show();
    runStudentExplanation(paramStudentId);
  }
});
