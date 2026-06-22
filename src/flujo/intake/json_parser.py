import json
import yaml
from pathlib import Path
from typing import Optional
from jsonschema import validate as json_validate

from ..paths import repo_root, workspace_root
from ..jobs.job import create_job

def load_intake_schema() -> dict:
    schema_path = repo_root() / "schemas" / "intake.schema.json"
    if not schema_path.exists():
        raise FileNotFoundError(f"No se encontró el esquema en: {schema_path}")
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)

def process_json_intake(json_path: Path) -> dict:
    """Valida un archivo JSON de intake y crea un job a partir de él."""
    json_path = Path(json_path)
    if not json_path.exists():
        return {"ok": False, "error": f"El archivo no existe: {json_path}"}
        
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return {"ok": False, "error": f"Error leyendo JSON: {e}"}
        
    # Validar contra el esquema
    try:
        schema = load_intake_schema()
        json_validate(instance=data, schema=schema)
    except Exception as e:
        return {"ok": False, "error": f"Validación de esquema falló: {e}"}
        
    pedido = data.get("pedido", {})
    contenido = pedido.get("contenido", {})
    titulo = contenido.get("titulo", "Pedido Sin Titulo")
    
    # Crear el job
    try:
        job_dir = create_job(name=titulo, source_path=json_path)
    except Exception as e:
        return {"ok": False, "error": f"No se pudo crear el job: {e}"}
        
    # Poblar brief.yaml
    brief_path = job_dir / "brief.yaml"
    if brief_path.exists():
        try:
            with open(brief_path, "r", encoding="utf-8") as f:
                brief = yaml.safe_load(f) or {}
                
            # Actualizar campos
            brief["origen"] = "json_intake"
            brief["cliente"] = pedido.get("solicitante", {}).get("nombre", "")
            brief["tipo_pieza"] = pedido.get("tipo_pieza", "")
            
            medidas = pedido.get("medidas", {})
            if "medidas" not in brief or brief["medidas"] is None:
                brief["medidas"] = {}
            brief["medidas"]["ancho_cm"] = medidas.get("ancho_cm")
            brief["medidas"]["alto_cm"] = medidas.get("alto_cm")
            brief["medidas"]["orientacion"] = medidas.get("orientacion")
            brief["medidas"]["sangrado_mm"] = medidas.get("sangrado_mm")
            brief["medidas"]["area_segura_mm"] = medidas.get("area_segura_mm")
            
            entrega = pedido.get("entrega", {})
            if "entrega" not in brief or brief["entrega"] is None:
                brief["entrega"] = {}
            formats = entrega.get("formatos", [])
            brief["entrega"]["editable_svg"] = "editable_svg" in formats
            brief["entrega"]["vectorizado_svg"] = "vectorizado_svg" in formats
            brief["entrega"]["pdf_impresion"] = "pdf_impresion" in formats
            brief["entrega"]["zip"] = "zip" in formats
            
            brief["productos"] = pedido.get("productos", [])
            
            if "contenido" not in brief or brief["contenido"] is None:
                brief["contenido"] = {}
            brief["contenido"]["titulo"] = contenido.get("titulo", "")
            brief["contenido"]["subtitulo"] = contenido.get("subtitulo", "")
            brief["contenido"]["cuerpo"] = contenido.get("cuerpo", "")
            brief["contenido"]["llamado_action"] = contenido.get("llamado_accion", "")
            brief["contenido"]["notas"] = pedido.get("notas", "")
            
            restricciones = pedido.get("restricciones", {})
            if "restricciones" not in brief or brief["restricciones"] is None:
                brief["restricciones"] = {}
            brief["restricciones"]["no_inventar_claims"] = restricciones.get("no_inventar_claims", True)
            brief["restricciones"]["texto_vectorizado"] = restricciones.get("texto_vectorizado", True)
            brief["restricciones"]["editable_para_illustrator"] = restricciones.get("editable_para_illustrator", True)
            
            # Guardar de nuevo
            with open(brief_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(brief, f, allow_unicode=True, default_flow_style=False)
                
        except Exception as e:
            return {"ok": True, "job_dir": str(job_dir), "warning": f"Job creado pero falló actualizar brief.yaml: {e}"}
            
    return {"ok": True, "job_dir": str(job_dir)}
