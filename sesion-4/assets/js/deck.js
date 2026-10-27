/*
 * Inicialización común de las presentaciones de la Sesión 4 (copia adaptada de la Sesión 3).
 * - Lee la duración de cada diapositiva (atributo data-min de cada <section> sin subsecciones)
 *   y antepone a sus notas del orador la duración y el minuto acumulado del bloque.
 * - Admite columnas verticales: una <section> que contiene otras es solo un contenedor.
 *   Sus diapositivas de detalle llevan data-min="0" y sus notas dicen que son material de consulta.
 * - Comprueba que la suma coincide con la duración del bloque (data-total-min en .slides).
 * - Las diapositivas con el atributo data-opcional se marcan en las notas como prescindibles.
 * - Inicializa reveal.js con el complemento de notas (tecla S) y de zoom (Alt + clic).
 */
(function () {
  "use strict";

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
    console.warn("[Sesión 4] La suma de minutos (" + total + ") no coincide con la duración del bloque (" + declared + ").");
  } else {
    console.info("[Sesión 4] Tiempos verificados: " + total + " min en " + sections.length + " diapositivas.");
  }

  Reveal.initialize({
    width: 1280,
    height: 720,
    margin: 0.05,
    center: false,
    hash: true,
    controls: true,
    progress: true,
    slideNumber: "h.v",
    transition: "slide",
    transitionSpeed: "default",
    backgroundTransition: "fade",
    showNotes: false,
    plugins: [RevealNotes, RevealZoom]
  });
})();
