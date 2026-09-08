/* The moving parts of the homepage.
   Three things: drifting words behind the headline, a headline that can't
   settle on a verb, and a slot machine that mints job titles. */
(function () {
  "use strict";

  var reduced = window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- 1. the headline that can't finish its own sentence ---------- */
  var VERBS = ["do", "am", "sell", "build", "charge", "owe", "fix",
               "am for", "cost", "count as"];

  var swap = document.querySelector(".hero h1 .swap");
  if (swap && !reduced) {
    var vi = 0;
    setInterval(function () {
      vi = (vi + 1) % VERBS.length;
      swap.classList.remove("glitch");
      // reflow so the animation restarts
      void swap.offsetWidth;
      swap.textContent = VERBS[vi];
      swap.classList.add("glitch");
    }, 2600);
  }

  /* ---------- 2. drifting words behind everything ---------- */
  var canvas = document.getElementById("driftCanvas");
  if (canvas && !reduced) {
    var ctx = canvas.getContext("2d");
    var words = (canvas.dataset.words || "").split("|").filter(Boolean);
    var particles = [];
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    var raf = null;

    function size() {
      var host = canvas.parentElement;
      canvas.width = host.offsetWidth * dpr;
      canvas.height = host.offsetHeight * dpr;
      canvas.style.width = host.offsetWidth + "px";
      canvas.style.height = host.offsetHeight + "px";
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }

    function seed() {
      particles = [];
      var w = canvas.width / dpr, h = canvas.height / dpr;
      var n = Math.max(10, Math.min(26, Math.round(w / 52)));
      for (var i = 0; i < n; i++) {
        particles.push({
          text: words[Math.floor(Math.random() * words.length)] || "?",
          x: Math.random() * w,
          y: Math.random() * h,
          vx: (Math.random() - 0.5) * 0.28,
          vy: (Math.random() - 0.5) * 0.16,
          size: 11 + Math.random() * 15,
          alpha: 0.06 + Math.random() * 0.16,
          // A few words burn brighter, then fade and get reassigned.
          life: 300 + Math.random() * 900
        });
      }
    }

    function frame() {
      var w = canvas.width / dpr, h = canvas.height / dpr;
      ctx.clearRect(0, 0, w, h);
      for (var i = 0; i < particles.length; i++) {
        var p = particles[i];
        p.x += p.vx; p.y += p.vy; p.life -= 1;

        if (p.x < -240) p.x = w + 40;
        if (p.x > w + 240) p.x = -40;
        if (p.y < -30) p.y = h + 20;
        if (p.y > h + 30) p.y = -20;

        if (p.life <= 0) {
          // A word stops being true and another takes its place.
          p.text = words[Math.floor(Math.random() * words.length)] || "?";
          p.life = 300 + Math.random() * 900;
          p.alpha = 0.06 + Math.random() * 0.16;
        }

        var fade = p.life < 60 ? p.life / 60 : 1;
        ctx.font = '600 ' + p.size + 'px "IBM Plex Mono", monospace';
        ctx.fillStyle = "rgba(18,17,15," + (p.alpha * fade) + ")";
        ctx.fillText(p.text, p.x, p.y);
      }
      raf = requestAnimationFrame(frame);
    }

    size(); seed(); frame();

    var t = null;
    window.addEventListener("resize", function () {
      clearTimeout(t);
      t = setTimeout(function () { size(); seed(); }, 180);
    });

    // Don't burn a phone battery in a background tab.
    document.addEventListener("visibilitychange", function () {
      if (document.hidden) { cancelAnimationFrame(raf); raf = null; }
      else if (!raf) { frame(); }
    });
  }

  /* ---------- 3. the job-title slot machine ---------- */
  var machine = document.getElementById("machine");
  if (machine) {
    var out = machine.querySelector(".machine-out");
    var doing = machine.querySelector(".machine-doing");
    var btn = machine.querySelector("[data-spin]");
    var pool = (machine.dataset.pool || "").split("|").filter(Boolean);
    var spinning = false;

    function scramble(finalText, done) {
      var frames = 16, i = 0;
      var tick = setInterval(function () {
        i++;
        out.textContent = pool[Math.floor(Math.random() * pool.length)] || "…";
        if (i >= frames) {
          clearInterval(tick);
          out.textContent = finalText;
          done && done();
        }
      }, 55);
    }

    function spin() {
      if (spinning) return;
      spinning = true;
      btn.disabled = true;
      doing.innerHTML = "";

      fetch("/api/title")
        .then(function (r) { return r.json(); })
        .then(function (d) {
          if (reduced) {
            out.textContent = d.title;
            render(d.doing);
            finish();
            return;
          }
          scramble(d.title, function () { render(d.doing); finish(); });
        })
        .catch(function () {
          out.textContent = "Even the title generator is confused.";
          finish();
        });

      function render(list) {
        // Reveal each line a beat apart - it reads like a confession.
        (list || []).forEach(function (line, idx) {
          setTimeout(function () {
            var row = document.createElement("div");
            row.innerHTML = "&rsaquo; <i>" + line + "</i>";
            doing.appendChild(row);
          }, reduced ? 0 : 160 * idx);
        });
      }
      function finish() {
        setTimeout(function () { spinning = false; btn.disabled = false; },
                   reduced ? 0 : 700);
      }
    }

    btn.addEventListener("click", spin);
    spin();
  }
})();
