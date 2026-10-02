import os
import logging
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

# Configuración de logs
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Servidor Dummy para mantener Render contento en el plan gratuito
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot activo")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    server.serve_forever()

# Estados de la conversación
EDAD, PESO_ESTATURA, SALUD, OBJETIVO, EXPERIENCIA, LUGAR = range(6)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "¡Hola! Bienvenido a tu asistente personal de Fitness y Nutrición. 🏋️‍♂️🥗\n\n"
        "Para diseñarte el plan perfecto, necesito hacerte unas breves preguntas.\n\n"
        "1️⃣ ¿Cuál es tu edad?"
    )
    return EDAD

async def recibir_edad(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['edad'] = update.message.text
    await update.message.reply_text(
        "2️⃣ ¿Cuál es tu peso (en kg) y tu estatura (en cm)?\n"
        "Ejemplo: 70 kg, 175 cm"
    )
    return PESO_ESTATURA

async def recibir_peso_estatura(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['peso_estatura'] = update.message.text
    reply_keyboard = [["Ninguno", "Problemas cardíacos"], ["Diabetes", "Problemas de articulaciones/columna"]]
    await update.message.reply_text(
        "3️⃣ ¿Tienes alguna condición de salud o afección importante?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return SALUD

async def recibir_salud(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['salud'] = update.message.text
    reply_keyboard = [["Perder peso / Quemar grasa"], ["Aumentar masa muscular"], ["Mantenimiento / Salud"]]
    await update.message.reply_text(
        "4️⃣ ¿Cuál es tu objetivo principal?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return OBJETIVO

async def recibir_objetivo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['objetivo'] = update.message.text
    reply_keyboard = [["Principiante"], ["Intermedio"], ["Avanzado"]]
    await update.message.reply_text(
        "5️⃣ ¿Cuál es tu nivel de experiencia realizando ejercicios?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return EXPERIENCIA

async def recibir_experiencia(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['experiencia'] = update.message.text
    reply_keyboard = [["Gimnasio"], ["En casa"]]
    await update.message.reply_text(
        "6️⃣ ¿Dónde prefieres entrenar?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return LUGAR

async def recibir_lugar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['lugar'] = update.message.text
    
    resumen = (
        "✅ *¡Cuestionario completado!*\n\n"
        "📋 *Tus datos registrados:*\n"
        f"• Edad: {context.user_data.get('edad')}\n"
        f"• Peso y Estatura: {context.user_data.get('peso_estatura')}\n"
        f"• Salud: {context.user_data.get('salud')}\n"
        f"• Objetivo: {context.user_data.get('objetivo')}\n"
        f"• Experiencia: {context.user_data.get('experiencia')}\n"
        f"• Lugar de entrenamiento: {context.user_data.get('lugar')}\n\n"
        "💪 Estamos procesando tu rutina y guía nutricional personalizada..."
    )
    
    await update.message.reply_text(resumen, reply_markup=ReplyKeyboardRemove(), parse_mode="Markdown")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Proceso cancelado. Envía /start cuando quieras volver a empezar.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def main():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise ValueError("No se encontró el token de Telegram. Configúralo en las variables de entorno.")

    # Iniciar servidor HTTP en segundo plano para Render
    Thread(target=run_dummy_server, daemon=True).start()

    application = Application.builder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            EDAD: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_edad)],
            PESO_ESTATURA: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_peso_estatura)],
            SALUD: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_salud)],
            OBJETIVO: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_objetivo)],
            EXPERIENCIA: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_experiencia)],
            LUGAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_lugar)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    
    print("Bot en marcha...")
    application.run_polling()

if _name_ == "_main_":
    main()
