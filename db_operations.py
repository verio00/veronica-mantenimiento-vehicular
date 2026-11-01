"""Operaciones CRUD sobre una colección PyMongo; testeables con dobles de prueba."""
from datetime import date, timedelta
from domain import construir_mantenimiento


def preparar_indices(coleccion):
    coleccion.create_index("codigo", unique=True)
    coleccion.create_index("placa")
    coleccion.create_index("estado")


def registrar(coleccion, documento):
    return coleccion.insert_one(documento)


def consultar(coleccion, filtro=None):
    return list(coleccion.find(filtro or {}, {"_id": 0}).sort("codigo", 1).limit(500))


def actualizar(coleccion, codigo, campos):
    # El código es un identificador inmutable; solo actualizamos campos permitidos.
    return coleccion.update_one({"codigo": codigo}, {"$set": campos})


def eliminar(coleccion, codigo):
    return coleccion.delete_one({"codigo": codigo})


def documentos_demostracion(hoy=None):
    hoy = hoy or date.today()
    ejemplos = [
        ("MAN-001", "ABC-123", "Cambio de aceite", "Media", -7, "Cambio preventivo de aceite y filtros", "Taller Central", 230),
        ("MAN-002", "DEF-456", "Revisión de frenos", "Alta", -3, "Revisión por ruidos al frenar", "Taller Los Olivos", 390),
        ("MAN-003", "GHI-789", "Neumáticos", "Media", 2, "Inspección y rotación de neumáticos", "Taller Central", 180),
        ("MAN-004", "JKL-234", "Sistema eléctrico", "Alta", 4, "Diagnóstico de luces intermitentes", "Taller Norte", 150),
        ("MAN-005", "MNO-567", "Inspección general", "Baja", 8, "Evaluación preventiva del camión", "Por asignar", 120),
        ("MAN-006", "PQR-890", "Motor", "Alta", 10, "Evaluación de vibraciones del motor", "Taller Central", 750),
    ]
    return [construir_mantenimiento(codigo, placa, tipo, prioridad, hoy + timedelta(days=offset),
                                   costo, descripcion, taller)
            for codigo, placa, tipo, prioridad, offset, descripcion, taller, costo in ejemplos]


def cargar_demostracion(coleccion, hoy=None):
    """No duplica documentos: solo inserta códigos de ejemplo ausentes."""
    nuevos = 0
    for doc in documentos_demostracion(hoy):
        result = coleccion.update_one({"codigo": doc["codigo"]}, {"$setOnInsert": doc}, upsert=True)
        if result.upserted_id is not None:
            nuevos += 1
    return nuevos
