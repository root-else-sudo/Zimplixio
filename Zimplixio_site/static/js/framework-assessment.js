document.addEventListener('DOMContentLoaded', function () {
  // --- Questions Data ---
  var QUESTIONS = [
    {
      key: 'industry',
      text: 'What industry are you in?',
      type: 'single',
      options: [
        'Technology', 'Legal & Compliance', 'Finance', 'Healthcare',
        'Manufacturing', 'Retail & E-commerce', 'Professional Services', 'Other'
      ]
    },
    {
      key: 'size',
      text: 'How large is your company?',
      type: 'single',
      options: ['1–10 employees', '11–50 employees', '51–200 employees', '200+ employees']
    },
    {
      key: 'current_usage',
      text: 'How would you describe your current AI usage?',
      type: 'single',
      options: [
        'None — we haven\'t started', 'Experimenting informally',
        'One tool in production', 'Multiple tools deployed'
      ]
    },
    {
      key: 'value_target',
      text: 'Where do you want AI to create value first?',
      type: 'single',
      options: [
        'Customer-facing products & services',
        'Internal / Engineering productivity',
        'Both equally'
      ]
    },
    {
      key: 'workflow_docs',
      text: 'How well-documented are your core workflows?',
      type: 'single',
      options: ['Not documented', 'Partially documented', 'Well documented']
    },
    {
      key: 'ai_literacy',
      text: 'How would you describe your team\'s AI literacy?',
      type: 'single',
      options: [
        'Low — most people haven\'t used AI tools',
        'Mixed — varies by role',
        'Moderate — comfortable with basic tools',
        'High — active daily users'
      ]
    },
    {
      key: 'concerns',
      text: 'What are your biggest concerns about AI adoption? (Select up to 3)',
      type: 'multi',
      maxSelect: 3,
      options: [
        'Cost overruns & runaway spend',
        'Data security & IP exposure',
        'Team resistance to change',
        'Lack of internal expertise',
        'Regulatory & compliance risk',
        'Moving too slowly vs competitors'
      ]
    },
    {
      key: 'goal_90_days',
      text: 'What is your primary goal in the next 90 days?',
      type: 'single',
      options: [
        'Identify where AI can help us',
        'Launch a focused pilot',
        'Scale something already working',
        'Build internal AI capability'
      ]
    }
  ];

  // --- State ---
  var state = {
    currentQuestion: 0,
    answers: {},
    loading: false,
    direction: 'forward'
  };

  // --- DOM Elements ---
  var startBtn = document.getElementById('start-assessment-btn');
  var formEl = document.getElementById('assessment-form');
  var loadingEl = document.getElementById('assessment-loading');
  var reportEl = document.getElementById('report-output');
  var errorEl = document.getElementById('assessment-error');
  var questionContainer = document.getElementById('question-container');
  var progressLabel = document.getElementById('progress-label');
  var progressPercent = document.getElementById('progress-percent');
  var progressBar = document.getElementById('progress-bar');
  var btnBack = document.getElementById('btn-back');
  var btnNext = document.getElementById('btn-next');
  var btnSubmit = document.getElementById('btn-submit');
  var btnRetry = document.getElementById('btn-retry');
  var errorMessage = document.getElementById('error-message');

  // --- Start Assessment ---
  if (startBtn) {
    startBtn.addEventListener('click', function () {
      var assessmentSection = document.getElementById('assessment');
      assessmentSection.scrollIntoView({ behavior: 'smooth' });
      formEl.classList.remove('hidden');
      renderQuestion();
    });
  }

  // --- Render Question ---
  function renderQuestion() {
    var q = QUESTIONS[state.currentQuestion];
    var idx = state.currentQuestion;
    var total = QUESTIONS.length;
    var pct = Math.round((idx / total) * 100);

    progressLabel.textContent = 'Question ' + (idx + 1) + ' of ' + total;
    progressPercent.textContent = pct + '%';
    progressBar.style.width = pct + '%';

    // Back button state
    btnBack.disabled = idx === 0;

    // Show submit on last question, next otherwise
    if (idx === total - 1) {
      btnNext.classList.add('hidden');
      btnSubmit.classList.remove('hidden');
      updateSubmitState();
    } else {
      btnNext.classList.remove('hidden');
      btnSubmit.classList.add('hidden');
    }

    // Build question HTML
    var animClass = state.direction === 'forward' ? 'question-slide' : 'question-slide-back';
    var html = '<div class="' + animClass + '">';
    html += '<h3 class="text-xl font-bold text-gray-900 mb-6">' + q.text + '</h3>';

    if (q.type === 'single') {
      html += '<div class="space-y-3">';
      for (var i = 0; i < q.options.length; i++) {
        var opt = q.options[i];
        var selected = state.answers[q.key] === opt;
        html += '<button class="assessment-option w-full text-left px-4 py-3 rounded-lg border ';
        html += selected ? 'selected border-indigo-500 bg-indigo-50' : 'border-gray-200';
        html += ' cursor-pointer" data-key="' + q.key + '" data-value="' + escapeAttr(opt) + '" data-type="single">';
        html += '<span class="text-sm">' + escapeHtml(opt) + '</span>';
        html += '</button>';
      }
      html += '</div>';
    } else {
      // Multi-select
      var currentSelections = state.answers[q.key] || [];
      html += '<p class="text-sm text-gray-500 mb-3">Select up to ' + q.maxSelect + '</p>';
      html += '<div class="space-y-3">';
      for (var j = 0; j < q.options.length; j++) {
        var optM = q.options[j];
        var isSelected = currentSelections.indexOf(optM) !== -1;
        html += '<button class="assessment-option w-full text-left px-4 py-3 rounded-lg border ';
        html += isSelected ? 'selected border-indigo-500 bg-indigo-50' : 'border-gray-200';
        html += ' cursor-pointer" data-key="' + q.key + '" data-value="' + escapeAttr(optM) + '" data-type="multi" data-max="' + q.maxSelect + '">';
        html += '<span class="flex items-center gap-2">';
        html += '<span class="w-4 h-4 rounded border flex-shrink-0 flex items-center justify-center ';
        html += isSelected ? 'bg-indigo-600 border-indigo-600' : 'border-gray-300';
        html += '">';
        if (isSelected) {
          html += '<svg class="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/></svg>';
        }
        html += '</span>';
        html += '<span class="text-sm">' + escapeHtml(optM) + '</span>';
        html += '</span>';
        html += '</button>';
      }
      html += '</div>';
    }
    html += '</div>';

    questionContainer.innerHTML = html;

    // Attach click handlers
    questionContainer.querySelectorAll('.assessment-option').forEach(function (btn) {
      btn.addEventListener('click', handleOptionClick);
    });

    updateNextState();
  }

  // --- Option Click Handler ---
  function handleOptionClick(e) {
    var btn = e.currentTarget;
    var key = btn.getAttribute('data-key');
    var value = btn.getAttribute('data-value');
    var type = btn.getAttribute('data-type');

    if (type === 'single') {
      state.answers[key] = value;
      renderQuestion();
    } else {
      var max = parseInt(btn.getAttribute('data-max'), 10);
      var current = state.answers[key] || [];
      var idx = current.indexOf(value);
      if (idx !== -1) {
        current.splice(idx, 1);
      } else if (current.length < max) {
        current.push(value);
      }
      state.answers[key] = current;
      renderQuestion();
    }
  }

  // --- Next/Back/Submit State ---
  function updateNextState() {
    var q = QUESTIONS[state.currentQuestion];
    var answer = state.answers[q.key];
    var hasAnswer = false;

    if (q.type === 'single') {
      hasAnswer = !!answer;
    } else {
      hasAnswer = Array.isArray(answer) && answer.length > 0;
    }

    btnNext.disabled = !hasAnswer;
  }

  function updateSubmitState() {
    var allAnswered = true;
    for (var i = 0; i < QUESTIONS.length; i++) {
      var a = state.answers[QUESTIONS[i].key];
      if (!a || (Array.isArray(a) && a.length === 0)) {
        allAnswered = false;
        break;
      }
    }
    btnSubmit.disabled = !allAnswered;
  }

  // --- Navigation ---
  btnBack.addEventListener('click', function () {
    if (state.currentQuestion > 0) {
      state.direction = 'back';
      state.currentQuestion--;
      renderQuestion();
    }
  });

  btnNext.addEventListener('click', function () {
    if (state.currentQuestion < QUESTIONS.length - 1) {
      state.direction = 'forward';
      state.currentQuestion++;
      renderQuestion();
    }
  });

  btnSubmit.addEventListener('click', function () {
    handleSubmit();
  });

  btnRetry.addEventListener('click', function () {
    errorEl.classList.add('hidden');
    formEl.classList.remove('hidden');
    renderQuestion();
  });

  // --- Submit Assessment ---
  function handleSubmit() {
    formEl.classList.add('hidden');
    loadingEl.classList.remove('hidden');
    state.loading = true;

    // Animate loading stages
    var stages = document.querySelectorAll('#loading-stages .loading-stage');
    stages.forEach(function (el, i) {
      setTimeout(function () {
        el.classList.add('visible');
      }, 400 * (i + 1));
    });

    // Read CSRF token
    var csrfMeta = document.querySelector('meta[name="csrf-token"]');
    var csrfToken = csrfMeta ? csrfMeta.getAttribute('content') : '';

    // Prepare answers — convert multi-select arrays to comma-separated strings for concerns
    var submitAnswers = {};
    for (var key in state.answers) {
      if (Object.prototype.hasOwnProperty.call(state.answers, key)) {
        submitAnswers[key] = state.answers[key];
      }
    }

    fetch('/framework/api/assessment/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify({ answers: submitAnswers })
    })
    .then(function (response) {
      return response.json().then(function (data) {
        return { status: response.status, data: data };
      });
    })
    .then(function (result) {
      state.loading = false;
      loadingEl.classList.add('hidden');

      if (result.data.success) {
        renderReport(result.data.report);
      } else {
        var msg = 'Something went wrong. Please try again.';
        if (result.status === 429) {
          msg = 'You\'ve reached the assessment limit. Please try again later.';
        } else if (result.status === 503) {
          msg = 'The assessment is temporarily unavailable. Please try again later.';
        } else if (result.data.error) {
          msg = result.data.error;
        }
        showError(msg);
      }
    })
    .catch(function () {
      state.loading = false;
      loadingEl.classList.add('hidden');
      showError('Connection error. Please check your internet and try again.');
    });
  }

  // --- Show Error ---
  function showError(msg) {
    errorMessage.textContent = msg;
    errorEl.classList.remove('hidden');
  }

  // --- Render Report ---
  function renderReport(report) {
    var html = '';
    html += '<div class="text-center mb-10">';
    html += '<p class="text-indigo-600 font-medium tracking-wider uppercase text-sm mb-2">Assessment Complete</p>';
    html += '<h2 class="text-2xl md:text-3xl font-bold text-gray-900">Your AI Readiness Report</h2>';
    html += '</div>';

    // Block 1 — Readiness Level
    var badgeClass = 'badge-developing';
    if (report.readiness_level === 'Early') badgeClass = 'badge-early';
    if (report.readiness_level === 'Ready') badgeClass = 'badge-ready';

    html += '<div class="report-block bg-white rounded-2xl border border-gray-200 shadow-sm p-6 mb-6">';
    html += '<h3 class="text-xs font-semibold tracking-wider uppercase text-gray-400 mb-3">Readiness Level</h3>';
    html += '<div class="flex items-center gap-3 mb-3">';
    html += '<span class="' + badgeClass + ' px-3 py-1 rounded-full text-sm font-bold">' + escapeHtml(report.readiness_level) + '</span>';
    html += '</div>';
    html += '<p class="text-gray-700">' + escapeHtml(report.readiness_summary) + '</p>';
    html += '</div>';

    // Block 2 — Where to Start
    html += '<div class="report-block bg-white rounded-2xl border border-gray-200 shadow-sm p-6 mb-6">';
    html += '<h3 class="text-xs font-semibold tracking-wider uppercase text-gray-400 mb-3">Where to Start</h3>';
    html += '<p class="text-lg font-bold text-indigo-700 mb-2">' + escapeHtml(report.priority_stage.name) + '</p>';
    html += '<p class="text-gray-700">' + escapeHtml(report.priority_stage.reason) + '</p>';
    html += '</div>';

    // Block 3 — Top Risks
    html += '<div class="report-block mb-6">';
    html += '<h3 class="text-xs font-semibold tracking-wider uppercase text-gray-400 mb-3">Top Risks</h3>';
    html += '<div class="grid md:grid-cols-3 gap-4">';
    for (var i = 0; i < report.top_risks.length; i++) {
      var risk = report.top_risks[i];
      html += '<div class="bg-white rounded-2xl border border-gray-200 shadow-sm p-5">';
      html += '<div class="flex items-center gap-2 mb-2">';
      html += '<span class="text-amber-500 text-lg">&#9888;</span>';
      html += '<span class="font-bold text-gray-900 text-sm">' + escapeHtml(risk.risk) + '</span>';
      html += '</div>';
      html += '<p class="text-gray-600 text-sm">' + escapeHtml(risk.detail) + '</p>';
      html += '</div>';
    }
    html += '</div>';
    html += '</div>';

    // Block 4 — First 30 Days
    html += '<div class="report-block bg-white rounded-2xl border border-gray-200 shadow-sm p-6 mb-6">';
    html += '<h3 class="text-xs font-semibold tracking-wider uppercase text-gray-400 mb-3">First 30 Days</h3>';
    html += '<ol class="space-y-3">';
    for (var j = 0; j < report.first_30_days.length; j++) {
      html += '<li class="flex gap-3">';
      html += '<span class="flex-shrink-0 w-6 h-6 rounded-full bg-indigo-100 text-indigo-700 text-xs font-bold flex items-center justify-center mt-0.5">' + (j + 1) + '</span>';
      html += '<span class="text-gray-700">' + escapeHtml(report.first_30_days[j]) + '</span>';
      html += '</li>';
    }
    html += '</ol>';
    html += '</div>';

    // Block 5 — Verdict
    html += '<div class="report-block mb-8">';
    html += '<div class="verdict-quote py-6">';
    html += '<p class="text-xl md:text-2xl text-gray-800 leading-relaxed">"' + escapeHtml(report.one_line_verdict) + '"</p>';
    html += '</div>';
    html += '</div>';

    // Actions
    html += '<div class="flex flex-wrap gap-4 justify-center no-print">';
    html += '<button id="btn-start-over" class="px-6 py-2.5 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors cursor-pointer">';
    html += '<svg class="inline-block w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>';
    html += 'Start Over</button>';
    html += '<button id="btn-download-pdf" class="px-6 py-2.5 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition-colors cursor-pointer">';
    html += '<svg class="inline-block w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>';
    html += 'Download PDF</button>';
    html += '</div>';

    reportEl.innerHTML = html;
    reportEl.classList.remove('hidden');

    // Stagger-reveal blocks
    var blocks = reportEl.querySelectorAll('.report-block');
    blocks.forEach(function (block, idx) {
      setTimeout(function () {
        block.classList.add('visible');
      }, 150 * (idx + 1));
    });

    // Attach action handlers
    var startOverBtn = document.getElementById('btn-start-over');
    if (startOverBtn) {
      startOverBtn.addEventListener('click', function () {
        state.currentQuestion = 0;
        state.answers = {};
        state.direction = 'forward';
        reportEl.classList.add('hidden');
        reportEl.innerHTML = '';
        formEl.classList.remove('hidden');
        renderQuestion();
        document.getElementById('assessment').scrollIntoView({ behavior: 'smooth' });
      });
    }

    var downloadBtn = document.getElementById('btn-download-pdf');
    if (downloadBtn) {
      downloadBtn.addEventListener('click', function () {
        window.print();
      });
    }
  }

  // --- Helpers ---
  function escapeHtml(str) {
    if (!str) return '';
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
  }

  function escapeAttr(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/'/g, '&#39;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
});
