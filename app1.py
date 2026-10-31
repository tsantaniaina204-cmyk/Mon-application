from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

game_state = {
    "messages": [],
    "scores": {}
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chrono-Royaume Magique</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f9;
            margin: 0;
            padding: 10px;
        }
        .container {
            max-width: 500px;
            margin: 0 auto;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #007bff;
            color: white;
            padding: 10px;
            border-radius: 5px;
        }
        .scores {
            margin: 10px 0;
            padding: 8px;
            background: #e9ecef;
            border-radius: 4px;
            font-weight: bold;
            font-size: 0.9em;
        }
        .chat-box {
            height: 250px;
            border: 1px solid #ccc;
            overflow-y: scroll;
            padding: 10px;
            margin-bottom: 10px;
            background: #fafafa;
            border-radius: 4px;
        }
        .msg {
            margin-bottom: 8px;
            padding: 8px;
            background: #fff;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 0.9em;
        }
        .input-area {
            display: flex;
            gap: 5px;
        }
        input[type="text"], select {
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 4px;
            width: 100%;
            margin-bottom: 5px;
            font-size: 1em;
        }
        .btn {
            background: #28a745;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
        }
        .btn-reset {
            background: #dc3545;
            color: white;
            text-decoration: none;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 0.8em;
        }
        .delete-link {
            color: red;
            float: right;
            text-decoration: none;
            font-weight: bold;
        }
    </style>
</head>
<body>

<div class="container">
    <div class="header">
        <span>Chrono-Royaume Magique</span>
        <a href="/reset" class="btn-reset">Reset</a>
    </div>

    <div class="scores">
        Scores : 
        {% if scores %}
            {% for user, pts in scores.items() %}
                <span>{{ user }}: {{ pts }} pts | </span>
            {% endfor %}
        {% else %}
            <span>Aucun score</span>
        {% endif %}
    </div>

    <!-- Formulaire principal standard -->
    <form action="/send" method="POST">
        <div>
            <label>Prénom :</label>
            <input type="text" name="username" value="Tsanta" required>
        </div>
        <div>
            <label>Rôle :</label>
            <select name="role">
                <option value="Sorcier">Sorcier</option>
                <option value="Magicien">Magicien</option>
                <option value="Guerrier">Guerrier</option>
                <option value="Roi/Reine">Roi/Reine</option>
            </select>
        </div>
        <div>
            <label>Scénario :</label>
            <select name="scenario">
                <option value="Royaume Effondré">Royaume Effondré</option>
                <option value="Faille Temporelle">Faille Temporelle</option>
            </select>
        </div>

        <div class="chat-box" id="chatbox">
            {% for m in messages %}
                <div class="msg">
                    <a href="/delete/{{ loop.index0 }}" class="delete-link">X</a>
                    <strong>{{ m.sender }} ({{ m.role }}) :</strong> {{ m.text }} 
                    <br><small style="color: #666;">⚖️ {{ m.comment }} (+{{ m.points }} pts)</small>
                </div>
            {% endfor %}
        </div>

        <div class="input-area">
            <input type="text" name="text" placeholder="Votre message..." required autocomplete="off">
            <button type="submit" class="btn">Envoyer</button>
        </div>
    </form>
</div>

<script>
    // Fait défiler le chat automatiquement en bas
    const cb = document.getElementById('chatbox');
    if(cb) { cb.scrollTop = cb.scrollHeight; }
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, messages=game_state["messages"], scores=game_state["scores"])

@app.route('/send', methods=['POST'])
def send():
    sender = request.form.get('username', 'Anonyme').strip() or 'Anonyme'
    role = request.form.get('role', 'Sorcier')
    scenario = request.form.get('scenario', 'Général')
    text = request.form.get('text', '').strip()
    
    if text:
        points = 10
        comment = "Réplique validée !"
        if 'amour' in text.lower() or 't’aime' in text.lower():
            points = 20
            comment = "Magnifique message romantique !"

        if sender not in game_state["scores"]:
            game_state["scores"][sender] = 100
        game_state["scores"][sender] += points
        
        game_state["messages"].append({
            "sender": sender,
            "role": role,
            "text": text,
            "comment": comment,
            "points": points
        })
        
    return redirect(url_for('index'))

@app.route('/delete/<int:index>')
def delete_msg(index):
    if 0 <= index < len(game_state["messages"]):
        game_state["messages"].pop(index)
    return redirect(url_for('index'))

@app.route('/reset')
def reset_data():
    game_state["messages"] = []
    game_state["scores"] = {}
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)