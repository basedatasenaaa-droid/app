import flet as ft
import requests
from config import API_URL
import time  # para delay opcional si es necesario

def main(page: ft.Page):
    page.title = "Usuarios - Registro/Login"
    page.window_width = 500
    page.window_height = 800
    page.scroll = ft.ScrollMode.AUTO
    page.bgcolor = "#FFFFFF"

    forms = []

    def input_estilo(label):
        return ft.TextField(label=label, width=300, border_color="#39A900", focused_border_color="#39A900")

    # ---------- LOGIN ----------
    cedula_login = input_estilo("Cédula")
    contrasena_login = input_estilo("Contraseña")
    contrasena_login.password = True
    contrasena_login.can_reveal_password = True
    login_resultado = ft.Text("", color="#39A900")

    def iniciar_sesion(e):
        login_resultado.value = "Conectando..."
        page.update()
        try:
            resp = requests.post(f"{API_URL}/usuarios/login", data={
                "cedula": cedula_login.value,
                "contrasena": contrasena_login.value
            }, timeout=30)
            resp.raise_for_status()
        except requests.exceptions.RequestException as ex:
            login_resultado.value = f"Error de red: {ex}"
            page.update()
            return

        data = resp.json()
        if data.get("ok"):
            login_resultado.value = "Bienvenido"
            mostrar_info_usuario(data["usuario"])
        else:
            login_resultado.value = data.get("mensaje", "Credenciales inválidas")
        page.update()

    login_form = ft.Column(
        [
            ft.Text("Iniciar sesión", size=24, weight="bold", color="#39A900"),
            cedula_login,
            contrasena_login,
            ft.ElevatedButton("Ingresar", on_click=iniciar_sesion, bgcolor="#39A900", color="white"),
            ft.TextButton("Crear cuenta", on_click=lambda e: cambiar_vista(registro_form), style=ft.ButtonStyle(color="#39A900")),
            login_resultado
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        visible=True
    )

    # ---------- REGISTRO ----------
    nombre_reg = input_estilo("Nombre")
    cedula_reg = input_estilo("Cédula")
    telefono_reg = input_estilo("Teléfono")
    correo_reg = input_estilo("Correo electrónico")
    contrasena_reg = input_estilo("Contraseña")
    contrasena_reg.password = True
    contrasena_reg.can_reveal_password = True
    codigo_bici = input_estilo("Código de bicicleta")
    resultado_registro = ft.Text("", color="#39A900")

    ruta_foto_bici = ft.Text(visible=False)
    ruta_foto_usuario = ft.Text(visible=False)

    def seleccionar_foto_bici(e):
        file_picker_bici.pick_files(allow_multiple=False, allowed_extensions=["jpg", "jpeg", "png"])

    def seleccionar_foto_usuario(e):
        file_picker_usuario.pick_files(allow_multiple=False, allowed_extensions=["jpg", "jpeg", "png"])

    def archivo_bici_seleccionado(e: ft.FilePickerResultEvent):
        if e.files:
            ruta_foto_bici.value = e.files[0].path
            page.update()

    def archivo_usuario_seleccionado(e: ft.FilePickerResultEvent):
        if e.files:
            ruta_foto_usuario.value = e.files[0].path
            page.update()

    def registrar_usuario(e):
        resultado_registro.value = "Registrando..."
        page.update()

        files = {}
        if ruta_foto_bici.value:
            with open(ruta_foto_bici.value, "rb") as f:
                files["foto_bici"] = ("foto_bici.png", f.read(), "image/png")
        if ruta_foto_usuario.value:
            with open(ruta_foto_usuario.value, "rb") as f:
                files["foto_usuario"] = ("foto_usuario.png", f.read(), "image/png")

        data = {
            "nombre": nombre_reg.value,
            "cedula": cedula_reg.value,
            "telefono": telefono_reg.value,
            "correo": correo_reg.value,
            "contrasena": contrasena_reg.value,
            "codigo": codigo_bici.value
        }

        try:
            resp = requests.post(f"{API_URL}/usuarios/registro", data=data, files=files, timeout=30)
            resp.raise_for_status()
            resultado_registro.value = resp.json().get("mensaje", "Registro exitoso")
        except requests.exceptions.RequestException as ex:
            resultado_registro.value = f"Error de red: {ex}"
        except Exception as ex:
            resultado_registro.value = f"Error inesperado: {ex}"
        page.update()

    registro_form = ft.Column(
        [
            ft.Text("Registro de Usuario", size=24, weight="bold", color="#39A900"),
            nombre_reg, cedula_reg, telefono_reg, correo_reg, contrasena_reg, codigo_bici,
            ft.ElevatedButton("Seleccionar foto de bicicleta", on_click=seleccionar_foto_bici, bgcolor="#39A900", color="white"),
            ft.ElevatedButton("Seleccionar foto del usuario", on_click=seleccionar_foto_usuario, bgcolor="#39A900", color="white"),
            ft.ElevatedButton("Registrarse", on_click=registrar_usuario, bgcolor="#39A900", color="white"),
            ft.TextButton("Ya tengo cuenta", on_click=lambda e: cambiar_vista(login_form), style=ft.ButtonStyle(color="#39A900")),
            resultado_registro
        ],
        visible=False,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    # ---------- PERFIL ----------
    perfil_qr = ft.Image(width=200, height=200, fit=ft.ImageFit.CONTAIN, border_radius=10)
    perfil_foto_bici = ft.Image(width=200, height=200, fit=ft.ImageFit.CONTAIN, border_radius=10)
    perfil_foto_usuario = ft.Image(width=200, height=200, fit=ft.ImageFit.CONTAIN, border_radius=10)
    datos_usuario = ft.Text("", size=14, color="#39A900")

    def mostrar_info_usuario(user):
        datos_usuario.value = (
            f"Nombre: {user.get('nombre','')}\n"
            f"Cédula: {user.get('cedula','')}\n"
            f"Teléfono: {user.get('telefono','')}\n"
            f"Correo: {user.get('correo','')}\n"
            f"Código: {user.get('codigo','')}"
        )

        # Asignar base64 directamente (Flet soporta data URI)
        qr_src = user.get("qr_blob", "")
        bici_src = user.get("foto_bici_blob", "")
        usuario_src = user.get("foto_usuario_blob", "")

        perfil_qr.src = qr_src
        perfil_foto_bici.src = bici_src
        perfil_foto_usuario.src = usuario_src

        # Forzar actualización inmediata
       # Forzar renderizado múltiple con delay pequeño (funciona en .exe)
        perfil_qr.update()
        perfil_foto_bici.update()
        perfil_foto_usuario.update()
        page.update()

        time.sleep(0.5)  # Pequeño delay para que Flet procese los base64 grandes
        perfil_qr.update()
        perfil_foto_bici.update()
        perfil_foto_usuario.update()
        page.update()

        cambiar_vista(perfil)

    perfil = ft.Column(
        [
            ft.Text("Perfil de Usuario", size=24, weight="bold", color="#39A900"),
            datos_usuario,
            ft.Text("Código QR generado:", color="#39A900"),
            perfil_qr,
            ft.Text("Foto de la bicicleta:", color="#39A900"),
            perfil_foto_bici,
            ft.Text("Foto del usuario:", color="#39A900"),
            perfil_foto_usuario,
            ft.TextButton("Cerrar sesión", on_click=lambda e: cambiar_vista(login_form), style=ft.ButtonStyle(color="#39A900"))
        ],
        visible=False,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        scroll=ft.ScrollMode.AUTO
    )

    # ---------- FilePickers ----------
    file_picker_bici = ft.FilePicker(on_result=archivo_bici_seleccionado)
    file_picker_usuario = ft.FilePicker(on_result=archivo_usuario_seleccionado)
    page.overlay.extend([file_picker_bici, file_picker_usuario])

    # ---------- Cambio de vista ----------
    def cambiar_vista(vista):
        for f in forms:
            f.visible = False
        vista.visible = True
        page.update()

    forms.extend([login_form, registro_form, perfil])
    page.add(ft.Column([login_form, registro_form, perfil], expand=True))
    cambiar_vista(login_form)

if __name__ == "__main__":
    ft.app(main)