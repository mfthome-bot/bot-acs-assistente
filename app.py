import os
import telegram
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler
import requests
import json
from flask import Flask

# Configurações - O Render vai inserir estas variáveis
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')

app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Bot ACS está online!"

def ask_deepseek(question):
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system", 
                "content": "Você é assistente especializado para Agente Comunitário de Saúde no Brasil. Responda SEMPRE em PORTUGUÊS. Ajude com: cadastro de pacientes, lembretes de medicamentos, relatórios para e-SUS, orientações de saúde. Use emojis e seja prático. Exemplos: gestantes, hipertensos, diabéticos, vacinas, pré-natal."
            },
            {
                "role": "user",
                "content": question
            }
        ],
        "stream": False
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        return f"Erro: {str(e)}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    print(f"📩 Mensagem recebida: {user_message}")
    
    response = ask_deepseek(user_message)
    await update.message.reply_text(response[:4000])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Olá! Sou seu assistente de ACS!\n\n"
        "📋 **Posso ajudar com:**\n"
        "• Cadastro de pacientes\n• Lembretes de medicamentos\n• Relatórios para e-SUS\n"
        "• Orientação para gestantes\n• Controle de hipertensos/diabéticos\n"
        "• Acompanhamento de vacinas\n\n"
        "💡 **Exemplos de uso:**\n"
        "\"Cadastrar gestante G001, 25 semanas\"\n"
        "\"Paciente H005, PA 150/90, precisa renovar receita\"\n"
        "\"Lembrar vacina da criança C003 em 15 dias\"\n\n"
        "Como posso ajudar você hoje? 😊"
    )

def run_bot():
    if not TELEGRAM_BOT_TOKEN or not DEEPSEEK_API_KEY:
        print("❌ Variáveis de ambiente não configuradas!")
        return
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 Bot ACS iniciado e rodando!")
    application.run_polling()

if __name__ == "__main__":
    run_bot()
