"""
app.py
======
API Flask pour l'analyse de photos ET videos signalees par les benevoles.
100% LOCAL - aucun appel a une API payante.

Routes :
  POST /analyser-photo  - Analyse une image ou video
  GET  /health          - Verification de sante
  GET  /formats         - Liste des formats acceptes
  GET  /                - Page de test interactive (pour la demo)
"""

import os
import tempfile
import time
import uuid

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from rules_engine import generer_mission
from vision_classifier import classify_image

# -- Initialisation de Flask --
app = Flask(__name__)
CORS(app)

# -- Configuration --
MAX_FILE_SIZE_MB = 50  # Limite : 50 Mo max par fichier
ALLOWED_EXTENSIONS = {
    # Images
    "png", "jpg", "jpeg", "gif", "webp",
    # Videos
    "mp4", "mov", "avi", "mkv", "webm", "flv", "wmv",
}
VIDEO_EXTENSIONS = {"mp4", "mov", "avi", "mkv", "webm", "flv", "wmv"}


def allowed_file(filename: str) -> bool:
    """Verifie que le fichier a une extension valide."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def is_video(filename: str) -> bool:
    """Verifie si le fichier est une video."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in VIDEO_EXTENSIONS


# ==============================
# ROUTES
# ==============================

@app.route("/", methods=["GET"])
def index():
    """Page de test interactive pour la demo hackathon."""
    return send_from_directory(".", "index.html")


@app.route("/analyser-photo", methods=["POST"])
def analyser_photo():
    """
    Endpoint principal : recoit une image ou video et retourne l'analyse.

    Accepte :
        - Images : jpg, png, gif, webp
        - Videos : mp4, mov, avi, mkv, webm, flv, wmv
        (pour les videos, une frame est automatiquement extraites)

    Request (multipart/form-data) :
        - fichier : image ou video (champ 'image', 'fichier', ou 'video')

    Response (JSON) :
        - classification_locale : resultat CLIP
        - mission : recommandations generees par les regles
        - statut : "ok" ou "partiel"
    """
    debut = time.time()

    # -- Etape 1 : Recuperer le fichier --
    file = (
        request.files.get("image")
        or request.files.get("fichier")
        or request.files.get("video")
    )

    if not file or file.filename == "":
        return jsonify({
            "erreur": True,
            "message": "Aucun fichier fourni. Envoyez une image ou video dans le champ 'image', 'fichier', ou 'video'."
        }), 400

    if not allowed_file(file.filename):
        exts = ", ".join(sorted(ALLOWED_EXTENSIONS))
        return jsonify({
            "erreur": True,
            "message": f"Format non supporte ({file.filename}). Extensions acceptees : {exts}"
        }), 400

    # -- Etape 2 : Verifier la taille du fichier --
    file.seek(0, os.SEEK_END)
    taille_mo = file.tell() / (1024 * 1024)
    file.seek(0)

    if taille_mo > MAX_FILE_SIZE_MB:
        return jsonify({
            "erreur": True,
            "message": f"Fichier trop volumineux ({taille_mo:.1f} Mo). Limite : {MAX_FILE_SIZE_MB} Mo."
        }), 400

    # -- Etape 3 : Sauvegarder dans un fichier temporaire --
    ext = file.filename.rsplit(".", 1)[1].lower()
    temp_filename = f"upload_{uuid.uuid4().hex}.{ext}"
    temp_path = os.path.join(tempfile.gettempdir(), temp_filename)

    try:
        file.save(temp_path)
    except Exception as e:
        return jsonify({
            "erreur": True,
            "message": f"Erreur lors de la sauvegarde : {str(e)}"
        }), 500

    # -- Etape 4 : Classification (image ou frame de video) --
    try:
        cv_result = classify_image(temp_path)
    except Exception as e:
        _cleanup(temp_path)
        return jsonify({
            "erreur": True,
            "message": f"Erreur de classification : {str(e)}"
        }), 503

    # -- Etape 5 : Generation des recommandations --
    try:
        mission = generer_mission(
            classe=cv_result["classe"],
            confiance=cv_result["confiance"],
            alternatives=cv_result["alternatives"],
        )
    except Exception as e:
        mission = {"erreur": True, "message": f"Erreur moteur de regles : {str(e)}"}

    # -- Etape 6 : Nettoyer --
    _cleanup(temp_path)

    # -- Etape 7 : Reponse avec timing --
    duree = round(time.time() - debut, 2)
    source = cv_result.get("source_type", "image")

    return jsonify({
        "statut": "ok",
        "source_type": source,
        "classification_locale": cv_result,
        "mission": mission,
        "temps_analyse_secondes": duree,
    })


@app.route("/health", methods=["GET"])
def health():
    """Endpoint de verification de sante."""
    return jsonify({
        "statut": "ok",
        "message": "Service d'analyse photo/video operationnel (100% local)",
        "formats_acceptes": sorted(ALLOWED_EXTENSIONS),
        "limite_fichier_mo": MAX_FILE_SIZE_MB,
    })


@app.route("/formats", methods=["GET"])
def formats():
    """Liste detaillee des formats supportes."""
    return jsonify({
        "images": sorted(["png", "jpg", "jpeg", "gif", "webp"]),
        "videos": sorted(VIDEO_EXTENSIONS),
        "limite_fichier_mo": MAX_FILE_SIZE_MB,
    })


# ==============================
# UTILITAIRES
# ==============================

def _cleanup(temp_path: str):
    """Supprime le fichier temporaire en toute securite."""
    try:
        if os.path.exists(temp_path):
            os.remove(temp_path)
    except OSError:
        pass


# -- Point d'entree --
if __name__ == "__main__":
    print("=" * 60)
    print("  API Analyse Photo/Video - Benevolat Citoyen (100% LOCAL)")
    print("  Test    : http://localhost:5000/")
    print("  Analyse : POST http://localhost:5000/analyser-photo")
    print("  Sante   : GET  http://localhost:5000/health")
    print("  Formats : GET  http://localhost:5000/formats")
    print("  Limite  : {} Mo par fichier".format(MAX_FILE_SIZE_MB))
    print("=" * 60)
    app.run(debug=True, host="0.0.0.0", port=5000)
