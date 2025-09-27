import os
from flask import Flask, request, jsonify
import requests # Importar para hacer la solicitud a la API de WhatsApp

# 1. LEE LAS VARIABLES DE ENTORNO (De Render)
# Usa os.environ.get() para obtener el valor de Render.
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN')
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
PHONE_NUMBER_ID = os.environ.get('PHONE_NUMBER_ID')
API_URL = "https://graph.facebook.com/v19.0" # URL base de la API

# 2. Crea la aplicación Flask
app = Flask(__name__)

# --- WEBHOOK PARA RECIBIR Y ENVIAR MENSAJES ---
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    # A. Manejo del método GET (Verificación del Webhook)
    if request.method == "GET":
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        # Comprueba que la verificación sea correcta
        if mode and token:
            if mode == 'subscribe' and token == VERIFY_TOKEN:
                print('WEBHOOK_VERIFIED')
                return challenge, 200 # <-- El retorno que elimina el TypeError

        # Si no se cumple la verificación, devuelve un error 403
        return 'Verification token mismatch', 403 

    # B. Manejo del método POST (Recepción de Mensajes)
    if request.method == "POST":
        data = request.get_json()
        print("Received webhook data:", data)

        try:
            # 1. Verificar si el mensaje proviene de WhatsApp
            # Tu código anterior pudo fallar si el webhook era de 'status' (cambio de estado)
            if data['entry'][0]['changes'][0]['value']['messages']:
                message_data = data['entry'][0]['changes'][0]['value']['messages'][0]
                
                # 2. Extraer información del mensaje
                sender_id = message_data['from']
                
                # Asegúrate de que el mensaje tenga un cuerpo de texto
                if 'text' in message_data and 'body' in message_data['text']:
                    message_body = message_data['text']['body'].lower() # Convertir a minúsculas
                else:
                    # Ignora si es una imagen, emoji o sticker por ahora
                    return 'ok', 200

                # 3. Lógica de respuesta simple (Responde a 'hola')
                if message_body == 'hola':
                    # URL para enviar el mensaje a la API de WhatsApp
                    send_url = f"{API_URL}/{PHONE_NUMBER_ID}/messages"
                    
                    headers = {
                        "Authorization": f"Bearer {ACCESS_TOKEN}",
                        "Content-Type": "application/json",
                    }
                    
                    # Cuerpo del mensaje que vamos a enviar
                    response_body = {
                        "messaging_product": "whatsapp",
                        "to": sender_id,
                        "type": "text",
                        "text": {
                            "body": "¡Hola! Soy tu Chatbot de AR Services. ¿En qué puedo ayudarte?"
                        }
                    }
                    
                    # Enviar la respuesta a la API de Meta
                    response = requests.post(send_url, headers=headers, json=response_body)
                    print("API Response Status:", response.status_code)
                    print("API Response Body:", response.text)

                    # Si hay un error, el log de Render lo mostrará aquí.
                    
        except Exception as e:
            # Si hay un error al procesar el mensaje, lo registramos.
            print(f"Error processing message: {e}")
            pass # No queremos que el fallo del webhook detenga el bot
            
        # Meta espera un retorno 200 para confirmar que recibimos el webhook
        return 'ok', 200

    # Si se usa un método HTTP que no es GET o POST
    return 'Method Not Allowed', 405
