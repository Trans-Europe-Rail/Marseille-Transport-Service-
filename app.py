import os
import csv
import requests
from flask import Flask, render_template, abort, jsonify

app = Flask(__name__)

BOT_API_URL = os.environ.get("BOT_API_URL", "").rstrip("/")
API_SECRET = os.environ.get("API_SECRET", "")
FICHIER_FACTURES = "historique_factures.csv"

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
    # Données par défaut si l'API du bot ne répond pas
    data = {"actifs": [], "classement": [], "historique": [], "historique_complet": []}
    
    if BOT_API_URL:
        try:
            resp = requests.get(
                f"{BOT_API_URL}/api/dashboard",
                headers={"X-API-Key": API_SECRET},
                timeout=5,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"Erreur récupération données bot : {e}")

    # Lecture des factures stockées localement
    factures = []
    if os.path.exists(FICHIER_FACTURES):
        try:
            with open(FICHIER_FACTURES, "r", encoding="utf-8") as f:
                lignes_fac = list(csv.reader(f))
            if len(lignes_fac) > 1:
                for row in reversed(lignes_fac[1:]):
                    factures.append({
                        "date": row[0], 
                        "conducteur": row[1], 
                        "type": row[2],
                        "libelle": row[3], 
                        "solde_depart": row[4], 
                        "montant": row[5], 
                        "solde_fin": row[6]
                    })
        except Exception as e:
            print(f"Erreur lecture factures CSV : {e}")

    # On fusionne le tout dans un seul dictionnaire
    data["factures"] = factures
    return data

@app.route("/")
def home():
    data = get_dashboard_data()
    return render_template(
        "index.html",
        actifs=data.get("actifs", []),
        classement=data.get("classement", []),
        historique=data.get("historique", []),
    )

@app.route("/actifs")
def page_actifs():
    data = get_dashboard_data()
    return render_template("actifs.html", actifs=data.get("actifs", []))

@app.route("/classement")
def page_classement():
    data = get_dashboard_data()
    return render_template("classement.html", classement=data.get("classement", []))

@app.route("/historique")
def page_historique():
    data = get_dashboard_data()
    return render_template("historique.html", historique=data.get("historique_complet", data.get("historique", [])))

@app.route("/factures")
def page_factures():
    data = get_dashboard_data()
    return render_template("factures.html", factures=data.get("factures", []))

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

@app.route("/api/data")
def api_data():
    return jsonify(get_dashboard_data())

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
    
