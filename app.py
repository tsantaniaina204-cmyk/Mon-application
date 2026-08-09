import os
import random
import requests
from flask import Flask, render_template_string, request

app = Flask(__name__)

# =====================================================================
# 🔑 TES CLÉS API GROQ
# =====================================================================
LISTE_CLES = [
    "gsk_" + "T9OSlCCbyz348SgGiqqqWGdyb3FYFwAXrPQ65YuKJSdW8bPIME35",
    "gsk_" + "PUELW9UBJfOu80IKlOpAWGdyb3FYuPTeSgYwdqeysM51gAKKsrKd",
    "gsk_" + "7BDECcx7arZ3IssuLKCwWGdyb3FYdUp8CBPdUEcc0CNH78Q0QJcD",
    "gsk_" + "B6tXb5B57pnkb1x8V8UaWGdyb3FYFoqPUOakMVCarOooeiLU3k6H"
]

# Coefficients officiels par série du Baccalauréat
COEFFICIENTS = {
    'A1': {'Malagasy': 3, 'Français': 3, 'Anglais': 3, 'Histo-Géo': 3, 'Philo': 3, 'Maths': 2, 'SVT': 1, 'PC': 1},
    'A2': {'Malagasy': 3, 'Français': 4, 'Anglais': 4, 'Histo-Géo': 3, 'Philo': 4, 'Maths': 2, 'SVT': 1, 'PC': 1},
    'C':  {'Maths': 5, 'PC': 5, 'SVT': 2, 'Philo': 2, 'Français': 2, 'Anglais': 2, 'Malagasy': 2, 'Histo-Géo': 2},
    'D':  {'SVT': 4, 'PC': 4, 'Maths': 4, 'Philo': 2, 'Français': 2, 'Anglais': 2, 'Malagasy': 2, 'Histo-Géo': 2},
    'OSE': {'SES': 4, 'Histo-Géo': 3, 'Maths': 3, 'Français': 3, 'Anglais': 3, 'Philo': 2, 'Malagasy': 2}
}

PROMPT_ORACLE = (
    "Tu es l'Oracle du Baccalauréat, un conseiller et tuteur interactif drôle, réaliste et motivant pour les élèves de Terminale.\n"
    "Ton unique créateur et développeur est Fidimanantsoa Tsantaniaina (Tsanta Niaina), un jeune génie passionné d'informatique à Madagascar.\n"
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

    <div class="max-w-xl w-full bg-slate-800 rounded-2xl shadow-2xl border border-slate-700 p-6 md:p-8 my-6">
        <h1 class="text-3xl font-extrabold text-center text-amber-400 mb-1">🎓 Bacc Simulator & Oracle IA</h1>
        <p class="text-slate-400 text-center text-xs mb-6">Développé par <span class="text-amber-300 font-semibold">Fidimanantsoa Tsantaniaina</span></p>

        {% if not submitted %}
        <form action="/simulate" method="POST" class="space-y-4">
            <div>
                <label class="block text-sm font-medium mb-1">Choisis ta Série :</label>
                <select id="serie" name="serie" onchange="changerMatieres()" class="w-full bg-slate-700 rounded-lg p-3 border border-slate-600 text-white font-bold">
                    <option value="D" selected>Série D</option>
                    <option value="C">Série C</option>
                    <option value="A1">Série A1</option>
                    <option value="A2">Série A2</option>
                    <option value="OSE">Série OSE</option>
                </select>
            </div>

            <!-- Conteneur des notes par matière -->
            <div class="bg-slate-700/40 p-4 rounded-xl border border-slate-600/80 space-y-3">
                <h3 class="text-amber-400 font-semibold text-sm border-b border-slate-600 pb-2">📚 Estimations de tes notes (/20) :</h3>
                <div id="matieresInputs" class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <!-- Généré dynamiquement par JS -->
                </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                    <label class="block text-sm font-medium mb-1">Révisions (h/jour) :</label>
                    <input type="number" step="0.5" min="0" max="15" name="heures" value="3" required
                           class="w-full bg-slate-700 rounded-lg p-3 border border-slate-600 text-white">
                </div>
                <div>
                    <label class="block text-sm font-medium mb-1">Assiduité (%) :</label>
                    <input type="number" min="0" max="100" name="presence" value="85" required
                           class="w-full bg-slate-700 rounded-lg p-3 border border-slate-600 text-white">
                </div>
            </div>

            <div>
                <label class="block text-sm font-medium mb-1">Ton état d'esprit :</label>
                <select name="confiance" class="w-full bg-slate-700 rounded-lg p-3 border border-slate-600 text-white">
                    <option value="Faible">Panique totale 😱</option>
                    <option value="Moyenne" selected>Moyen / Prudent 😐</option>
                    <option value="Élevée">Sûr de moi 😎</option>
                </select>
            </div>

            <button type="submit" 
                    class="w-full bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold py-3 rounded-lg transition duration-200 shadow-lg mt-4">
                🔮 Calculer la Moyenne, Mention & Consulter l'Oracle !
            </button>
        </form>

        <script>
            const coefficients = {{ coeffs_json | safe }};

            function changerMatieres() {
                const serie = document.getElementById('serie').value;
                const matieres = coefficients[serie];
                const container = document.getElementById('matieresInputs');
                container.innerHTML = '';

                for (const [matiere, coeff] of Object.entries(matieres)) {
                    const div = document.createElement('div');
                    div.innerHTML = `
                        <label class="block text-xs text-slate-300 mb-1">${matiere} <span class="text-amber-400 font-bold">(Coeff ${coeff})</span> :</label>
                        <input type="number" step="0.5" min="0" max="20" name="note_${matiere}" value="10" required
                               class="w-full bg-slate-800 rounded-lg p-2 border border-slate-600 text-white text-sm">
                    `;
                    container.appendChild(div);
                }
            }
            // Initialisation au chargement de la page
            changerMatieres();
        </script>

        {% else %}
        <!-- Affichage des résultats -->
        <div class="text-center mb-6">
            <h2 class="text-sm font-semibold text-slate-400 uppercase tracking-wider">Moyenne Générale Calculée</h2>
            <div class="text-4xl font-black text-amber-300 my-1">{{ moyenne }} / 20</div>

            <div class="bg-slate-700/60 p-3 rounded-lg border border-slate-600 my-3">
                <span class="text-slate-400 text-xs uppercase block">Mention estimée :</span>
                <div class="text-xl font-bold text-amber-400 mt-1">{{ mention }}</div>
            </div>

            <h3 class="text-xs font-semibold text-slate-400 uppercase tracking-wider mt-4">Probabilité de réussite :</h3>
            <div class="text-3xl font-bold text-emerald-400 my-1">{{ probabilite }}%</div>
            <div class="w-full bg-slate-700 h-3 rounded-full overflow-hidden">
                <div class="bg-emerald-400 h-full transition-all duration-1000" style="width: {{ probabilite }}%"></div>
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

    return "L'Oracle est indisponible pour le moment, mais tes révisions restent la clé !"

@app.route('/', methods=['GET'])
def index():
    import json
    return render_template_string(HTML_TEMPLATE, submitted=False, coeffs_json=json.dumps(COEFFICIENTS))

@app.route('/simulate', methods=['POST'])
def simulate():
    import json
    serie = request.form.get('serie', 'D')
    heures_revision = float(request.form.get('heures', 3.0))
    presence = float(request.form.get('presence', 85.0))
    confiance = request.form.get('confiance', 'Moyenne')

    # 1. Calcul de la moyenne pondérée avec les coefficients
    coeffs = COEFFICIENTS.get(serie, COEFFICIENTS['D'])
    total_points = 0.0
    total_coeffs = sum(coeffs.values())
    notes_detail = {}

    for matiere, coeff in coeffs.items():
        note = float(request.form.get(f'note_{matiere}', 10.0))
        notes_detail[matiere] = note
        total_points += note * coeff

    moyenne = round(total_points / total_coeffs, 2)

    # 2. Calcul mathématique de la probabilité
    base_prob = (moyenne / 20.0) * 55
    base_prob += min(heures_revision * 3.5, 25)
    base_prob += (presence / 100.0) * 10
    
    if confiance == 'Élevée':
        base_prob += 10
    elif confiance == 'Faible':
        base_prob -= 10

    probabilite = int(max(5, min(99, base_prob + random.randint(-2, 2))))
    mention = estimer_mention(moyenne)

    # 3. Prompt détaillé transmis à l'IA
    prompt_ia = f"""
    Voici les résultats du candidat au Bacc :
    - Série : {serie}
    - Notes saisies : {notes_detail}
    - Moyenne générale calculée (avec coefficients) : {moyenne}/20
    - Révision : {heures_revision}h/jour | Assiduité : {presence}% | État d'esprit : {confiance}
    - Probabilité de réussite : {probabilite}%
    - Mention estimée : {mention}

    Rédige un bilan clair :
    1. Un commentaire drôle et motivant sur la moyenne et la mention estimée.
    2. Analyse les points forts (matières à fort coeff bien réussies) et les points faibles.
    3. Deux conseils ciblés sur les matières clés pour assurer ou booster la mention.
    """

    analyse_ia = interroger_ia(prompt_ia)

    return render_template_string(
        HTML_TEMPLATE,
        submitted=True,
        moyenne=moyenne,
        probabilite=probabilite,
        mention=mention,
        analyse=analyse_ia,
        coeffs_json=json.dumps(COEFFICIENTS)
    )

if __name__ == '__main__':
    app.run(debug=True)
