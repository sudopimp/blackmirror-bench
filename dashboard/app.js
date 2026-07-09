/**
 * BlackMirror-Bench dashboard (ES)
 * Vanilla JS — no modules — works under file:// and static hosts.
 */
(function (global) {
  "use strict";

  /**
   * Shape raw snapshot leaderboard rows for the table view model.
   * Pure function — unit-tested from Python via Node or structural checks.
   */
  function shapeLeaderboard(rows) {
    if (!Array.isArray(rows)) return [];
    return rows
      .map(function (r, i) {
        var tracks = r.tracks || {};
        return {
          rank: i + 1,
          model_id: String(r.model_id || ""),
          display_name: String(r.display_name || r.model_id || "—"),
          note: String(r.note || ""),
          split: String(r.split || ""),
          bm_score: Number(r.bm_score),
          tracks: {
            T1: Number(tracks.T1 || 0),
            T2: Number(tracks.T2 || 0),
            T3: Number(tracks.T3 || 0),
            T4: Number(tracks.T4 || 0),
            T5: Number(tracks.T5 || 0),
          },
          n_tasks: Number(r.n_tasks || 0),
          as_of: String(r.as_of || ""),
        };
      })
      .sort(function (a, b) {
        return b.bm_score - a.bm_score;
      })
      .map(function (r, i) {
        r.rank = i + 1;
        return r;
      });
  }

  function pct(n) {
    if (typeof n !== "number" || isNaN(n)) return "—";
    return (n * 100).toFixed(1) + "%";
  }

  function fmtScore(n) {
    if (typeof n !== "number" || isNaN(n)) return "—";
    return n.toFixed(3);
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function trackBarsHtml(tracks) {
    var ids = ["T1", "T2", "T3", "T4", "T5"];
    return (
      '<div class="track-bars" role="group" aria-label="Puntuaciones por pista">' +
      ids
        .map(function (id) {
          var v = tracks[id] || 0;
          var w = Math.max(0, Math.min(100, v * 100));
          return (
            '<div class="track-row">' +
            '<span class="tid">' +
            id +
            "</span>" +
            '<div class="bar" aria-hidden="true"><span style="width:' +
            w +
            '%"></span></div>' +
            '<span class="val">' +
            pct(v) +
            "</span>" +
            "</div>"
          );
        })
        .join("") +
      "</div>"
    );
  }

  function renderLeaderboard(tbody, rows) {
    if (!tbody) return;
    if (!rows.length) {
      tbody.innerHTML =
        '<tr><td colspan="5">No hay resultados en la instantánea del ranking.</td></tr>';
      return;
    }
    tbody.innerHTML = rows
      .map(function (r) {
        var top = r.rank === 1 ? " is-top" : "";
        return (
          "<tr class=\"" +
          top +
          "\">" +
          '<td class="rank" aria-label="Puesto ' +
          r.rank +
          '">#' +
          r.rank +
          "</td>" +
          '<td class="model-cell">' +
          '<span class="name">' +
          escapeHtml(r.display_name) +
          "</span>" +
          '<span class="note">' +
          escapeHtml(r.note) +
          " · " +
          escapeHtml(r.split) +
          " · " +
          r.n_tasks +
          " tareas</span>" +
          "</td>" +
          '<td class="num bm" data-testid="bm-score">' +
          fmtScore(r.bm_score) +
          '<div class="bar" aria-hidden="true"><span style="width:' +
          Math.max(0, Math.min(100, r.bm_score * 100)) +
          '%"></span></div>' +
          "</td>" +
          '<td class="bar-cell">' +
          trackBarsHtml(r.tracks) +
          "</td>" +
          '<td class="num">' +
          pct(r.tracks.T1) +
          "</td>" +
          "</tr>"
        );
      })
      .join("");
  }

  function renderHeroStats(el, rows, protocol) {
    if (!el) return;
    var top = rows[0];
    var nModels = rows.length;
    var tasks = (protocol && protocol.tasks) || (top && top.n_tasks) || 0;
    el.innerHTML =
      '<div class="stat"><span class="label">Modelos en ranking</span><span class="value">' +
      nModels +
      "</span></div>" +
      '<div class="stat"><span class="label">Tareas (protocolo)</span><span class="value">' +
      tasks +
      "</span></div>" +
      '<div class="stat"><span class="label">Mejor BM-Score</span><span class="value accent" data-testid="top-bm">' +
      (top ? fmtScore(top.bm_score) : "—") +
      "</span></div>" +
      '<div class="stat"><span class="label">Líder</span><span class="value" style="font-size:1.05rem">' +
      (top ? escapeHtml(top.display_name) : "—") +
      "</span></div>";
  }

  function renderAxes(el, axes) {
    if (!el || !axes) return;
    el.innerHTML = axes
      .map(function (a) {
        return (
          '<article class="axis-card">' +
          '<div class="code">' +
          escapeHtml(a.id) +
          "</div>" +
          "<h3>" +
          escapeHtml(a.name) +
          "</h3>" +
          "<p>" +
          escapeHtml(a.blurb) +
          "</p>" +
          "</article>"
        );
      })
      .join("");
  }

  function renderTracks(el, tracks) {
    if (!el || !tracks) return;
    el.innerHTML = tracks
      .map(function (t) {
        return (
          '<article class="track-card">' +
          '<div class="code">' +
          escapeHtml(t.id) +
          "</div>" +
          "<h3>" +
          escapeHtml(t.name) +
          "</h3>" +
          "<p>" +
          escapeHtml(t.blurb) +
          "</p>" +
          "</article>"
        );
      })
      .join("");
  }

  function setBanner(el, kind, msg) {
    if (!el) return;
    el.className = "status-banner" + (kind ? " is-" + kind : "");
    el.textContent = msg || "";
    el.hidden = !msg;
  }

  function readEmbeddedSnapshot() {
    var node = document.getElementById("bmb-data");
    if (!node) return null;
    try {
      return JSON.parse(node.textContent);
    } catch (e) {
      return null;
    }
  }

  function boot(snapshot) {
    var banner = document.getElementById("status-banner");
    var tbody = document.getElementById("leaderboard-body");
    var hero = document.getElementById("hero-stats");
    var axesEl = document.getElementById("axes-grid");
    var tracksEl = document.getElementById("tracks-grid");
    var asOfEl = document.getElementById("meta-as-of");
    var goldEl = document.getElementById("meta-gold");
    var splitEl = document.getElementById("meta-split");

    if (!snapshot || !snapshot.leaderboard) {
      setBanner(
        banner,
        "error",
        "No se pudo cargar la instantánea de resultados. Reabrí el archivo o regenerá dashboard/snapshot.json."
      );
      return;
    }

    var rows = shapeLeaderboard(snapshot.leaderboard);
    renderHeroStats(hero, rows, snapshot.protocol);
    renderLeaderboard(tbody, rows);
    renderAxes(axesEl, snapshot.axes || []);
    renderTracks(tracksEl, snapshot.tracks_meta || []);

    if (asOfEl) asOfEl.textContent = snapshot.as_of || "—";
    if (goldEl) goldEl.textContent = snapshot.gold || "—";
    if (splitEl) splitEl.textContent = snapshot.split_primary || "—";

    // Optional soft notice when embedded (file://) path
    if (location.protocol === "file:") {
      setBanner(
        banner,
        "info",
        "Modo archivo local: se usan datos embebidos (sin red). Ideal para abrir index.html directamente."
      );
    }

    document.documentElement.dataset.ready = "1";
  }

  // Export for tests / console
  global.BMB = {
    shapeLeaderboard: shapeLeaderboard,
    fmtScore: fmtScore,
    pct: pct,
    boot: boot,
    readEmbeddedSnapshot: readEmbeddedSnapshot,
  };

  function init() {
    var snap = readEmbeddedSnapshot();
    if (snap) {
      boot(snap);
      return;
    }
    // Fallback: try relative fetch (http(s) static server)
    fetch("snapshot.json")
      .then(function (r) {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .then(boot)
      .catch(function () {
        setBanner(
          document.getElementById("status-banner"),
          "error",
          "Sin datos: falta el bloque embebido #bmb-data y no se pudo leer snapshot.json."
        );
      });
  }

  // Only auto-boot in a real browser document (Node unit tests export BMB only).
  if (typeof document !== "undefined" && document.getElementById) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", init);
    } else {
      init();
    }
  }
})(typeof window !== "undefined" ? window : globalThis);
