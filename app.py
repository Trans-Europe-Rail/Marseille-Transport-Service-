import os
import requests
from flask import Flask, render_template

app = Flask(__name__)

# URL de l'API exposée par le service du bot (Render), ex: https://mon-bot.onrender.com
BOT_API_URL = os.environ.get("BOT_API_URL", "").rstrip("/")


@app.route("/")
def home():
    actifs, classement, historique = [], [], []

    if BOT_API_URL:
        try:
            resp = requests.get(f"{BOT_API_URL}/api/dashboard", timeout=5)
            resp.raise_for_status()
            data = resp.json()
            actifs = data.get("actifs", [])
            classement = data.get("classement", [])
            historique = data.get("historique", [])
        except Exception as e:
            print(f"Erreur récupération données bot : {e}")

    return render_template("index.html", actifs=actifs, classement=classement, historique=historique)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
  
