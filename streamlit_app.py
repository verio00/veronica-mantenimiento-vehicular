"""Sistema de gestión de mantenimiento vehicular - Verónica | Actividad 12.

CRUD real con MongoDB Atlas, Python, PyMongo y Streamlit.
"""
from __future__ import annotations

import hmac
import os
from datetime import date
from decimal import Decimal

import pandas as pd
import streamlit as st
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError

from db_operations import (actualizar, cargar_demostracion, consultar, eliminar,
                           preparar_indices, registrar)
from domain import (ESTADOS, PRIORIDADES, TIPOS, construir_mantenimiento,
                    validar_actualizacion)

st.set_page_config(page_title="Verónica | Mantenimiento Vehicular", page_icon="🚚", layout="wide")


def secreto(key: str) -> str:
    try:
        return str(st.secrets.get(key, os.environ.get(key, ""))).strip()
    except (FileNotFoundError, KeyError):
        return os.environ.get(key, "").strip()


@st.cache_resource(show_spinner=False)
def cliente_mongo(uri: str):
    client = MongoClient(uri, serverSelectionTimeoutMS=12000, connectTimeoutMS=12000)
    client.admin.command("ping")
    return client


def notificacion():
    message = st.session_state.pop("aviso", None)
    if message:
        st.success(message)


def tras_guardar(message: str):
    st.session_state["aviso"] = message
    st.rerun()


def control_acceso():
    clave_correcta = secreto("ADMIN_PASSWORD")
    with st.sidebar:
        st.title("🔐 Panel de acceso")
        if not clave_correcta:
            st.warning("Falta ADMIN_PASSWORD en los secretos. CRUD de escritura deshabilitado.")
            return False
        if st.session_state.get("es_admin"):
            st.success("Modo administrador")
            if st.button("Cerrar sesión", use_container_width=True):
                st.session_state["es_admin"] = False
                st.rerun()
            return True
        with st.form("acceso"):
            clave = st.text_input("Contraseña de administración", type="password")
            entrar = st.form_submit_button("Ingresar", use_container_width=True)
        if entrar:
            if hmac.compare_digest(clave, clave_correcta):
                st.session_state["es_admin"] = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta")
        st.info("La consulta es pública. Crear, editar y eliminar requieren la clave del administrador.")
        return False


def tabla(df):
    if df.empty:
        st.info("No hay registros que coincidan con los filtros.")
        return
    st.dataframe(df, use_container_width=True, hide_index=True)


def vista_consultar(registros):
    st.subheader("🔎 Consultar mantenimientos · READ")
    c1, c2, c3 = st.columns(3)
    busqueda = c1.text_input("Buscar por código, placa o mantenimiento", placeholder="MAN-001 o ABC-123")
    filtro_estado = c2.selectbox("Filtrar por estado", ["Todos", *ESTADOS])
    filtro_prioridad = c3.selectbox("Filtrar por prioridad", ["Todas", *PRIORIDADES])
    filtrados = [r for r in registros
                 if (not busqueda or busqueda.lower() in " ".join(str(r.get(k, "")) for k in
                     ("codigo", "placa", "tipo", "descripcion")).lower())
                 and (filtro_estado == "Todos" or r.get("estado") == filtro_estado)
                 and (filtro_prioridad == "Todas" or r.get("prioridad") == filtro_prioridad)]
    rows = []
    for r in filtrados:
        rows.append({
            "Código": r.get("codigo", ""),
            "Placa": r.get("placa", ""),
            "Tipo": r.get("tipo", ""),
            "Prioridad": r.get("prioridad", ""),
            "Estado": r.get("estado", ""),
            "Fecha programada": r.get("fecha_programada", ""),
            "Costo estimado (S/)": f'{r.get("costo_centimos", 0) / 100:,.2f}',
            "Taller": r.get("taller", ""),
        })
    st.caption(f"{len(filtrados)} de {len(registros)} mantenimientos visibles")
    tabla(pd.DataFrame(rows))
    if filtrados:
        with st.expander("Ver descripción y observaciones"):
            for r in filtrados:
                st.write(f'**{r["codigo"]} · {r["placa"]}** — {r.get("descripcion", "")}')
                if r.get("observacion"):
                    st.caption("Seguimiento: " + r["observacion"])


def vista_registrar(col, admin):
    st.subheader("➕ Registrar mantenimiento · CREATE")
    if not admin:
        st.info("Ingresa como administrador desde la barra lateral para registrar.")
        return
    with st.form("crear", clear_on_submit=False):
        c1, c2 = st.columns(2)
        codigo = c1.text_input("Código único *", placeholder="MAN-007")
        placa = c2.text_input("Placa del vehículo *", placeholder="ABC-123")
        tipo = c1.selectbox("Tipo de mantenimiento *", TIPOS)
        prioridad = c2.selectbox("Prioridad *", PRIORIDADES, index=1)
        fecha = c1.date_input("Fecha programada *", value=date.today())
        costo = c2.number_input("Costo estimado (S/) *", min_value=0.0, max_value=1000000.0, value=150.0, step=10.0)
        taller = st.text_input("Taller responsable", value="Por asignar")
        descripcion = st.text_area("Descripción del problema o mantenimiento *", max_chars=400)
        enviado = st.form_submit_button("Guardar mantenimiento", type="primary")
    if enviado:
        try:
            doc = construir_mantenimiento(codigo, placa, tipo, prioridad, fecha, costo, descripcion, taller)
            registrar(col, doc)
            tras_guardar(f"Mantenimiento {doc['codigo']} registrado en MongoDB Atlas.")
        except ValueError as exc:
            st.error(str(exc))
        except DuplicateKeyError:
            st.error("Ese código ya existe. Utiliza un código diferente.")
        except PyMongoError:
            st.error("No fue posible guardar el registro. Revisa la conexión y permisos de Atlas.")


def vista_actualizar(col, registros, admin):
    st.subheader("✏️ Actualizar mantenimiento · UPDATE")
    if not admin:
        st.info("Ingresa como administrador desde la barra lateral para modificar.")
        return
    if not registros:
        st.info("Primero registra o carga mantenimientos de demostración.")
        return
    codigos = [r["codigo"] for r in registros]
    codigo = st.selectbox("Selecciona el código", codigos, key="codigo_actualizar")
    doc = next(r for r in registros if r["codigo"] == codigo)
    with st.form("editar"):
        c1, c2, c3 = st.columns(3)
        estado = c1.selectbox("Estado", ESTADOS, index=ESTADOS.index(doc.get("estado", "Pendiente")))
        prioridad = c2.selectbox("Prioridad", PRIORIDADES, index=PRIORIDADES.index(doc.get("prioridad", "Media")))
        costo = c3.number_input("Costo estimado (S/)", min_value=0.0, max_value=1000000.0,
                                 value=float(Decimal(doc.get("costo_centimos", 0)) / 100), step=10.0)
        observacion = st.text_area("Observación de seguimiento", value=doc.get("observacion", ""), max_chars=400)
        enviado = st.form_submit_button("Guardar actualización", type="primary")
    if enviado:
        try:
            campos = validar_actualizacion(estado, prioridad, costo, observacion)
            resultado = actualizar(col, codigo, campos)
            if resultado.matched_count:
                tras_guardar(f"Mantenimiento {codigo} actualizado en MongoDB Atlas.")
            else:
                st.warning("No se encontró el documento; pudo haber sido eliminado.")
        except ValueError as exc:
            st.error(str(exc))
        except PyMongoError:
            st.error("No se pudo actualizar el mantenimiento.")


def vista_eliminar(col, registros, admin):
    st.subheader("🗑️ Eliminar mantenimiento · DELETE")
    if not admin:
        st.info("Ingresa como administrador desde la barra lateral para eliminar.")
        return
    if not registros:
        st.info("No hay mantenimientos que eliminar.")
        return
    with st.form("eliminar"):
        codigo = st.selectbox("Código que deseas eliminar", [r["codigo"] for r in registros])
        comprobacion = st.checkbox("Confirmo que quiero eliminar este registro de demostración")
        enviado = st.form_submit_button("Eliminar definitivamente")
    if enviado:
        if not comprobacion:
            st.warning("Debes marcar la casilla de confirmación.")
            return
        try:
            resultado = eliminar(col, codigo)
            if resultado.deleted_count:
                tras_guardar(f"Mantenimiento {codigo} eliminado de MongoDB Atlas.")
            else:
                st.warning("El documento ya no existía.")
        except PyMongoError:
            st.error("No se pudo eliminar el mantenimiento.")


def vista_datos(col, admin):
    st.subheader("🧪 Datos ficticios de demostración")
    st.write("Carga seis mantenimientos de ejemplo con códigos MAN-001 a MAN-006. Si los códigos ya existen, no se duplican ni se sobrescriben.")
    if not admin:
        st.info("Inicia sesión como administrador para cargar los ejemplos.")
        return
    if st.button("Cargar 6 registros de ejemplo", type="primary"):
        try:
            nuevos = cargar_demostracion(col)
            tras_guardar(f"Carga completada: {nuevos} registros nuevos en Atlas.")
        except PyMongoError:
            st.error("No se pudieron crear los documentos. Comprueba permisos e índices únicos.")


def main():
    st.title("🚚 Verónica | Gestión de Mantenimiento Vehicular")
    st.caption("Actividad 12 · Tecnologías Emergentes · Python + Streamlit + MongoDB Atlas")
    admin = control_acceso()
    uri, nombre_bd = secreto("MONGO_URI"), secreto("MONGO_DB_NAME") or "mantenimiento_vehicular"
    if not uri:
        st.error("No se ha configurado MONGO_URI. Sigue las instrucciones de PASO_A_PASO.md.")
        st.stop()
    try:
        client = cliente_mongo(uri)
        col = client[nombre_bd]["mantenimientos"]
        preparar_indices(col)
        registros = consultar(col)
    except PyMongoError:
        st.error("No se pudo conectar a MongoDB Atlas. Comprueba la URI, el usuario, la contraseña y Network Access.")
        st.stop()

    st.success(f"Conectado a MongoDB Atlas · BD: {nombre_bd} · Colección: mantenimientos")
    notificacion()
    total = len(registros)
    pendientes = sum(r.get("estado") == "Pendiente" for r in registros)
    proceso = sum(r.get("estado") == "En proceso" for r in registros)
    terminados = sum(r.get("estado") == "Finalizado" for r in registros)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total", total)
    c2.metric("Pendientes", pendientes)
    c3.metric("En proceso", proceso)
    c4.metric("Finalizados", terminados)

    t1, t2, t3, t4, t5 = st.tabs(["🔎 Consultar", "➕ Registrar", "✏️ Actualizar", "🗑️ Eliminar", "🧪 Datos de prueba"])
    with t1:
        vista_consultar(registros)
    with t2:
        vista_registrar(col, admin)
    with t3:
        vista_actualizar(col, registros, admin)
    with t4:
        vista_eliminar(col, registros, admin)
    with t5:
        vista_datos(col, admin)
    st.divider()
    st.caption("Proyecto académico · Datos ficticios · Los cambios se almacenan en MongoDB Atlas")


if __name__ == "__main__":
    main()
