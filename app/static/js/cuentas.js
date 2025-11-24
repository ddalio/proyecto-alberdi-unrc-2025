(function () {
  // ===== MOSTRAR TOASTS AUTOMÁTICAMENTE =====
  function mostrarToasts() {
    const toasts = document.querySelectorAll(".toast");
    toasts.forEach((toast) => {
      const bsToast = new bootstrap.Toast(toast);
      bsToast.show();
    });
  }

  // ===== VALIDACIÓN PARA CREACIÓN DE USUARIO =====
  function validarYEnviarCreacion(event) {
    event.preventDefault();

    const password = document.getElementById("crearPassword").value;
    const password2 = document.getElementById("crearPassword2").value;
    const email = document.getElementById("crearEmail").value;
    const btnCrear = document.getElementById("btnCrearUsuario");

    // Ocultar mensajes de error previos
    document.getElementById("crearPasswordMismatch").classList.add("d-none");
    document
      .getElementById("crearPasswordRequirements")
      .classList.add("d-none");
    document.getElementById("crearEmailError").classList.add("d-none");

    // Verificar que las contraseñas coincidan
    if (password !== password2) {
      document
        .getElementById("crearPasswordMismatch")
        .classList.remove("d-none");
      return false;
    }

    // Verificar requisitos de contraseña
    if (!validarRequisitosPassword(password)) {
      document
        .getElementById("crearPasswordRequirements")
        .classList.remove("d-none");
      return false;
    }

    // Deshabilitar botón y mostrar loading
    btnCrear.disabled = true;
    btnCrear.innerHTML =
      '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Creando y enviando email...';

    // Primero crear el usuario, luego enviar email de verificación
    crearUsuarioYEnviarVerificacion();
    return false;
  }

  function crearUsuarioYEnviarVerificacion() {
    const formData = new FormData(document.getElementById("formCrearUsuario"));
    const btnCrear = document.getElementById("btnCrearUsuario");

    fetch('{{ url_for("cuentas.crear_cuenta") }}', {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          return enviarEmailVerificacion(data.usuario_id);
        } else {
          throw new Error(data.error || "Error al crear usuario");
        }
      })
      .then((emailResult) => {
        if (emailResult.success) {
          // Todo exitoso, recargar la página
          mostrarMensajeExito(
            "Usuario creado y email de verificación enviado exitosamente"
          );
          setTimeout(() => {
            window.location.reload();
          }, 2000);
        } else {
          throw new Error(
            emailResult.error || "Error al enviar email de verificación"
          );
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        document.getElementById("crearEmailError").classList.remove("d-none");
        btnCrear.disabled = false;
        btnCrear.innerHTML =
          '<i class="bi bi-send me-2"></i>Crear y Enviar Verificación';
      });
  }

  function enviarEmailVerificacion(usuarioId) {
    return fetch('{{ url_for("cuentas.enviar_verificacion") }}', {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        usuario_id: usuarioId,
      }),
    }).then((response) => response.json());
  }

  function mostrarMensajeExito(mensaje) {
    // Crear un toast de éxito
    const toastContainer = document.querySelector(".toast-container");
    const toastHtml = `
            <div class="toast align-items-center text-white bg-success border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">${mensaje}</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
    toastContainer.insertAdjacentHTML("beforeend", toastHtml);

    // Mostrar el toast
    const toastElement = toastContainer.lastElementChild;
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
  }

  // ===== VALIDACIÓN DE CAMBIO DE CONTRASEÑA =====
  function validarCambioPassword(event) {
    event.preventDefault();

    const nuevaPassword = document.getElementById("editarPassword").value;
    const confirmarPassword = document.getElementById("editarPassword2").value;
    const passwordError = document.getElementById("passwordError");
    const passwordMismatch = document.getElementById("passwordMismatch");
    const passwordRequirements = document.getElementById(
      "passwordRequirements"
    );
    const btnActualizar = document.getElementById("btnActualizar");

    passwordError.classList.add("d-none");
    passwordMismatch.classList.add("d-none");
    passwordRequirements.classList.add("d-none");

    if (!nuevaPassword && !confirmarPassword) {
      return enviarFormularioEdicion();
    }

    if (
      (nuevaPassword && !confirmarPassword) ||
      (!nuevaPassword && confirmarPassword)
    ) {
      passwordMismatch.textContent =
        "Debe completar ambos campos de contraseña";
      passwordMismatch.classList.remove("d-none");
      return false;
    }

    // Verificar que las contraseñas coincidan
    if (nuevaPassword !== confirmarPassword) {
      passwordMismatch.textContent = "Las contraseñas no coinciden";
      passwordMismatch.classList.remove("d-none");
      return false;
    }

    // Verificar requisitos de contraseña
    if (!validarRequisitosPassword(nuevaPassword)) {
      passwordRequirements.classList.remove("d-none");
      return false;
    }

    // Deshabilitar botón para evitar múltiples envíos
    btnActualizar.disabled = true;
    btnActualizar.innerHTML =
      '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Validando...';

    // Verificar si la nueva contraseña es igual a la anterior
    return verificarPasswordAnterior(nuevaPassword);
  }

  function validarRequisitosPassword(password) {
    const regex =
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    return regex.test(password);
  }

  function verificarPasswordAnterior(nuevaPassword) {
    const usuario = document.getElementById("editarUsuario").value;
    const btnActualizar = document.getElementById("btnActualizar");

    return fetch('{{ url_for("cuentas.verificar_password") }}', {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        usuario: usuario,
        nueva_password: nuevaPassword,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.es_igual) {
          // Mostrar error y mantener el modal abierto
          document.getElementById("passwordError").classList.remove("d-none");
          btnActualizar.disabled = false;
          btnActualizar.innerHTML = "Actualizar";
          return false;
        } else {
          // Contraseña válida, enviar formulario
          return enviarFormularioEdicion();
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        btnActualizar.disabled = false;
        btnActualizar.innerHTML = "Actualizar";
        alert("Error de conexión. Intente nuevamente.");
        return false;
      });
  }

  function enviarFormularioEdicion() {
    const form = document.getElementById("formEditarUsuario");
    form.submit();
    return true;
  }

  function reenviarVerificacionEmail(usuario, email) {
    const modalReenviar = document.getElementById("modalReenviarOverlay");
    const reenviarContenido = document.getElementById("reenviarContenido");
    const btnReenviar = document.getElementById("btnReenviarVerificacion");

    // Mostrar modal de confirmación
    reenviarContenido.innerHTML = `
            <div class="text-center">
                <i class="bi bi-envelope-check display-4 text-primary mb-3"></i>
                <h6>Reenviar email de verificación</h6>
                <p>¿Estás seguro de que querés reenviar el email de verificación a <strong>${email}</strong>?</p>
                <small class="text-muted">El usuario recibirá un enlace para verificar su cuenta.</small>
            </div>
        `;

    modalReenviar.classList.remove("d-none");
    document.body.style.overflow = "hidden";

    // Configurar el botón de reenvío
    btnReenviar.onclick = function () {
      btnReenviar.disabled = true;
      btnReenviar.innerHTML =
        '<span class="spinner-border spinner-border-sm" role="status"></span> Enviando...';

      fetch('{{ url_for("cuentas.enviar_verificacion") }}', {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          usuario: usuario,
        }),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            reenviarContenido.innerHTML = `
                        <div class="text-center">
                            <i class="bi bi-check-circle display-4 text-success mb-3"></i>
                            <h6>¡Email enviado!</h6>
                            <p>El email de verificación fue enviado exitosamente a <strong>${email}</strong>.</p>
                        </div>
                    `;
            btnReenviar.classList.add("d-none");

            // Cerrar automáticamente después de 2 segundos
            setTimeout(() => {
              closeReenviarModal();
              window.location.reload();
            }, 2000);
          } else {
            throw new Error(data.error || "Error al enviar email");
          }
        })
        .catch((error) => {
          reenviarContenido.innerHTML = `
                    <div class="text-center">
                        <i class="bi bi-exclamation-triangle display-4 text-danger mb-3"></i>
                        <h6>Error</h6>
                        <p>No se pudo enviar el email de verificación: ${error.message}</p>
                    </div>
                `;
          btnReenviar.disabled = false;
          btnReenviar.innerHTML = '<i class="bi bi-send me-2"></i>Reenviar';
        });
    };
  }

  function closeReenviarModal() {
    document.getElementById("modalReenviarOverlay").classList.add("d-none");
    document.body.style.overflow = "";
  }

  // Ejecutar cuando el DOM esté listo
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mostrarToasts);
  } else {
    mostrarToasts();
  }

  // ===== TOGGLE VISIBILIDAD CONTRASEÑA =====
  function setupPasswordToggle() {
    document.querySelectorAll(".toggle-password").forEach((button) => {
      button.addEventListener("click", function () {
        const targetId = this.getAttribute("data-target");
        const passwordInput = document.getElementById(targetId);

        if (passwordInput) {
          const type =
            passwordInput.getAttribute("type") === "password"
              ? "text"
              : "password";
          passwordInput.setAttribute("type", type);

          // Cambiar icono
          const icon = this.querySelector("i");
          if (type === "password") {
            icon.className = "bi bi-eye";
          } else {
            icon.className = "bi bi-eye-slash";
          }
        }
      });
    });
  }

  // Configurar toggles para todas las contraseñas
  setupPasswordToggle();

  const inputBusqueda = document.getElementById("inputBusqueda");
  const btnBuscar = document.getElementById("btnBuscar");
  const loadingBusqueda = document.getElementById("loadingBusqueda");
  const tbodyCuentas = document.getElementById("tbodyCuentas");
  const contadorResultados = document.getElementById("contadorResultados");

  let timeoutBusqueda = null;

  function realizarBusqueda(termino) {
    loadingBusqueda.classList.remove("d-none");
    btnBuscar.classList.add("d-none");

    fetch('{{ url_for("cuentas.buscar_cuenta_ajax") }}', {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        busqueda: termino,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          actualizarTabla(data.resultados);
          contadorResultados.textContent = `Mostrando ${data.total} cuenta${
            data.total !== 1 ? "s" : ""
          }`;
        } else {
          console.error("Error:", data.error);
          contadorResultados.textContent = "Error en la búsqueda";
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        contadorResultados.textContent = "Error de conexión";
      })
      .finally(() => {
        loadingBusqueda.classList.add("d-none");
        btnBuscar.classList.remove("d-none");
      });
  }

  function actualizarTabla(resultados) {
    if (resultados.length === 0) {
      tbodyCuentas.innerHTML = `
          <tr>
            <td colspan="7" class="text-center text-muted">
              No se encontraron cuentas
            </td>
          </tr>
        `;
      return;
    }

    let html = "";
    resultados.forEach((cuenta) => {
      html += `
          <tr>
            <td>${cuenta.nombre_usuario}</td>
            <td>${cuenta.nombre}</td>
            <td>${cuenta.apellido}</td>
            <td>${cuenta.email}</td>
            <td>${cuenta.rol}</td>
            <td>
              ${
                cuenta.email_verificado
                  ? '<span class="badge bg-success">Sí</span>'
                  : '<span class="badge bg-warning">No</span>'
              }
            </td>
            <td class="acciones">
              <button type="button" 
                      class="btn btn-link p-0 text-decoration-none ver-detalles-btn"
                      data-usuario="${cuenta.nombre_usuario}"
                      title="Ver detalles">
                <i class="bi bi-eye"></i>
              </button>
              <button type="button" 
                      class="btn btn-link p-0 text-decoration-none ms-2 editar-cuenta-btn"
                      data-usuario="${cuenta.nombre_usuario}"
                      title="Editar">
                <i class="bi bi-pencil"></i>
              </button>
              ${
                !cuenta.email_verificado
                  ? `
              <button type="button" 
                      class="btn btn-link p-0 text-decoration-none ms-2 reenviar-verificacion-btn"
                      data-usuario="${cuenta.nombre_usuario}"
                      data-email="${cuenta.email}"
                      title="Reenviar verificación">
                <i class="bi bi-send"></i>
              </button>
              `
                  : ""
              }
              <form action="/cuentas/eliminar/${cuenta.nombre_usuario}" 
                    method="POST" 
                    style="display: inline"
                    class="ms-2"
                    onsubmit="return confirm('¿Estás seguro de eliminar la cuenta de ${
                      cuenta.nombre_usuario
                    }?');">
                <button type="submit" class="btn btn-link p-0 text-decoration-none" title="Eliminar">
                  <i class="bi bi-trash"></i>
                </button>
              </form>
            </td>
          </tr>
        `;
    });

    tbodyCuentas.innerHTML = html;

    // Re-asignar event listeners
    reassignEventListeners();
  }

  const modalCrear = document.getElementById("modalCrearOverlay");
  const modalEditar = document.getElementById("modalEditarOverlay");
  const modalDetalles = document.getElementById("modalDetallesOverlay");
  const modalReenviar = document.getElementById("modalReenviarOverlay");
  const detallesContenido = document.getElementById("detallesContenido");
  const formEditarUsuario = document.getElementById("formEditarUsuario");

  // Botones modales
  const openCrearBtn = document.getElementById("openCrearModalBtn");
  const closeCrearBtns = document.querySelectorAll(".close-crear-modal");
  const closeEditarBtns = document.querySelectorAll(".close-editar-modal");
  const closeDetallesBtns = document.querySelectorAll(".close-detalles-modal");
  const closeReenviarBtns = document.querySelectorAll(".close-reenviar-modal");

  // Funciones modales
  function openCrearModal() {
    modalCrear.classList.remove("d-none");
    document.body.style.overflow = "hidden";
    document.getElementById("formCrearUsuario")?.reset();
    // Limpiar mensajes de error
    document.querySelectorAll("#formCrearUsuario .alert").forEach((alert) => {
      alert.classList.add("d-none");
    });
  }

  function closeCrearModal() {
    modalCrear.classList.add("d-none");
    document.body.style.overflow = "";
  }

  function openEditarModal() {
    modalEditar.classList.remove("d-none");
    document.body.style.overflow = "hidden";
  }

  function closeEditarModal() {
    modalEditar.classList.add("d-none");
    document.body.style.overflow = "";
  }

  function openDetallesModal() {
    modalDetalles.classList.remove("d-none");
    document.body.style.overflow = "hidden";
  }

  function closeDetallesModal() {
    modalDetalles.classList.add("d-none");
    document.body.style.overflow = "";
    detallesContenido.innerHTML = `
        <div class="text-center">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Cargando...</span>
          </div>
          <p class="mt-2">Cargando detalles...</p>
        </div>
      `;
  }

  // Cargar datos en el modal de edición
  function cargarDatosEdicion(nombreUsuario) {
    fetch(`/cuentas/detalles-json/${nombreUsuario}`)
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          // Llenar el formulario con los datos
          document.getElementById("editarUsuario").value =
            data.cuenta.nombre_usuario;
          document.getElementById("editarUsuarioDisplay").value =
            data.cuenta.nombre_usuario;
          document.getElementById("editarNombre").value = data.cuenta.nombre;
          document.getElementById("editarApellido").value =
            data.cuenta.apellido;
          document.getElementById("editarEmail").value = data.cuenta.email;
          document.getElementById("editarRol").value =
            data.cuenta.rol.toLowerCase();

          // Guardar hash de contraseña anterior si está disponible
          if (data.cuenta.password_hash) {
            document.getElementById("passwordAnteriorHash").value =
              data.cuenta.password_hash;
          }

          // Limpiar campos de contraseña y mensajes de error
          document.getElementById("editarPassword").value = "";
          document.getElementById("editarPassword2").value = "";
          document.querySelectorAll(".alert").forEach((alert) => {
            alert.classList.add("d-none");
          });

          // Configurar el action del formulario
          formEditarUsuario.action = `/cuentas/editar/${data.cuenta.nombre_usuario}`;

          openEditarModal();
        }
      })
      .catch((error) => {
        console.error("Error cargando datos para edición:", error);
      });
  }

  window.abrirModalDetalles = function (nombreUsuario) {
    cargarDetallesUsuario(nombreUsuario);
    openDetallesModal();
  };

  function cargarDetallesUsuario(nombreUsuario) {
    fetch(`/cuentas/detalles-json/${nombreUsuario}`)
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
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
                    <tr>
                      <td><strong>Rol:</strong></td>
                      <td>
                        <span class="badge ${
                          data.cuenta.rol === "Administrador"
                            ? "bg-danger"
                            : "bg-secondary"
                        }">
                          ${data.cuenta.rol}
                        </span>
                      </td>
                    </tr>
                    <tr>
                      <td><strong>Email verificado:</strong></td>
                      <td>
                        <span class="badge ${
                          data.cuenta.email_verificado
                            ? "bg-success"
                            : "bg-warning"
                        }">
                          ${data.cuenta.email_verificado ? "Sí" : "No"}
                        </span>
                      </td>
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
              <div class="mt-3 p-3 bg-light rounded">
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <h6 class="mb-1">Email no verificado</h6>
                    <p class="mb-0 text-muted">El usuario no ha verificado su email aún.</p>
                  </div>
                  <button type="button" class="btn btn-outline-primary btn-sm" 
                          onclick="reenviarVerificacionEmail('${data.cuenta.nombre_usuario}', '${data.cuenta.email}')">
                    <i class="bi bi-send me-1"></i>Reenviar verificación
                  </button>
                </div>
              </div>
              `
                  : ""
              }
            `;
        } else {
          detallesContenido.innerHTML = `
              <div class="alert alert-danger">
                Error: ${data.error}
              </div>
            `;
        }
      })
      .catch((error) => {
        detallesContenido.innerHTML = `
            <div class="alert alert-danger">
              Error al cargar los detalles: ${error}
            </div>
          `;
      });
  }

  // Re-asignar event listeners
  function reassignEventListeners() {
    // Detalles
    document.querySelectorAll(".ver-detalles-btn").forEach((btn) => {
      btn.addEventListener("click", function () {
        const usuario = this.getAttribute("data-usuario");
        abrirModalDetalles(usuario);
      });
    });

    // Editar
    document.querySelectorAll(".editar-cuenta-btn").forEach((btn) => {
      btn.addEventListener("click", function () {
        const usuario = this.getAttribute("data-usuario");
        cargarDatosEdicion(usuario);
      });
    });

    // Reenviar verificación
    document.querySelectorAll(".reenviar-verificacion-btn").forEach((btn) => {
      btn.addEventListener("click", function () {
        const usuario = this.getAttribute("data-usuario");
        const email = this.getAttribute("data-email");
        reenviarVerificacionEmail(usuario, email);
      });
    });
  }

  // Event listeners iniciales
  openCrearBtn && openCrearBtn.addEventListener("click", openCrearModal);
  closeCrearBtns.forEach((btn) =>
    btn.addEventListener("click", closeCrearModal)
  );
  closeEditarBtns.forEach((btn) =>
    btn.addEventListener("click", closeEditarModal)
  );
  closeDetallesBtns.forEach((btn) =>
    btn.addEventListener("click", closeDetallesModal)
  );
  closeReenviarBtns.forEach((btn) =>
    btn.addEventListener("click", closeReenviarModal)
  );

  // Event listeners para botones iniciales
  reassignEventListeners();

  // Cerrar modales al hacer click fuera
  [modalCrear, modalEditar, modalDetalles, modalReenviar].forEach((modal) => {
    modal &&
      modal.addEventListener("click", function (e) {
        if (e.target === modal) {
          if (modal === modalCrear) closeCrearModal();
          if (modal === modalEditar) closeEditarModal();
          if (modal === modalDetalles) closeDetallesModal();
          if (modal === modalReenviar) closeReenviarModal();
        }
      });
  });

  // Cerrar con Esc
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      if (!modalCrear.classList.contains("d-none")) closeCrearModal();
      if (!modalEditar.classList.contains("d-none")) closeEditarModal();
      if (!modalDetalles.classList.contains("d-none")) closeDetallesModal();
      if (!modalReenviar.classList.contains("d-none")) closeReenviarModal();
    }
  });

  // Event listeners para búsqueda
  inputBusqueda.addEventListener("input", function () {
    const termino = this.value.trim();
    clearTimeout(timeoutBusqueda);

    timeoutBusqueda = setTimeout(() => {
      if (termino.length >= 2 || termino.length === 0) {
        realizarBusqueda(termino);
      }
    }, 300);
  });

  btnBuscar.addEventListener("click", function () {
    realizarBusqueda(inputBusqueda.value.trim());
  });

  inputBusqueda.addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
      e.preventDefault();
      realizarBusqueda(this.value.trim());
    }
  });
})();
