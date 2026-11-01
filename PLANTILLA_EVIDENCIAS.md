# Capturas de evidencia para el informe (todas deben ser reales)

| N.º | Pantalla | Qué debe observarse | Observación sugerida |
|---|---|---|---|
| 1 | MongoDB Atlas | Clúster creado y activo; censurar usuarios/IPs | “Clúster disponible para almacenar datos NoSQL.” |
| 2 | MongoDB Atlas Data Explorer | `mantenimiento_vehicular.mantenimientos`, seis documentos ficticios | “Los registros están almacenados en documentos.” |
| 3 | URL pública Streamlit | Mensaje de conexión y tabla con seis mantenimientos | “La consulta recupera información desde Atlas.” |
| 4 | CREATE en Streamlit | Registro `MAN-999` creado, total siete | “La aplicación permite insertar un documento.” |
| 5 | READ en Streamlit | Resultado filtrado `MAN-999` | “Se puede localizar el mantenimiento por código.” |
| 6 | UPDATE en Streamlit + Atlas | `MAN-999` en estado `Finalizado` | “El estado nuevo persiste en la base remota.” |
| 7 | DELETE en Streamlit | Confirmación de eliminación de `MAN-999` | “La aplicación eliminó exclusivamente el dato temporal.” |
| 8 | MongoDB Atlas Data Explorer | Filtro `{"codigo":"MAN-999"}` sin resultados | “Atlas confirma la eliminación del documento.” |
| 9 | GitHub y Streamlit | Repositorio propio y URL real de la app | “El código es público y la aplicación está desplegada.” |

**No** reutilices las capturas de Jeferson, ni incluyas contraseñas, URI completa o datos de vehículos reales.
