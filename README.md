## CAMTOM Replacement (nuevo proveedor Integralaia)

Proyecto reorganizado para mantener tablas/conexiones de tracking TK y cambiar proveedor de extracción.

## 1) Configuración rápida (lista para correr)

```bash
cp .env.example .env
# editar .env y poner PROVIDER_API_KEY real
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
- `PROVIDER_API_KEY=...` (obligatoria)
- `PROVIDER_TIMEOUT_SECONDS=60`
- `APP_HOST=0.0.0.0`
- `APP_PORT=8000`
- `APP_RELOAD=false`

## 3) Endpoints del servicio

- `GET /health`
- `GET /config-check`
- `POST /api/v2/procesarfactura/{doc_impoid}`

Ejemplo:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/config-check
curl -X POST "http://localhost:8000/api/v2/procesarfactura/123456"
```

## 4) Flujo funcional

1. Se consultan pendientes en `IA_IM_ProcesarFacturasIA`.
2. Se marca inicio de procesamiento.
3. Se llama `POST /api/middleware/create-operation-from-mdw`.
4. Se consulta extracción con `GET /api/mw/operations/{doc_impoid}/documents/extracted-data`.
5. Se marca éxito/error en la tabla de tracking.

## 5) Endpoints usados del proveedor

Base URL docs:
`https://dev-visado-api-abcrepecev.integralaia.com/docs`

- `POST /api/middleware/create-operation-from-mdw`
- `GET /api/mw/document-types`
- `PUT /api/mw/document-types/{document_code}/extraction-schema`
- `GET /api/mw/operations/{doc_impoid}/documents/extracted-data`
