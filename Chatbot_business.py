#Receive WhatsApp message and Generate a Response with ChatGPT
import os
import openai
import mysql.connector
from flask import Flask, jsonify, request

app = Flask(__name__)

#WHEN WE RECEIVE REQUESTS AT THIS ROUTE
@app.route("/webhook/", methods=["POST", "GET"])
def webhook_whatsapp():
    #IF DATA RECEIVED VIA GET
    if request.method == "GET":
        #IF OKEN MATCHES TOKEN RECEIVED
        if request.args.get('hub.verify_token') == os.environ["WEBHOOK_VERIFY_TOKEN"]: # TOKEN == META TOKEN
            #ENTER CHALLENGE VALUE RECEIVED FROM FACEBOOK IN BROWSER
            return request.args.get('hub.challenge')
        else:
            #IF NOT EQUAL, RETURN AN ERROR MESSAGE
          return "Error de autentificacion."
    #RECEIVE ALL THE DATA SENT VIA JSON
    data=request.get_json()
    #EXTRACT PHONE NUMBER AND MESSAGE
    telefonoCliente=data['entry'][0]['changes'][0]['value']['messages'][0]['from']
    #EXTRACT CUSTOMER'S MESSAGE
    mensaje=data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
    #EXTRACT WHATSAPP ID FROM ARRAY
    idWA=data['entry'][0]['changes'][0]['value']['messages'][0]['id']
    #EXTRACT WHATSAPP TIMESTAMP FROM ARRAY
    timestamp=data['entry'][0]['changes'][0]['value']['messages'][0]['timestamp']

    #GENERATE RESPONSE 
    #IF THERE IS MESSAGE
    if mensaje is not None:

        # OpenAI API Key
        openai.api_key = os.environ["OPENAI_API_KEY"]
        # ChatGPT in Python
        model_engine = "gpt-3.5-turbo-instruct"

        # Define the system instruction and user message using 'mensaje' variable
        system_instruction = {'role':'system', 'content':'''
Al iniciar una conversacion si ya existio una previa desestimala y usas este saludo: "Hola, soy tu asistente\
de VideoNorte, un negocio especializado en la conversión de formatos antiguos de video y audio a formato digital.\
¿En qué puedo ayudarte hoy?"\
Nunca generas preguntas de usuarios, ni auto completas, esperas su pregunta para generar respuestas.\
Eres un chatbot de un negocio llamado VideoNorte, dedicado a la conversión de formatos antiguos de video\
y audio formato a digital. \
Los precios son:\
CASETE VHS-Vhsc hasta 1 hora de duracion = $ 450\
(si es más de una hora se fracciona cada media hora $ 225.)\
Castetes Hi8-8mm-Minidv-Minidvd o de audio $ 800 hasta 1 hora de duracion.\
(Los precios corresponden a la conversion a archivo digital, o archivo de datos,\
formato MPEG,( 1 hora pesa 3gb ))\
Los precios no incluyen pendrive o disco rígido externo.\
Precios: Pendrive 32gb $ 6500 marca kingston.\
Guardado en formato Dvd el valor $ 500 más por Dvd utilizado.\
Los descuentos por cantidad son superando los 50 videos, ( 10% menos ).\
Diapositivas, negativos o fotos de papel a formato digital JPG = $ 20 c/u (todo a su máxima resolución,\
incluye mejora de color y restauración de imágenes.)\
El importe mínimo por cualquier trabajo es de $ 600.\
Estamos en Capitán J. G. de Bermudez 3457 Olivos, de Lunes a Jueves de 9 a 16hs, Saludos
'''}
        user_message = {'role':'user', 'content': mensaje}

        # Add the system instruction and user message to the list of messages
        messages = [
            system_instruction,
            user_message
        ]

        # Concatenate messages into a single string
        combined_message = f"[{system_instruction['role']}] {system_instruction['content']}\n[{user_message['role']}] {user_message['content']}"

        prompt = combined_message
        completion = openai.Completion.create(engine=model_engine,
                                            prompt=prompt,
                                            max_tokens=700,
                                            n=1,
                                            stop=None,
                                            temperature=0.6)
        respuesta=""
        for choice in completion.choices:
            choice_text = choice.text.replace("[system]", "")  # Remove [system] tag
            respuesta=respuesta+choice_text
            print(f"Response: %s" % choice_text)

        respuesta=respuesta.replace("\\n","\\\n")
        respuesta=respuesta.replace("\\","")
        #Connect to database
        mydb = mysql.connector.connect(
          host = os.environ.get("DB_HOST", "localhost"),
          user = os.environ["DB_USER"],
          password = os.environ["DB_PASSWORD"],
          database = os.environ["DB_NAME"]
        )
        mycursor = mydb.cursor()
        #PARAMETERIZED QUERIES: VALUES ARE PASSED SEPARATELY, NEVER CONCATENATED INTO THE SQL
        mycursor.execute("SELECT COUNT(id) FROM registro WHERE id_wa = %s", (idWA,))
        cantidad, = mycursor.fetchone()
        if cantidad == 0:
            sql = ("INSERT INTO registro "
                   "(mensaje_recibido, mensaje_enviado, id_wa, timestamp_wa, telefono_wa) "
                   "VALUES (%s, %s, %s, %s, %s)")
            mycursor.execute(sql, (mensaje, respuesta, idWA, timestamp, telefonoCliente))
            mydb.commit()
            enviar(telefonoCliente,respuesta)
        mycursor.close()
        mydb.close()
        #Return Json status
        return jsonify({"status": "success"}, 200)
    
def enviar(telefonoRecibe,respuesta):
  from heyoo import WhatsApp
  #Facebook access from META
  token=os.environ["WHATSAPP_TOKEN"]
  #Telephone number identifier
  idNumeroTeléfono=os.environ["WHATSAPP_PHONE_ID"]
 #STARTING MESSAGE SENDING
  mensajeWa=WhatsApp(token,idNumeroTeléfono)
  telefonoRecibe=telefonoRecibe.replace("549","54")
  #SENDING TEXT MESSAGE
  mensajeWa.send_message(respuesta,telefonoRecibe)
#STARTING FLASK
if __name__ == "__main__":
  app.run(debug=False)
