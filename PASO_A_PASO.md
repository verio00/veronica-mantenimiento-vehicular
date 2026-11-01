# Guía desde cero: Actividad 12 de Verónica

## Meta de la actividad

Crear y **desplegar** una aplicación de mantenimiento vehicular con **CREATE, READ, UPDATE y DELETE**, usando una **colección real en MongoDB Atlas**; entregar **URL pública de Streamlit, URL de GitHub y evidencias con capturas reales**. Es una solución propia diferente al inventario escolar de Jeferson.

## Paso 1. Preparar tus cuentas y tu computador

1. Instala **Python 3.11+**, **Git** y **Visual Studio Code**. En Windows, al instalar Python, marca *Add Python to PATH* si aparece.
2. Crea o inicia sesión en MongoDB Atlas (https://www.mongodb.com/cloud/atlas/register), GitHub (https://github.com) y Streamlit Community Cloud (https://share.streamlit.io).
3. Extrae el ZIP, abre en VS Code la carpeta `Veronica_S12_MantenimientoVehicular`, y abre `Terminal > New Terminal`.
4. Ejecuta `py --version` y `git --version` para confirmar las instalaciones.

## Paso 2. Crear MongoDB Atlas (base real)

1. MongoDB Atlas: **New Project** → escribe `S12-Veronica-Mantenimiento`.
2. **Create / Build a Database** → elige el plan **Free** si está disponible → clúster `ClusterVeronica` (o nombre disponible) → **Create**.
3. **Database Access**: crea un **usuario de base de datos** y guarda su contraseña de forma privada. Para un usuario dedicado, asigna `readWrite` **solo** en `mantenimiento_vehicular` (los permisos de administración no son necesarios). El inicio de sesión de Atlas y el usuario de base de datos son distintos.
4. **Network Access**: añade tu IP actual. Para Streamlit Cloud, posteriormente será necesario autorizar las direcciones de salida aplicables. Si para la demostración necesitas autorizar temporalmente `0.0.0.0/0`, comprende que abre el acceso desde cualquier IP y **usa solo credenciales robustas, mínimos permisos y datos ficticios**; revoca la regla si deja de ser necesaria.
5. En la página del clúster selecciona **Connect → Drivers → Python**. Copia tu URI `mongodb+srv://...` y reemplaza usuario y contraseña. Si tienen caracteres especiales, codifícalos para usar en la URI.
6. No es obligatorio crear manualmente la colección: PyMongo crea la base y la colección al insertar los primeros documentos. Si prefieres verlas antes en Atlas: **Browse Collections → Create Database** con base `mantenimiento_vehicular` y colección `mantenimientos`.

## Paso 3. Configuración y dependencias en VS Code

Con la terminal abierta **dentro de la carpeta del proyecto**, ejecuta línea por línea:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .streamlit\secrets.toml.example .streamlit\secrets.toml
```

Edita `.streamlit/secrets.toml` con los valores **reales** (estos son ejemplos, no contraseñas):

```toml
MONGO_URI = "mongodb+srv://TU_USUARIO:TU_PASSWORD@TU_HOST.mongodb.net/?retryWrites=true&w=majority"
MONGO_DB_NAME = "mantenimiento_vehicular"
ADMIN_PASSWORD = "COLOCA_UNA_CLAVE_DISTINTA_Y_SEGURA"
```

**Seguridad:** este archivo está excluido en `.gitignore`. Jamás compartas una captura de la URI o contraseñas.

## Paso 4. Encender la aplicación local

```powershell
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

Abre el enlace local que aparece, habitualmente `http://localhost:8501`. Si Atlas permite tu conexión y la URI es correcta, verás **Conectado a MongoDB Atlas**. Si falla, verifica *Network Access*, *Database Access*, URI y conectividad. Inicia sesión con `ADMIN_PASSWORD` (panel lateral).

## Paso 5. Crear datos de ejemplo y comprobar CRUD

1. **Datos de prueba** → **Cargar 6 registros**. Captura en Atlas la colección con `MAN-001` ... `MAN-006` (son ficticios).
2. **CREATE**: sección Registrar → código `MAN-999`, placa `PRU-999`, tipo `Motor`, prioridad `Alta`, costo `350`, descripción `Prueba de mantenimiento para actividad S12` → Guardar. Confirma que el total crece de 6 a 7.
3. **READ**: sección Consultar → buscar `MAN-999` y mostrar el registro. En Atlas, filtra por `{"codigo":"MAN-999"}`.
4. **UPDATE**: selecciona `MAN-999`, cambia Estado a `Finalizado` y guarda; en Atlas confirma la actualización.
5. **DELETE**: en la pestaña Eliminar, elige `MAN-999`, marca la casilla de confirmación y elimina. Comprueba en Atlas que el filtro `{"codigo":"MAN-999"}` no devuelve resultados y que la colección conserva los seis datos de prueba.
6. Toma capturas en cada fase ANTES de pasar a la siguiente, especialmente la actualización y la eliminación.

## Paso 6. Pruebas automatizadas opcionales

```powershell
.\.venv\Scripts\python.exe -m pip install pytest
.\.venv\Scripts\python.exe -m pytest -q
```

Estas pruebas verifican las reglas y las llamadas CRUD **sin conectarse a Atlas**. El CRUD real se valida manualmente con las capturas.

## Paso 7. Subir tu proyecto a GitHub (sin secretos)

1. Crea un repositorio nuevo y vacío llamado `veronica-mantenimiento-vehicular` en https://github.com/new. No agregues un README inicial porque el proyecto ya lo incluye.
2. En VS Code, abre una terminal en la carpeta del proyecto y ejecuta:

```powershell
git init
git add .
git status
git check-ignore -v .streamlit/secrets.toml
git commit -m "Actividad S12 mantenimiento vehicular CRUD MongoDB"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/veronica-mantenimiento-vehicular.git
git push -u origin main
```

Reemplaza `TU_USUARIO` con tu nombre de usuario real. El comando `git check-ignore` debería indicar que `secrets.toml` está ignorado. Si no aparece ignorado, detente antes de hacer el commit. Si Git pide identidad de autor, configúrala mediante `git config --global user.name "Tu Nombre"` y `git config --global user.email "tu-correo"`.

## Paso 8. Publicar en Streamlit Community Cloud

1. Abre https://share.streamlit.io y conecta tu cuenta de GitHub.
2. **Create app → Yup, I have an app** (si aparece) → elige repositorio `TU_USUARIO/veronica-mantenimiento-vehicular`, rama `main`, archivo `streamlit_app.py`.
3. En **Advanced settings → Secrets**, pega el contenido de `.streamlit/secrets.toml` (sin subir ese archivo a GitHub).
4. Elige un subdominio libre, por ejemplo `veronica-mantenimiento-s12` si está disponible, y selecciona **Deploy**.
5. Abre la **URL real** generada, verifica conexión, login administrador, consulta y todas las operaciones CRUD. No inventes la URL en el informe; cópiala de la aplicación publicada.

## Paso 9. Informe y evidencias

Completa el archivo `Plantilla_Informe_Veronica_S12_Mantenimiento.docx` incluido en la carpeta y usa `PLANTILLA_EVIDENCIAS.md` como guía de capturas. El informe se presenta con **URLs reales**, no enlaces de ejemplo.

## Respuestas rápidas a errores comunes

- `py no se reconoce`: instala/reinstala Python y habilita PATH, o usa `python` en lugar de `py`.
- `No module named streamlit`: instala `requirements.txt` usando **el Python de `.venv`** indicado arriba.
- `ServerSelectionTimeoutError`: comprueba la URI, acceso IP, usuario de BD y red; no envíes contraseñas.
- `Authentication failed`: contraseñas incorrectas o usuario sin permiso para la base.
- `E11000 duplicate key`: el código `MAN-999` ya existe; utiliza uno distinto o elimina el registro de prueba.
- `Access denied` en Streamlit: verifica que pegaste `ADMIN_PASSWORD` en **Advanced settings → Secrets** y no en GitHub.

## Documentación oficial

- MongoDB conexión a Atlas: https://www.mongodb.com/docs/atlas/driver-connection/
- Streamlit deploy: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
- Streamlit secrets: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management
