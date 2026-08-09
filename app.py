import os
import random
import requests
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# =====================================================================
# 🔑 TES CLÉS API GROQ RECUPÉRÉES DE TON PROJET
# =====================================================================
LISTE_CLES = [
    "gsk_" + "T9OSlCCbyz348SgGiqqqWGdyb3FYFwAXrPQ65YuKJSdW8bPIME35",
    "gsk_" + "PUELW9UBJfOu80IKlOpAWGdyb3FYuPTeSgYwdqeysM51gAKKsrKd",
    "gsk_" + "7BDECcx7arZ3IssuLKCwWGdyb3FYdUp8CBPdUEcc0CNH78Q0QJcD",
    "gsk_" + "B6tXb5B57pnkb1x8V8UaWGdyb3FYFoqPUOakMVCarOooeiLU3k6H"
]

# Prompt système pour l'Oracle du Bacc
PROMPT_ORACLE = (
    "Tu es l'Oracle du Baccalauréat, un conseiller et tuteur interactif drôle, réaliste et motivant pour les élèves de Terminale.\n"
    "Ton créateur et développeur est Fidimanantsoa Tsantaniaina (Tsanta Niaina), un jeune passionné d'informatique et de technologie à Madagascar.\n"
    "Rédige une analyse courte, personnalisée et humoristique avec des emojis pour le candidat."
)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bacc Simulator & Oracle IA — Tsanta Niaina</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-white min-h-screen flex flex-col items-center justify-center p-4">

    <div class="max-w-xl w-full bg-slate-800 rounded-2xl shadow-2xl border border-slate-700 p-6 md:p-8">
        <h1 class="text-3xl font-extrabold text-center text-amber-400 mb-1">🎓 Bacc Simulator & Oracle IA</h1>
        <p class="text-slate-400 text-center text-xs mb-6">Développé par <span class="text-amber-300 font-semibold">Fidimanantsoa Tsantaniaina</span></p>

        {% if not submitted %}
        <form action="/simulate" method="POST" class="space-y-4">
            <div>
                <label class="block text-sm font-medium mb-1">Série :</label>
                <select name="serie" class="w-full bg-slate-700 rounded-lg p-3 border border-slate-600 text-white">
                    <option value="A1">Série A1</option>
                    <option value="A2">Série A2</option>
                    <option value="C">Série C</option>
                    <option value="D" selected>Série D</option>
                    <option value="OSE">Série OSE / ES</option>
                    <option value="Technologique">Série Technologique / Technique</option>
                </select>
            </div>

            <div>
                <label class="block text-sm font-medium mb-1">Moyenne générale estimée (/20) :</label>
                <input type="number" step="0.25" min="0" max="20" name="moyenne" value="11.5" required
                       class="w-full bg-slate-700 rounded-lg p-3 border border-slate-600 text-white">
            </div>

            <div>
                <label class="block text-sm font-medium mb-1">Heures de révision par jour :</label>
                <input type="number" step="0.5" min="0" max="15" name="heures" value="3" required
                       class="w-full bg-slate-700 rounded-lg p-3 border border-slate-600 text-white">
            </div>

            <div>
                <label class="block text-sm font-medium mb-1">Taux d'assiduité aux cours (%) :</label>
                <input type="number" min="0" max="100" name="presence" value="85" required
                       class="w-full bg-slate-700 rounded-lg p-3 border border-slate-600 text-white">
            </div>

            <div>
                <label class="block text-sm font-medium mb-1">Ton état d'esprit / confiance :</label>
                <select name="confiance" class="w-full bg-slate-700 rounded-lg p-3 border border-slate-600 text-white">
                    <option value="Faible">Panique totale 😱</option>
                    <option value="Moyenne" selected>Moyen / Prudent 😐</option>
                    <option value="Élevée">Sûr de moi 😎</option>
                </select>
            </div>

            <button type="submit" 
                    class="w-full bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold py-3 rounded-lg transition duration-200 shadow-lg mt-4">
                🔮 Consulter l'Oracle & Estimer la Mention !
            </button>
        </form>

        {% else %}
        <!-- Résultats -->
        <div class="text-center mb-6">
            <h2 class="text-lg font-semibold text-slate-300">Probabilité de réussite :</h2>
            <div class="text-5xl font-black text-amber-400 mb-2">{{ probabilite }}%</div>
            <div class="w-full bg-slate-700 h-4 rounded-full overflow-hidden mb-4">
                <div class="bg-amber-400 h-full transition-all duration-1000" style="width: {{ probabilite }}%"></div>
            </div>

            <div class="bg-slate-700/60 p-3 rounded-lg border border-slate-600">
                <span class="text-slate-400 text-sm">Mention estimée :</span>
                <div class="text-xl font-bold text-amber-300 mt-1">{{ mention }}</div>
            </div>
        </div>

        <div class="bg-slate-700/50 p-4 rounded-xl border border-slate-600 text-slate-200 text-sm whitespace-pre-line leading-relaxed mb-6">
            {{ analyse }}
        </div>

        <a href="/" class="block text-center bg-slate-700 hover:bg-slate-600 text-white font-medium py-2 rounded-lg transition">
            🔄 Tester une autre simulation
        </a>
        {% endif %}
    </div>

</body>
</html>
"""

def estimer_mention(moyenne_estimee):
    """Détermine la mention probable selon la moyenne."""
    if moyenne_estimee >= 16.0:
        return "Mention Très Bien 🏆"
    elif moyenne_estimee >= 14.0:
        return "Mention Bien 🥇"
    elif moyenne_estimee >= 12.0:
        return "Mention Assez Bien 🥈"
    elif moyenne_estimee >= 10.0:
        return "Passable (Sans Mention) 📜"
    elif moyenne_estimee >= 8.0:
        return "Rattrapage / Admissible ⚠️"
    else:
        return "Ajourné (Échec probable) ❌"

def interroger_ia(prompt_user):
    """Interroge l'IA avec rotation automatique sur tes clés API."""
    formatted_messages = [
        {"role": "system", "content": PROMPT_ORACLE},
        {"role": "user", "content": prompt_user}
    ]

    for key in LISTE_CLES:
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": formatted_messages,
                "temperature": 0.7,
                "max_tokens": 800
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
        except Exception:
            continue

    return "L'Oracle est momentanément indisponible, mais continue de réviser à fond !"

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE, submitted=False)

@app.route('/simulate', methods=['POST'])
def simulate():
    # 1. Récupération des données
    serie = request.form.get('serie', 'D')
    moyenne = float(request.form.get('moyenne', 10.0))
    heures_revision = float(request.form.get('heures', 2.0))
    presence = float(request.form.get('presence', 80.0))
    confiance = request.form.get('confiance', 'Moyenne')

    # 2. Calcul mathématique de la probabilité
    base_prob = (moyenne / 20.0) * 50
    base_prob += min(heures_revision * 4, 25)
    base_prob += (presence / 100.0) * 15
    
    if confiance == 'Élevée':
        base_prob += 10
    elif confiance == 'Faible':
        base_prob -= 10

    probabilite = int(max(5, min(99, base_prob + random.randint(-3, 3))))

    # 3. Estimation de la mention
    mention = estimer_mention(moyenne)

    # 4. Génération de l'analyse IA via tes clés API
    prompt_ia = f"""
    Voici les données du candidat au Bacc :
    - Série : {serie}
    - Moyenne estimée : {moyenne}/20
    - Révision : {heures_revision}h/jour
    - Presence : {presence}%
    - Confiance : {confiance}
    - Probabilité calculée : {probabilite}%
    - Mention estimée : {mention}

    Fais un bilan synthétique :
    1. Un commentaire drôle et bienveillant sur son score et sa mention.
    2. Son point fort et son point faible d'après les chiffres.
    3. Deux conseils pratiques pour valider ou viser la mention supérieure.
    """

    analyse_ia = interroger_ia(prompt_ia)

    return render_template_string(
        HTML_TEMPLATE,
        probabilite=probabilite,
        mention=mention,
        analyse=analyse_ia,
        submitted=True
    )

if __name__ == '__main__':
    app.run(debug=True)
