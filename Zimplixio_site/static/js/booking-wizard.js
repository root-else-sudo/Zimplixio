/**
 * booking-wizard.js
 * Calendly-like 3-step booking wizard:
 *   Step 1 → pick a date (calendar grid)
 *   Step 2 → pick a time (pill buttons)
 *   Step 3 → fill in your details (form)
 */

(function () {
  'use strict';

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const state = {
    currentStep: 1,
    selectedDate: null,   // "2026-04-07"
    selectedTime: null,   // "09:00"
    displayDate: null,    // "Monday, April 7, 2026"
    displayTime: null,    // "9:00 AM"
    calYear: today.getFullYear(),
    calMonth: today.getMonth(),
    availableDays: new Set(),
  };

  const MONTH_NAMES = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December',
  ];
  const DAY_LABELS = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'];

  const visitorTz = (function () {
    try { return Intl.DateTimeFormat().resolvedOptions().timeZone; }
    catch (e) { return 'America/New_York'; }
  }());

  function convertSlotToLocal(dateStr, timeStr, tz) {
    try {
      var parts = dateStr.split('-').map(Number);
      var tp = timeStr.split(':').map(Number);
      var tentative = new Date(Date.UTC(parts[0], parts[1] - 1, parts[2], tp[0], tp[1], 0));
      var nyFmt = new Intl.DateTimeFormat('en-US', {
        timeZone: 'America/New_York',
        hour: '2-digit', minute: '2-digit', hour12: false,
      });
      var nyParts = nyFmt.formatToParts(tentative);
      var nyH = parseInt(nyParts.find(function (p) { return p.type === 'hour'; }).value, 10);
      var nyM = parseInt(nyParts.find(function (p) { return p.type === 'minute'; }).value, 10);
      var diffMs = ((tp[0] * 60 + tp[1]) - (nyH * 60 + nyM)) * 60000;
      var correctUtc = new Date(tentative.getTime() + diffMs);
      var localParts = new Intl.DateTimeFormat('en-US', {
        timeZone: tz,
        hour: 'numeric', minute: '2-digit', hour12: true, timeZoneName: 'short',
      }).formatToParts(correctUtc);
      var hour = localParts.find(function (p) { return p.type === 'hour'; }).value;
      var minute = localParts.find(function (p) { return p.type === 'minute'; }).value;
      var period = localParts.find(function (p) { return p.type === 'dayPeriod'; });
      var tzName = localParts.find(function (p) { return p.type === 'timeZoneName'; });
      return hour + ':' + minute + (period ? ' ' + period.value : '') + (tzName ? ' ' + tzName.value : '');
    } catch (e) {
      return timeStr;
    }
  }

  // ─── DOM refs ────────────────────────────────────────────────────────────────
  function el(id) { return document.getElementById(id); }

  // ─── Step navigation ─────────────────────────────────────────────────────────
  function goToStep(n) {
    for (let i = 1; i <= 3; i++) {
      const step = el('booking-step-' + i);
      if (step) step.classList.toggle('hidden', i !== n);
    }
    state.currentStep = n;
    updateProgressDots(n);
  }

  function updateProgressDots(n) {
    for (let i = 1; i <= 3; i++) {
      const dot = el('progress-dot-' + i);
      const line = el('progress-line-' + i);
      if (!dot) continue;
      if (i < n) {
        dot.className = 'w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold bg-indigo-600 text-white border-2 border-indigo-600';
        dot.innerHTML = '<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/></svg>';
      } else if (i === n) {
        dot.className = 'w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold bg-indigo-600 text-white border-2 border-indigo-600';
        dot.textContent = i;
      } else {
        dot.className = 'w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold bg-white text-gray-400 border-2 border-gray-300';
        dot.textContent = i;
      }
      if (line) {
        line.className = i < n
          ? 'flex-1 h-0.5 bg-indigo-600 mx-1'
          : 'flex-1 h-0.5 bg-gray-300 mx-1';
      }
    }
  }

  // ─── Calendar ─────────────────────────────────────────────────────────────────
  function fetchAvailableDays(year, month) {
    const monthStr = year + '-' + String(month + 1).padStart(2, '0');
    const calGrid = el('cal-grid');
    if (calGrid) {
      calGrid.innerHTML = '<div class="col-span-7 flex justify-center py-8"><div class="w-6 h-6 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin"></div></div>';
    }
    fetch('/book/available-days/?month=' + monthStr)
      .then(function (r) { return r.json(); })
      .then(function (data) {
        state.availableDays = new Set(data.available_days || []);
        renderCalendar();
      })
      .catch(function () {
        state.availableDays = new Set();
        renderCalendar();
      });
  }

  function renderCalendar() {
    const calGrid = el('cal-grid');
    const calTitle = el('cal-title');
    if (!calGrid) return;

    const year = state.calYear;
    const month = state.calMonth;

    if (calTitle) {
      calTitle.textContent = MONTH_NAMES[month] + ' ' + year;
    }

    // Day-of-week headers (Mon–Sun)
    let html = DAY_LABELS.map(function (d) {
      return '<div class="text-center text-xs font-semibold text-gray-400 py-1">' + d + '</div>';
    }).join('');

    // First day of month (0=Sun … 6=Sat → convert to Mon-based offset)
    const firstDay = new Date(year, month, 1).getDay(); // 0=Sun
    const offset = (firstDay + 6) % 7; // Mon=0 … Sun=6

    for (let i = 0; i < offset; i++) {
      html += '<div></div>';
    }

    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const todayISO = today.toISOString().slice(0, 10);

    for (let day = 1; day <= daysInMonth; day++) {
      const iso = year + '-' + String(month + 1).padStart(2, '0') + '-' + String(day).padStart(2, '0');
      const isPast = iso <= todayISO;
      const isAvail = state.availableDays.has(iso);
      const isSelected = iso === state.selectedDate;

      let cls, attrs;
      if (isSelected) {
        cls = 'w-9 h-9 mx-auto rounded-full flex items-center justify-center text-sm font-semibold bg-indigo-600 text-white cursor-pointer select-none';
        attrs = 'data-date="' + iso + '"';
      } else if (!isPast && isAvail) {
        cls = 'w-9 h-9 mx-auto rounded-full flex items-center justify-center text-sm font-medium text-indigo-700 ring-2 ring-indigo-400 hover:bg-indigo-50 cursor-pointer select-none transition-colors';
        attrs = 'data-date="' + iso + '"';
      } else {
        cls = 'w-9 h-9 mx-auto rounded-full flex items-center justify-center text-sm text-gray-300 cursor-not-allowed select-none';
        attrs = '';
      }

      html += '<div class="flex items-center justify-center py-0.5">' +
        '<div class="' + cls + '" ' + attrs + '>' + day + '</div>' +
        '</div>';
    }

    calGrid.innerHTML = html;

    // Attach click handlers
    calGrid.querySelectorAll('[data-date]').forEach(function (cell) {
      cell.addEventListener('click', function () {
        onDateClick(cell.getAttribute('data-date'));
      });
    });

    // Prev/next nav
    const prevBtn = el('cal-prev');
    const nextBtn = el('cal-next');
    const nowM = today.getMonth();
    const nowY = today.getFullYear();
    if (prevBtn) {
      prevBtn.disabled = (year === nowY && month <= nowM);
      prevBtn.classList.toggle('opacity-30', prevBtn.disabled);
      prevBtn.classList.toggle('cursor-not-allowed', prevBtn.disabled);
    }
  }

  function onDateClick(dateStr) {
    state.selectedDate = dateStr;
    const d = new Date(dateStr + 'T00:00:00');
    state.displayDate = d.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
    // Update selected date display in step 2
    const step2DateLabel = el('step2-date-label');
    if (step2DateLabel) step2DateLabel.textContent = state.displayDate;
    fetchSlots(dateStr);
    goToStep(2);
  }

  // ─── Slots ───────────────────────────────────────────────────────────────────
  function fetchSlots(dateStr) {
    const slotContainer = el('slot-container');
    if (slotContainer) {
      slotContainer.innerHTML = '<div class="flex justify-center py-8"><div class="w-6 h-6 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin"></div></div>';
    }
    fetch('/book/slots/?date=' + dateStr)
      .then(function (r) { return r.json(); })
      .then(function (data) { renderSlots(data.slots || []); })
      .catch(function () { renderSlots([]); });
  }

  function renderSlots(slots) {
    const slotContainer = el('slot-container');
    if (!slotContainer) return;
    if (!slots.length) {
      slotContainer.innerHTML = '<p class="text-center text-gray-500 py-8 text-sm">No available times for this day.<br>Please go back and pick another date.</p>';
      return;
    }
    const html = slots.map(function (s) {
      var localLabel = convertSlotToLocal(state.selectedDate, s.value, visitorTz);
      return '<button type="button" data-value="' + s.value + '" data-label="' + localLabel + '" ' +
        'class="slot-pill px-4 py-3 rounded-lg border-2 border-indigo-300 text-indigo-700 font-medium text-sm hover:bg-indigo-50 hover:border-indigo-500 transition-colors text-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400">' +
        localLabel + '</button>';
    }).join('');
    slotContainer.innerHTML = '<div class="grid grid-cols-3 gap-3">' + html + '</div>';
    slotContainer.querySelectorAll('.slot-pill').forEach(function (btn) {
      btn.addEventListener('click', function () {
        onTimeClick(btn.getAttribute('data-value'), btn.getAttribute('data-label'));
      });
    });
  }

  function onTimeClick(value, label) {
    state.selectedTime = value;
    state.displayTime = label;
    // Populate hidden inputs
    const dateInput = document.querySelector('input[name="requested_date"]');
    const timeInput = document.querySelector('input[name="requested_time"]');
    if (dateInput) dateInput.value = state.selectedDate;
    if (timeInput) timeInput.value = state.selectedTime;
    var tzInput = document.querySelector('input[name="visitor_timezone"]');
    if (tzInput) tzInput.value = visitorTz;
    renderSummaryBar();
    goToStep(3);
  }

  function renderSummaryBar() {
    const bar = el('step3-summary');
    if (bar) {
      bar.textContent = state.displayDate + ' · ' + state.displayTime;
    }
  }

  // ─── Month navigation ─────────────────────────────────────────────────────────
  function prevMonth() {
    if (state.calMonth === 0) {
      state.calMonth = 11;
      state.calYear--;
    } else {
      state.calMonth--;
    }
    fetchAvailableDays(state.calYear, state.calMonth);
  }

  function nextMonth() {
    if (state.calMonth === 11) {
      state.calMonth = 0;
      state.calYear++;
    } else {
      state.calMonth++;
    }
    fetchAvailableDays(state.calYear, state.calMonth);
  }

  // ─── Back buttons ─────────────────────────────────────────────────────────────
  function goBack(targetStep) {
    if (targetStep === 1) {
      // Re-render calendar with current selection highlighted
      renderCalendar();
    }
    goToStep(targetStep);
  }

  // ─── Init ─────────────────────────────────────────────────────────────────────
  document.addEventListener('DOMContentLoaded', function () {
    // Wire month nav
    const prevBtn = el('cal-prev');
    const nextBtn = el('cal-next');
    if (prevBtn) prevBtn.addEventListener('click', prevMonth);
    if (nextBtn) nextBtn.addEventListener('click', nextMonth);

    // Wire back buttons
    const backToStep1 = el('back-to-step1');
    const backToStep2 = el('back-to-step2');
    if (backToStep1) backToStep1.addEventListener('click', function () { goBack(1); });
    if (backToStep2) backToStep2.addEventListener('click', function () { goBack(2); });

    // Start on step 1
    goToStep(1);

    // Fetch available days for current month
    fetchAvailableDays(state.calYear, state.calMonth);
  });
})();
