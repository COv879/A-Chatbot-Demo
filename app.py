from flask import Flask, render_template, request
import openai
from dotenv import load_dotenv
import os
import time


load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')


app = Flask(__name__)

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
    respuesta_chatgpt = None
    if request.method == 'POST':
        comentario = request.form.get('comentario')

        # Obtener respuesta de ChatGPT utilizando la función con reintentos
        respuesta_chatgpt = obtener_respuesta_chatgpt(comentario)

        # Renderizar la página con la respuesta de ChatGPT
        return render_template('index.html', comentario=comentario, respuesta_chatgpt=respuesta_chatgpt)
    
    return render_template('index.html', comentario=None, respuesta_chatgpt=None)

if __name__ == '__main__':
    app.run(debug=True)
