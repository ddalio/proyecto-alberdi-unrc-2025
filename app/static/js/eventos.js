document.addEventListener("DOMContentLoaded", function () {
  const toastElList = [].slice.call(document.querySelectorAll(".toast"));
  toastElList.forEach(function (toastEl) {
    const toast = new bootstrap.Toast(toastEl, { delay: 5000 }); // se oculta automáticamente en 5s
    toast.show();
  });
});

document
  .getElementById("downloadPdfBtn")
  ?.addEventListener("click", function () {
    const campo = document.getElementById("campo")?.value;
    const valor = document.getElementById("valor")?.value;

    let url = "/eventos/pdf";

    // Si hay filtros, se los paso por querystring
    if (campo && valor) {
      url += `?campo=${encodeURIComponent(campo)}&valor=${encodeURIComponent(
        valor
      )}`;
    }

    window.location.href = url;
  });

/********************************************
 * MODAL PARA AGREGAR PAGO
 ********************************************/
(function () {
  const overlay = document.getElementById("paymentModalOverlay");
  const openBtns = document.querySelectorAll(".openAddPaymentBtn");
  const closeBtn = document.getElementById("closePaymentModalBtn");
  const cancelBtn = document.getElementById("cancelPaymentBtn");
  const form = document.getElementById("paymentForm");

  // Inputs / spans que llenamos
  const inputEventId = document.getElementById("modal_event_id");
  const spanEventId = document.getElementById("modal_event_id_text");
  const inputDesc = document.getElementById("modal_event_desc");
  const inputFecha = document.getElementById("modal_fecha_pago");
  const inputMonto = document.getElementById("modal_monto_pago");
  const spanMontoTotal = document.getElementById("modal_event_monto");
  const spanMontoDeuda = document.getElementById("modal_event_monto_deuda");
  const spanAdeuda = document.getElementById("modal_event_adeuda");
  const spanClienteNombre = document.getElementById("modal_cliente_nombre");
  const spanClienteDni = document.getElementById("modal_cliente_dni");
  const spanResponsable = document.getElementById("modal_responsable");

  function formatNumber(v) {
    return Number(v || 0).toFixed(2);
  }

  function openModal(actionUrl, details) {
    form.action = actionUrl || "#";

    inputEventId.value = details.id || "";
    spanEventId.textContent = details.id || "-";
    inputDesc.value = details.descripcion || "";
    inputMonto.value = details.monto || "";
    inputFecha.value = new Date().toISOString().slice(0, 10);

    spanMontoTotal.textContent = formatNumber(details.monto);
    spanMontoDeuda.textContent = formatNumber(details.monto_deuda);
    spanAdeuda.textContent =
      details.adeuda === "1" || details.adeuda === 1 || details.adeuda === true
        ? "Sí"
        : "No";

    spanClienteNombre.textContent = details.cliente_nombre
      ? details.cliente_nombre +
        (details.cliente_apellido ? " " + details.cliente_apellido : "")
      : "-";

    spanClienteDni.textContent = details.cliente_dni || "-";

    spanResponsable.textContent = details.responsable_nombre
      ? details.responsable_nombre +
        (details.responsable_apellido ? " " + details.responsable_apellido : "")
      : "-";

    overlay.classList.remove("d-none");
    overlay.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
  }

  function closeModal() {
    overlay.classList.add("d-none");
    overlay.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";

    form.action = "#";
    inputEventId.value = "";
    inputDesc.value = "";
    inputMonto.value = "";
  }

  // Abrir modal
  openBtns.forEach((btn) => {
    btn.addEventListener("click", function (e) {
      e.preventDefault();

      const details = {
        id: btn.dataset.id,
        descripcion: btn.dataset.descripcion,
        monto: btn.dataset.monto,
        monto_deuda: btn.dataset.montoDeuda || btn.dataset.monto_deuda || 0,
        adeuda: btn.dataset.adeuda,
        cliente_nombre: btn.dataset.clienteNombre || btn.dataset.cliente_nombre,
        cliente_apellido:
          btn.dataset.clienteApellido || btn.dataset.cliente_apellido,
        cliente_dni: btn.dataset.clienteDni || btn.dataset.cliente_dni,
        responsable_nombre:
          btn.dataset.responsableNombre || btn.dataset.responsable_nombre,
        responsable_apellido:
          btn.dataset.responsableApellido || btn.dataset.responsable_apellido,
      };

      const action = btn.dataset.action;
      openModal(action, details);
    });
  });

  // Botones de cerrar/cancelar
  closeBtn && closeBtn.addEventListener("click", closeModal);
  cancelBtn && cancelBtn.addEventListener("click", closeModal);

  // Cerrar clickeando fuera
  overlay &&
    overlay.addEventListener("click", function (e) {
      if (e.target === overlay) closeModal();
    });

  // Cerrar con ESC
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !overlay.classList.contains("d-none")) {
      closeModal();
    }
  });

  // Validación mínima
  form &&
    form.addEventListener("submit", function (e) {
      const monto = inputMonto.value;
      const fecha = inputFecha.value;

      if (!monto || !fecha) {
        e.preventDefault();
        alert("Complete monto y fecha del pago.");
      }
    });
})();
