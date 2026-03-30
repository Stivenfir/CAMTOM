## CAMTOM Replacement (nuevo proveedor Integralaia)

Esta versión reorganiza el procesamiento para **mantener las tablas/conexiones de tracking TK** y cambiar el proveedor de extracción a la API de Integralaia.

### Nueva estructura

```text
src/camtom_replacement/
  api/app.py
  core/config.py
  db/sql_server.py
  repositories/tracking_repository.py
  providers/integralaia_provider.py
  services/extraction_service.py
```

### Endpoints usados del proveedor

- `POST /api/middleware/create-operation-from-mdw`
- `GET /api/mw/document-types`
- `PUT /api/mw/document-types/{document_code}/extraction-schema`
- `GET /api/mw/operations/{doc_impoid}/documents/extracted-data`

Base URL de referencia:
`https://dev-visado-api-abcrepecev.integralaia.com/docs`

### Variables de entorno

- `SQL_SERVER` (default `172.16.10.54\\DBABC21`)
- `SQL_DATABASE` (default `Repecev2005_H`)
- `SQL_USERNAME` (default `Repecev2005`)
- `SQL_PASSWORD` (default vacío)
- `PROVIDER_BASE_URL` (default `https://dev-visado-api-abcrepecev.integralaia.com`)
- `PROVIDER_API_KEY` (default vacío)
- `PROVIDER_TIMEOUT_SECONDS` (default `60`)

### Ejecución

```bash
uvicorn src.camtom_replacement.api.app:app --host 0.0.0.0 --port 8000
```

### Endpoint de procesamiento

```bash
curl -X POST "http://localhost:8000/api/v2/procesarfactura/{doc_impoid}"
```

Este flujo:
1. Consulta pendientes en `IA_IM_ProcesarFacturasIA`.
2. Marca inicio/fin/error en la misma tabla de tracking.
3. Crea operación en middleware del nuevo proveedor.
4. Consulta datos extraídos por `doc_impoid`.
