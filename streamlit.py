import streamlit as st
import requests
import matplotlib.pyplot as plt
import pandas as pd

API_BASE_URL = "http://127.0.0.1:5000"

# Fonction pour se connecter et obtenir un token
def login(username, password):
    response = requests.post(f"{API_BASE_URL}/login", json={"username": username, "password": password})
    if response.status_code == 200:
        return response.json().get("token")
    return None

# Fonction pour récupérer les détails d'un Pokémon
def get_pokemon_details(name, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE_URL}/pokemon/{name}", headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

# Interface utilisateur Streamlit
st.title("Pokémon App 🏆")

# Formulaire de connexion
if "token" not in st.session_state:
    st.session_state["token"] = None
if "page" not in st.session_state:
    st.session_state["page"] = 1
if "items_per_page" not in st.session_state:
    st.session_state["items_per_page"] = 10

if st.session_state["token"] is None:
    with st.form("login_form"):
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        submitted = st.form_submit_button("Se connecter")
        
        if submitted:
            token = login(username, password)
            if token:
                st.session_state["token"] = token
                st.success("Connexion réussie !")
                st.rerun()
            else:
                st.error("Identifiants incorrects")
else:
    st.sidebar.write("✅ Connecté !")
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    
    # Pagination
    st.session_state["items_per_page"] = st.sidebar.selectbox("Pokémon par page", [10, 20, 30, 50])
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅️ Précédent") and st.session_state["page"] > 1:
            st.session_state["page"] -= 1
            st.rerun()
    with col2:
        if st.button("Suivant ➡️"):
            st.session_state["page"] += 1
            st.rerun()
    
    # Récupération des Pokémon
    response = requests.get(f"{API_BASE_URL}/pokemon/list/{st.session_state['page']}/{st.session_state['items_per_page']}", headers=headers)
    if response.status_code == 200:
        data = response.json().get("results", [])
        pokemon_names = [poke["name"] for poke in data]
        selected_pokemon = st.selectbox("Choisissez un Pokémon :", pokemon_names)
        
        if selected_pokemon:
            details = get_pokemon_details(selected_pokemon, st.session_state['token'])
            if details:
                st.image(details["image"], caption=details["name"].capitalize(), width=200)
                st.write(f"**Nom :** {details['name'].capitalize()}")
                st.write(f"**Taille :** {details['height'] / 10} m")
                st.write(f"**Poids :** {details['weight'] / 10} kg")
                st.write(f"**Types :** {', '.join(details['types'])}")
                
                # Graphique de répartition des types
                st.subheader("Répartition des Types")
                type_counts = pd.Series(details['types']).value_counts()
                fig, ax = plt.subplots()
                type_counts.plot(kind='bar', ax=ax, color='skyblue')
                ax.set_ylabel("Nombre")
                ax.set_xlabel("Type de Pokémon")
                ax.set_title("Répartition des Types de Pokémon")
                st.pyplot(fig)
                
                # Graphique de la taille et du poids
                st.subheader("Comparaison Taille vs Poids")
                fig, ax = plt.subplots()
                ax.bar(["Taille (m)", "Poids (kg)"], [details['height'] / 10, details['weight'] / 10], color=['green', 'orange'])
                ax.set_ylabel("Valeur")
                ax.set_title("Comparaison de la Taille et du Poids")
                st.pyplot(fig)
            else:
                st.error("Impossible de récupérer les détails du Pokémon")
    else:
        st.error(f"Erreur {response.status_code}: {response.text}")
