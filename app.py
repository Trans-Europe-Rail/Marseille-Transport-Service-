import os
import requests
from flask import Flask, render_template, abort

app = Flask(__name__)

BOT_API_URL = os.environ.get("BOT_API_URL", "").rstrip("/")
API_SECRET = os.environ.get("API_SECRET", "")

# Récapitulatif statique des commandes du bot (affiché sur /commandes)
COMMANDES = [
    {"cat": "Prise & suivi de service", "commands": [
        ("/debut", "Lance ta prise de service : ligne, arrêt de départ, bus, dépôt, météo en jeu"),
        ("/pause", "Met ton service en pause"),
        ("/reprise", "Reprend ton service après une pause (le temps de pause est déduit automatiquement)"),
        ("/changement_bus", "Déclare un bus de secours en cas de panne ou de crash en cours de route"),
        ("/fin", "Termine ton service : compte-rendu complet, CSV joint et envoyé par mail"),
    ]},
    {"cat": "Signalement", "commands": [
        ("/incident", "Signale un incident avec type et gravité, transmis dans #incidents"),
        ("/signalement_arret", "Signale un problème sur un arrêt ou une portion de route"),
        ("/garage_secours", "Demande l'envoi d'une assistance technique d'urgence"),
    ]},
    {"cat": "Stats & suivi", "commands": [
        ("/actifs", "Affiche qui est en service en ce moment"),
        ("/classement", "Classement des conducteurs par temps de service"),
        ("/profil", "Statistiques personnelles : temps cumulé, services, salaire virtuel"),
        ("/historique_recent", "Les 5 derniers services de la compagnie"),
    ]},
    {"cat": "Administration", "commands": [
        ("/reseau_stats", "Statistiques globales de la compagnie (admin)"),
        ("/prime", "Ajoute ou retire une prime à un conducteur (admin)"),
        ("/admin_reset_service", "Force l'arrêt d'un service bloqué (admin)"),
    ]},
    {"cat": "Autres", "commands": [
        ("/soutien", "Affiche la valeur du bot et le lien pour soutenir le développeur"),
        ("/consignes", "Rappel du règlement et des bonnes pratiques"),
        ("/meteo_jeu", "Configure les conditions de saison et de température"),
    ]},
]


def get_dashboard_data():
    if not BOT_API_URL:
        return {"actifs": [], "classement": [], "historique": [], "historique_complet": []}
    try:
        resp = requests.get(
            f"{BOT_API_URL}/api/dashboard",
            headers={"X-API-Key": API_SECRET},
            timeout=5,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Erreur récupération données bot : {e}")
        return {"actifs": [], "classement": [], "historique": [], "historique_complet": []}


@app.route("/")
def home():
    data = get_dashboard_data()
    return render_template(
        "index.html",
        actifs=data.get("actifs", []),
        classement=data.get("classement", []),
        historique=data.get("historique", []),
    )


@app.route("/commandes")
def commandes():
    return render_template("commandes.html", categories=COMMANDES)


@app.route("/conducteur/<nom>")
def conducteur(nom):
    data = get_dashboard_data()
    fiche = next((c for c in data.get("classement", []) if c["nom"] == nom), None)
    services = [h for h in data.get("historique_complet", []) if h["conducteur"] == nom]

    if not fiche and not services:
        abort(404)

    return render_template("conducteur.html", nom=nom, fiche=fiche, services=services)


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
    
