from datetime import date
import pytest
from domain import (construir_mantenimiento, normalizar_codigo, normalizar_placa,
                    soles_a_centimos, validar_actualizacion)
from db_operations import documentos_demostracion


def test_normalizar_codigo():
    assert normalizar_codigo(" man-009 ") == "MAN-009"
    with pytest.raises(ValueError):
        normalizar_codigo("PRU-001")


def test_placa():
    assert normalizar_placa(" abc-123 ") == "ABC-123"
    with pytest.raises(ValueError):
        normalizar_placa("!")


def test_dinero_centimos():
    assert soles_a_centimos("90.15") == 9015
    assert soles_a_centimos("2.505") == 251
    with pytest.raises(ValueError):
        soles_a_centimos(-3)


def test_crear_documento():
    result = construir_mantenimiento("MAN-077", "XYZ-123", "Motor", "Alta", date(2026, 11, 2), 150,
                                    "Inspeccionar el motor", "Central")
    assert result["codigo"] == "MAN-077"
    assert result["estado"] == "Pendiente"
    assert result["costo_centimos"] == 15000


def test_actualizacion():
    changes = validar_actualizacion("Finalizado", "Baja", "12.99", "Trabajo completo")
    assert changes["costo_centimos"] == 1299
    assert changes["estado"] == "Finalizado"


def test_ejemplos_unicos():
    docs = documentos_demostracion(date(2026,11,1))
    assert len(docs) == 6
    assert len({x["codigo"] for x in docs}) == 6
