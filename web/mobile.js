// ═══ EG Craft — Mobile detection + touch controls ═══
// Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
// Proprietary software. Copying, distribution, or modification without
// written permission is prohibited.
// هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

/* ─────────────────────────────────────────────────────────────
 * Mobile detection + touch-controls bridge for EG Craft.
 *
 * The DOM elements this script binds to (#egc-loader, #egc-touch,
 * #joystick, .btn, #egc-fs, #egc-start) are injected into pygbag's
 * generated index.html by scripts/post_build.py. If any of them are
 * missing (e.g. running outside the bundled page), the TouchControls
 * constructor exits silently — desktop mode is unaffected.
 * ───────────────────────────────────────────────────────────── */
(function () {
  'use strict';

  const EGC = window.EGC = window.EGC || {};

  /* ─────────────────────────────────────────────────────────────
   * Mobile detection (smartphone / tablet / phablet)
   * Combines User-Agent, viewport, touch capability, and pixel ratio.
   * ───────────────────────────────────────────────────────────── */
  EGC.detectMobile = function () {
    const ua = navigator.userAgent || navigator.vendor || '';
    const isTouch = ('ontouchstart' in window) ||
                    (navigator.maxTouchPoints > 0) ||
                    (navigator.msMaxTouchPoints > 0);
    const isMobileUA = /android|iphone|ipod|ipad|iemobile|blackberry|opera mini|mobile|tablet/i.test(ua);
    const isSmallViewport = (window.innerWidth <= 900 && window.innerHeight <= 900);
    const isHighDPI = (window.devicePixelRatio || 1) >= 1.5;

    const isPhone = isMobileUA && (isTouch || isSmallViewport);
    const isTablet = isMobileUA && !isPhone && isTouch;
    return {
      isPhone: !!isPhone,
      isTablet: !!isTablet,
      isTouch: !!isTouch,
      isMobile: !!(isPhone || isTablet),
      isHighDPI: !!isHighDPI,
      ua: ua,
    };
  };

  EGC.enterFullscreen = function () {
    const el = document.documentElement;
    try {
      if (el.requestFullscreen)         el.requestFullscreen();
      else if (el.webkitRequestFullscreen)  el.webkitRequestFullscreen();
      else if (el.mozRequestFullScreen)    el.mozRequestFullScreen();
      else if (el.msRequestFullscreen)      el.msRequestFullscreen();
    } catch (_) { /* silently ignore */ }
    setTimeout(function () { window.scrollTo(0, 1); }, 100);
  };

  EGC.exitFullscreen = function () {
    try {
      if (document.exitFullscreen)        document.exitFullscreen();
      else if (document.webkitExitFullscreen) document.webkitExitFullscreen();
      else if (document.mozCancelFullScreen)  document.mozCancelFullScreen();
      else if (document.msExitFullscreen)      document.msExitFullscreen();
    } catch (_) { /* silently ignore */ }
  };

  EGC.lockOrientation = function () {
    try {
      const so = screen.orientation || screen.mozOrientation ||
                 screen.msOrientation;
      if (so && so.lock) {
        so.lock('landscape').catch(function () {});
      }
    } catch (_) { /* silently ignore */ }
  };

  EGC.unlockAudio = function () {
    // Browsers require a user gesture to start audio
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      if (ctx.state === 'suspended') ctx.resume();
    } catch (_) { /* silently ignore */ }
  };

  /* ─────────────────────────────────────────────────────────────
   * Touch-controls binding
   * ───────────────────────────────────────────────────────────── */
  EGC.TouchControls = function () {
    // The mobile UI is injected by post_build.py into pygbag's index.html.
    // If we're running outside that context, bail — desktop mode.
    this.loader     = document.getElementById('egc-loader');
    this.touchRoot  = document.getElementById('egc-touch');
    if (!this.touchRoot) {
      // No mobile UI in the page — nothing to bind.
      return;
    }

    this.joystick   = document.getElementById('joystick');
    this.knob       = document.getElementById('knob');
    this.startBtn   = document.getElementById('egc-start');
    this.fsBtn      = document.getElementById('egc-fs');

    // Virtual state (consumed by the pygbag game via window.EGC.input)
    this.input = {
      moveX: 0, moveY: 0,
      lookDX: 0, lookDY: 0,
      jump: false, sneak: false, flyToggle: false,
      breakHeld: false, placeHeld: false,
      invToggle: false, hotbarIndex: 0,
    };
    window.EGC.input = this.input;

    this.joystickState = { active: false, cx: 0, cy: 0 };
    this.lookState    = { active: false, lastX: 0, lastY: 0 };

    this._bind();
  };

  EGC.TouchControls.prototype._bind = function () {
    const self = this;
    const det = EGC.detectMobile();

    if (det.isMobile || det.isTouch) {
      // Show the touch controls overlay
      this.touchRoot.classList.add('visible');
      if (this.fsBtn) this.fsBtn.style.display = 'block';

      // Start button: enter fullscreen + lock orientation + hide loader
      if (this.startBtn) {
        this.startBtn.style.display = 'inline-block';
        this.startBtn.addEventListener('click', function () {
          EGC.enterFullscreen();
          EGC.lockOrientation();
          EGC.unlockAudio();
          self._hideLoader();
        });
      }

      // Fullscreen button (manual)
      if (this.fsBtn) {
        this.fsBtn.addEventListener('click', function () {
          if (document.fullscreenElement || document.webkitFullscreenElement) {
            EGC.exitFullscreen();
          } else {
            EGC.enterFullscreen();
            EGC.lockOrientation();
          }
        });
      }

      // Update the fullscreen button label on change
      const fsListener = function () {
        const inFs = document.fullscreenElement || document.webkitFullscreenElement;
        if (self.fsBtn) self.fsBtn.textContent = inFs ? '✕ خروج' : '⛶ ملء الشاشة';
      };
      document.addEventListener('fullscreenchange', fsListener);
      document.addEventListener('webkitfullscreenchange', fsListener);
    } else {
      // Desktop — auto-hide the loader after a short delay
      setTimeout(function () { self._hideLoader(); }, 1500);
    }

    // ─── Joystick drag (multi-touch-safe) ────────────────────────
    if (this.joystick) {
      this.joystick.addEventListener('touchstart', function (e) {
        e.preventDefault();
        const t = e.changedTouches[0];
        const r = self.joystick.getBoundingClientRect();
        self.joystickState.active = true;
        self.joystickState.cx = r.left + r.width / 2;
        self.joystickState.cy = r.top + r.height / 2;
        self._updateKnob(t.clientX, t.clientY);
      }, { passive: false });

      this.joystick.addEventListener('touchmove', function (e) {
        e.preventDefault();
        if (!self.joystickState.active) return;
        const t = e.changedTouches[0];
        self._updateKnob(t.clientX, t.clientY);
      }, { passive: false });

      const joystickEnd = function (e) {
        e.preventDefault();
        self.joystickState.active = false;
        self.input.moveX = 0;
        self.input.moveY = 0;
        if (self.knob) self.knob.style.transform = 'translate(-50%, -50%)';
      };
      this.joystick.addEventListener('touchend',   joystickEnd, { passive: false });
      this.joystick.addEventListener('touchcancel', joystickEnd, { passive: false });
    }

    // ─── Action buttons ──────────────────────────────────────────
    const btns = this.touchRoot.querySelectorAll('.btn');
    btns.forEach(function (btn) {
      const key   = btn.dataset.key;
      const mouse = btn.dataset.mouse;

      const press = function (e) {
        e.preventDefault();
        if (key === 'space')  self.input.jump = true;
        if (key === 'space2') self.input.flyToggle = true;
        if (key === 'shift')  self.input.sneak = true;
        if (key === 'e')      self.input.invToggle = true;
        if (mouse === 'left')  self.input.breakHeld = true;
        if (mouse === 'right') self.input.placeHeld = true;
      };
      const release = function (e) {
        e.preventDefault();
        if (key === 'space')  self.input.jump = false;
        if (key === 'shift')  self.input.sneak = false;
        if (key === 'e')      self.input.invToggle = false;
        if (key === 'space2') self.input.flyToggle = false;
        if (mouse === 'left')  self.input.breakHeld = false;
        if (mouse === 'right') self.input.placeHeld = false;
      };

      btn.addEventListener('touchstart',  press,   { passive: false });
      btn.addEventListener('touchend',    release, { passive: false });
      btn.addEventListener('touchcancel', release, { passive: false });
      btn.addEventListener('mousedown',   press);
      btn.addEventListener('mouseup',     release);
      btn.addEventListener('mouseleave',  release);
    });

    // Orientation change → re-lock
    window.addEventListener('orientationchange', function () {
      setTimeout(function () {
        if (document.fullscreenElement || document.webkitFullscreenElement) {
          EGC.lockOrientation();
        }
      }, 100);
    });
  };

  EGC.TouchControls.prototype._updateKnob = function (tx, ty) {
    const dx = tx - this.joystickState.cx;
    const dy = ty - this.joystickState.cy;
    const dist = Math.sqrt(dx * dx + dy * dy);
    const maxR = 50;
    const clampedDist = Math.min(dist, maxR);
    const angle = Math.atan2(dy, dx);
    const kx = Math.cos(angle) * clampedDist;
    const ky = Math.sin(angle) * clampedDist;
    if (this.knob) {
      this.knob.style.transform =
        'translate(calc(-50% + ' + kx + 'px), calc(-50% + ' + ky + 'px))';
    }
    this.input.moveX = kx / maxR;
    this.input.moveY = -ky / maxR;
  };

  EGC.TouchControls.prototype._hideLoader = function () {
    if (!this.loader) return;
    this.loader.style.opacity = '0';
    this.loader.style.transition = 'opacity 0.4s ease';
    const self = this;
    setTimeout(function () {
      self.loader.style.display = 'none';
    }, 400);
  };

  /* ─────────────────────────────────────────────────────────────
   * Boot
   * ───────────────────────────────────────────────────────────── */
  function _boot() {
    new EGC.TouchControls();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', _boot);
  } else {
    _boot();
  }
})();
