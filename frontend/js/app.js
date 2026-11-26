/**
 * AttendSynth AI — Shared UI Logic, Sidebar, Toasts, and App Shell
 */

const App = {
  init() {
    this.setupMobileSidebar();
    this.highlightActiveNav();
    this.refreshCohortStatus();
  },

  setupMobileSidebar() {
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('mobileSidebarToggle');
    const backdrop = document.getElementById('sidebarBackdrop');

    if (toggleBtn && sidebar) {
      toggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('show');
        if (backdrop) backdrop.classList.toggle('show');
      });
    }

    if (backdrop && sidebar) {
      backdrop.addEventListener('click', () => {
        sidebar.classList.remove('show');
        backdrop.classList.remove('show');
      });
    }
  },

  highlightActiveNav() {
    const currentPath = window.location.pathname.toLowerCase();
    const navLinks = document.querySelectorAll('.nav-link-item');

    navLinks.forEach((link) => {
      const href = link.getAttribute('href').toLowerCase();
      // Handle index.html or root
      if ((currentPath === '/' || currentPath.endsWith('index.html')) && (href.endsWith('index.html') || href === '/')) {
        link.classList.add('active');
      } else if (currentPath.includes(href) && href !== '/' && !href.endsWith('index.html')) {
        link.classList.add('active');
      } else {
        link.classList.remove('active');
      }
    });
  },

  async refreshCohortStatus() {
    const countEl = document.getElementById('sidebarStudentCount');
    const metaEl = document.getElementById('sidebarCohortMeta');
    const pillEl = document.getElementById('sidebarStatusPill');

    if (!countEl || !metaEl) return;

    try {
      const data = await window.API.getHealth();
      const cohort = data.active_cohort;

      if (cohort && cohort.loaded && cohort.student_count > 0) {
        countEl.textContent = `${cohort.student_count.toLocaleString()} Students`;
        metaEl.textContent = `Term: ${cohort.academic_year || '—'} · Seed: ${cohort.seed ?? '—'}`;
        if (pillEl) pillEl.style.backgroundColor = '#10B981';
      } else {
        countEl.textContent = 'No Active Dataset';
        metaEl.textContent = 'Generate a cohort to begin.';
        if (pillEl) pillEl.style.backgroundColor = '#94A3B8';
      }
    } catch (err) {
      countEl.textContent = 'Backend Offline';
      metaEl.textContent = 'Unable to connect to API.';
      if (pillEl) pillEl.style.backgroundColor = '#EF4444';
    }
  },

  showToast(message, type = 'info') {
    let container = document.getElementById('toastContainer');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toastContainer';
      container.className = 'toast-container-custom';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = 'toast-custom';

    const iconMap = {
      success: '<i class="bi bi-check-circle-fill text-success"></i>',
      warning: '<i class="bi bi-exclamation-triangle-fill text-warning"></i>',
      danger: '<i class="bi bi-x-circle-fill text-danger"></i>',
      info: '<i class="bi bi-info-circle-fill text-primary"></i>',
    };

    toast.innerHTML = `
      <div style="font-size: 1.25rem;">${iconMap[type] || iconMap.info}</div>
      <div style="flex: 1; font-weight: 500;">${message}</div>
      <button type="button" class="btn-close btn-close-sm" aria-label="Close" style="font-size: 0.75rem;"></button>
    `;

    const closeBtn = toast.querySelector('.btn-close');
    closeBtn.addEventListener('click', () => toast.remove());

    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transition = 'opacity 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 4500);
  },

  setLoading(element, isLoading, text = 'Processing...') {
    if (!element) return;
    if (isLoading) {
      element.dataset.origHtml = element.innerHTML;
      element.disabled = true;
      element.innerHTML = `
        <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
        ${text}
      `;
    } else {
      element.disabled = false;
      if (element.dataset.origHtml) {
        element.innerHTML = element.dataset.origHtml;
      }
    }
  },
};

window.App = App;
document.addEventListener('DOMContentLoaded', () => App.init());
