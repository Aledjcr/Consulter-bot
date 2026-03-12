import os
import resend
from dotenv import load_dotenv

# Cargamos variables de entorno desde .env
load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")

USER_EMAIL = os.getenv("USER_EMAIL", "alejandro.gotravel@gmail.com")

def send_notification(new_status, old_status):
    print(f"Enviando mail via Resend: El trámite cambió.")
    
    # Extraemos el "último paso" si es posible para el asunto
    short_status = new_status.split("|")[-1].strip() if "|" in new_status else new_status[:50]
    
    try:
        params = {
            "from": "Migraciones Bot <onboarding@resend.dev>",
            "to": [USER_EMAIL], 
            "subject": f"🔔 Actualización: {short_status}",
            "html": f"""
                <div style="font-family: sans-serif; color: #333; max-width: 600px; border: 1px solid #eee; padding: 20px; border-radius: 10px;">
                    <h2 style="color: #2c3e50;">🚀 Actualización de Trámite</h2>
                    <p>Se ha detectado un cambio real en el portal de Migraciones.</p>
                    
                    <div style="background-color: #f8f9fa; padding: 15px; border-left: 5px solid #e9ecef; margin-bottom: 10px;">
                        <strong style="color: #6c757d;">Estado anterior:</strong><br>
                        <span style="color: #495057;">{old_status}</span>
                    </div>
                    
                    <div style="background-color: #e7f3ff; padding: 15px; border-left: 5px solid #007bff; margin-bottom: 20px;">
                        <strong style="color: #0056b3;">Nuevo estado:</strong><br>
                        <span style="color: #003d82; font-weight: bold;">{new_status}</span>
                    </div>
                    
                    <hr style="border: 0; border-top: 1px solid #eee;">
                    <p style="font-size: 12px; color: #999;">Este es un aviso automático generado por tu Bot de Consulta.</p>
                </div>
            """,
        }
        email = resend.Emails.send(params)
        print(f"Email enviado con éxito. ID: {email['id']}")
    except Exception as e:
        print(f"Error al enviar el email: {str(e)}")
