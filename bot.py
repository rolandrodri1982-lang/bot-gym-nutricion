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

# Estados de la conversación principal
EDAD, PESO_ESTATURA, SALUD, OBJETIVO, EXPERIENCIA, LUGAR = range(6)

# Estado de la revisión de progreso
NUEVO_PESO = 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "¡Hola! Bienvenido a tu entrenador personal y guía nutricional IA. 🏋️‍♂️️🥗\n\n"
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
    lugar = context.user_data.get("lugar", "Gimnasio")

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

    # Detalle de rutina adaptada según Gimnasio vs En Casa
    if "casa" in lugar.lower():
        rutina_detalle = (
            "🏋️ *RUTINA SEMANAL DETALLADA (EN CASA / CALISTENIA):*\n\n"
            "📌 *Día 1: Empuje (Pecho, Hombro, Tríceps)*\n"
            "• Flexiones de pecho (Push-ups): 4 series de 10-12 reps.\n"
            "• Flexiones declinadas o en pica (Hombros): 3 series de 8-10 reps.\n"
            "• Elevaciones laterales (con botellas/mancuernas): 3 series de 12-15 reps.\n"
            "• Fondos en silla o banco (Tríceps): 3 series de 10-12 reps.\n\n"
            "📌 *Día 2: Tirón (Espalda, Bíceps, Abdomen)*\n"
            "• Dominadas o Remo con mochila/mancuerna: 4 series de 8-10 reps.\n"
            "• Curl de bíceps con mancuernas/mochila: 3 series de 12 reps.\n"
            "• Plancha abdominal: 3 series sostenidas de 45 segundos.\n"
            "• Crunches/Elevación de piernas: 3 series de 15 reps.\n\n"
            "📌 *Día 3: Pierna (Inferior)*\n"
            "• Sentadillas con peso corporal o mochila: 4 series de 15 reps.\n"
            "• Zancadas/Lunges alternados: 3 series de 12 reps por pierna.\n"
            "• Puentes de glúteo/isquios: 3 series de 15 reps.\n"
            "• Elevación de talones (Pantorrillas): 4 series de 20 reps.\n\n"
            "📌 *Día 4: Cardio & Movilidad*\n"
            "• Burpees o saltos de tijera: 4 rondas de 45 seg trabajo / 15 seg descanso.\n"
            "• Estiramientos completos: 15 minutos.\n\n"
            "📌 *Día 5: Full Body / Repaso general*\n"
            "• Circuito combinado de 3 rondas con ejercicios de días anteriores."
        )
    else:
        rutina_detalle = (
            "🏋️ *RUTINA SEMANAL DETALLADA (GIMNASIO):*\n\n"
            "📌 *Día 1: Empuje (Pecho, Hombro y Tríceps)*\n"
            "• Press de banca plano con barra o mancuernas: 4 series de 8-10 reps.\n"
            "• Press inclinado con mancuernas (Pecho superior): 3 series de 10-12 reps.\n"
            "• Press Militar con barra/mancuernas (Hombros): 3 series de 10 reps.\n"
            "• Elevaciones laterales con mancuernas (Hombros): 4 series de 12-15 reps.\n"
            "• Extensión de tríceps en polea alta: 3 series de 12 reps.\n\n"
            "📌 *Día 2: Tirón (Espalda, Bíceps y Abdomen)*\n"
            "• Jalón al pecho en polea alta (Espalda alta): 4 series de 10 reps.\n"
            "• Remo con barra o en máquina: 3 series de 10-12 reps.\n"
            "• Curl de bíceps con barra Z o mancuernas: 3 series de 12 reps.\n"
            "• Curl martillo para antebrazo/bíceps: 3 series de 12 reps.\n"
            "• Elevación de piernas colgado o en banco (Abdomen): 3 series de 15 reps.\n\n"
            "📌 *Día 3: Pierna Completa*\n"
            "• Sentadilla libre o en máquina Smith: 4 series de 8-10 reps.\n"
            "• Prensa de piernas: 3 series de 10-12 reps.\n"
            "• Curl femoral acostado o sentado (Isquios): 3 series de 12 reps.\n"
            "• Elevación de pantorrillas de pie: 4 series de 15-20 reps.\n\n"
            "📌 *Día 4: Cardio Activo & Abdomen*\n"
            "• Caminadora inclorada o Elíptica: 30 minutos a ritmo constante.\n"
            "• Rutina de abdominales en polea/colchoneta: 15 minutos.\n\n"
            "📌 *Día 5: Enfoque Hombros & Brazos / Torso*\n"
            "• Press inclinado + Elevaciones laterales con mancuernas.\n"
            "• Super-serie Bíceps y Tríceps: 3 series de 12 reps."
        )

    plan_texto = (
        f"{rutina_detalle}\n\n"
        "🥗 *PAUTAS DE NUTRICIÓN RECOMENDADAS:*\n"
        "• Proteínas: Pollo, carne magra, pescado, huevos o lomo.\n"
        "• Carbohidratos: Avena, arroz integral, camote, papa o yuca (especialmente post-entrenamiento).\n"
        "• Grasas saludables: Aguacate, frutos secos, aceite de oliva.\n"
        "• Agua: Beber entre 2.5 y 3.5 litros diarios.\n\n"
        "📅 *SEGUIMIENTO Y CONTROL DE PROGRESO:*\n"
        "Para garantizar resultados y cambiar tu rutina a tiempo:\n"
        "1. Te recomendamos realizar un chequeo de control *cada 15 o 30 días*.\n"
        "2. Envía el comando */revision* para registrar tu nuevo peso y evaluar la evolución de tu plan.\n\n"
        "🔄 Envía /start en cualquier momento si deseas rehacer el cuestionario completo."
    )

    await update.message.reply_text(plan_texto, parse_mode="Markdown")
    return ConversationHandler.END

# Función de Revisión de Progreso Quincenal/Mensual
async def iniciar_revision(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "📊 *CONTROL Y REVISIÓN DE PROGRESO* 📊\n\n"
        "¡Excelente compromiso! Llevar un registro periódico permite ajustar tus cargas o cambiar tu rutina.\n\n"
        "¿Cuál es tu peso actual en kg? (Ejemplo: 82)"
    )
    return NUEVO_PESO

async def guardar_nuevo_peso(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    nuevo_peso = update.message.text
    await update.message.reply_text(
        f"✅ ¡Registro guardado con éxito! Tu peso actual registrado es *{nuevo_peso} kg*.\n\n"
        "💪 *Recomendación de tu entrenador IA:*\n"
        "• Si tu objetivo es *perder peso* y has reducido medidas, mantén las cargas e intensifica el cardio.\n"
        "• Si tu objetivo es *ganar masa muscular*, intenta subir gradualmente el peso en ejercicios clave (como Press Militar o Sentadilla).\n"
        "• Recuerda realizar este chequeo nuevamente en *15 días*.\n\n"
        "Si deseas cambiar completamente de rutina, puedes enviar /start.",
        parse_mode="Markdown"
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Proceso cancelado. Envía /start cuando quieras reiniciar.",
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

    # Manejador del Cuestionario Inicial
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

    # Manejador de la Revisión de Progreso Quincenal/Mensual
    revision_handler = ConversationHandler(
        entry_points=[CommandHandler("revision", iniciar_revision)],
        states={
            NUEVO_PESO: [MessageHandler(filters.TEXT & ~filters.COMMAND, guardar_nuevo_peso)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(revision_handler)

    print("Bot en marcha...")
    application.run_polling()

if __name__ == "__main__":
    main()
