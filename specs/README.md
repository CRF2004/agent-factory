# Specs

These JSON Schemas are generated from the backend Pydantic models.

Regenerate with:

```bash
PYTHONPATH=backend python -m app.schemas.export_json_schemas
```

The Pydantic models are the implementation contract; the JSON Schemas are the portable validation and UI-generation contract.
