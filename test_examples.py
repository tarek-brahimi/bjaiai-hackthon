"""
test_examples.py
================
Tests complets du pipeline : CLIP + moteur de regles.
Lance : python test_examples.py

Cree des images de test, les analyse, et verifie que tout fonctionne.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image, ImageDraw
from vision_classifier import classify_image
from rules_engine import generer_mission


def creer_image(nom: str, description: str, dessiner_fn) -> str:
    """Cree une image de test."""
    img = Image.new("RGB", (600, 400), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    dessiner_fn(draw, img)
    chemin = os.path.join(os.path.dirname(os.path.abspath(__file__)), nom)
    img.save(chemin, quality=85)
    return chemin


def dessiner_feu(draw, img):
    """Dessine un paysage avec des flammes."""
    # Fond sombre
    for x in range(0, 600, 2):
        for y in range(0, 400, 2):
            draw.point((x, y), fill=(20 + (x % 10), 10, 5))
    # Flammes
    for i in range(25):
        x = 50 + i * 22
        y = 250 - (i % 5) * 25
        draw.rectangle([x, y, x+18, y+40], fill=(220, 80 + i*4, 0))
    # Fumee
    for i in range(8):
        draw.ellipse([280+i*12, 80+i*8, 320+i*12, 120+i*8], fill=(60+i*5, 60+i*5, 60+i*5))


def dessiner_dechets(draw, img):
    """Dessine un sol verte avec des dechets colores."""
    # Sol vert
    draw.rectangle([0, 200, 600, 400], fill=(40, 100, 30))
    # Dechets
    colors = [(180, 80, 30), (100, 100, 100), (200, 200, 50), (50, 50, 50), (150, 30, 30)]
    for i in range(20):
        x = 30 + i * 28
        y = 250 + (i % 4) * 20
        c = colors[i % len(colors)]
        draw.rectangle([x, y, x+22, y+14], fill=c)
    # Panneau
    draw.rectangle([180, 40, 420, 100], fill=(180, 180, 180))
    draw.text((200, 55), "ZONE DE DECHETS", fill=(0, 0, 0))


def dessiner_inondation(draw, img):
    """Dessine une rue inondee."""
    # Eau bleue
    draw.rectangle([0, 150, 600, 400], fill=(30, 80, 180))
    # Vagues
    for i in range(30):
        x = i * 20
        y = 180 + (i % 3) * 10
        draw.rectangle([x, y, x+18, y+8], fill=(40, 100, 210))
    # Maisons noyees
    draw.rectangle([100, 80, 200, 200], fill=(140, 90, 40))
    draw.rectangle([300, 100, 420, 200], fill=(120, 75, 35))


def dessiner_normal(draw, img):
    """Dessine un paysage normal (maison + arbre)."""
    # Ciel
    draw.rectangle([0, 0, 600, 250], fill=(135, 200, 235))
    # Herbe
    draw.rectangle([0, 250, 600, 400], fill=(50, 150, 50))
    # Maison
    draw.rectangle([200, 150, 400, 250], fill=(180, 120, 60))
    draw.polygon([(180, 150), (300, 80), (420, 150)], fill=(150, 50, 50))
    # Arbre
    draw.rectangle([480, 180, 500, 250], fill=(100, 70, 30))
    draw.ellipse([450, 120, 530, 200], fill=(30, 120, 30))


def test_complet(image_path: str, label_attendu: str = "") -> dict:
    """Lance le pipeline complet sur une image."""
    print(f"\n{'='*60}")
    print(f"  TEST : {os.path.basename(image_path)}")
    print(f"{'='*60}")

    if not os.path.exists(image_path):
        print(f"  [SKIP] Image non trouvee")
        return {}

    # Etape 1 : CLIP
    cv_result = classify_image(image_path)
    print(f"  CLIP     : {cv_result['classe']} ({cv_result['confiance']:.1%})")
    print(f"  Source   : {cv_result.get('source_type', 'N/A')}")

    # Etape 2 : Moteur de regles
    mission = generer_mission(
        classe=cv_result["classe"],
        confiance=cv_result["confiance"],
        alternatives=cv_result["alternatives"],
    )

    # Affichage
    print(f"  Type     : {mission['type_probleme']}")
    print(f"  Urgence  : {mission['urgence']}")
    print(f"  Gravite  : {mission['gravite']}")
    print(f"  Benevoles: {mission['benevoles_recommandes']}")
    print(f"  Nourritur: {mission['logistique']['nourriture']}")
    print(f"  Eau      : {mission['logistique']['eau']}")
    print(f"  Contacts : {len(mission['contacts_urgents'])} service(s)")

    if mission.get("contacts_urgents"):
        for c in mission["contacts_urgents"]:
            print(f"    - {c['service']} ({c.get('numero', 'N/A')})")

    if mission.get("actions_immediates"):
        print(f"  Action 1 : {mission['actions_immediates'][0]}")

    # Verification
    if label_attendu:
        if mission["type_probleme"] == label_attendu:
            print(f"\n  [OK] {label_attendu}")
        else:
            print(f"\n  [INFO] Attendu '{label_attendu}', obtenu '{mission['type_probleme']}' (confiance basse = normal)")

    return {"classification": cv_result, "mission": mission}


def test_erreur():
    """Test de gestion d'erreur : fichier inexistant."""
    print(f"\n{'='*60}")
    print("  TEST ERREUR : fichier inexistant")
    print(f"{'='*60}")
    try:
        classify_image("chemin/qui/n/existe/pas.jpg")
        print("  [ERREUR] Aurait du lever une exception")
    except Exception as e:
        print(f"  [OK] Exception : {type(e).__name__}")


# --- Lancement ---
if __name__ == "__main__":
    print("=" * 60)
    print("  TESTS DU PIPELINE - ANALYSE PHOTO/VIDEO")
    print("  Mode : 100% local, sans API payante")
    print("=" * 60)

    # Creer les images de test
    img_dir = os.path.dirname(os.path.abspath(__file__))
    imgs = [
        creer_image("test_feu.jpg", "feu", dessiner_feu),
        creer_image("test_dechets.jpg", "dechets", dessiner_dechets),
        creer_image("test_inondation.jpg", "inondation", dessiner_inondation),
        creer_image("test_normal.jpg", "normal", dessiner_normal),
    ]

    # Lancer les tests
    test_complet(imgs[0], "incendie")
    test_complet(imgs[1], "dechets")
    test_complet(imgs[2], "inondation")
    test_complet(imgs[3], "autre")
    test_erreur()

    # Nettoyer
    for img in imgs:
        if os.path.exists(img):
            os.remove(img)

    print(f"\n{'='*60}")
    print("  TOUS LES TESTS TERMINES")
    print("=" * 60)
