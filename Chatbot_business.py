#Código para Recibir WhatsApp y crear una respuesta con ChatGPT
import openai
from flask import Flask, jsonify, request

app = Flask(__name__)

#CUANDO RECIBAMOS LAS PETICIONES EN ESTA RUTA
@app.route("/webhook/", methods=["POST", "GET"])
def webhook_whatsapp():
    #SI HAY DATOS RECIBIDOS VIA GET
    if request.method == "GET":
        #SI EL TOKEN ES IGUAL AL QUE RECIBIMOS
        if request.args.get('hub.verify_token') == "my token": # TU TOKEN CREADO PARA IGUAL A FACEBOOK META
            #ESCRIBIMOS EN EL NAVEGADOR EL VALOR DEL RETO RECIBIDO DESDE FACEBOOK
            return request.args.get('hub.challenge')
        else:
            #SI NO SON IGUALES RETORNAMOS UN MENSAJE DE ERROR
          return "Error de autentificacion."
    #RECIBIMOS TODOS LOS DATOS ENVIADO VIA JSON
    data=request.get_json()
    #EXTRAEMOS EL NUMERO DE TELEFONO Y EL MANSAJE
    telefonoCliente=data['entry'][0]['changes'][0]['value']['messages'][0]['from']
    #EXTRAEMOS EL MENSAJE DEL CLIENTE
    mensaje=data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
    #EXTRAEMOS EL ID DE WHATSAPP DEL ARRAY
    idWA=data['entry'][0]['changes'][0]['value']['messages'][0]['id']
    #EXTRAEMOS EL TIEMPO DE WHATSAPP DEL ARRAY
    timestamp=data['entry'][0]['changes'][0]['value']['messages'][0]['timestamp']
    #ESCRIBIMOS EL NUMERO DE TELEFONO Y EL MENSAJE EN EL ARCHIVO TEXTO
    #SI HAY UN MENSAJE
    if mensaje is not None:

        # Indica el API Key
        openai.api_key = "#############################################"
        # Uso de ChapGPT en Python
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
                #CONECTAMOS A LA BASE DE DATOS
        import mysql.connector
        mydb = mysql.connector.connect(
          host = "localhost",
          user = "root",
          password = "",
          database='chatBot test'
        )
        mycursor = mydb.cursor()
        query="SELECT count(id) AS cantidad FROM registro WHERE id_wa='" + idWA + "';"
        mycursor.execute(query)

        cantidad, = mycursor.fetchone()
        cantidad=str(cantidad)
        cantidad=int(cantidad)
        if cantidad==0 :
            sql = ("INSERT INTO registro"+ 
            "(mensaje_recibido,mensaje_enviado,id_wa      ,timestamp_wa   ,telefono_wa) VALUES "+
            "('"+mensaje+"'   ,'"+respuesta+"','"+idWA+"' ,'"+timestamp+"','"+telefonoCliente+"');")
            mycursor.execute(sql)
            mydb.commit()
            enviar(telefonoCliente,respuesta)
        #RETORNAMOS EL STATUS EN UN JSON
        return jsonify({"status": "success"}, 200)
    
def enviar(telefonoRecibe,respuesta):
  from heyoo import WhatsApp
  #TOKEN DE ACCESO DE FACEBOOK
  token='#####################################################' # TOKEN DE ACCESO FACEBOOK META
  #IDENTIFICADOR DE NÚMERO DE TELÉFONO
  idNumeroTeléfono='156646180865098'
  #INICIALIZAMOS ENVIO DE MENSAJES
  mensajeWa=WhatsApp(token,idNumeroTeléfono)
  telefonoRecibe=telefonoRecibe.replace("549","54")
  #ENVIAMOS UN MENSAJE DE TEXTO
  mensajeWa.send_message(respuesta,telefonoRecibe)
#INICIAMSO FLASK
if __name__ == "__main__":
  app.run(debug=True)