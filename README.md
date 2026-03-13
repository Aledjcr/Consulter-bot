# 🤖 Migraciones Argentina Status Bot 🚀

Este proyecto es un **Script de Automatización Inteligente** diseñado para monitorear el estado de trámites de ciudadanía en el portal de Migraciones Argentina de manera automática y eficiente.
Acá un video del bot funcionando https://youtu.be/zYviBpVFUm4
---

## 📖 La Historia Detrás del Proyecto
Este script nació de una necesidad cotidiana: la tediosa tarea de entrar manualmente cada día a un portal web, completar un formulario y verificar si hubo cambios en un trámite que suele tomar meses. 

Lo que comenzó como una solución personal para ahorrar tiempo, se convirtió en un **proyecto de estudio sobre automatización moderna**, explorando cómo las herramientas de IA y las tecnologías de scraping pueden trabajar en conjunto para simplificar procesos burocráticos repetitivos. 

> Este proyecto fue desarrollado mi asistente de IA (**Antigravity**), demostrando que manejando los fundamentos podemos crear cosas que aporten valor!

---

## 🛠️ Tecnologías Usadas

- **[Python](https://www.python.org/)**: El motor principal del script.
- **[Playwright](https://playwright.dev/)**: Para la automatización del navegador, permitiendo navegar y completar formularios como un humano.
- **[Playwright Stealth](https://github.com/berstend/puppeteer-extra/tree/master/packages/puppeteer-extra-plugin-stealth)**: Capa de seguridad para evitar bloqueos por parte de sistemas anti-bot (WAF).
- **[Resend API](https://resend.com/)**: El servicio elegido para el envío de notificaciones por correo electrónico de forma profesional.
- **[GitHub Actions](https://github.com/features/actions)**: La infraestructura "serverless" que ejecuta el script diariamente en la nube, ¡completamente gratis!

---

## 🚀 ¿Cómo Funciona?

1. **Navegación Inteligente**: El script inicia un navegador invisible, accede al portal y completa los datos del trámite.
2. **Detección de Cambios**: Extrae el estado actual y lo compara con el último estado guardado en un archivo `state.json`.
3. **Persistencia**: Si hay cambios, actualiza el archivo y envía una alerta por email inmediatamente.
4. **Cloud-Native**: Gracias a GitHub Actions, el repositorio mismo actúa como base de datos del estado y servidor de ejecución.

---

## 🔒 Seguridad y Privacidad
El proyecto está diseñado siguiendo las mejores prácticas:
- **Zero Hardcoding**: Los datos sensibles (N° de trámite, fecha de nacimiento, API Keys) se manejan mediante variables de entorno o GitHub Secrets.
- **GitIgnore**: Los archivos locales de configuración (`.env`) y capturas de depuración nunca se suben al repositorio.

---

## 🗺️ Potencial y Casos de Uso
Si bien este script monitoriza un trámite específico, la arquitectura es **escalable y adaptable** a múltiples escenarios:
- **E-commerce**: Monitoreo de stock de productos difíciles de conseguir.
- **Finanzas**: Alertas de cambios en tasas o valores en portales bancarios.
- **Administración**: Seguimiento de cualquier trámite gubernamental con portales de consulta.
- **QA/Testing**: Pruebas automatizadas de flujos de usuario complejos en aplicaciones web.

---

## ⚙️ Configuración Rápida
Para implementarlo tú mismo, consulta la [Guía de Configuración Local](./walkthrough.md) o la [Guía para Linux VM](./VM_SETUP_LINUX.md).

-- Desarrollado con ❤️ 
