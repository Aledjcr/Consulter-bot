// [DEPRECADO] Este archivo es un borrador incompleto. 
// Usa 'scraper.py' para la funcionalidad real del bot.
// checker.js

const puppeteer = require('puppeteer');
const nodemailer = require('nodemailer'); // Necesitarás instalar esta librería: npm install nodemailer

// --- CONFIGURACIÓN ---
const URL_DASHBOARD = 'https://www.migraciones.gob.ar/accesible/consultaTramiteCiudadania/ConsultaCiudadania.php';
const USERNAME = '2306372';
const DATE = '13/09/1995';

// Selectores CSS/XPath de los elementos en la página
const SELECTOR_USER = '#username';      // ID del campo de usuario
const SELECTOR_PASS = '#password';      // ID del campo de contraseña
const SELECTOR_LOGIN_BTN = 'button[type="submit"]'; // Selector del botón de login
const SELECTOR_ESTADO = '.clase-del-campo-a-revisar'; // Clase o ID del campo de estado

// Configuración de Email (usando Gmail como ejemplo)
const EMAIL_USER = 'tu_email@gmail.com';
const EMAIL_PASS = 'tu_password_o_app_password'; // Si usas Gmail, necesita una "Contraseña de aplicación"

// --- FUNCIONES ---

async function sendNotification(currentState) {
    let transporter = nodemailer.createTransport({
        service: 'gmail',
        auth: {
            user: EMAIL_USER,
            pass: EMAIL_PASS,
        }
    });

    let mailOptions = {
        from: EMAIL_USER,
        to: EMAIL_USER, // O el correo que quieras
        subject: '🚨 ¡ALERTA DE CAMBIO DE ESTADO! 🚨',
        text: `El estado del campo en el dashboard ha cambiado. Nuevo estado: ${currentState}`,
        html: `<h2>¡El estado ha cambiado!</h2><p>El nuevo valor del campo es: <strong>${currentState}</strong></p>`
    };

    await transporter.sendMail(mailOptions);
    console.log("Notificación por correo enviada.");
}

async function checkStatus() {
    const browser = await puppeteer.launch({
        headless: true // Lo ejecuta sin abrir la ventana del navegador (recomendado para servidores)
    });
    const page = await browser.newPage();
    let statusValue = null;

    try {
        // 1. Navegar a la página de Login
        await page.goto(URL_LOGIN, { waitUntil: 'networkidle2' });

        // 2. Ingresar credenciales y hacer Login
        await page.type(SELECTOR_USER, USERNAME);
        await page.type(SELECTOR_PASS, PASSWORD);
        await Promise.all([
            page.waitForNavigation({ waitUntil: 'networkidle2' }), // Espera a que termine la navegación
            page.click(SELECTOR_LOGIN_BTN)
        ]);

        console.log("Login exitoso. Navegando al Dashboard...");

        // 3. (Opcional) Navegar específicamente al Dashboard si no fue el destino post-login
        if (page.url() !== URL_DASHBOARD) {
            await page.goto(URL_DASHBOARD, { waitUntil: 'networkidle2' });
        }

        // 4. Obtener el estado del campo
        // Espera a que el selector aparezca en la página
        await page.waitForSelector(SELECTOR_ESTADO, { timeout: 10000 });

        // Extrae el texto del elemento (puedes necesitar .getAttribute('value') o .textContent)
        statusValue = await page.$eval(SELECTOR_ESTADO, el => el.textContent.trim());

        console.log(`Estado actual encontrado: ${statusValue}`);

        // --- LÓGICA DE VERIFICACIÓN ---
        // Aquí debes cargar el "estado anterior" guardado (ver punto 3)
        // Por simplicidad, asumiremos que "estado anterior" es 'PENDIENTE' y el nuevo es 'COMPLETADO'
        const previousState = 'PENDIENTE'; // <-- Esto debería venir de una base de datos o archivo

        if (statusValue !== previousState) {
            console.log("¡El estado ha cambiado! Enviando notificación...");
            await sendNotification(statusValue);
            // Aquí deberías GUARDAR el nuevo estado (statusValue) como el "estado anterior"
        } else {
            console.log("El estado no ha cambiado. Todo OK.");
        }

    } catch (error) {
        console.error("Error en la automatización:", error);
        // Opcional: Enviar un mail de error si la automatización falla.
    } finally {
        await browser.close();
    }
}

checkStatus();