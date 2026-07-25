import os
from flask import Flask, render_template

app = Flask(__name__)

# Liste complète de toutes les commandes du bot (pour la page /commandes)
COMMANDES = [
    {
        "cat": "Prise & suivi de service",
        "commands": [
            ("/debut", "Lance ta prise de service : ligne, arrêt de départ, bus, dépôt, météo en jeu"),
            ("/pause", "Met ton service en pause"),
            ("/reprise", "Reprend ton service après une pause (le temps de pause est déduit automatiquement)"),
            ("/changement_bus", "Déclare un bus de secours en cas de panne ou de crash en cours de route"),
            ("/fin", "Termine ton service : compte-rendu complet, CSV joint et envoyé par mail"),
        ]
    },
    {
        "cat": "Signalement & Assistance",
        "commands": [
            ("/incident", "Signale un incident avec type et gravité, transmis dans #incidents"),
            ("/signalement_arret", "Signale un problème sur un arrêt ou une portion de route"),
            ("/garage_secours", "Demande l'envoi d'une assistance technique d'urgence"),
        ]
    },
    {
        "cat": "Stats & Suivi",
        "commands": [
            ("/actifs", "Affiche qui est en service en ce moment"),
            ("/classement", "Classement des conducteurs par temps de service"),
            ("/profil", "Statistiques personnelles : temps cumulé, services, salaire virtuel"),
            ("/historique_recent", "Les 5 derniers services de la compagnie"),
            ("/solde", "Vérifie ton salaire virtuel et ton solde actuel"),
        ]
    },
    {
        "cat": "Finances & Facturation",
        "commands": [
            ("/facture", "Génère et envoie une facture d'achat (bus ou gazole) avec fichier Excel au format .xlsx"),
            ("/essence", "Enregistre un passage au dépôt pour faire le plein ou recharger ton bus"),
        ]
    },
    {
        "cat": "Immersion & Vie du réseau",
        "commands": [
            ("/planning", "Affiche le planning des lignes et des services recommandés de la semaine"),
            ("/contrat", "Consulte les contrats de transport spéciaux en cours pour la compagnie"),
            ("/mission", "Accepte une mission spéciale aléatoire pour ta prochaine tournée"),
            ("/meteo_live", "Vérifie les conseils météo pour configurer correctement ton jeu OMSI 2"),
            ("/meteo_jeu", "Configure les conditions de saison et de température pour ta ligne"),
            ("/inventaire_bus", "Affiche la flotte des véhicules officiels de la compagnie"),
            ("/bonus_carburant", "Vérifie ton bonus d'éco-conduite du mois"),
            ("/radio", "Choisis ou affiche la station de radio jouée dans ton bus en jeu"),
            ("/carte_du_jeu", "Accès interactif aux différentes lignes du réseau (Métro et Bus)"),
            ("/consignes", "Rappel du règlement et des bonnes pratiques de la compagnie"),
            ("/aide_conducteur", "Affiche le guide rapide de prise en main du bot pour les chauffeurs"),
        ]
    },
    {
        "cat": "Administration & Propriétaire",
        "commands": [
            ("/reseau_stats", "Statistiques globales de la compagnie (admin)"),
            ("/prime", "Ajoute ou retire une prime à un conducteur (admin)"),
            ("/admin_reset_service", "Force l'arrêt d'un service bloqué (admin)"),
            ("/acheter_bus", "Ajoute un nouveau bus au catalogue de la compagnie (admin)"),
            ("/reparer_bus", "Envoie un bus en maintenance d'urgence au garage"),
            ("/licencier", "Retire un conducteur de l'effectif de la compagnie (admin)"),
            ("/recruter", "Affiche les instructions pour intégrer de nouveaux chauffeurs (admin)"),
            ("/taxe", "Applique une taxe de régulation financière exceptionnelle (admin)"),
            ("/bilan_financier", "Affiche le rapport financier global de l'entreprise (admin)"),
            ("/prime_speciale", "Attribue une prime exceptionnelle à l'ensemble des chauffeurs (admin)"),
        ]
    },
    {
        "cat": "Autres",
        "commands": [
            ("/soutien", "Affiche la valeur du bot et le lien pour soutenir le développeur"),
            ("/conge", "Déclare une demande de congé"),
            ("/absence", "Signale une absence"),
            ("/greve", "Déclare un mouvement de grève sur le réseau"),
        ]
    },
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/commandes')
def commandes():
    return render_template('commandes.html', categories=COMMANDES)

@app.route('/lignes')
def lignes():
    return render_template('lignes.html')

# (Tu laisses tes autres routes /actifs, /classement, etc. ici...)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
