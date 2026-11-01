"""Pruebas de las 4 llamadas CRUD con una colección simulada (sin Atlas)."""
from datetime import date
from db_operations import registrar, consultar, actualizar, eliminar, cargar_demostracion
from domain import construir_mantenimiento


class Resultado:
    def __init__(self, matched_count=0, deleted_count=0, upserted_id=None):
        self.matched_count, self.deleted_count, self.upserted_id = matched_count, deleted_count, upserted_id


class Cursor:
    def __init__(self, docs): self.docs = docs
    def sort(self, field, direction):
        self.docs.sort(key=lambda x: x.get(field, "")); return self
    def limit(self, n): self.docs = self.docs[:n]; return self
    def __iter__(self): return iter(self.docs)


class FakeCollection:
    def __init__(self): self.docs = {}
    def insert_one(self, doc):
        self.docs[doc['codigo']] = dict(doc)
        return Resultado(upserted_id=doc['codigo'])
    def find(self, filtro, proyeccion):
        return Cursor([dict(v) for v in self.docs.values() if all(v.get(k)==x for k,x in filtro.items())])
    def update_one(self, filtro, op, upsert=False):
        code = filtro['codigo']
        if code in self.docs:
            if '$set' in op: self.docs[code].update(op['$set'])
            return Resultado(matched_count=1)
        if upsert:
            self.docs[code] = dict(op['$setOnInsert'])
            return Resultado(upserted_id=code)
        return Resultado()
    def delete_one(self, filtro):
        code = filtro['codigo']
        if code in self.docs:
            del self.docs[code]; return Resultado(deleted_count=1)
        return Resultado()


def test_crud_completo():
    col = FakeCollection()
    doc = construir_mantenimiento('MAN-099','ABC-123','Motor','Alta',date(2026,11,1),200,
                                  'Inspección preventiva')
    registrar(col, doc)
    assert consultar(col)[0]['codigo'] == 'MAN-099'
    assert actualizar(col,'MAN-099',{'estado':'Finalizado'}).matched_count == 1
    assert consultar(col)[0]['estado'] == 'Finalizado'
    assert eliminar(col,'MAN-099').deleted_count == 1
    assert consultar(col) == []


def test_carga_idempotente():
    col = FakeCollection()
    assert cargar_demostracion(col, date(2026,11,1)) == 6
    assert cargar_demostracion(col, date(2026,11,1)) == 0
    assert len(consultar(col)) == 6
