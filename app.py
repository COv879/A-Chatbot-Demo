from flask import Flask, render_template, request, session
import openai
from dotenv import load_dotenv
import os
import time


load_dotenv()

app = Flask(__name__)

openai.api_key = os.getenv('OPENAI_API_KEY')
app.secret_key = os.getenv('SECRET_KEY')

# Función para obtener respuesta de ChatGPT con reintentos si ocurre el error 429
def obtener_respuesta_chatgpt(comentario):
    intentos = 3  
    for i in range(intentos):
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",  # Modelo a usar
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": comentario}
                ]
            )
            return response.choices[0].message.content

        except Exception as e:
            error_message = str(e)
            if "Rate limit" in error_message:  # Verificar si el error es de límite de solicitudes
                if i < intentos - 1:
                    time.sleep(2 ** i)  # Espera entre intentos (exponencial: 2, 4, 8 segundos)
                else:
                    return "Error: Se ha excedido el límite de solicitudes. Intente más tarde."
            else:
                return f"Error al comunicarse con ChatGPT: {error_message}"

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'conversation' not in session:
        session['conversation'] = []


    if request.method == 'POST':
        comentario = request.form.get('comentario')

        # Obtener respuesta de ChatGPT utilizando la función con reintentos
        respuesta_chatgpt = obtener_respuesta_chatgpt(comentario)

        # Agregar el mensaje del usuario y la respuesta de ChatGPT a la conversación
        session['conversation'].append({'role': 'user', 'message': comentario})
        session['conversation'].append({'role': 'assistant', 'message': respuesta_chatgpt})
        
        # Asegurarse de que los datos persistan
        session.modified = True

    # Renderizar la página con la conversación
    return render_template('index.html', conversation=session['conversation'])

if __name__ == '__main__':
    app.run(debug=True)
