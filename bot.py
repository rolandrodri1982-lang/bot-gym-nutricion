import os
import logging
import asyncio
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

# Servidor HTTP para cumplir el requerimiento de Render
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        return

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    server.serve_forever()

# Estados de la conversación
EDAD, PESO_ESTATURA, SALUD, OBJETIVO, EXPERIENCIA, LUGAR = range(6)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "¡Hola! Bienvenido a tu entrenador personal y guía nutricional IA. 🏋️‍♂️🥗\n\n"
        "Para diseñarte el plan perfecto, necesito hacerte 6 breves preguntas.\n\n"
        "1️⃣ ¿Cuál es tu edad?"
    )
    return EDAD

async def recibir_edad(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["edad"] = update.message.text
    await update.message.reply_text(
        "2️⃣ ¿Cuál es tu peso (en kg) y tu estatura (en cm)?\n"
        "Ejemplo: 70 kg, 175 cm"
    )
    return PESO_ESTATURA

async def recibir_peso_estatura(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["peso_estatura"] = update.message.text
    reply_keyboard = [
        ["Ninguno", "Problemas cardíacos"],
        ["Diabetes", "Problemas de articulaciones/columna"],
    ]
    await update.message.reply_text(
        "3️⃣ ¿Tienes alguna condición de salud o afección importante?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return SALUD

async def recibir_salud(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["salud"] = update.message.text
    reply_keyboard = [
        ["Perder peso / Quemar grasa"],
        ["Aumentar masa muscular"],
        ["Mantenimiento / Salud"],
    ]
    await update.message.reply_text(
        "4️⃣ ¿Cuál es tu objetivo principal?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return OBJETIVO

async def recibir_objetivo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["objetivo"] = update.message.text
    reply_keyboard = [["Principiante"], ["Intermedio"], ["Avanzado"]]
    await update.message.reply_text(
        "5️⃣ ¿Cuál es tu nivel de experiencia realizando ejercicios?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return EXPERIENCIA

async def recibir_experiencia(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["experiencia"] = update.message.text
    reply_keyboard = [["Gimnasio"], ["En casa"]]
    await update.message.reply_text(
        "6️⃣ ¿Dónde prefieres entrenar?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return LUGAR

async def recibir_lugar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["lugar"] = update.message.text

    edad = context.user_data.get("edad", "No especificado")
    peso_estatura = context.user_data.get("peso_estatura", "No especificado")
    salud = context.user_data.get("salud", "Ninguno")
    objetivo = context.user_data.get("objetivo", "Salud General")
    experiencia = context.user_data.get("experiencia", "Principiante")
    lugar = context.user_data.get("lugar", "En casa")

    resumen = (
        "✅ *¡Cuestionario completado!*\n\n"
        "📋 *Tus datos registrados:*\n"
        f"• Edad: {edad}\n"
        f"• Peso y Estatura: {peso_estatura}\n"
        f"• Salud: {salud}\n"
        f"• Objetivo: {objetivo}\n"
        f"• Nivel: {experiencia}\n"
        f"• Lugar: {lugar}\n"
    )

    await update.message.reply_text(
        resumen, reply_markup=ReplyKeyboardRemove(), parse_mode="Markdown"
    )

    # Generación del Plan Entrenador / Nutrición
    plan_texto = (
        "💪 *TU PLAN PERSONALIZADO DE ENTRENAMIENTO Y NUTRICIÓN*\n\n"
        "🏋️ *Rutina Semanal Recomendada:*\n"
        "• *Día 1 (Empuje):* Pecho, Hombros y Tríceps (3 series de 10-12 reps).\n"
        "• *Día 2 (Tirón):* Espalda, Bíceps y Abdomen (3 series de 10-12 reps).\n"
        "• *Día 3 (Pierna):* Cuádriceps, Isquiotibiales y Pantorrillas.\n"
        "• *Día 4:* Cardio moderado (30 min) + Movilidad / Estiramientos.\n"
        "• *Día 5:* Rutina Full-Body o enfoque según preferencia.\n\n"
        "🥗 *Pautas de Nutrición Básicas:*\n"
        "• Prioriza proteína magra (pollo, pescado, huevos, tofu) en cada comida.\n"
        "• Mantén una buena hidratación (2.5 a 3 litros de agua al día).\n"
        "• Consume carbohidratos complejos (avena, arroz integral, camote) alrededor de tus entrenamientos.\n\n"
        "🔄 Envía /start en cualquier momento si deseas rehacer el cuestionario."
    )

    await update.message.reply_text(plan_texto, parse_mode="Markdown")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Proceso cancelado. Envía /start cuando quieras volver a empezar.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END

def main():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise ValueError("No se encontró el token de Telegram.")

    t = Thread(target=run_dummy_server, daemon=True)
    t.start()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    application = Application.builder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            EDAD: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_edad)],
            PESO_ESTATURA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_peso_estatura)
            ],
            SALUD: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_salud)],
            OBJETIVO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_objetivo)
            ],
            EXPERIENCIA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_experiencia)
            ],
            LUGAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_lugar)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    print("Bot en marcha...")
    application.run_polling()

if __name__ == "__main__":
    main()
