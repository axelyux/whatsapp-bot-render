import os
from flask import Flask, request, jsonify
import requests

# Reemplaza los valores con los que obtuviste de Meta Developers
# (Los tokens largos aquí NO son seguros. Usa variables de entorno en producción)
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN')
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
PHONE_NUMBER_ID = os.environ.get('PHONE_NUMBER_ID')

# Crea la aplicación Flask
app = Flask(__name__)

# --- WEBHOOK PARA RECIBIR MENSAJES ---
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Esta parte se usa para la VERIFICACIÓN del webhook
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        # Comprueba el token de verificación
        if mode and token:
            if mode == 'subscribe' and token == VERIFY_TOKEN:
                print('WEBHOOK_VERIFIED')
                return challenge, 200
            else:
                return 'Verification token mismatch', 403
        else:
            # FIX: Si se accede por navegador (sin parámetros), devolvemos 200 para evitar el error 500
            # Meta nunca enviará un GET sin parámetros, solo un navegador lo haría.
            return 'Webhook activo. Esperando conexión de Meta.', 200 
    
    elif request.method == 'POST':
        # Esta parte maneja los MENSAJES ENTRANTES
        data = request.get_json()
        print('Received webhook data:', data)

        # Procesa el mensaje si es del tipo correcto
        if 'entry' in data and data['entry']:
            for entry in data['entry']:
                for change in entry.get('changes', []):
                    if change.get('field') == 'messages':
                        for message in change.get('value', {}).get('messages', []):
                            # Obtenemos el texto del mensaje y el número del remitente
                            if message.get('type') == 'text':
                                incoming_text = message['text']['body'].lower()
                                from_number = message['from']
                                
                                # Lógica del chatbot: Si el mensaje es "hola", responde
                                if 'hola' in incoming_text:
                                    response_text = '¡Hola! 👋 ¡Tu bot está funcionando!'
                                    send_whatsapp_message(from_number, response_text)

        return 'ok', 200

def send_whatsapp_message(to_number, text_message):
    """Función para enviar un mensaje de vuelta."""
    # Usamos la versión de la API de Facebook/Meta que estaba en tu código original
    url = f'https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages' 
    
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }

    data = {
        'messaging_product': 'whatsapp',
        'recipient_type': 'individual',
        'to': to_number,
        'type': 'text',
        'text': {
            'body': text_message
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    print('API response:', response.json())

if __name__ == '__main__':
    # Cambia a un puerto diferente para intentar forzar un nuevo subdominio en ngrok

    app.run(host='0.0.0.0', port=9001) 
