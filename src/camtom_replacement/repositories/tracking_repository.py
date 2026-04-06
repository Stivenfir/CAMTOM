from datetime import datetime
from typing import Any

from camtom_replacement.db.sql_server import SqlServerClient


class TrackingRepository:
    """Repositorio para mantener las mismas tablas de tracking (TK)."""

    def __init__(self, db: SqlServerClient) -> None:
        self.db = db

    def get_pending_documents(self, doc_impoid: int) -> list[tuple[Any, ...]]:
        query = """
            SELECT
                dbo.RutaDocumentosServer7(IA_IM_ProcesarFacturasIA.DocimpoID) + '\\' + IAPR_RutaFactura AS ruta_factura,
                IAPR_ProcesarFacturaID,
                IMDocumentosSoporteDo.BSDocsoprtedeclaimpoid
            FROM IA_IM_ProcesarFacturasIA
            INNER JOIN IMDocumentosSoporteDo
                ON IA_IM_ProcesarFacturasIA.IMDocumentosSoporteDoID = IMDocumentosSoporteDo.IMDocumentosSoporteDoID
            WHERE IA_IM_ProcesarFacturasIA.DocImpoID = ?
                AND IAPR_FacturaEnviadaProcesar = 1
                AND ISNULL(IAPR_Procesado, 0) = 0
        """

        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (doc_impoid,))
            rows = cursor.fetchall()
            cursor.close()
        return rows

    def mark_start(self, procesar_factura_id: int) -> None:
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE IA_IM_ProcesarFacturasIA
                SET IAPR_FechaInicioProcesamiento = ?
                WHERE IAPR_ProcesarFacturaID = ?
                """,
                (datetime.now(), procesar_factura_id),
            )
            conn.commit()
            cursor.close()

    def mark_success(self, procesar_factura_id: int) -> None:
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE IA_IM_ProcesarFacturasIA
                SET
                    IAPR_Procesado = 1,
                    IAPR_ErrorProcesamientoIA = 0,
                    IAPR_ErrorProcesamientoIACadena = '',
                    IAPR_FechaFinalizacionProcesamiento = ?
                WHERE IAPR_ProcesarFacturaID = ?
                """,
                (datetime.now(), procesar_factura_id),
            )
            conn.commit()
            cursor.close()

    def mark_error(self, procesar_factura_id: int, message: str) -> None:
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE IA_IM_ProcesarFacturasIA
                SET
                    IAPR_Procesado = 1,
                    IAPR_ErrorProcesamientoIA = 1,
                    IAPR_ErrorProcesamientoIACadena = ?,
                    IAPR_FechaFinalizacionProcesamiento = ?
                WHERE IAPR_ProcesarFacturaID = ?
                """,
                (message[:1000], datetime.now(), procesar_factura_id),
            )
            conn.commit()
            cursor.close()

    def build_operation_payload(
        self,
        doc_impoid: int,
        documents: list[tuple[str, int, int]],
    ) -> dict[str, Any]:
        return {
            "doc_impoid": str(doc_impoid),
            "do_number": str(doc_impoid),
            "operation_date": datetime.now().date().isoformat(),
            "client_name": "",
            "executive_name": "",
            "details": {
                "documents": [
                    {
                        "ruta_factura": ruta_factura,
                        "procesar_factura_id": procesar_factura_id,
                        "soporte_id": soporte_id,
                    }
                    for ruta_factura, procesar_factura_id, soporte_id in documents
                ]
            },
        }
