import os
import csv
import requests
from flask import Flask, render_template, abort, jsonify
from lignes_data import LIGNES

app = Flask(__name__)

BOT_API_URL = os.environ.get("BOT_API_URL", "").rstrip("/")
API_SECRET = os.environ.get("API_SECRET", "")
FICHIER_FACTURES = "historique_factures.csv"

COMMANDES = [
    {"cat": "Prise & suivi de service", "commands": [
        ("/debut", "Lance ta prise de service OMSI 2"),
        ("/pause", "Met ton service en pause"),
        ("/reprise", "Reprend ton service après une pause"),
        ("/changement_bus", "Change de bus en cours de route en cas de pépin ou de crash"),
        ("/fin", "Termine ton service et génère le compte-rendu OMSI 2"),
        ("/essence", "Enregistre un passage au dépôt pour faire le plein ou recharger ton bus"),
    ]},
    {"cat": "Signalement", "commands": [
        ("/incident", "Signale un incident ou une panne sur ta ligne"),
        ("/signalement_arret", "Signale un problème sur un arrêt ou une portion de route"),
        ("/garage_secours", "Demande l'envoi d'une assistance technique d'urgence"),
        ("/greve", "Déclare un mouvement de grève sur le réseau"),
    ]},
    {"cat": "Stats & suivi personnel", "commands": [
        ("/profil", "Affiche tes statistiques personnelles de conducteur"),
        ("/actifs", "Affiche la liste des conducteurs actuellement en service"),
        ("/classement", "Affiche le classement des meilleurs conducteurs"),
        ("/historique_recent", "Affiche les 5 derniers services enregistrés de la compagnie"),
        ("/solde", "Vérifie ton salaire virtuel et ton solde actuel"),
        ("/bonus_carburant", "Vérifie ton bonus d'éco-conduite du mois"),
    ]},
    {"cat": "Finances", "commands": [
        ("/facture", "Génère et envoie une facture d'achat (bus ou gazole) dans le salon #factures"),
        ("/bilan_financier", "[PROPRIÉTAIRE] Affiche le rapport financier global de l'entreprise"),
        ("/taxe", "[PROPRIÉTAIRE] Applique une taxe de régulation financière exceptionnelle"),
        ("/prime", "[PROPRIÉTAIRE] Ajoute ou retire une prime financière à un conducteur"),
        ("/prime_speciale", "[PROPRIÉTAIRE] Attribue une prime exceptionnelle à l'ensemble des chauffeurs"),
    ]},
    {"cat": "Flotte & exploitation", "commands": [
        ("/inventaire_bus", "Affiche la flotte des véhicules officiels de la compagnie"),
        ("/acheter_bus", "[PROPRIÉTAIRE] Ajoute un nouveau bus au catalogue de la compagnie"),
        ("/reparer_bus", "Envoie un bus en maintenance d'urgence au garage suite à des dégâts"),
        ("/planning", "Affiche le planning des lignes et des services recommandés de la semaine"),
        ("/contrat", "Consulte les contrats de transport spéciaux en cours pour la compagnie"),
        ("/mission", "Accepte une mission spéciale aléatoire pour ta prochaine tournée"),
        ("/carte_du_jeu", "Accès aux différentes lignes du réseau"),
    ]},
    {"cat": "Ambiance & confort de jeu", "commands": [
        ("/meteo_live", "Vérifie les conseils météo pour configurer correctement ton jeu OMSI 2"),
        ("/meteo_jeu", "Configure les conditions de saison et de température pour ta ligne"),
        ("/radio", "Choisis ou affiche la station de radio jouée dans ton bus en jeu"),
    ]},
    {"cat": "Ressources humaines", "commands": [
        ("/recruter", "[PROPRIÉTAIRE] Affiche les instructions pour intégrer de nouveaux chauffeurs"),
        ("/licencier", "[PROPRIÉTAIRE] Retire un conducteur de l'effectif de la compagnie"),
        ("/conge", "Déclare une demande de congé"),
        ("/absence", "Signale une absence"),
    ]},
    {"cat": "Administration", "commands": [
        ("/reseau_stats", "[PROPRIÉTAIRE/ADMIN] Affiche les statistiques globales de toute la compagnie"),
        ("/admin_reset_service", "[PROPRIÉTAIRE] Force l'arrêt d'un service bloqué pour un utilisateur"),
    ]},
    {"cat": "Autres", "commands": [
        ("/soutien", "Affiche la valeur réelle du bot et le lien pour participer"),
        ("/consignes", "Affiche le rappel du règlement et des bonnes pratiques de la compagnie"),
        ("/aide_conducteur", "Affiche le guide rapide de prise en main du bot pour les chauffeurs"),
    ]},
]

def get_dashboard_data():
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

    factures = []
    total_bus = 0
    total_gazole = 0
    montant_total_depense = 0

    if os.path.exists(FICHIER_FACTURES):
        try:
            with open(FICHIER_FACTURES, "r", encoding="utf-8") as f:
                lignes_fac = list(csv.reader(f))
            if len(lignes_fac) > 1:
                for row in reversed(lignes_fac[1:]):
                    montant = int(row[5]) if row[5].isdigit() else 0
                    type_achat = row[2]

                    if type_achat == "Bus":
                        total_bus += montant
                    elif type_achat == "Gazole":
                        total_gazole += montant
                    
                    montant_total_depense += montant

                    factures.append({
                        "date": row[0], 
                        "conducteur": row[1], 
                        "type": type_achat,
                        "libelle": row[3], 
                        "solde_depart": row[4], 
                        "montant": montant, 
                        "solde_fin": row[6]
                    })
        except Exception as e:
            print(f"Erreur lecture factures CSV : {e}")

    data["factures"] = factures
    data["stats_factures"] = {
        "total_bus": total_bus,
        "total_gazole": total_gazole,
        "total_global": montant_total_depense,
        "nombre_total": len(factures)
    }
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
    return render_template("factures.html", factures=data.get("factures", []), stats_factures=data.get("stats_factures", {}))

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

CATEGORIES_LIGNES = ["Métro", "Tram", "Bus", "Car départemental", "Car régional", "Bus des Collines", "Bus de la Marcouline", "Bus de la Côte Bleue", "Navette maritime"]

@app.route('/lignes')
def lignes():
    categories = {}
    for cat in CATEGORIES_LIGNES:
        items = [(num, l) for num, l in LIGNES.items() if l["type"] == cat]
        if items:
            categories[cat] = items
    return render_template('lignes.html', categories=categories, total=len(LIGNES))

@app.route('/lignes/<numero>')
def ligne_detail(numero):
    ligne = LIGNES.get(numero)
    if not ligne:
        abort(404)
    return render_template('ligne_detail.html', numero=numero, ligne=ligne)

@app.route('/carte')
def carte():
    couleurs = {
        "Métro": "#5bc0eb",
        "Tramway": "#FF6FA5",
        "Bus": "#F2A24C",
        "Car départemental": "#8B7FD4",
        "Car régional": "#6FCF97",
        "Bus des Collines": "#D4A574",
        "Bus de la Marcouline": "#7FB3D5",
        "Bus de la Côte Bleue": "#5BC0BE",
        "Navette maritime": "#4FA5D8",
    }
    blocs = []
    for cat in CATEGORIES_LIGNES:
        items = sorted([num for num, l in LIGNES.items() if l["type"] == cat])
        blocs.append((cat, couleurs.get(cat, "#5bc0eb"), items))
    return render_template('carte.html', blocs=blocs)
    
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))


