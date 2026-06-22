import os
import imaplib
import email
import zipfile
import subprocess
from pathlib import Path
from datetime import datetime

from ..paths import repo_root, workspace_root

def check_and_apply_email_airdrops() -> dict:
    """Se conecta al buzón IMAP especificado en variables de entorno,
    busca correos con asunto '[flujo-airdrop]' de remitentes autorizados,
    descarga el archivo adjunto (que debe ser un ZIP de airdrop),
    lo extrae en _airdrop/ y ejecuta la validación y aplicación automática.
    """
    host = os.getenv("FLUJO_IMAP_HOST")
    user = os.getenv("FLUJO_IMAP_USER")
    password = os.getenv("FLUJO_IMAP_PASSWORD")
    sender_whitelist = os.getenv("FLUJO_IMAP_ALLOWED_SENDERS", "").lower().split(",")
    
    if not (host and user and password):
        return {"ok": False, "error": "Faltan variables de entorno IMAP (FLUJO_IMAP_HOST, FLUJO_IMAP_USER, FLUJO_IMAP_PASSWORD)."}
        
    try:
        # Conexión SSL
        mail = imaplib.IMAP4_SSL(host)
        mail.login(user, password)
        mail.select("inbox")
        
        # Buscar correos no leídos con el asunto específico
        status, response = mail.search(None, '(UNSEEN SUBJECT "[flujo-airdrop]")')
        if status != "OK":
            return {"ok": True, "processed": 0, "message": "No se encontraron correos nuevos."}
            
        email_ids = response[0].split()
        if not email_ids:
            return {"ok": True, "processed": 0, "message": "No hay correos pendientes."}
            
        processed_count = 0
        applied_airdrops = []
        
        for e_id in email_ids:
            status, data = mail.fetch(e_id, "(RFC822)")
            if status != "OK":
                continue
                
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)
            
            # Verificar remitente
            from_header = str(msg.get("From", "")).lower()
            authorized = False
            for sender in sender_whitelist:
                if sender.strip() and sender.strip() in from_header:
                    authorized = True
                    break
                    
            if not authorized:
                # Marcar como leído para no procesarlo de nuevo, o ignorar
                mail.store(e_id, "+FLAGS", "\\Seen")
                continue
                
            # Buscar adjuntos .zip
            for part in msg.walk():
                if part.get_content_maintype() == "multipart":
                    continue
                if part.get("Content-Disposition") is None:
                    continue
                    
                filename = part.get_filename()
                if filename and filename.lower().endswith(".zip"):
                    # Descargar el zip
                    zip_data = part.get_payload(decode=True)
                    
                    # Guardar temporalmente
                    temp_zip = Path(workspace_root()) / "temp_airdrop.zip"
                    temp_zip.write_bytes(zip_data)
                    
                    # Extraer en _airdrop/
                    airdrop_dir = Path(repo_root()) / "_airdrop"
                    airdrop_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Limpiar _airdrop antes de extraer
                    for f in airdrop_dir.glob("**/*"):
                        if f.is_file():
                            f.unlink()
                            
                    with zipfile.ZipFile(temp_zip, "r") as zip_ref:
                        zip_ref.extractall(airdrop_dir)
                        
                    try:
                        temp_zip.unlink()
                    except:
                        pass
                        
                    # Aplicar el airdrop usando el CLI mismo
                    cmd = [
                        "py", "-m", "flujo", "airdrop", "apply", 
                        "--allow-airdrop-engine", 
                        f"Auto-applied from email at {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                    ]
                    
                    res = subprocess.run(cmd, cwd=str(repo_root()), capture_output=True, text=True)
                    
                    # Marcar correo como leído
                    mail.store(e_id, "+FLAGS", "\\Seen")
                    processed_count += 1
                    applied_airdrops.append({
                        "filename": filename,
                        "success": res.returncode == 0,
                        "stdout": res.stdout,
                        "stderr": res.stderr
                    })
                    break # Solo un zip por correo
                    
        return {
            "ok": True,
            "processed": processed_count,
            "results": applied_airdrops
        }
        
    except Exception as e:
        return {"ok": False, "error": str(e)}
