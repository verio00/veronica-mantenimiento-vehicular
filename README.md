# Verónica | Sistema de Gestión de Mantenimiento Vehicular

**Actividad 12 · Curso Tecnologías Emergentes · Caso académico ficticio.**

Aplicación CRUD para gestionar mantenimientos de camiones, desarrollada con **Python, Streamlit, PyMongo y MongoDB Atlas**.

## Problemática

Los registros de mantenimiento en mensajes u hojas dispersas dificultan consultar los vehículos pendientes, el historial inmediato de cada incidencia y la actualización de los trabajos realizados.

## Solución

Se implementa una interfaz que permite **crear, leer, actualizar y eliminar** documentos de la colección `mantenimientos` en la base de datos `mantenimiento_vehicular` alojada en MongoDB Atlas. La consulta es pública; las operaciones de escritura requieren una contraseña definida como secreto.

### Operaciones

| Acción | Ejemplo | Operación PyMongo |
|---|---|---|
| CREATE | Registrar MAN-099 | `insert_one()` |
| READ | Buscar por placa/código y consultar | `find()` |
| UPDATE | Cambiar estado a Finalizado | `update_one()` + `$set` |
| DELETE | Eliminar MAN-099 (dato temporal) | `delete_one()` |

La carga de seis registros ficticios usa `update_one(..., upsert=True)` y no sobrescribe los existentes.

## Instalación local (Windows PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .streamlit\secrets.toml.example .streamlit\secrets.toml
```

Completa tu cadena de conexión real, `MONGO_DB_NAME` y una contraseña robusta en `.streamlit/secrets.toml` (excluido por `.gitignore`).

```powershell
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

Para comprobar el código puro y la integración simulada:

```powershell
.\.venv\Scripts\python.exe -m pip install pytest
.\.venv\Scripts\python.exe -m pytest -q
```

**Prueba real pendiente:** conectar a tu clúster y verificar los 4 cambios desde Streamlit y MongoDB Atlas. Las pruebas automáticas no conectan con una cuenta real.

## Despliegue

1. Crea un repositorio nuevo de GitHub para estos archivos; **jamás incluyas `secrets.toml`**.
2. Ve a Streamlit Community Cloud → Create app → selecciona el repositorio, rama `main` y archivo principal `streamlit_app.py`.
3. En **Advanced settings → Secrets**, pega tus secretos locales.
4. Publica y verifica la conexión y las operaciones CRUD con datos ficticios.

Lee `PASO_A_PASO.md` para una guía completa con instrucciones de Atlas, GitHub y capturas.

## Estructura

```
streamlit_app.py               # Interfaz Streamlit
 domain.py                    # Validaciones y documentos
 db_operations.py             # CRUD MongoDB
 requirements.txt             # Dependencias de despliegue
 .streamlit/secrets.toml.example
 .gitignore
 tests/                       # Pruebas automatizadas sin Atlas
 PASO_A_PASO.md               # Guía paso a paso
 PLANTILLA_EVIDENCIAS.md       # Lista de capturas para el informe
```

> **Datos personales:** no usar placas, nombres o historiales reales en la actividad ni publicar contraseñas.
