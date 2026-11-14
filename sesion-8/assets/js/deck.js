/*
 * Inicialización común de las presentaciones de la Sesión 8 (copia adaptada de la Sesión 7).
 * - Lee la duración de cada diapositiva (atributo data-min de cada <section> sin subsecciones)
 *   y antepone a sus notas del orador la duración y el minuto acumulado del bloque.
 * - Admite columnas verticales: una <section> que contiene otras es solo un contenedor.
 *   Sus diapositivas de detalle llevan data-min="0" y sus notas dicen que son material de consulta.
 * - Comprueba que la suma coincide con la duración del bloque (data-total-min en .slides).
 * - Las diapositivas con el atributo data-opcional se marcan en las notas como prescindibles.
 * - El contador de la esquina muestra la diapositiva y el total: «5/16». En una columna vertical,
 *   la fila va después de un punto («5.2/16»); el total cuenta las columnas del recorrido.
 * - Inicializa reveal.js con el complemento de notas (tecla S) y de zoom (Alt + clic).
 * - Tema claro (predeterminado) u oscuro: el botón junto al número de diapositiva y la tecla T lo alternan,
 *   y la elección se guarda en el navegador. Con «?tema=oscuro» en la dirección se abre en el oscuro.
 *   Los colores fijos de los SVG, de las tablas de calor y de los bloques <style> de cada presentación
 *   se convierten al cargar en las variables del tema (tema-si.css), sin modificar los archivos.
 *   La portada de la sesión (index.html) también carga este archivo, solo para el tema.
 */
(function () {
  "use strict";

  // ---------- Tema claro u oscuro ----------
  var CLAVE = "si-tema";
  var raiz = document.documentElement;

  // Colores del tema oscuro original → variable de tema-si.css
  var HEX = {
    "#0a0e17": "--bg", "#111827": "--bg-2", "#172033": "--bg-3", "#1c2538": "--grid", "#2a3550": "--line",
    "#e8ecf4": "--text", "#a3adc2": "--muted", "#38bdf8": "--accent", "#f5b942": "--accent-2", "#a78bfa": "--violet",
    "#4ade80": "--ok", "#f87171": "--bad", "#12203a": "--glow", "#7dd3fc": "--accent-hover", "#8790a6": "--dim",
    "#fecaca": "--bad-text", "#0f2a3a": "--tint-accent", "#10261a": "--tint-ok", "#2a2210": "--tint-amber",
    "#1d1733": "--tint-violet", "#2a1416": "--tint-bad", "#1d2638": "--panel-2",
    "#c7f0ff": "--code", "#d1fae5": "--ok-text", "#fde9bf": "--amber-text", "#3b4560": "--dot", "#0f1626": "--illus-bg"
  };
  var RGB = {
    "10,14,23": "--bg", "17,24,39": "--bg-2", "23,32,51": "--bg-3", "42,53,80": "--line", "232,236,244": "--text",
    "163,173,194": "--muted", "56,189,248": "--accent", "245,185,66": "--accent-2", "167,139,250": "--violet",
    "74,222,128": "--ok", "248,113,113": "--bad"
  };
  // Celdas de calor: mezclas de #172033 con un color vivo (color_calor en ejemplos/graficas_en_diapositivas.py).
  // Conservan el color vivo y parten de --heat-base, que en el tema claro es casi blanco.
  var VIVOS = [[56, 189, 248], [74, 222, 128], [248, 113, 113], [245, 185, 66], [167, 139, 250]];
  var BASE_CALOR = [23, 32, 51];

  function calor(c) {
    var mejor = null;
    VIVOS.forEach(function (v) {
      var num = 0, den = 0, err = 0, i, t;
      for (i = 0; i < 3; i++) { num += (c[i] - BASE_CALOR[i]) * (v[i] - BASE_CALOR[i]); den += Math.pow(v[i] - BASE_CALOR[i], 2); }
      t = num / den;
      for (i = 0; i < 3; i++) { err += Math.pow(c[i] - (BASE_CALOR[i] + t * (v[i] - BASE_CALOR[i])), 2); }
      if (t > -0.01 && t < 1.01 && (!mejor || err < mejor.err)) { mejor = { vivo: v, t: t, err: err }; }
    });
    if (!mejor || mejor.err > 12) { return null; }
    var pct = Math.round(Math.max(0, Math.min(1, mejor.t)) * 1000) / 10;
    return "color-mix(in srgb, rgb(" + mejor.vivo.join(",") + ") " + pct + "%, var(--heat-base))";
  }

  function convertir(texto) {
    return texto
      .replace(/rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([\d.]+)\s*\)/g, function (m, r, g, b, a) {
        var v = RGB[r + "," + g + "," + b];
        return v ? "color-mix(in srgb, var(" + v + ") " + Math.round(parseFloat(a) * 1000) / 10 + "%, transparent)" : m;
      })
      .replace(/rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)/g, function (m, r, g, b) {
        return calor([+r, +g, +b]) || m;
      })
      .replace(/#[0-9a-fA-F]{6}\b/g, function (m) {
        var v = HEX[m.toLowerCase()];
        return v ? "var(" + v + ")" : m;
      });
  }

  var sonda = null;
  function computado(valor) {
    if (!sonda) { sonda = document.createElement("i"); sonda.style.display = "none"; document.body.appendChild(sonda); }
    sonda.style.color = "";
    sonda.style.color = valor;
    return getComputedStyle(sonda).color;
  }

  function normalizar() {
    var todos = function (sel) { return Array.prototype.slice.call(document.querySelectorAll(sel)); };
    todos("style").forEach(function (s) {
      var nuevo = convertir(s.textContent);
      if (nuevo !== s.textContent) { s.textContent = nuevo; }
    });
    todos("[style]").forEach(function (el) {
      var st = el.getAttribute("style"), nuevo = convertir(st);
      if (nuevo !== st) { el.setAttribute("style", nuevo); }
    });
    // Atributos de presentación de los SVG. Se pasan al estilo en línea solo cuando son los que mandan:
    // si una clase (p. ej. .cs{fill:…}) les gana, esa clase ya quedó convertida en el primer paso.
    todos("svg, svg *").forEach(function (el) {
      ["fill", "stroke", "stop-color", "flood-color"].forEach(function (a) {
        var v = el.getAttribute(a);
        if (!v || el.style.getPropertyValue(a)) { return; }
        var nuevo = convertir(v);
        if (nuevo !== v && getComputedStyle(el).getPropertyValue(a) === computado(v)) {
          el.style.setProperty(a, nuevo);
        }
      });
    });
  }

  function leerTema() {
    var m = /[?&]tema=(claro|oscuro)\b/.exec(location.search);
    if (m) { return m[1]; }
    try { return localStorage.getItem(CLAVE) === "oscuro" ? "oscuro" : "claro"; } catch (e) { return "claro"; }
  }

  var LUNA = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
  var SOL = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>';
  var boton = null;

  function aplicarTema(tema) {
    raiz.setAttribute("data-tema", tema);
    if (boton) {
      var otro = tema === "oscuro" ? "claro" : "oscuro";
      boton.innerHTML = tema === "oscuro" ? SOL : LUNA;
      boton.setAttribute("aria-label", "Cambiar al tema " + otro);
      boton.title = "Cambiar al tema " + otro + " (tecla T)";
    }
  }

  function alternarTema() {
    var tema = raiz.getAttribute("data-tema") === "oscuro" ? "claro" : "oscuro";
    aplicarTema(tema);
    try { localStorage.setItem(CLAVE, tema); } catch (e) { /* sin almacenamiento: el cambio dura hasta recargar */ }
  }

  aplicarTema(leerTema());
  normalizar();
  // Las vistas previas de la vista del orador (tecla S) no llevan botón; siguen el tema de la ventana principal
  if (!/receiver/.test(location.search)) {
    boton = document.createElement("button");
    boton.type = "button";
    boton.className = document.querySelector(".reveal .slides") ? "tema-toggle en-presentacion" : "tema-toggle";
    boton.addEventListener("click", function () { alternarTema(); boton.blur(); });
    document.body.appendChild(boton);
    aplicarTema(raiz.getAttribute("data-tema"));
  }
  window.addEventListener("storage", function (e) {
    if (e.key === CLAVE) { aplicarTema(e.newValue === "oscuro" ? "oscuro" : "claro"); }
  });

  // ---------- Presentación (no aplica a la portada de la sesión) ----------
  if (!document.querySelector(".reveal .slides") || !window.Reveal) { return; }


  // ---------- Presentación (no aplica a la portada de la sesión) ----------
  function fmt(n) {
    var r = Math.round(n * 10) / 10;
    return String(r).replace(".", ",");
  }

  var slidesEl = document.querySelector(".reveal .slides");
  var declared = parseFloat(slidesEl.getAttribute("data-total-min") || "0");
  // Diapositivas reales: las <section> que no contienen otras <section>
  var sections = Array.prototype.filter.call(
    document.querySelectorAll(".reveal .slides section"),
    function (s) { return !s.querySelector("section"); }
  );

  var total = 0;
  sections.forEach(function (s) { total += parseFloat(s.getAttribute("data-min") || "0"); });

  var acc = 0;
  sections.forEach(function (s, i) {
    var m = parseFloat(s.getAttribute("data-min") || "0");
    var vertical = s.parentElement && s.parentElement.tagName === "SECTION" && s.previousElementSibling &&
      s.previousElementSibling.tagName === "SECTION";
    var notes = s.querySelector("aside.notes");
    if (!notes) {
      notes = document.createElement("aside");
      notes.className = "notes";
      s.appendChild(notes);
    }
    var header = document.createElement("p");
    header.className = "timing";
    if (m > 0) {
      header.innerHTML = "<strong>⏱ " + fmt(m) + " min</strong> · minuto " + fmt(acc) + "–" + fmt(acc + m) +
        " de " + fmt(declared || total) + " · diapositiva " + (i + 1) + " de " + sections.length;
      if (s.hasAttribute("data-opcional")) {
        header.innerHTML += "<br><strong>Opcional:</strong> se puede saltar si el tiempo no alcanza.";
      }
    } else {
      header.innerHTML = "<strong>Material de consulta</strong> (no consume tiempo de clase)" +
        (vertical ? " · detalle del original, en la columna vertical: flecha ↓ para seguir, → para volver al recorrido" : "") +
        " · diapositiva " + (i + 1) + " de " + sections.length;
    }
    notes.insertBefore(header, notes.firstChild);
    acc += m;
  });

  if (declared && Math.abs(total - declared) > 0.01) {
    console.warn("[Sesión 8] La suma de minutos (" + total + ") no coincide con la duración del bloque (" + declared + ").");
  } else {
    console.info("[Sesión 8] Tiempos verificados: " + total + " min en " + sections.length + " diapositivas.");
  }

  Reveal.initialize({
    width: 1280,
    height: 720,
    margin: 0.05,
    center: false,
    hash: true,
    controls: true,
    progress: true,
    slideNumber: function (slide) {
      slide = slide || Reveal.getCurrentSlide();
      var idx = Reveal.getIndices(slide);
      var actual = String(idx.h + 1) + (Reveal.isVerticalSlide(slide) ? "." + (idx.v + 1) : "");
      return [actual, "/", Reveal.getHorizontalSlides().length];
    },
    transition: "slide",
    transitionSpeed: "default",
    backgroundTransition: "fade",
    showNotes: false,
    plugins: [RevealNotes, RevealZoom]
  });
  Reveal.addKeyBinding({ keyCode: 84, key: "T", description: "Cambiar entre el tema claro y el oscuro" }, alternarTema);
})();
