# :robot::speech_balloon: WhatsApp Chatbot with ChatGPT API Integration and Database Storage

![WhatsApp chatbot conversation](https://github.com/FedeMaguire/Whatsapp-ChatGPT-Chatbot/blob/main/screenshots/Screenshot%202023-11-27%20152443.jpg?raw=true)

## Overview

A customer-service chatbot for WhatsApp, built in 2023 as a paid project for **VideoNorte**, a business in Buenos Aires, Argentina, that converts old video and audio formats to digital.

The bot answers customer questions about services, prices, and opening hours. It uses OpenAI's API with business-specific system instructions, so replies stay within the information the business provided. Every incoming message and the bot's reply are stored in a MySQL database for later reference and analysis.

*The bot's instructions and replies are written in Spanish.*

![WhatsApp chat example](https://github.com/FedeMaguire/Whatsapp-ChatGPT-Chatbot/blob/main/screenshots/whatsapp%20chat.jpg?raw=true)

## How it works

1. A customer sends a WhatsApp message to the business number.
2. Meta's WhatsApp Cloud API forwards it to a Flask webhook.
3. The bot sends the message to OpenAI's API together with the business's system instructions.
4. The message, the reply, the WhatsApp message ID, the timestamp, and the customer's phone number are saved in MySQL. The message ID check prevents answering the same message twice.
5. The reply is sent back to the customer through the WhatsApp Cloud API.

## Tech stack

- **Python** with **Flask** (webhook server)
- **OpenAI API** (`gpt-3.5-turbo-instruct`)
- **WhatsApp Cloud API** (Meta), using the `heyoo` library
- **MySQL** (`mysql-connector-python`); the table schema is in `Database_queries.sql`
- **ngrok** to expose the local Flask server to Meta's webhook during development

## Setup

### Libraries

```
pip install openai Flask requests mysql-connector-python heyoo
```

### Prerequisites

**1. An OpenAI API key**

![OpenAI API key](https://github.com/FedeMaguire/Whatsapp-ChatGPT-Chatbot/blob/main/screenshots/openai%20api.jpg?raw=true)

**2. A WhatsApp Cloud API token from Meta**

![Meta token](https://github.com/FedeMaguire/Whatsapp-ChatGPT-Chatbot/blob/main/screenshots/token.jpg?raw=true)

**3. A public webhook URL.** For development, Flask runs a local server and ngrok exposes it to Meta.

![ngrok](https://github.com/FedeMaguire/Whatsapp-ChatGPT-Chatbot/blob/main/screenshots/ngrok.jpg?raw=true)

![Webhook URL](https://github.com/FedeMaguire/Whatsapp-ChatGPT-Chatbot/blob/main/screenshots/url%20devolucion.jpg?raw=true)

**4. A MySQL database** created from `Database_queries.sql`.

### Configuration

API keys and database credentials are read from environment variables, so no secrets are stored in the code:

```
OPENAI_API_KEY=...
WHATSAPP_TOKEN=...
WHATSAPP_PHONE_ID=...
WEBHOOK_VERIFY_TOKEN=...
DB_HOST=localhost
DB_USER=...
DB_PASSWORD=...
DB_NAME=...
```

## Notes

- Running the bot requires paid OpenAI API usage and a WhatsApp Business account on Meta's platform. ngrok is only for development; a production deployment needs a hosted server with a permanent URL.
- The code reflects the 2023 version of the OpenAI Python library (`openai.Completion`). Newer library versions use a different interface.
- **2026 update:** credentials moved to environment variables, and database queries switched to parameterized statements.
