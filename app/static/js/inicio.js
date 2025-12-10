let calendar;
let vistaActual = "dayGridMonth";

document.addEventListener("DOMContentLoaded", function () {
  const calendarEl = document.getElementById("calendar");

  // Obtener la URL de eventos desde el atributo data-url-eventos del HTML
  const eventosUrl = calendarEl.dataset.urlEventos;

  calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: "dayGridMonth",
    height: "100%",
    contentHeight: "100%",
    locale: "es",
    fixedWeekCount: false,
    selectable: true,
    editable: true,
    events: eventosUrl,
    eventDisplay: "block",
    displayEventTime: false,

    views: {
      dayGridMonth: {
        displayEventTime: false,
      },
      timeGridWeek: {
        allDaySlot: false,
        slotMinTime: "08:00:00",
        slotMaxTime: "24:00:00",
        slotDuration: "02:00:00",
        displayEventTime: true,
        nowIndicator: false,
        expandRows: true,
      },
    },

    buttonText: {
      today: "Hoy",
      month: "Mes",
      week: "Semana",
    },

    eventClick: function (info) {
      const evento = info.event;
      const props = evento.extendedProps || {};

      // Rellenar el modal con datos del evento
      document.getElementById("modalDescripcion").textContent =
        evento.title || "Sin descripción";

      document.getElementById("modalInicio").textContent = evento.start
        ? evento.start.toLocaleDateString("es-ES")
        : "No especificada";

      document.getElementById("modalFin").textContent = evento.end
        ? evento.end.toLocaleDateString("es-ES")
        : "No especificada";

      document.getElementById("modalObservaciones").textContent =
        props.observaciones || "Sin observaciones";

      document.getElementById("modalMonto").textContent =
        props.monto_total?.toLocaleString("es-ES") || "0";

      document.getElementById("modalAdeuda").textContent = props.adeuda
        ? "Sí"
        : "No";

      document.getElementById("modalDni").textContent =
        props.dni || "No especificado";

      document.getElementById("modalResponsableApertura").textContent =
        props.responsable_apertura || "No especificado";

      document.getElementById("modalResponsableCierre").textContent =
        props.responsable_cierre || "No especificado";

      const modalElement = document.getElementById("eventoModal");
      const modal = new bootstrap.Modal(modalElement);
      modal.show();

      info.jsEvent.preventDefault();
      return false;
    },
  });

  calendar.render();
});

// Cambiar entre vista mensual y semanal
function toggleVista() {
  if (!calendar) return;

  const iconoVista = document.getElementById("iconoVista");
  const textoVista = document.getElementById("textoVista");

  if (vistaActual === "dayGridMonth") {
    calendar.changeView("timeGridWeek");
    vistaActual = "timeGridWeek";

    iconoVista.className = "bi bi-calendar-month me-2";
    textoVista.textContent = "Mes";
  } else {
    calendar.changeView("dayGridMonth");
    vistaActual = "dayGridMonth";

    iconoVista.className = "bi bi-calendar-week me-2";
    textoVista.textContent = "Semana";
  }
}

// Descargar calendario como imagen
document.getElementById("btnDescargarImagen").addEventListener("click", () => {
  const element = document.getElementById("calendar");

  html2canvas(element, {
    backgroundColor: "#ffffff",
    scale: 2,
  }).then(function (canvas) {
    const link = document.createElement("a");
    link.download = "calendario.png";
    link.href = canvas.toDataURL("image/png");
    link.click();
  });
});
