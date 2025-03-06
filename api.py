from flask import Flask, jsonify, request
import requests
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
POKEMON_API_URL = "https://pokeapi.co/api/v2/pokemon"
app.config['SECRET_KEY'] = 'supersecretkey'  # Clé secrète pour JWT

# Décorateur pour vérifier l'authentification
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Token manquant, accès refusé"}), 401
        try:
            decoded_token = jwt.decode(token.split("Bearer ")[-1], app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expiré"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token invalide"}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def get_accueil():
    return jsonify({"name": "Bienvenue"})

@app.route('/login', methods=['POST'])
def login():
    auth = request.json
    if not auth or not auth.get('username') or not auth.get('password'):
        return jsonify({"error": "Nom d'utilisateur et mot de passe requis"}), 400
    if auth['username'] == 'amal' and auth['password'] == 'chafter':  # Utilisateur fictif
        token = jwt.encode({'user': auth['username'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token})
    return jsonify({"error": "Identifiants incorrects"}), 401

@app.route('/pokemon/list/<int:page>/<int:items>', methods=['GET'])
@token_required
def get_pagination_pokemon(page, items):
    offset = (page - 1) * items
    response = requests.get(f"{POKEMON_API_URL}?limit={items}&offset={offset}")
    if response.status_code == 200:
        data = response.json()
        return jsonify({
            'count': data['count'],
            'pokemon_liste': [poke['name'] for poke in data['results']],
            'results': data['results']
        }), 200
    return jsonify({"error": "Impossible de récupérer les Pokémon"}), 400

@app.route('/pokemon/<string:name>', methods=['GET'])
@token_required
def get_pokemon(name):
    response = requests.get(f"{POKEMON_API_URL}/{name}/")
    if response.status_code == 200:
        data = response.json()
        return jsonify({
            "name": data["name"],
            "height": data["height"],
            "weight": data["weight"],
            "types": [t["type"]["name"] for t in data["types"]],
            "image": data["sprites"]["front_default"]
        }), 200
    return jsonify({"error": "Pokémon non trouvé"}), 404

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
