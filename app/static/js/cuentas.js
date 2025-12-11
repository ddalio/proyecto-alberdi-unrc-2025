(function () {
  // ==================== BOTÓN AÑADIR USUARIO ====================
  const btnAñadirUsuario = getById("openCrearModalBtn");

  safeAddEventListener(btnAñadirUsuario, "click", () => {
    abrirModal(modales.crear);

    const errorCrear = getById("crearError");
    if (errorCrear) errorCrear.classList.add("d-none");
  });

  // ==================== UTILIDADES ====================
  function getById(id) {
    return document.getElementById(id);
  }

  function safeSetValue(id, value) {
    const el = getById(id);
    if (el) el.value = value || "";
  }

  function safeAddEventListener(el, event, handler) {
    if (el) el.addEventListener(event, handler);
  }

  function mostrarToast(mensaje, tipo = "success") {
    const toastContainer = document.querySelector(".toast-container");
    if (!toastContainer) return;

    const toastHtml = `
      <div class="toast align-items-center text-bg-${tipo} border-0" role="alert">
        <div class="d-flex">
          <div class="toast-body">${mensaje}</div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
      </div>
    `;
    toastContainer.insertAdjacentHTML("beforeend", toastHtml);
    const toastEl = toastContainer.lastElementChild;
    new bootstrap.Toast(toastEl).show();
  }

  // ==================== TOASTS AUTOMÁTICOS ====================
  const toastContainer = document.getElementById("toastContainer");

  function mostrarToast(mensaje, tipo = "success") {
    if (!toastContainer) return;

    const toastHtml = `
        <div class="toast align-items-center text-bg-${tipo} border-0 mb-2" role="alert" data-bs-autohide="true" data-bs-delay="5000">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bi ${
                      tipo === "success"
                        ? "bi-check-circle-fill"
                        : "bi-bell-fill"
                    } me-2"></i>${mensaje}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    toastContainer.insertAdjacentHTML("beforeend", toastHtml);
    const toastEl = toastContainer.lastElementChild;
    new bootstrap.Toast(toastEl).show();
  }

  // ==================== TOGGLE VISIBILIDAD CONTRASEÑA ====================
  function setupPasswordToggle() {
    document.querySelectorAll(".toggle-password").forEach((btn) => {
      btn.addEventListener("click", () => {
        const targetId = btn.dataset.target;
        const input = getById(targetId);
        if (!input) return;

        const type = input.type === "password" ? "text" : "password";
        input.type = type;

        const icon = btn.querySelector("i");
        if (icon)
          icon.className =
            type === "password" ? "bi bi-eye" : "bi bi-eye-slash";
      });
    });
  }

  setupPasswordToggle();

  // ==================== MODALES ====================
  const modales = {
    crear: getById("modalCrearOverlay"),
    editar: getById("modalEditarOverlay"),
    detalles: getById("modalDetallesOverlay"),
    reenviar: getById("modalReenviarOverlay"),
  };

  function abrirModal(modal) {
    if (modal) {
      modal.classList.remove("d-none");
      document.body.style.overflow = "hidden";
    }
  }

  function cerrarModal(modal) {
    if (modal) {
      modal.classList.add("d-none");
      document.body.style.overflow = "";
    }
  }

  function asignarCierreModales() {
    document
      .querySelectorAll(".close-crear-modal")
      .forEach((btn) =>
        safeAddEventListener(btn, "click", () => cerrarModal(modales.crear))
      );
    document
      .querySelectorAll(".close-editar-modal")
      .forEach((btn) =>
        safeAddEventListener(btn, "click", () => cerrarModal(modales.editar))
      );
    document
      .querySelectorAll(".close-detalles-modal")
      .forEach((btn) =>
        safeAddEventListener(btn, "click", () => cerrarModal(modales.detalles))
      );
    document
      .querySelectorAll(".close-reenviar-modal")
      .forEach((btn) =>
        safeAddEventListener(btn, "click", () => cerrarModal(modales.reenviar))
      );

    Object.values(modales).forEach((modal) => {
      if (!modal) return;
      modal.addEventListener("click", (e) => {
        if (e.target === modal) cerrarModal(modal);
      });
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        Object.values(modales).forEach((modal) => {
          if (modal && !modal.classList.contains("d-none")) cerrarModal(modal);
        });
      }
    });
  }

  asignarCierreModales();

  // ==================== FORMULARIOS ====================
  const formEditar = getById("formEditarUsuario");
  const btnActualizar = getById("btnActualizar");
  const errorEditar = getById("editarError");

  function enviarEdicion() {
    if (!formEditar) return;

    const formData = new FormData(formEditar);
    btnActualizar.disabled = true;
    btnActualizar.innerHTML =
      '<span class="spinner-border spinner-border-sm"></span> Actualizando...';

    fetch(formEditar.action, {
      method: "POST",
      body: formData,
      headers: { "X-Requested-With": "XMLHttpRequest" },
    })
      .then((res) => res.json())
      .then((data) => {
        if (!data.success) {
          if (errorEditar) {
            errorEditar.textContent = data.message || "Error al actualizar";
            errorEditar.classList.remove("d-none");
          }

          if (data.datos) {
            Object.keys(data.datos).forEach((key) => {
              const input = formEditar.querySelector(`[name="${key}"]`);
              if (input) input.value = data.datos[key];
            });
          }

          abrirModal(modales.editar);
          btnActualizar.disabled = false;
          btnActualizar.innerHTML = "Actualizar";
        } else {
          if (errorEditar) errorEditar.classList.add("d-none");
          mostrarToast(data.message || "Usuario actualizado", "success");
          cerrarModal(modales.editar);
          btnActualizar.disabled = false;
          btnActualizar.innerHTML = "Actualizar";

          setTimeout(() => {
            window.location.reload();
          }, 1200);
        }
      })
      .catch((err) => {
        console.error(err);
        if (errorEditar) {
          errorEditar.textContent = "Ocurrió un error inesperado";
          errorEditar.classList.remove("d-none");
        }
        btnActualizar.disabled = false;
        btnActualizar.innerHTML = "Actualizar";
      });
  }

  safeAddEventListener(formEditar, "submit", (e) => {
    e.preventDefault();
    enviarEdicion();
  });

  function cargarDatosEdicion(usuario) {
    fetch(`/cuentas/detalles/${usuario}`)
      .then((res) => res.json())
      .then((data) => {
        if (!data.success)
          return console.error("Error cargando datos", data.error);

        safeSetValue("editarUsuario", data.cuenta.nombre_usuario);
        safeSetValue("editarUsuarioDisplay", data.cuenta.nombre_usuario);
        safeSetValue("editarNombre", data.cuenta.nombre);
        safeSetValue("editarApellido", data.cuenta.apellido);
        safeSetValue("editarEmail", data.cuenta.email);
        safeSetValue("editarRol", data.cuenta.rol.toLowerCase());

        safeSetValue("editarPassword", "");
        safeSetValue("editarPassword2", "");

        formEditar.action = `/cuentas/editar/${data.cuenta.nombre_usuario}`;
        abrirModal(modales.editar);
      })
      .catch((err) => console.error("Error cargando datos de edición:", err));
  }

  // ==================== DETALLES ====================
  window.abrirModalDetalles = function (usuario) {
    cargarDetallesUsuario(usuario);
    abrirModal(modales.detalles);
  };

  function cargarDetallesUsuario(usuario) {
    const detallesContenido = getById("detallesContenido");
    detallesContenido.innerHTML = `
      <div class="text-center">
        <div class="spinner-border" role="status"></div>
        <p class="mt-2">Cargando detalles...</p>
      </div>
    `;

    fetch(`/cuentas/detalles/${usuario}`)
      .then((res) => res.json())
      .then((data) => {
        if (!data.success) {
          detallesContenido.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
          return;
        }

        detallesContenido.innerHTML = `
          <div class="row">
            <div class="col-md-6">
              <h6 class="text-muted">Información Básica</h6>
              <table class="table table-borderless table-sm">
                <tr><td><strong>Usuario:</strong></td><td>${
                  data.cuenta.nombre_usuario
                }</td></tr>
                <tr><td><strong>Nombre:</strong></td><td>${
                  data.cuenta.nombre
                }</td></tr>
                <tr><td><strong>Apellido:</strong></td><td>${
                  data.cuenta.apellido
                }</td></tr>
                <tr><td><strong>Rol:</strong></td>
                  <td><span class="badge ${
                    data.cuenta.rol === "Administrador"
                      ? "bg-danger"
                      : "bg-secondary"
                  }">${data.cuenta.rol}</span></td>
                </tr>
              </table>
            </div>
            <div class="col-md-6">
              <h6 class="text-muted">Información de Contacto</h6>
              <table class="table table-borderless table-sm">
                <tr><td><strong>Email:</strong></td><td>${
                  data.cuenta.email
                }</td></tr>
                <tr><td><strong>Fecha Creación:</strong></td><td>${
                  data.cuenta.fecha_creacion
                }</td></tr>
                <tr><td><strong>Último Acceso:</strong></td><td>${
                  data.cuenta.ultimo_acceso
                }</td></tr>
              </table>
            </div>
          </div>
          ${
            !data.cuenta.email_verificado
              ? `
          <div class="mt-3 p-3 bg-light rounded d-flex justify-content-between align-items-center">
            <div>
              <h6 class="mb-1">Email no verificado</h6>
              <p class="mb-0 text-muted">El usuario no ha verificado su email aún.</p>
            </div>
            <button type="button" class="btn btn-outline-primary btn-sm reenviar-verificacion-btn"
              data-usuario="${data.cuenta.nombre_usuario}" data-email="${data.cuenta.email}">
              <i class="bi bi-send me-1"></i>Reenviar verificación
            </button>
          </div>
          `
              : ""
          }
        `;
      })
      .catch((err) => {
        detallesContenido.innerHTML = `<div class="alert alert-danger">Error al cargar los detalles: ${err}</div>`;
      });
  }

  // ==================== REENVIAR VERIFICACIÓN ====================
  function reenviarVerificacionEmail(usuario, email) {
    const modal = modales.reenviar;
    const contenido = getById("reenviarContenido");
    const btnReenviar = getById("btnReenviarVerificacion");

    contenido.innerHTML = `
      <div class="text-center">
        <i class="bi bi-envelope-check display-4 text-primary mb-3"></i>
        <h6>Reenviar email de verificación</h6>
        <p>¿Estás seguro de que querés reenviar el email de verificación a <strong>${email}</strong>?</p>
        <small class="text-muted">El usuario recibirá un enlace para verificar su cuenta.</small>
      </div>
    `;

    abrirModal(modal);

    btnReenviar.onclick = () => {
      btnReenviar.disabled = true;
      btnReenviar.innerHTML =
        '<span class="spinner-border spinner-border-sm" role="status"></span> Enviando...';

      fetch("/cuentas/verificar-email", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ usuario }),
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.success) {
            contenido.innerHTML = `
              <div class="text-center">
                <i class="bi bi-check-circle display-4 text-success mb-3"></i>
                <h6>¡Email enviado!</h6>
                <p>El email de verificación fue enviado a <strong>${email}</strong>.</p>
              </div>
            `;
            btnReenviar.classList.add("d-none");
            setTimeout(() => cerrarModal(modal), 2000);
          } else {
            throw new Error(data.error || "Error al enviar email");
          }
        })
        .catch((err) => {
          contenido.innerHTML = `
            <div class="text-center">
              <i class="bi bi-exclamation-triangle display-4 text-danger mb-3"></i>
              <h6>Error</h6>
              <p>No se pudo enviar el email: ${err.message}</p>
            </div>
          `;
          btnReenviar.disabled = false;
          btnReenviar.innerHTML = '<i class="bi bi-send me-2"></i>Reenviar';
        });
    };
  }

  // ==================== TABLA Y BÚSQUEDA ====================
  const tbodyCuentas = getById("tbodyCuentas");
  const inputBusqueda = getById("inputBusqueda");
  const btnBuscar = getById("btnBuscar");
  const loadingBusqueda = getById("loadingBusqueda");
  const contadorResultados = getById("contadorResultados");

  let timeoutBusqueda;

  function realizarBusqueda(termino) {
    loadingBusqueda.classList.remove("d-none");
    btnBuscar.classList.add("d-none");

    fetch("/cuentas/buscar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ busqueda: termino }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (!data.success) {
          contadorResultados.textContent = "Error en la búsqueda";
          return;
        }

        actualizarTabla(data.resultados);
        contadorResultados.textContent = `Mostrando ${data.total} cuenta${
          data.total !== 1 ? "s" : ""
        }`;
      })
      .catch((err) => {
        console.error(err);
        contadorResultados.textContent = "Error de conexión";
      })
      .finally(() => {
        loadingBusqueda.classList.add("d-none");
        btnBuscar.classList.remove("d-none");
      });
  }

  function actualizarTabla(resultados) {
    if (resultados.length === 0) {
      tbodyCuentas.innerHTML = `<tr><td colspan="7" class="text-center text-muted">No se encontraron cuentas</td></tr>`;
      return;
    }

    tbodyCuentas.innerHTML = resultados
      .map(
        (c) => `
      <tr>
        <td>${c.nombre_usuario}</td>
        <td>${c.nombre}</td>
        <td>${c.apellido}</td>
        <td>${c.email}</td>
        <td>${c.rol}</td>
        <td class="acciones">
          <button type="button" class="btn btn-link p-0 text-decoration-none ver-detalles-btn" data-usuario="${
            c.nombre_usuario
          }" title="Ver detalles">
            <i class="bi bi-eye"></i>
          </button>
          <button type="button" class="btn btn-link p-0 text-decoration-none ms-2 editar-cuenta-btn" data-usuario="${
            c.nombre_usuario
          }" title="Editar">
            <i class="bi bi-pencil"></i>
          </button>
          ${
            !c.email_verificado
              ? `
          <button type="button" class="btn btn-link p-0 text-decoration-none ms-2 reenviar-verificacion-btn" data-usuario="${c.nombre_usuario}" data-email="${c.email}" title="Reenviar verificación">
            <i class="bi bi-send"></i>
          </button>`
              : ""
          }
          <form action="/cuentas/eliminar/${
            c.nombre_usuario
          }" method="POST" style="display:inline" class="ms-2" onsubmit="return confirm('¿Estás seguro de eliminar ${
          c.nombre_usuario
        }?');">
            <button type="submit" class="btn btn-link p-0 text-decoration-none" title="Eliminar">
              <i class="bi bi-trash"></i>
            </button>
          </form>
        </td>
      </tr>
    `
      )
      .join("");
  }

  // ==================== DELEGACIÓN DE EVENTOS ====================
  tbodyCuentas.addEventListener("click", (e) => {
    const btnDetalles = e.target.closest(".ver-detalles-btn");
    const btnEditar = e.target.closest(".editar-cuenta-btn");
    const btnReenviar = e.target.closest(".reenviar-verificacion-btn");

    if (btnDetalles) abrirModalDetalles(btnDetalles.dataset.usuario);
    if (btnEditar) cargarDatosEdicion(btnEditar.dataset.usuario);
    if (btnReenviar)
      reenviarVerificacionEmail(
        btnReenviar.dataset.usuario,
        btnReenviar.dataset.email
      );
  });

  inputBusqueda.addEventListener("input", function () {
    clearTimeout(timeoutBusqueda);
    const termino = this.value.trim();
    timeoutBusqueda = setTimeout(() => {
      if (termino.length >= 2 || termino.length === 0)
        realizarBusqueda(termino);
    }, 300);
  });

  btnBuscar.addEventListener("click", () =>
    realizarBusqueda(inputBusqueda.value.trim())
  );
  inputBusqueda.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      realizarBusqueda(inputBusqueda.value.trim());
    }
  });
})();
