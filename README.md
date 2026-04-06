## CAMTOM Replacement (nuevo proveedor Integralaia)

Proyecto reorganizado para mantener tablas/conexiones de tracking TK y cambiar proveedor de extracción.

## 1) Configuración rápida (lista para correr)

```bash
cp .env.example .env
# editar .env (si tienes token, agrégalo en PROVIDER_API_KEY)
python -m venv .venv
source .venv/bin/activate   # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
./start_local.sh
```

También puedes correr con:

```bash
python run.py
```

## 2) Variables de entorno

Archivo `.env`:

- `SQL_SERVER=172.16.10.54\\DBABC21`
- `SQL_DATABASE=Repecev2005_H`
- `SQL_USERNAME=Repecev2005`
- `SQL_PASSWORD=`
- `PROVIDER_BASE_URL=https://dev-visado-api-abcrepecev.integralaia.com`
- `PROVIDER_API_KEY=...` (opcional)
- `PROVIDER_USE_DOC_HASH=false` (poner `true` para enviar `doc_impoid` + `hash` SHA256 en query string)
- `PROVIDER_TIMEOUT_SECONDS=60`
- `APP_HOST=0.0.0.0`
- `APP_PORT=8000`
- `APP_RELOAD=false`

## 3) Endpoints del servicio

- `GET /health`
- `GET /config-check`
- `POST /api/v2/procesarfactura/{doc_impoid}`
- `POST /api/v2/procesar-carpeta`

Ejemplo:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/config-check
curl -X POST "http://localhost:8000/api/v2/procesarfactura/123456"
curl -X POST "http://localhost:8000/api/v2/procesar-carpeta" \
  -H "Content-Type: application/json" \
  -d '{"doc_impoid":123456,"folder_path":"./facturas_inbox"}'
```

## 4) Flujo funcional

1. Se consultan pendientes en `IA_IM_ProcesarFacturasIA`.
2. Se marca inicio de procesamiento.
3. Se llama `POST /api/mw/operations` para crear/actualizar la operación con payload completo.
4. Se consulta extracción con `GET /api/mw/operations/{doc_impoid}/documents/extracted-data`.
5. Se marca éxito/error en la tabla de tracking.

### Prueba rápida con carpeta local

1. Crea (o usa) la carpeta `./facturas_inbox`.
2. Copia ahí una o más facturas (pdf, xlsx, etc.).
3. Ejecuta `POST /api/v2/procesar-carpeta` con `doc_impoid` y `folder_path`.
4. El servicio recorre todos los archivos de esa carpeta y devuelve el resultado de extracción por archivo.

### Autenticación / seguridad del middleware

- Por defecto, el servicio puede llamar sin token (no se bloquea startup si `PROVIDER_API_KEY` está vacío).
- Si defines `PROVIDER_API_KEY`, se envía `x-api-key: ...`.
- Si defines `PROVIDER_USE_DOC_HASH=true`, además se envían `doc_impoid` y `hash=SHA256(doc_impoid)` en query string (compatible con flujos legados tipo `GetCreateOperationUrl`).

## 5) Endpoints usados del proveedor

Base URL docs:
`https://dev-visado-api-abcrepecev.integralaia.com/docs`

- `POST /api/mw/operations`
- `GET /api/mw/document-types`
- `PUT /api/mw/document-types/{document_code}/extraction-schema`
- `GET /api/mw/operations/{doc_impoid}/documents/extracted-data`
