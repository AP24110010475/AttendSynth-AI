/**
 * AttendSynth AI — Centralized Fetch API Client
 */

const API_BASE = '/api';

const API = {
  async _request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

    const config = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...(options.headers || {}),
      },
    };

    try {
      const response = await fetch(url, config);
      if (!response.ok) {
        let errMessage = `Request failed (${response.status})`;
        try {
          const errData = await response.json();
          errMessage = errData.detail || errData.message || errMessage;
        } catch (_) {}
        throw new Error(errMessage);
      }
      return await response.json();
    } catch (err) {
      console.error(`API Error [${endpoint}]:`, err);
      throw err;
    }
  },

  // Health & Cohort Status
  getHealth() {
    return this._request('/health');
  },

  // Generator
  getGeneratorDefaults() {
    return this._request('/generator/defaults');
  },

  generateCohort(payload) {
    return this._request('/generate', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  // Dataset Explorer
  getDataset(params = {}) {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, val]) => {
      if (val !== undefined && val !== null && val !== '' && val !== 'All') {
        query.append(key, val);
      }
    });
    const qs = query.toString() ? `?${query.toString()}` : '';
    return this._request(`/dataset${qs}`);
  },

  // Analytics
  getAnalytics(department = 'All') {
    const qs = department && department !== 'All' && department !== 'All Departments'
      ? `?department=${encodeURIComponent(department)}`
      : '';
    return this._request(`/analytics${qs}`);
  },

  // Risk Engine
  getRiskAnalysis() {
    return this._request('/risk');
  },

  getStudentRisk(studentId) {
    return this._request(`/risk/student/${encodeURIComponent(studentId)}`);
  },

  // Machine Learning
  trainML(payload) {
    return this._request('/ml/train', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  // Data Quality
  getDataQuality() {
    return this._request('/quality');
  },

  // Export URLs
  getExportUrl(type, format, filtered = false, filters = {}) {
    const query = new URLSearchParams();
    if (filtered) {
      query.append('filtered', 'true');
      Object.entries(filters).forEach(([k, v]) => {
        if (v && v !== 'All') query.append(k, v);
      });
    }
    const qs = query.toString() ? `?${query.toString()}` : '';
    if (type === 'quality') {
      return `/api/export/quality/${format}`;
    }
    return `/api/export/${format}${qs}`;
  },

  // Generative AI Assistant
  getAiStatus() {
    return this._request('/ai/status');
  },

  analyzeWithAi() {
    return this._request('/ai/analyze', { method: 'POST' });
  },

  getAiRecommendations() {
    return this._request('/ai/recommend', { method: 'POST' });
  },

  chatWithAi(query, history = []) {
    return this._request('/ai/chat', {
      method: 'POST',
      body: JSON.stringify({ query, history }),
    });
  },

  generateAiReport() {
    return this._request('/ai/report', { method: 'POST' });
  },

  explainStudentWithAi(studentId) {
    return this._request('/ai/explain-student', {
      method: 'POST',
      body: JSON.stringify({ student_id: studentId }),
    });
  },
};

window.API = API;
