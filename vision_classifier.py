"""
vision_classifier.py
====================
Classification locale d'images ET videos avec CLIP (zero-shot).
Le modele est charge une seule fois au demarrage du module.
Supporte les images (jpg, png...) et les videos (mp4, mov...) en extrayant
la meilleure frame.
"""

import os
import cv2
import numpy as np
from transformers import pipeline
from PIL import Image

# -- Categories reconnues par notre plateforme de benevolat --
CATEGORIES = [
    "trash and garbage pile",
    "deforested area needing reforestation",
    "dirty urban street",
    "damaged public infrastructure",
    "fire or smoke",
    "flood or water damage",
    "normal safe scene",
]

# -- Chargement unique du modele (variable globale) --
print("[vision_classifier] Chargement du modele CLIP (premier lancement ~30s)...")
_classifier = pipeline(
    "zero-shot-image-classification",
    model="openai/clip-vit-base-patch32",
    device=-1,  # -1 = CPU, pas de GPU
)
print("[vision_classifier] Modele CLIP pret.")


def _est_une_video(file_path: str) -> bool:
    """Detecte si le fichier est une video selon son extension."""
    video_exts = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv", ".wmv"}
    ext = os.path.splitext(file_path)[1].lower()
    return ext in video_exts


def _extraire_frame_video(video_path: str, nb_frames: int = 5) -> Image.Image:
    """
    Extrait plusieurs frames d'une video et retourne la plus "interessante"
    (celle avec le plus de variance = la plus detaillee pour CLIP).

    Args:
        video_path: chemin vers le fichier video
        nb_frames: nombre de frames a extraire pour comparaison

    Returns:
        PIL Image de la meilleure frame

    Raises:
        ValueError: si la video est vide, corrompue, ou illisible
    """
    if not os.path.exists(video_path):
        raise ValueError(f"Fichier video introuvable : {video_path}")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(
            f"Impossible d'ouvrir la video : {os.path.basename(video_path)}. "
            "Le fichier est peut-etre corrompu ou dans un format non supporte."
        )

    try:
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duree = total_frames / fps if fps > 0 else 0

        if total_frames == 0:
            raise ValueError("Video vide (0 frames)")

        if duree < 0.1:
            raise ValueError(f"Video trop courte ({duree:.2f}s)")

        # Prendre des frames espacees egalement dans la video
        indices = np.linspace(0, total_frames - 1, nb_frames, dtype=int)
        frames = []

        for idx in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
            ret, frame = cap.read()
            if ret and frame is not None:
                # Verifier que la frame n'est pas toute noire
                if np.mean(frame) > 5:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_img = Image.fromarray(frame_rgb)
                    frames.append(pil_img)

        if not frames:
            raise ValueError(
                "Aucune frame exploitable dans la video. "
                "La video est peut-etre toute noire ou corrompue."
            )

        # Choisir la frame avec le plus de variance (la plus "interessante")
        best = max(frames, key=lambda img: np.var(np.array(img)))
        return best

    finally:
        cap.release()


def classify_image(image_path: str) -> dict:
    """
    Classifie une image OU une frame extraite d'une video.

    Args:
        image_path: chemin local vers le fichier image ou video

    Returns:
        dict avec :
            - classe (str): categorie predite
            - confiance (float): score de confiance 0-1
            - alternatives (list): top 3 autres categories avec scores
            - source_type (str): "image" ou "video"
    """
    # Si c'est une video, extraire la meilleure frame
    if _est_une_video(image_path):
        image = _extraire_frame_video(image_path)
        source_type = "video"
    else:
        image = Image.open(image_path).convert("RGB")
        source_type = "image"

    # Classification zero-shot
    result = _classifier(image, candidate_labels=CATEGORIES)

    meilleure = result[0]
    alternatives = [
        {"classe": r["label"], "confiance": round(r["score"], 4)}
        for r in result[1:4]
    ]

    return {
        "classe": meilleure["label"],
        "confiance": round(meilleure["score"], 4),
        "alternatives": alternatives,
        "source_type": source_type,
    }
