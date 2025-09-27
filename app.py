from flask import Flask, request, jsonify, render_template_string
from blackbox2 import TechJournalistAgent
from json import JSONEncoder

class SafeJSONEncoder(JSONEncoder):
    def encode(self, o):
        return super().encode(o).replace('\\u003c', '<').replace('\\u003e', '>').replace('\\u0026', '&')

app = Flask(__name__)

app.json_encoder = SafeJSONEncoder

agent = TechJournalistAgent()

@app.route('/')
def home():
    html = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Phil - Journaliste Tech</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .chat-container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            width: 100%;
            max-width: 600px;
            height: 80vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .chat-header {
            background: linear-gradient(135deg, #4f46e5, #7c3aed);
            color: white;
            padding: 20px;
            text-align: center;
            font-weight: bold;
            font-size: 1.2rem;
        }
        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        .message {
            max-width: 70%;
            padding: 12px 18px;
            border-radius: 18px;
            word-wrap: break-word;
        }
        .bot-message {
            align-self: flex-start;
            background-color: #f3f4f6;
        }
        .user-message {
            align-self: flex-end;
            background-color: #4f46e5;
            color: white;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">Phil - Journaliste Tech</div>
        <div class="chat-messages" id="chat-messages">
            <div class="message bot-message">Bonjour, je suis Phil, votre journaliste tech. Que souhaitez-vous savoir sur la technologie ?</div>
        </div>
        <form id="chat-form" style="display: flex; padding: 10px; border-top: 1px solid #ddd;">
            <input type="text" id="chat-input" placeholder="Tapez votre message..." style="flex: 1; padding: 10px; border-radius: 10px; border: 1px solid #ccc;"/>
            <button type="submit" style="margin-left: 10px; padding: 10px 20px; border-radius: 10px; background-color: #4f46e5; color: white; border: none;">Envoyer</button>
        </form>
    </div>
    <script>
        const form = document.getElementById('chat-form');
        const input = document.getElementById('chat-input');
        const messages = document.getElementById('chat-messages');

        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            const text = input.value.trim();
            if (text === '') return;
            const userMessage = document.createElement('div');
            userMessage.className = 'message user-message';
            userMessage.textContent = text;
            messages.appendChild(userMessage);
            input.value = '';
            messages.scrollTop = messages.scrollHeight;

            let page = 1;
            async function fetchResponse(message, page) {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({message: message, page: page}),
                });
                return await response.json();
            }

            const data = await fetchResponse(text, page);
            const botMessage = document.createElement('div');
            botMessage.className = 'message bot-message';
            // Use innerHTML to render clickable links properly
            botMessage.innerHTML = data.response;
            messages.appendChild(botMessage);
            messages.scrollTop = messages.scrollHeight;

            while (data.has_more) {
                page++;
                const nextData = await fetchResponse(text, page);
                const nextBotMessage = document.createElement('div');
                nextBotMessage.className = 'message bot-message';
                nextBotMessage.innerHTML = nextData.response;
                messages.appendChild(nextBotMessage);
                messages.scrollTop = messages.scrollHeight;
                if (!nextData.has_more) break;
            }
        });
    </script>
</body>
</html>"""
    return render_template_string(html)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')

    full_response = agent.generate_response(user_message)

    return jsonify({'response': full_response, 'has_more': False})

if __name__ == '__main__':
    app.run(debug=True)
