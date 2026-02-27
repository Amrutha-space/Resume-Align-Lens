/**
 * Resume Align Lens — Application Logic
 * Handles form submission, state transitions, and results rendering.
 */

'use strict';

// ---- State ----
let currentStep = 0;
let loadingInterval = null;

// ---- DOM References ----
const form = document.getElementById('analyzeForm');
const loadingPanel = document.getElementById('loadingPanel');
const errorPanel = document.getElementById('errorPanel');
const resultsSection = document.getElementById('resultsSection');
const analyzeBtn = document.getElementById('analyzeBtn');
const jobDescInput = document.getElementById('jobDescription');
const resumeTextInput = document.getElementById('resumeText');
const resumeFileInput = document.getElementById('resumeFile');
const uploadZone = document.getElementById('uploadZone');
const fileSelectedIndicator = document.getElementById('fileSelectedIndicator');
const jdCharCount = document.getElementById('jdCharCount');
const resumeCharCount = document.getElementById('resumeCharCount');

// ---- Character counters ----
jobDescInput.addEventListener('input', () => {
  jdCharCount.textContent = `${jobDescInput.value.length.toLocaleString()} characters`;
});

resumeTextInput.addEventListener('input', () => {
  resumeCharCount.textContent = `${resumeTextInput.value.length.toLocaleString()} characters`;
});

// ---- File Upload Handling with region  ----
uploadZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  uploadZone.classList.add('drag-over');
});

uploadZone.addEventListener('dragleave', () => {
  uploadZone.classList.remove('drag-over');
});

uploadZone.addEventListener('drop', (e) => {
  e.preventDefault();
  uploadZone.classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file) {
    assignFile(file);
  }
});

resumeFileInput.addEventListener('change', () => {
  const file = resumeFileInput.files[0];
  if (file) {
    assignFile(file);
  }
});

function assignFile(file) {
  const dt = new DataTransfer();
  dt.items.add(file);
  resumeFileInput.files = dt.files;
  fileSelectedIndicator.textContent = `✓ ${file.name} (${formatBytes(file.size)})`;
}

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

// ---- Form Submission ----
form.addEventListener('submit', async (e) => {
  e.preventDefault();

  const jd = jobDescInput.value.trim();
  const resumeText = resumeTextInput.value.trim();
  const resumeFile = resumeFileInput.files[0];

  if (!jd) {
    shakeElement(jobDescInput);
    jobDescInput.focus();
    return;
  }

  if (!resumeText && !resumeFile) {
    shakeElement(uploadZone);
    return;
  }

  const formData = new FormData();
  formData.append('job_description', jd);
  if (resumeFile) {
    formData.append('resume_file', resumeFile);
  }
  if (resumeText) {
    formData.append('resume_text', resumeText);
  }

  showLoading();

  try {
    const response = await fetch('/api/analyze', {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();

    if (!response.ok || !data.success) {
      throw new Error(data.error || 'Analysis failed. Please try again.');
    }

    showResults(data);

  } catch (err) {
    showError(err.message || 'An unexpected error occurred.');
  }
});

// ---- State Transitions ----
function showLoading() {
  hideAll();
  form.style.display = 'none';
  loadingPanel.style.display = 'block';
  analyzeBtn.disabled = true;
  currentStep = 0;
  startLoadingSteps();
}

function showError(message) {
  stopLoadingSteps();
  hideAll();
  form.style.display = 'block';
  analyzeBtn.disabled = false;
  errorPanel.style.display = 'block';
  document.getElementById('errorMessage').textContent = message;
}

function showResults(data) {
  stopLoadingSteps();
  hideAll();
  resultsSection.style.display = 'flex';
  renderResults(data);
  resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function hideAll() {
  loadingPanel.style.display = 'none';
  errorPanel.style.display = 'none';
  resultsSection.style.display = 'none';
}

function resetForm() {
  hideAll();
  form.style.display = 'block';
  analyzeBtn.disabled = false;
  currentStep = 0;
  stopLoadingSteps();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ---- Loading Steps ----
function startLoadingSteps() {
  const steps = document.querySelectorAll('.loading-step');
  steps.forEach(s => {
    s.classList.remove('active', 'done');
  });
  steps[0].classList.add('active');
  currentStep = 0;

  loadingInterval = setInterval(() => {
    const steps = document.querySelectorAll('.loading-step');
    if (currentStep < steps.length - 1) {
      steps[currentStep].classList.remove('active');
      steps[currentStep].classList.add('done');
      currentStep++;
      steps[currentStep].classList.add('active');
    }
  }, 5500);
}

function stopLoadingSteps() {
  if (loadingInterval) {
    clearInterval(loadingInterval);
    loadingInterval = null;
  }
}

// ---- Results Rendering ----
function renderResults(data) {
  const { analysis, score } = data;

  renderScore(score);
  renderAssessment(analysis.overall_assessment);
  renderTopActions(score.top_3_actions);
  renderStrengths(analysis.strengths);
  renderWeaknesses(analysis.weaknesses);
  renderKeywords(analysis.missing_keywords);
  renderSkillGaps(analysis.skill_gaps);
  renderSectionImprovements(analysis.section_improvements);
  renderBulletOptimizations(analysis.bullet_optimizations);
}

function renderScore(score) {
  // Animate score number
  animateNumber(
    document.getElementById('scoreNumber'),
    0,
    score.overall_score,
    900
  );

  // Badge
  const badge = document.getElementById('scoreBadge');
  badge.textContent = score.score_label;
  badge.className = 'score-badge ' + getScoreClass(score.overall_score);

  // Rationale
  document.getElementById('scoreRationale').textContent = score.score_rationale || '';

  // Dimensions
  const dimGrid = document.getElementById('dimensionsGrid');
  dimGrid.innerHTML = '';
  const dims = score.dimension_scores || {};
  const dimLabels = {
    technical_skills_match: 'Technical Skills',
    experience_relevance: 'Experience Relevance',
    keyword_coverage: 'Keyword Coverage',
    achievement_quality: 'Achievement Quality',
    presentation_quality: 'Presentation Quality',
  };
  Object.entries(dimLabels).forEach(([key, label]) => {
    const val = dims[key] ?? 0;
    const row = document.createElement('div');
    row.className = 'dimension-row';
    row.innerHTML = `
      <div class="dimension-label">${label}</div>
      <div class="dimension-bar-track">
        <div class="dimension-bar-fill" style="width:0%" data-target="${val}"></div>
      </div>
      <div class="dimension-value">${val}</div>
    `;
    dimGrid.appendChild(row);
  });

  // Animate bars after render
  setTimeout(() => {
    document.querySelectorAll('.dimension-bar-fill').forEach(bar => {
      bar.style.width = bar.dataset.target + '%';
    });
  }, 100);

  // Hiring record
  const hiringEl = document.getElementById('hiringRec');
  hiringEl.innerHTML = `
    <strong>Hiring Recommendation</strong>
    ${esc(score.hiring_recommendation)} 
    <span style="color:var(--text-muted)"> · Confidence: ${esc(score.confidence_in_assessment)}</span>
  `;
}

// Overall assessment section

function renderAssessment(text) {
  const el = document.getElementById('assessmentBanner');
  if (!text) { el.style.display = 'none'; return; }
  el.style.display = 'block';
  el.style.paddingLeft = '52px';
  el.textContent = text;
}

function renderTopActions(actions) {
  const section = document.getElementById('topActionsSection');
  if (!actions || actions.length === 0) { section.style.display = 'none'; return; }
  section.innerHTML = `
    <div class="top-actions-title">Priority Actions</div>
    <div class="top-actions-list">
      ${actions.map((a, i) => `
        <div class="top-action-item">
          <span class="top-action-num">${String(i + 1).padStart(2, '0')}</span>
          <span>${esc(a)}</span>
        </div>
      `).join('')}
    </div>
  `;
}

function renderStrengths(items) {
  const list = document.getElementById('strengthsList');
  const count = document.getElementById('strengthsCount');
  items = items || [];
  count.textContent = items.length;
  list.innerHTML = items.length === 0
    ? '<div style="color:var(--text-muted);font-size:13px;">No notable strengths identified.</div>'
    : items.map(item => `
      <div class="diag-item">
        <div class="diag-item-point">${esc(item.point)}</div>
        <div class="diag-item-reasoning">${esc(item.reasoning)}</div>
        <span class="confidence-chip ${esc(item.confidence)}">${esc(item.confidence)} Confidence</span>
      </div>
    `).join('');
}

function renderWeaknesses(items) {
  const list = document.getElementById('weaknessesList');
  const count = document.getElementById('weaknessesCount');
  items = items || [];
  count.textContent = items.length;
  list.innerHTML = items.length === 0
    ? '<div style="color:var(--text-muted);font-size:13px;">No significant weaknesses identified.</div>'
    : items.map(item => `
      <div class="diag-item">
        <div class="diag-item-point">${esc(item.point)}</div>
        <div class="diag-item-reasoning">${esc(item.reasoning)}</div>
        <span class="confidence-chip ${esc(item.confidence)}">${esc(item.confidence)} Confidence</span>
      </div>
    `).join('');
}

function renderKeywords(items) {
  const el = document.getElementById('keywordsList');
  const section = document.getElementById('keywordsSection');
  items = items || [];
  if (items.length === 0) { section.style.display = 'none'; return; }
  el.innerHTML = items.map(item => `
    <div class="keyword-chip ${esc(item.importance)}" title="${esc(item.reasoning)}">
      <span class="keyword-name">${esc(item.keyword)}</span>
      <span class="keyword-importance">${esc(item.importance)}</span>
    </div>
  `).join('');
}

function renderSkillGaps(items) {
  const el = document.getElementById('skillGapsList');
  const section = document.getElementById('skillGapsSection');
  items = items || [];
  if (items.length === 0) { section.style.display = 'none'; return; }
  el.innerHTML = items.map(item => `
    <div class="skill-gap-item">
      <div class="skill-gap-left">
        <div class="skill-gap-name">${esc(item.skill)}</div>
        <span class="severity-chip ${esc(item.gap_severity)}">${esc(item.gap_severity)}</span>
      </div>
      <div class="skill-gap-right">
        <div class="skill-gap-reasoning">${esc(item.reasoning)}</div>
        <div class="skill-gap-action">${esc(item.suggested_action)}</div>
      </div>
    </div>
  `).join('');
}

function renderSectionImprovements(items) {
  const el = document.getElementById('sectionImprovementsList');
  const card = document.getElementById('sectionImprovementsCard');
  items = items || [];
  if (items.length === 0) { card.style.display = 'none'; return; }
  el.innerHTML = items.map(item => `
    <div class="improvement-item">
      <div class="improvement-section-tag">${esc(item.section)}</div>
      <div class="improvement-issue">${esc(item.issue)}</div>
      <div class="improvement-suggestion">${esc(item.suggestion)}</div>
      <div class="improvement-reasoning">${esc(item.reasoning)}</div>
    </div>
  `).join('');
}

function renderBulletOptimizations(items) {
  const el = document.getElementById('bulletOptsList');
  const card = document.getElementById('bulletOptsCard');
  items = items || [];
  if (items.length === 0) { card.style.display = 'none'; return; }
  el.innerHTML = items.map(item => `
    <div class="bullet-opt-item">
      <div class="bullet-opt-meta">Pattern: ${esc(item.original_pattern)} → ${esc(item.improved_pattern)}</div>
      <div class="bullet-comparison">
        <div class="bullet-before">
          <span class="bullet-label">Before</span>
          ${esc(item.example_before)}
        </div>
        <div class="bullet-after">
          <span class="bullet-label">After</span>
          ${esc(item.example_after)}
        </div>
      </div>
      <div class="bullet-reasoning">${esc(item.reasoning)}</div>
    </div>
  `).join('');
}

// ---- Helpers ----
function getScoreClass(score) {
  if (score >= 75) return 'excellent';
  if (score >= 55) return 'good';
  if (score >= 35) return 'average';
  return 'poor';
}

function animateNumber(el, from, to, duration) {
  const start = performance.now();
  function update(time) {
    const elapsed = time - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.round(from + (to - from) * eased);
    if (progress < 1) requestAnimationFrame(update);
  }
  requestAnimationFrame(update);
}

function shakeElement(el) {
  el.style.animation = 'none';
  el.offsetHeight; // reflow
  el.style.animation = 'shake 0.4s ease';
  setTimeout(() => { el.style.animation = ''; }, 400);
}

function esc(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// Shake animation
const shakeStyle = document.createElement('style');
shakeStyle.textContent = `
  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    20% { transform: translateX(-6px); }
    40% { transform: translateX(6px); }
    60% { transform: translateX(-4px); }
    80% { transform: translateX(4px); }
  }
`;
document.head.appendChild(shakeStyle);
