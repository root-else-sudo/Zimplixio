/* Zimplixio — Interactive World Map (D3 + TopoJSON) — Globe Edition */
(function () {
  'use strict';

  var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var isTouch = navigator.maxTouchPoints > 0;

  /* ── Data ─────────────────────────────────────────────────────────────── */

  var CONTINENTAL = [
    // Americas
    { name: 'United States',         lat: 38.0,  lon: -97.0,   tag: 'Americas' },
    { name: 'Canada',                lat: 56.0,  lon: -96.0,   tag: 'Americas' },
    { name: 'Mexico',                lat: 23.0,  lon: -102.0,  tag: 'Americas' },
    { name: 'Costa Rica',            lat: 9.93,  lon: -84.09,  tag: 'Americas' },
    { name: 'Argentina',             lat: -34.0, lon: -64.0,   tag: 'Americas' },
    { name: 'Brasil',                lat: -10.0, lon: -55.0,   tag: 'Americas' },
    // Europe
    { name: 'Belgium',               lat: 50.8,  lon: 4.5,     tag: 'Europe' },
    { name: 'France',                lat: 46.2,  lon: 2.2,     tag: 'Europe' },
    { name: 'Germany',               lat: 51.2,  lon: 10.4,    tag: 'Europe' },
    { name: 'Ireland',               lat: 53.4,  lon: -8.2,    tag: 'Europe' },
    { name: 'Netherlands',           lat: 52.1,  lon: 5.3,     tag: 'Europe' },
    { name: 'Romania',               lat: 45.9,  lon: 25.0,    tag: 'Europe' },
    { name: 'Spain',                 lat: 40.5,  lon: -3.7,    tag: 'Europe' },
    { name: 'Switzerland',           lat: 46.8,  lon: 8.2,     tag: 'Europe' },
    { name: 'United Kingdom',        lat: 55.0,  lon: -3.2,    tag: 'Europe' },
    // Africa
    { name: 'Egypt',                 lat: 26.8,  lon: 30.8,    tag: 'Africa' },
    { name: 'South Africa',          lat: -30.6, lon: 22.9,    tag: 'Africa' },
    // Asia
    { name: 'India',                 lat: 20.6,  lon: 78.9,    tag: 'Asia' },
    { name: 'Indonesia',             lat: -0.8,  lon: 113.9,   tag: 'Asia' },
    { name: 'Japan',                 lat: 36.2,  lon: 138.3,   tag: 'Asia' },
    { name: 'Vietnam',               lat: 14.1,  lon: 108.3,   tag: 'Asia' },
    { name: 'Philippines',           lat: 12.9,  lon: 121.8,   tag: 'Asia' },
    { name: 'Bangladesh',            lat: 23.7,  lon: 90.4,    tag: 'Asia' },
    { name: 'United Arab Emirates',  lat: 23.4,  lon: 53.8,    tag: 'Asia' },
    { name: 'Taiwan',                lat: 23.7,  lon: 121.0,   tag: 'Asia' },
    { name: 'Israel',                lat: 31.5,  lon: 34.8,    tag: 'Asia' },
    { name: 'Qatar',                 lat: 25.3,  lon: 51.2,    tag: 'Asia' },
    { name: 'Singapore',             lat: 1.35,  lon: 103.8,   tag: 'Asia' },
    // Australia
    { name: 'Australia',             lat: -25.3, lon: 133.8,   tag: 'Pacific' },
  ];

  var CITIES = [
    { name: 'Atlanta',     state: 'GA', lat: 33.75,  lon: -84.39,  tag: 'Georgia' },
    { name: 'Miami',       state: 'FL', lat: 25.76,  lon: -80.19,  tag: 'Florida' },
    { name: 'Houston',     state: 'TX', lat: 29.76,  lon: -95.37,  tag: 'Texas' },
    { name: 'Los Angeles', state: 'CA', lat: 34.05,  lon: -118.24, tag: 'California' },
    { name: 'Detroit',     state: 'MI', lat: 42.33,  lon: -83.05,  tag: 'Michigan' },
    { name: 'New York',    state: 'NY', lat: 40.71,  lon: -74.01,  tag: 'New York' },
    { name: 'Chicago',     state: 'IL', lat: 41.88,  lon: -87.63,  tag: 'Illinois' },
    { name: 'New Orleans', state: 'LA', lat: 29.95,  lon: -90.07,  tag: 'Louisiana' },
    { name: 'Boston',      state: 'MA', lat: 42.36,  lon: -71.06,  tag: 'Massachusetts' },
    { name: 'Newark',      state: 'NJ', lat: 40.74,  lon: -74.17,  tag: 'New Jersey' },
    { name: 'Charlotte',   state: 'NC', lat: 35.23,  lon: -80.84,  tag: 'North Carolina' },
    { name: 'Portland',    state: 'OR', lat: 45.52,  lon: -122.67, tag: 'Oregon' },
  ];

  // SVG pin shapes — tip at (0,0), body extends upward
  var PIN_LG = 'M0,0 C-2,-2 -7,-6 -7,-12 a7,7 0 1,1 14,0 C7,-6 2,-2 0,0 Z'; // continental
  var PIN_SM = 'M0,0 C-1.5,-1.5 -5,-4.5 -5,-9 a5,5 0 1,1 10,0 C5,-4.5 1.5,-1.5 0,0 Z'; // city

  var AMERICAS = new Set([
    840, 124, 484, 32, 76, 152, 170, 218, 600, 604, 858, 862,
    320, 340, 188, 222, 591, 558, 192, 332, 214, 388, 630, 740, 328,
  ]);

  /* ── Interpolated projection factory ─────────────────────────────────── */

  function makeInterpolatedProjection(rawA, rawB) {
    var proj = d3.geoProjectionMutator(function (t) {
      return function (lambda, phi) {
        var a = rawA(lambda, phi);
        var b = rawB(lambda, phi);
        if (!a || !b) return null;
        return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];
      };
    });
    var p = proj(0);
    var currentT = 0;
    p.alpha = function (_) {
      return arguments.length ? (proj(currentT = +_), p) : currentT;
    };
    return p;
  }

  /* ── Boot ─────────────────────────────────────────────────────────────── */

  document.addEventListener('DOMContentLoaded', function () {
    var el = document.getElementById('world-map-container');
    if (!el) return;
    if (typeof d3 === 'undefined' || typeof topojson === 'undefined') {
      console.warn('WorldMap: D3 or TopoJSON not loaded');
      return;
    }
    init(el);
  });

  /* ── Init ─────────────────────────────────────────────────────────────── */

  function init(el) {
    var W = el.clientWidth;
    var H = el.clientHeight;
    var globeScale = Math.min(W, H) / 2 * 0.88;
    var flatScale  = W / 5.2;

    var svg = d3.select(el).append('svg')
      .attr('viewBox', '0 0 ' + W + ' ' + H)
      .attr('preserveAspectRatio', 'xMidYMid meet')
      .attr('role', 'img')
      .attr('aria-label', 'World map showing Zimplixio global presence');

    // Interpolated projection — starts at orthographic (alpha = 0)
    var proj = makeInterpolatedProjection(d3.geoOrthographicRaw, d3.geoNaturalEarth1Raw)
      .scale(globeScale)
      .translate([W / 2, H / 2])
      .rotate([80, -15, 0])  // center Americas on the globe
      .clipAngle(90);         // clip back hemisphere

    var path     = d3.geoPath().projection(proj);
    var graticule = d3.geoGraticule();

    // Sphere (globe ocean background)
    var sphereEl = svg.append('path')
      .datum({ type: 'Sphere' })
      .attr('class', 'map-sphere')
      .attr('d', path);

    // Graticule (latitude/longitude grid)
    var graticuleEl = svg.append('path')
      .datum(graticule())
      .attr('class', 'map-graticule')
      .attr('d', path);

    // Main group — countries, pins (zoom transform applied here)
    var g = svg.append('g');

    var tooltip = d3.select(el).append('div').attr('class', 'map-tooltip');
    var state    = { view: 'world', busy: false, timer: null, dragging: false };

    var ctx = {
      proj, path, graticule, sphereEl, graticuleEl,
      globeScale, flatScale, W, H, g, svg, tooltip, state,
    };

    Promise.all([
      fetch(el.dataset.worldUrl).then(function (r) { return r.json(); }),
      fetch(el.dataset.usUrl).then(function (r) { return r.json(); }),
    ]).then(function (results) {
      drawWorld(results[0], results[1], ctx, el);
    }).catch(function (err) {
      console.warn('WorldMap: failed to load geodata', err);
    });

    var resizeTimer;
    window.addEventListener('resize', function () {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(function () { el.innerHTML = ''; init(el); }, 300);
    });
  }

  /* ── Draw world ───────────────────────────────────────────────────────── */

  function drawWorld(world, us, ctx, el) {
    var countries = topojson.feature(world, world.objects.countries);
    var hint = el.nextElementSibling; // .map-hint (mobile only)

    ctx.g.selectAll('.map-country')
      .data(countries.features.filter(function (d) { return +d.id !== 10; }))
      .enter().append('path')
      .attr('class', function (d) {
        return 'map-country' + (AMERICAS.has(+d.id) ? ' map-country--americas' : '');
      })
      .attr('d', ctx.path);

    drawPins(ctx.g, CONTINENTAL, ctx.proj, ctx.tooltip, 'c-pin');
    if (reducedMotion) drawPins(ctx.g, CITIES, ctx.proj, ctx.tooltip, 'city-pin');

    // ── Unified click handler (globe / flat / us states) ──────────────────
    ctx.svg.on('click', function (event) {
      if (ctx.state.busy || ctx.state.dragging) return;
      var target = event.target;
      var d = d3.select(target).datum();

      if (ctx.state.view === 'world') {
        // Globe: click Americas country or any c-pin → morph to flat world
        if ((d && AMERICAS.has(+d.id)) || target.closest('.c-pin')) {
          if (hint) hint.style.display = 'none';
          var desktopHint = el.querySelector('.map-globe-hint');
          if (desktopHint) { desktopHint.style.animation = 'none'; desktopHint.style.opacity = '0'; }
          transitionToFlat(world, us, ctx);
        }
      } else if (ctx.state.view === 'flat') {
        // Flat world: click US country path (id=840) or the US country pin → zoom into US
        var usPath = target.closest('.map-country');
        var usPathDatum = usPath ? d3.select(usPath).datum() : null;
        var clickedUS = (d && +d.id === 840) ||
                        (d && d.name === 'United States') ||
                        (usPathDatum && +usPathDatum.id === 840);
        if (clickedUS) {
          zoomToUS(us, ctx);
        }
      } else if (ctx.state.view === 'us') {
        // US zoomed: click outside US states / city pins → zoom back to flat world
        if (!target.closest('.map-state') && !target.closest('.city-pin')) {
          if (hint) hint.style.display = '';
          zoomBackToFlat(ctx);
        }
      }
    });

    // ── Drag to rotate the globe ──────────────────────────────────────────
    var drag = d3.drag()
      .on('start', function () {
        ctx.state.dragging = false;
        if (ctx.state.view === 'world') ctx.svg.style('cursor', 'grabbing');
      })
      .on('drag', function (event) {
        if (ctx.state.view !== 'world' || ctx.state.busy) return;
        ctx.state.dragging = true;
        var r = ctx.proj.rotate();
        var sensitivity = 75 / ctx.proj.scale();
        ctx.proj.rotate([
          r[0] + event.dx * sensitivity,
          r[1] - event.dy * sensitivity,
          r[2],
        ]);
        ctx.sphereEl.attr('d', ctx.path);
        ctx.graticuleEl.attr('d', ctx.path);
        ctx.g.selectAll('.map-country').attr('d', ctx.path);
        ctx.g.selectAll('.c-pin').each(function (d) {
          if (!d) return;
          var visible = globeVisible(ctx.proj, d.lon, d.lat);
          var coords  = visible ? ctx.proj([d.lon, d.lat]) : null;
          d3.select(this)
            .style('opacity', coords ? 1 : 0)
            .attr('transform', coords
              ? 'translate(' + coords[0] + ',' + coords[1] + ')'
              : 'translate(-9999,-9999)');
        });
      })
      .on('end', function () {
        setTimeout(function () { ctx.state.dragging = false; }, 0);
        if (ctx.state.view === 'world') ctx.svg.style('cursor', 'grab');
      });

    ctx.svg.call(drag).style('cursor', 'grab');

    // Mouse-out from flat or us → return to globe after short delay
    ctx.svg.on('mouseleave', function () {
      if (!isTouch && ctx.state.view !== 'world' && !ctx.state.busy) {
        ctx.state.timer = setTimeout(function () { transitionToGlobe(ctx); }, 600);
      }
    }).on('mouseenter', function () { clearTimeout(ctx.state.timer); });
  }

  /* ── US hint animation ────────────────────────────────────────────────── */

  function startUSHint(ctx) {
    if (reducedMotion) return;
    var usNode = ctx.g.selectAll('.map-country')
      .filter(function (d) { return +d.id === 840; })
      .node();
    if (!usNode) return;

    ctx._usHintInterval = setInterval(function () {
      if (ctx.state.view !== 'flat') { stopUSHint(ctx); return; }
      usNode.classList.toggle('map-country--us-hint');
    }, 900);
  }

  function stopUSHint(ctx) {
    clearInterval(ctx._usHintInterval);
    ctx._usHintInterval = null;
    var usNode = ctx.g.selectAll('.map-country')
      .filter(function (d) { return +d.id === 840; })
      .node();
    if (usNode) usNode.classList.remove('map-country--us-hint');
  }

  /* ── Globe → Flat ─────────────────────────────────────────────────────── */

  function transitionToFlat(world, us, ctx) {
    if (ctx.state.busy || ctx.state.view !== 'world') return;
    ctx.state.busy = true;
    ctx.svg.style('cursor', 'default');

    // Hide pins during morph
    ctx.g.selectAll('.c-pin').transition().duration(150).style('opacity', 0);

    var scaleInterp  = d3.interpolateNumber(ctx.globeScale, ctx.flatScale);
    var rotateInterp = d3.interpolate([80, -15, 0], [0, 0, 0]);

    d3.transition()
      .duration(reducedMotion ? 0 : 900)
      .ease(d3.easeCubicInOut)
      .tween('projection', function () {
        return function (t) {
          ctx.proj
            .alpha(t)
            .scale(scaleInterp(t))
            .rotate(rotateInterp(t));
          ctx.sphereEl.attr('d', ctx.path);
          ctx.graticuleEl.attr('d', ctx.path);
          ctx.g.selectAll('.map-country').attr('d', ctx.path);
        };
      })
      .on('end', function () {
        // Natural Earth doesn't support clipAngle — remove it so the full map renders
        ctx.proj.clipAngle(null);
        ctx.g.selectAll('.map-country').attr('d', ctx.path);
        // Fade out globe chrome
        ctx.sphereEl.transition().duration(250).style('opacity', 0);
        ctx.graticuleEl.transition().duration(250).style('opacity', 0);
        // Show all country pins at their Natural Earth positions
        ctx.g.selectAll('.c-pin').each(function (d) {
          if (!d) return;
          var coords = ctx.proj([d.lon, d.lat]);
          if (!coords) return;
          d3.select(this)
            .attr('transform', 'translate(' + coords[0] + ',' + coords[1] + ')')
            .transition().duration(reducedMotion ? 0 : 400).style('opacity', 1);
        });
        ctx.state.view = 'flat';
        ctx.state.busy = false;
        startUSHint(ctx);
      });
  }

  /* ── Flat → Globe ─────────────────────────────────────────────────────── */

  function transitionToGlobe(ctx) {
    if (ctx.state.busy || ctx.state.view === 'world') return;
    ctx.state.busy = true;

    stopUSHint(ctx);
    ctx.g.selectAll('.map-country').style('opacity', null); // reset before morph
    hideTooltip(ctx.tooltip);

    // Remove US layers and hide all pins before morphing
    ctx.g.selectAll('.city-pin, .map-state, .city-pin-layer, .states-layer')
      .transition().duration(reducedMotion ? 0 : 150).style('opacity', 0).remove();
    ctx.g.selectAll('.c-pin')
      .transition().duration(reducedMotion ? 0 : 150).style('opacity', 0);

    function startMorph() {
      ctx.sphereEl.style('opacity', 0).transition().duration(200).style('opacity', 1);
      ctx.graticuleEl.style('opacity', 0).transition().duration(200).style('opacity', 1);
      ctx.proj.clipAngle(90);

      var scaleInterp  = d3.interpolateNumber(ctx.flatScale, ctx.globeScale);
      var rotateInterp = d3.interpolate([0, 0, 0], [80, -15, 0]);

      d3.transition()
        .duration(reducedMotion ? 0 : 900)
        .ease(d3.easeCubicInOut)
        .tween('projection', function () {
          return function (t) {
            ctx.proj.alpha(1 - t).scale(scaleInterp(t)).rotate(rotateInterp(t));
            ctx.sphereEl.attr('d', ctx.path);
            ctx.graticuleEl.attr('d', ctx.path);
            ctx.g.selectAll('.map-country').attr('d', ctx.path);
          };
        })
        .on('end', function () {
          ctx.g.selectAll('.c-pin').each(function (d) {
            if (!d) return;
            var visible = globeVisible(ctx.proj, d.lon, d.lat);
            var coords  = visible ? ctx.proj([d.lon, d.lat]) : null;
            d3.select(this)
              .attr('transform', coords
                ? 'translate(' + coords[0] + ',' + coords[1] + ')'
                : 'translate(-9999,-9999)')
              .style('opacity', coords ? 1 : 0);
          });
          ctx.svg.style('cursor', 'grab');
          ctx.state.view = 'world';
          ctx.state.busy = false;
        });
    }

    if (ctx.state.view === 'flat') {
      // Already at flat (g at identity) — skip zoom-back, morph immediately
      startMorph();
    } else {
      // Coming from 'us' — zoom g back to identity first, then morph
      ctx.g.transition()
        .duration(reducedMotion ? 0 : 400)
        .ease(d3.easeCubicIn)
        .attr('transform', 'translate(0,0) scale(1)')
        .on('end', startMorph);
    }
  }

  /* ── Zoom to US ───────────────────────────────────────────────────────── */

  function zoomToUS(us, ctx) {
    if (ctx.state.busy) return;
    ctx.state.busy = true;

    stopUSHint(ctx);

    // Dim world countries to focus attention on the US
    ctx.g.selectAll('.map-country')
      .transition().duration(reducedMotion ? 0 : 600)
      .style('opacity', 0.12);

    // Use continental US corners — avoids Alaska & Hawaii inflating the bounding box
    var tl = ctx.proj([-125, 50]); // top-left  (NW corner)
    var br = ctx.proj([-66,  24]); // bottom-right (SE corner)
    if (!tl || !br) { ctx.state.busy = false; return; }

    var bW = br[0] - tl[0];
    var bH = br[1] - tl[1];
    var k  = Math.min(ctx.W / bW, ctx.H / bH) * 0.82;
    var tx = ctx.W / 2 - k * (tl[0] + bW / 2);
    var ty = ctx.H / 2 - k * (tl[1] + bH / 2);

    ctx.g.transition()
      .duration(reducedMotion ? 0 : 700)
      .ease(d3.easeCubicInOut)
      .attr('transform', 'translate(' + tx + ',' + ty + ') scale(' + k + ')')
      .on('end', function () {
        // Hide continental pins — they have no scale compensation and blow up at zoom
        ctx.g.selectAll('.c-pin').style('opacity', 0);
        ctx.state.view = 'us';
        ctx.state.busy = false;
        // Insert states layer first, then pin layer — fixed DOM order guarantees pins are always on top
        var statesLayer = ctx.g.append('g').attr('class', 'states-layer');
        var pinLayer    = ctx.g.append('g').attr('class', 'city-pin-layer');
        drawStates(statesLayer, us, ctx.proj);
        staggerCityPins(pinLayer, ctx.proj, ctx.tooltip, k);
      });
  }

  /* ── Zoom back to flat world ────────────────────────────────────────────── */

  function zoomBackToFlat(ctx) {
    if (ctx.state.busy) return;
    ctx.state.busy = true;
    hideTooltip(ctx.tooltip);

    // Restore world country opacity
    ctx.g.selectAll('.map-country')
      .transition().duration(reducedMotion ? 0 : 400)
      .style('opacity', 1);

    ctx.g.selectAll('.city-pin, .map-state, .city-pin-layer, .states-layer')
      .transition().duration(reducedMotion ? 0 : 200)
      .style('opacity', 0).remove();

    ctx.g.transition()
      .duration(reducedMotion ? 0 : 600)
      .ease(d3.easeCubicInOut)
      .attr('transform', 'translate(0,0) scale(1)')
      .on('end', function () {
        // Restore continental pins now that g is back to identity scale
        ctx.g.selectAll('.c-pin').style('opacity', 1);
        ctx.state.view = 'flat';
        ctx.state.busy = false;
        startUSHint(ctx);
      });
  }

  /* ── US state layer ───────────────────────────────────────────────────── */

  function drawStates(g, us, proj) {
    var statePath = d3.geoPath().projection(proj);
    var features = topojson.feature(us, us.objects.states).features
      .slice()
      .sort(function (a, b) {
        return d3.geoCentroid(a)[0] - d3.geoCentroid(b)[0]; // west → east sweep
      });
    features.forEach(function (feature, i) {
      setTimeout(function () {
        g.append('path')
          .datum(feature)
          .attr('class', 'map-state')
          .attr('d', statePath)
          .style('opacity', 0)
          .transition().duration(reducedMotion ? 0 : 300).ease(d3.easeCubicOut)
          .style('opacity', 1);
      }, reducedMotion ? 0 : i * 30);
    });
  }

  /* ── Staggered city pins ──────────────────────────────────────────────── */

  function staggerCityPins(g, proj, tooltip, k) {
    var pinScale = 1 / (k || 1); // compensate for parent g zoom transform
    CITIES.forEach(function (city, i) {
      setTimeout(function () {
        var coords = proj([city.lon, city.lat]);
        if (!coords) return;
        var pg = g.append('g')
          .attr('class', 'map-pin-group city-pin')
          .attr('transform', 'translate(' + coords[0] + ',' + coords[1] + ') scale(' + pinScale + ')')
          .style('opacity', 0);
        pg.append('path').attr('class', 'map-pin-icon').attr('d', PIN_SM).attr('fill', '#ef4444');
        pg.append('circle').attr('class', 'map-pin-dot').attr('cx', 0).attr('cy', -9).attr('r', 2);
        pg.transition().duration(reducedMotion ? 0 : 250).ease(d3.easeCubicOut).style('opacity', 1);
        pg.on('mouseenter', function (event) {
          showTooltip(tooltip, city, event, pg.node().closest('#world-map-container'));
        }).on('mousemove', function (event) {
          positionTooltip(tooltip, event, pg.node().closest('#world-map-container'));
        }).on('mouseleave', function () { hideTooltip(tooltip); });
      }, reducedMotion ? 0 : i * 70);
    });
  }

  /* ── Visibility check (great-circle distance from globe center) ───────── */

  function globeVisible(proj, lon, lat) {
    var r   = proj.rotate();
    var R   = Math.PI / 180;
    var lon1 = -r[0] * R, lat1 = -r[1] * R;
    var lon2 =  lon  * R, lat2 =  lat  * R;
    var d = Math.acos(
      Math.sin(lat1) * Math.sin(lat2) +
      Math.cos(lat1) * Math.cos(lat2) * Math.cos(lon2 - lon1)
    );
    return d < Math.PI / 2; // within 90° of center = visible hemisphere
  }

  /* ── Static pins ──────────────────────────────────────────────────────── */

  function drawPins(g, pins, proj, tooltip, cls) {
    pins.forEach(function (pin) {
      var visible = globeVisible(proj, pin.lon, pin.lat);
      var coords  = visible ? proj([pin.lon, pin.lat]) : null;
      // Always create — bind pin data so drag handler can use d.lon/d.lat directly
      var pg = g.append('g')
        .datum(pin)
        .attr('class', 'map-pin-group ' + cls)
        .attr('transform', coords
          ? 'translate(' + coords[0] + ',' + coords[1] + ')'
          : 'translate(-9999,-9999)')
        .style('opacity', coords ? 1 : 0);
      pg.append('path').attr('class', 'map-pin-icon').attr('d', PIN_LG).attr('fill', '#ef4444');
      pg.append('circle').attr('class', 'map-pin-dot').attr('cx', 0).attr('cy', -12).attr('r', 3);
      pg.on('mouseenter', function (event) {
        showTooltip(tooltip, pin, event, pg.node().closest('#world-map-container'));
      }).on('mousemove', function (event) {
        positionTooltip(tooltip, event, pg.node().closest('#world-map-container'));
      }).on('mouseleave', function () { hideTooltip(tooltip); });
    });
  }

  /* ── Tooltip helpers ──────────────────────────────────────────────────── */

  function showTooltip(tt, d, event, container) {
    var label = d.name;
    if (d.state)        label += ', ' + d.state;
    else if (d.country) label += ', ' + d.country;
    tt.html(
      '<div class="map-tooltip-name">' + label + '</div>' +
      (d.tag ? '<div class="map-tooltip-tag">' + d.tag + '</div>' : '')
    );
    positionTooltip(tt, event, container);
    tt.classed('is-visible', true);
  }

  function positionTooltip(tt, event, container) {
    if (!container) return;
    var r  = container.getBoundingClientRect();
    var x  = event.clientX - r.left + 12;
    var y  = event.clientY - r.top  - 10;
    var tw = tt.node().offsetWidth;
    var th = tt.node().offsetHeight;
    if (x + tw > container.clientWidth)  x -= tw + 24;
    if (y + th > container.clientHeight) y -= th + 20;
    if (x < 0) x = 8;
    if (y < 0) y = 8;
    tt.style('left', x + 'px').style('top', y + 'px');
  }

  function hideTooltip(tt) { tt.classed('is-visible', false); }

}());
