/* Zimplixio — Twisted Particle Stream (canvas ImageData, no WebGL) */
(function () {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  document.addEventListener('DOMContentLoaded', function () {
    var container = document.getElementById('hero-particles');
    if (!container) return;

    var canvas = document.createElement('canvas');
    canvas.style.cssText = 'position:absolute;inset:0;width:100%;height:100%';
    container.appendChild(canvas);
    var ctx = canvas.getContext('2d');

    var W, H;
    var imgData, data;
    var time = 0;

    var COUNT = 20000;

    var pU       = new Float32Array(COUNT);
    var pV       = new Float32Array(COUNT);
    var pSurface = new Uint8Array(COUNT);
    var pNoise   = new Float32Array(COUNT);

    var PI = Math.PI;

    /*  Ribbon definition: [freq, twistRate, amp, timeSpeed, phaseOffset, yOffset]
        yOffset is in normalized Y units (-1 top → +1 bottom)
        6 ribbons spread across the full hero height                              */
    var RIBBONS = [
      [1.10, 1.20, 0.14, 0.80, 0,          -1.00],
      [0.90, 1.00, 0.16, 1.00, PI * 0.55,  -0.55],
      [1.25, 1.45, 0.15, 0.70, PI * 1.00,  -0.10],
      [0.80, 0.85, 0.17, 1.20, PI * 1.40,   0.38],
      [1.15, 1.60, 0.13, 0.60, PI * 1.80,   0.78],
      [0.75, 0.95, 0.14, 0.90, PI * 0.30,   1.00]
    ];

    var NR = RIBBONS.length;

    var camX = 0.18, camY = 0;
    var targetCamX = 0.18, targetCamY = 0;
    var mouse = { x: -9999, y: -9999 };

    /* ---- init ---- */
    function init() {
      for (var i = 0; i < COUNT; i++) {
        pU[i]       = Math.random() * PI * 4;
        pV[i]       = (Math.random() - 0.5) * 2;
        pSurface[i] = i % NR;
        pNoise[i]   = (Math.random() - 0.5) * 0.025;
      }
    }

    function resize() {
      W = canvas.width  = container.offsetWidth;
      H = canvas.height = container.offsetHeight;
      imgData = ctx.createImageData(W, H);
      data    = imgData.data;
      init();
    }

    /* ---- twisted ribbon surface ---- */
    function surfacePoint(u, v, noise, rb, t) {
      var freq  = rb[0], twist = rb[1], amp = rb[2];
      var tOff  = t * rb[3] + rb[4];
      var yOff  = rb[5];

      /* centerline: x sweeps full width, slightly beyond ±1 to fill edges */
      var x = (u / (PI * 4)) * 2.4 - 1.2;
      var y = yOff
            + amp * Math.sin(u * freq       + tOff)
            + amp * 0.45 * Math.sin(u * freq * 2.1 - tOff * 0.65);
      var z = amp * 0.7 * Math.cos(u * freq * 0.85 + tOff * 0.5);

      /* twist: ribbon cross-section rotates with u */
      var tw = u * twist + tOff * 0.1;
      var w  = 0.20; /* ribbon half-width */

      return {
        x: x + noise,
        y: y + v * w * Math.cos(tw) + noise,
        z: z + v * w * Math.sin(tw)
      };
    }

    /* ---- render loop ---- */
    var lastTime = 0;

    function frame(now) {
      var dt = Math.min(now - lastTime, 50);
      lastTime = now;
      time    += dt * 0.00036;

      camX += (targetCamX - camX) * 0.07;
      camY += (targetCamY - camY) * 0.07;

      var cosY = Math.cos(camY), sinY = Math.sin(camY);
      var cosX = Math.cos(camX), sinX = Math.sin(camX);
      var cx   = W * 0.5,  cy = H * 0.5;
      var scX  = W * 0.68; /* compensates for perspective foreshortening */
      var scY  = H * 0.65; /* fills full height */
      var fov  = 560;

      data.fill(0);

      for (var i = 0; i < COUNT; i++) {
        var rb = RIBBONS[pSurface[i]];
        var pt = surfacePoint(pU[i], pV[i], pNoise[i], rb, time);

        /* rotate Y */
        var rx1 =  pt.x * cosY + pt.z * sinY;
        var rz1 = -pt.x * sinY + pt.z * cosY;
        /* rotate X */
        var ry1 =  pt.y * cosX - rz1 * sinX;
        var rz2 =  pt.y * sinX + rz1 * cosX;

        /* perspective */
        var zp = rz2 + 2.0;
        if (zp < 0.01) continue;

        var fs = fov / (fov + zp * 130);
        var sx = (cx + rx1 * scX * fs) | 0;
        var sy = (cy + ry1 * scY * fs) | 0;

        if (sx < 0 || sx >= W || sy < 0 || sy >= H) continue;

        /* depth → color: deep indigo (far) → bright sky-blue (near) */
        var depth  = Math.max(0, Math.min(1, (rz2 + 1.2) / 2.4));
        var bright = depth * depth;

        var R = (37  + bright * 180) | 0;
        var G = (99  + bright * 156) | 0;
        var B = (235 + bright * 18 ) | 0;
        var A = (35  + bright * 190) | 0;

        /* additive blending — ribbon folds accumulate to near-white */
        var idx = (sy * W + sx) << 2;
        data[idx]     = data[idx]     + R > 255 ? 255 : data[idx]     + R;
        data[idx + 1] = data[idx + 1] + G > 255 ? 255 : data[idx + 1] + G;
        data[idx + 2] = data[idx + 2] + B > 255 ? 255 : data[idx + 2] + B;
        data[idx + 3] = data[idx + 3] + A > 255 ? 255 : data[idx + 3] + A;
      }

      ctx.putImageData(imgData, 0, 0);
      requestAnimationFrame(frame);
    }

    /* ---- events ---- */
    window.addEventListener('resize', resize);

    document.addEventListener('mousemove', function (e) {
      var rect = container.getBoundingClientRect();
      if (e.clientX >= rect.left && e.clientX <= rect.right &&
          e.clientY >= rect.top  && e.clientY <= rect.bottom) {
        targetCamY = ((e.clientX - rect.left) / W - 0.5) *  1.20;
        targetCamX = ((e.clientY - rect.top)  / H - 0.5) *  0.65 + 0.18;
      } else {
        targetCamX = 0.18;
        targetCamY = 0;
      }
    });

    resize();
    requestAnimationFrame(frame);
  });
})();
