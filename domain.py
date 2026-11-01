"""Reglas de validación independientes de Streamlit y MongoDB.

Actividad 12 - Tecnologías Emergentes | Caso académico con datos ficticios.
"""
from __future__ import annotations

import re
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

TIPOS = ("Cambio de aceite", "Revisión de frenos", "Neumáticos", "Motor", "Sistema eléctrico", "Inspección general", "Otro")
ESTADOS = ("Pendiente", "En proceso", "Finalizado")
PRIORIDADES = ("Baja", "Media", "Alta")


def normalizar_codigo(value: str) -> str:
    code = (value or "").strip().upper()
    if not re.fullmatch(r"MAN-[0-9]{3,5}", code):
        raise ValueError("El código debe tener el formato MAN-001 (3 a 5 dígitos).")
    return code


def normalizar_placa(value: str) -> str:
    placa = (value or "").strip().upper()
    if not re.fullmatch(r"[A-Z0-9-]{5,10}", placa):
        raise ValueError("La placa debe tener entre 5 y 10 caracteres (letras, números o guion).")
    return placa


def soles_a_centimos(value) -> int:
    try:
        cost = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError("El costo debe ser un número válido.") from None
    if not cost.is_finite() or cost < 0 or cost > Decimal("1000000"):
        raise ValueError("El costo debe estar entre S/ 0 y S/ 1 000 000.")
    return int((cost * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def construir_mantenimiento(codigo: str, placa: str, tipo: str, prioridad: str,
                            fecha_programada: date, costo, descripcion: str,
                            taller: str = "Por asignar") -> dict:
    if tipo not in TIPOS:
        raise ValueError("El tipo de mantenimiento no es válido.")
    if prioridad not in PRIORIDADES:
        raise ValueError("La prioridad no es válida.")
    if not isinstance(fecha_programada, date):
        raise ValueError("La fecha programada no es válida.")
    descripcion = (descripcion or "").strip()
    if not 8 <= len(descripcion) <= 400:
        raise ValueError("La descripción debe contener entre 8 y 400 caracteres.")
    taller = (taller or "").strip() or "Por asignar"
    if len(taller) > 100:
        raise ValueError("El taller puede tener hasta 100 caracteres.")
    now = datetime.now(timezone.utc)
    return {
        "codigo": normalizar_codigo(codigo),
        "placa": normalizar_placa(placa),
        "tipo": tipo,
        "prioridad": prioridad,
        "fecha_programada": fecha_programada.isoformat(),
        "costo_centimos": soles_a_centimos(costo),
        "descripcion": descripcion,
        "taller": taller,
        "estado": "Pendiente",
        "creado_en": now,
        "actualizado_en": now,
    }


def validar_actualizacion(estado: str, prioridad: str, costo, observacion: str) -> dict:
    if estado not in ESTADOS or prioridad not in PRIORIDADES:
        raise ValueError("Estado o prioridad no válidos.")
    observacion = (observacion or "").strip()
    if len(observacion) > 400:
        raise ValueError("La observación debe tener como máximo 400 caracteres.")
    return {
        "estado": estado,
        "prioridad": prioridad,
        "costo_centimos": soles_a_centimos(costo),
        "observacion": observacion,
        "actualizado_en": datetime.now(timezone.utc),
    }
