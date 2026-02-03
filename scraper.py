import asyncio
import json
import os
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from datetime import datetime

# Configuración
# Cargamos desde .env (local) o Secrets (GitHub)
from dotenv import load_dotenv
load_dotenv()

URL = "https://www.migraciones.gob.ar/accesible/consultaTramiteCiudadania/ConsultaCiudadania.php"
ID_TRAMITE = os.getenv("ID_TRAMITE")
FECHA_NAC = os.getenv("FECHA_NAC")

if not ID_TRAMITE or not FECHA_NAC:
    # Error fatal si no hay credenciales, para no procesar datos vacíos o erróneos
    raise ValueError("ERROR: ID_TRAMITE o FECHA_NAC no encontrados. Asegúrate de configurar el archivo .env")


# Rutas absolutas para evitar problemas en diferentes entornos (ej: GitHub Actions)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, "state.json")

async def check_status():
    async with async_playwright() as p:
        # Argumentos para pasar bajo el radar
        args = [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage"  # Necesario para VMs con poca memoria /dev/shm
        ]
        
        try:
            # En Linux/Ubuntu VM, es más seguro no forzar 'channel="chrome"' 
            # ya que suele usarse el chromium base de playwright
            if os.name == 'nt': # Solo en Windows intentamos Chrome real
                browser = await p.chromium.launch(headless=True, channel="chrome", args=args)
            else:
                browser = await p.chromium.launch(headless=True, args=args)
        except Exception as e:
            print(f"Intento de inicio fallido ({e}), usando Chromium base...")
            browser = await p.chromium.launch(headless=True, args=args)
            
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 720},
            extra_http_headers={"Referer": "https://www.migraciones.gob.ar/"}
        )
        page = await context.new_page()
        
        # Aplicar Stealth (API v2.0.1)
        stealth_enforcer = Stealth()
        await stealth_enforcer.apply_stealth_async(page)
        
        print(f"[{datetime.now()}] Navegando a {URL} (Stealth Mode Ultra)...")
        try:
            # Usamos 'load' en lugar de 'networkidle' para evitar esperas interminables si hay analytics
            response = await page.goto(URL, wait_until="load", timeout=60000)
            
            if response:
                print(f"Respuesta recibida. Status: {response.status}")
                # print(f"Headers: {dict(response.headers)}")
            else:
                print("No se recibió respuesta del servidor.")
            
            # Espera generosa para que el JS termine de renderizar el form
            await page.wait_for_timeout(7000)
        except Exception as e:
            await browser.close()
            return f"Error de conexión: {e}"
        
        # DEBUG: Tomar captura y ver HTML
        await page.screenshot(path="debug_page.png")
        html_content = await page.content()
        title = await page.title()
        print(f"Título de la página: {title}")
        
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        
        # Si la página está vacía, intentamos recargar una vez
        if len(html_content) < 100:
            print(f"Página detectada como sospechosamente pequeña ({len(html_content)} bytes). Snippet: {html_content[:50]}")
            print("Reintentando recarga con espera 'load'...")
            await page.reload(wait_until="load")
            await page.wait_for_timeout(5000)
            html_content = await page.content()
            print(f"Nueva longitud tras reintento: {len(html_content)}")

        if "no puede ser mostrada" in html_content or "disculpe las molestias" in html_content or "404 - Error" in html_content:
            await browser.close()
            return f"Error: El portal tiene problemas de conexión o bloqueo (HTML detectado: {'Bloqueo/WAF' if 'mostrada' in html_content else '404/No encontrado'})."

        print("Captura de depuración guardada como debug_page.png. Analizando contenido...")

        # Llenar el formulario
        print("Buscando campos en todos los frames...")
        try:
            # A veces la web carga pero tarda en mostrar el form
            await page.wait_for_timeout(5000) 
            
            target_frame = None
            # Buscamos en todos los frames
            all_frames = page.frames
            print(f"Frames detectados: {len(all_frames)}")
            
            for frame in all_frames:
                try:
                    # Buscamos campos con nombres comunes en este portal
                    # El portal accesible suele usar nombres de campos muy simples
                    exists = await frame.query_selector("input")
                    if exists:
                        target_frame = frame
                        print(f"¡Frame con inputs encontrado: {frame.name or 'principal'}!")
                        break
                except:
                    continue

            if not target_frame:
                target_frame = page

            # Esperamos específicamente a que aparezcan inputs con mucho más tiempo
            print("Esperando a que el formulario sea visible...")
            try:
                await target_frame.wait_for_selector("input", timeout=30000)
            except Exception as e:
                # Si falla, tomamos captura para ver qué hay en lugar del form
                await page.screenshot(path="debug_timeout_inputs.png")
                html_snippet = (await page.content())[:200]
                return f"Error: No se encontraron campos de entrada tras 30s. Contenido: {html_snippet}..."
            
            # Listar inputs encontrados para ayudar al usuario si falla
            inputs = await target_frame.query_selector_all("input")
            for inp in inputs:
                name = await inp.get_attribute("name")
                idd = await inp.get_attribute("id")
                print(f"Input detectado: name={name}, id={idd}")

            # Llenar datos usando los IDs encontrados
            print(f"Llenando trámite: {ID_TRAMITE}")
            # Intentamos varios selectores para el trámite
            for sel in ["#id_orden", "input[name*='tramite']", "input[id*='orden']"]:
                if await target_frame.query_selector(sel):
                    await target_frame.fill(sel, ID_TRAMITE)
                    break
            
            # Dividir fecha y probar tanto campos individuales como el campo único
            dia, mes, anio = FECHA_NAC.split("/")
            print(f"Llenando fecha: {FECHA_NAC}")
            
            fill_success = False
            if await target_frame.query_selector("#dia"):
                await target_frame.fill("#dia", dia)
                await target_frame.fill("#mes", mes)
                await target_frame.fill("#anio", anio)
                fill_success = True
            
            # Intentar también el campo de fecha completa SOLO si es visible y no llenamos los otros
            if not fill_success:
                for sel in ["#fecha_nacimiento", "input[name*='fecha']"]:
                    field = await target_frame.query_selector(sel)
                    if field and await field.is_visible():
                        # Usamos evaluate para forzar el valor si es readonly
                        await target_frame.evaluate("(args) => { document.querySelector(args.sel).value = args.val; }", {"sel": sel, "val": FECHA_NAC})
                        fill_success = True
                        break

            # Listar botones para debug
            buttons = await target_frame.query_selector_all("input[type='submit'], button, input[type='button']")
            for btn in buttons:
                val = await btn.get_attribute("value") or await btn.inner_text()
                idd = await btn.get_attribute("id")
                print(f"Botón detectado: id={idd}, valor/texto={val}")

            # Tomar captura después de llenar para ver si todo está ok
            await page.screenshot(path="debug_after_fill.png")
            print("Captura 'debug_after_fill.png' guardada.")

            print("Enviando formulario...")
            # Click en consultar - Probamos varios selectores de botones comunes
            submit_selectors = [
                "#buscar_datos",
                "input[type='submit']",
                "input[value*='Consultar']",
                "input[value*='enviar']",
                "button.btn-primary",
                "#Consultar"
            ]
            clicked = False
            for sel in submit_selectors:
                if await target_frame.query_selector(sel):
                    await target_frame.click(sel)
                    clicked = True
                    break
            
            if not clicked:
                print("No se encontró el botón de envío por selector, intentando presionar Enter...")
                await page.keyboard.press("Enter")

            # Esperar resultado (ajustar tiempo si es lento)
            # Primero esperamos a que aparezca el contenedor de resultados
            try:
                await target_frame.wait_for_selector("#datos_respuesta, .resultado, .panel-body", timeout=15000)
            except:
                print("Tiempo de espera agotado esperando el contenedor de respuesta.")
            
            await page.wait_for_load_state("networkidle", timeout=10000)
            
            # Extraer resultado
            await page.screenshot(path="debug_result.png")
            
            # Intentamos extraer información específica si está disponible
            result_info = ""
            for res_sel in ["#datos_respuesta", ".panel-body", "#contenedor"]:
                res_el = await target_frame.query_selector(res_sel)
                if res_el and await res_el.is_visible():
                    # Extraemos el texto y limpiamos líneas vacías o de encabezado genérico
                    lines = await res_el.inner_text()
                    lines = [l.strip() for l in lines.split("\n") if l.strip()]
                    # Intentamos quedarnos con lo que importa (ej: Progreso del trámite)
                    relevant_lines = []
                    found_relevant = False
                    for line in lines:
                        if "Progreso" in line or "Estado" in line or "PASO" in line or "TRÁMITE" in line:
                            found_relevant = True
                        if found_relevant:
                            relevant_lines.append(line)
                    
                    result_info = " | ".join(relevant_lines) if relevant_lines else " ".join(lines)
                    break
            
            status_text = result_info if result_info else "No se pudo extraer el texto del resultado"
            status_text = status_text.strip()
            
        except Exception as e:
            print(f"Error durante el proceso: {e}")
            status_text = f"Error: {e}"
            
        await browser.close()
        return status_text

def get_last_status():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("status")
        except Exception as e:
            print(f"Error al leer el archivo de estado: {e}")
    return None

def save_status(status):
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump({"status": status, "last_check": str(datetime.now())}, f, ensure_ascii=False)
    except Exception as e:
        print(f"Error al guardar el archivo de estado: {e}")

def normalize_status(text):
    """Limpia el texto para una comparación más robusta."""
    if not text:
        return ""
    # Quitamos espacios extra, saltos de línea y normalizamos a minúsculas
    return " ".join(text.lower().split()).strip()

async def main():
    current_status = await check_status()
    
    # Si hubo un error en el scraping, no notificamos por mail de cambio de estado
    if current_status.startswith("Error"):
        print(f"Abortando notificación: {current_status}")
        return

    last_status = get_last_status()
    
    # Normalizamos ambos para comparar
    curr_norm = normalize_status(current_status)
    last_norm = normalize_status(last_status)
    
    print(f"Estado actual (crudo): {current_status}")
    
    if curr_norm != last_norm:
        print("¡EL ESTADO HA CAMBIADO!")
        print(f"Anterior (norm): '{last_norm}'")
        print(f"Actual   (norm): '{curr_norm}'")
        from notifier import send_notification
        send_notification(current_status, last_status)
        save_status(current_status)
    else:
        print("Sin cambios desde la última revisión.")

if __name__ == "__main__":
    asyncio.run(main())
