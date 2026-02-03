import os
import resend
from dotenv import load_dotenv

# Cargamos variables de entorno desde .env
load_dotenv()

# Configura tu API KEY en un archivo .env: RESEND_API_KEY=re_123...
resend.api_key = os.getenv("RESEND_API_KEY")

def send_notification(new_status, old_status):
    print(f"Enviando mail via Resend: El trámite cambió.")
    
    try:
        params = {
            "from": "Tramite Bot <onboarding@resend.dev>",
            "to": ["alejandro.gotravel@gmail.com"], 
            "subject": "⚠️ ¡Cambio de estado en tu trámite de Migraciones!",
            "html": f"""
                <h1>Actualización de Trámite</h1>
                <p>Se ha detectado un cambio en el portal de Migraciones.</p>
                <p><strong>Estado anterior:</strong> {old_status}</p>
                <p><strong>Estado actual:</strong> {new_status}</p>
                <hr>
                <p>Este es un aviso automático.</p>
            """,
        }
        email = resend.Emails.send(params)
        print(f"Email enviado con éxito. ID: {email['id']}")
    except Exception as e:
        print(f"Error al enviar el email: {str(e)}")
