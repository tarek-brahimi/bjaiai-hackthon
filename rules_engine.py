"""
rules_engine.py
===============
MOTEUR DE REGLES LOCAL - remplace toute API payante.
Genere les recommandations de mission a partir des regles et templates Python.
Aucun LLM, aucun appel reseau, tout est deterministe.
"""

# Dictionnaire des regles par classe detectee
# Chaque classe CLIP est mappee vers toutes les informations necessaires
# pour construire une mission de benevolat complete.

REGLES = {
    # --- DECHETS ---
    "trash and garbage pile": {
        "type_probleme": "dechets",
        "titre_type": "Zone de dechets a nettoyer",
        "description_template": "Un amas de dechets a ete identifie sur cette zone. {detail_gravite}",
        "benevoles_base": {"elevee": 10, "moyenne": 6, "faible": 3},
        "nourriture_par_benevole": "1 sandwich + 1 barre energetique",
        "eau_par_benevole": "2 litres",
        "materiel_necessaire": [
            "sacs poubelle rouge et jaune",
            "pince a dechet",
            "brouette",
            "gel hydroalcoolique",
        ],
        "risques_securite": [
            "Objets tranchants possibles",
            "Contamination bacteriologique",
            "Porter des gants obligatoire",
        ],
        "actions_immediates": [
            "Delimiter la zone de travail",
            "Distribuer les gants et sacs aux benevoles",
            "Trier les dechets : plastique / organique / dangereux",
            "Ranger les sacs remplis au point de rassemblement",
            "Appeler le service municipal pour enlevement",
        ],
        "materiel_protection": ["gants", "chaussures fermees", "masque anti-poussiere"],
        "vehicules_requis": [],
    },

    # --- DEFORESTATION ---
    "deforested area needing reforestation": {
        "type_probleme": "reboisement",
        "titre_type": "Zone a reboiser",
        "description_template": "Une zone deforestee a ete reperee. {detail_gravite}",
        "benevoles_base": {"elevee": 15, "moyenne": 10, "faible": 5},
        "nourriture_par_benevole": "1 repas + 1 eau",
        "eau_par_benevole": "2 litres + 5 litres pour arrosage",
        "materiel_necessaire": [
            "plants d'arbres",
            "pelle et beche",
            "arrosoir ou tuyau d'arrosage",
            "tuteur pour chaque plant",
        ],
        "risques_securite": [
            "Terrain potentiellement glissant",
            "Port de chaussures fermees obligatoire",
        ],
        "actions_immediates": [
            "Identifier les zones prioritaires a reboiser",
            "Preparer les trous de plantation",
            "Planter les arbres avec tuteur",
            "Arroser chaque plant apres mise en terre",
            "Installer des protecteurs contre les animaux",
        ],
        "materiel_protection": ["gants de jardinage", "chaussures fermees"],
        "vehicules_requis": [],
    },

    # --- PROPRETE URBAINE ---
    "dirty urban street": {
        "type_probleme": "proprete_urbaine",
        "titre_type": "Rue sale a nettoyer",
        "description_template": "Une rue urbaine presente un etat de salissure important. {detail_gravite}",
        "benevoles_base": {"elevee": 8, "moyenne": 5, "faible": 3},
        "nourriture_par_benevole": "1 sandwich + 1 eau",
        "eau_par_benevole": "2 litres + 3 litres pour rincage",
        "materiel_necessaire": [
            "balais et balai brosse",
            "seaux",
            "detergent multi-usage",
            "brouette",
        ],
        "risques_securite": [
            "Eau sale au sol : risque de glissade",
            "Produits chimiques : porter des gants",
            "Circulation vehicle : baliser la zone",
        ],
        "actions_immediates": [
            "Baliser la zone de circulation si possible",
            "Balayer les dechets solides en premier",
            "Laver au detergent les taches importantes",
            "Rincer a l'eau claire",
            "Vider les seaux dans les caniveaux",
        ],
        "materiel_protection": ["gants", "chaussures antiderapantes"],
        "vehicules_requis": [],
    },

    # --- INFRASTRUCTURE DEGRADEE ---
    "damaged public infrastructure": {
        "type_probleme": "degradation",
        "titre_type": "Infrastructure degradee a reparer",
        "description_template": "Une infrastructure publique presente des dommages visibles. {detail_gravite}",
        "benevoles_base": {"elevee": 12, "moyenne": 8, "faible": 4},
        "nourriture_par_benevole": "1 repas pour la mi-journee",
        "eau_par_benevole": "2 litres",
        "materiel_necessaire": [
            "kit de bricolage de base",
            "scotch de signalisation",
            "perceuse-visseuse",
            "vis et chevilles",
        ],
        "risques_securite": [
            "Structure instable : ne pas s'approcher trop pres",
            "Eclats de bois ou de metal possibles",
            "Port de gants et lunettes obligatoire",
        ],
        "actions_immediates": [
            "Baliser la zone pour eviter les passants",
            "Faire des photos du dommage pour le rapport",
            "Evaluer si la reparation est faisable par des benevoles",
            "Si structure instable : appeler les services techniques municipaux",
            "Proceder aux reparations simples si possible",
        ],
        "materiel_protection": ["gants", "lunettes de protection", "casque si besoin"],
        "vehicules_requis": [],
    },

    # --- INCENDIE (URGENCE MAXIMALE) ---
    "fire or smoke": {
        "type_probleme": "incendie",
        "titre_type": "Incendie ou fumee detecte",
        "description_template": "Des flammes ou de la fumee ont ete observees. {detail_gravite}",
        "benevoles_base": {"elevee": 15, "moyenne": 10, "faible": 5},
        "nourriture_par_benevole": "1 repas + barres energetiques",
        "eau_par_benevole": "3 litres (boisson, PAS pour le feu)",
        "materiel_necessaire": [
            "extincteur si disponible",
            "couverture anti-feu",
            "telephone pour appeler les pompiers",
        ],
        "risques_securite": [
            "NE PAS intervenir soi-meme sur un feu important",
            "Fumee toxique : s'eloigner en remontant",
            "Risque d'explosion de bonbonnes ou vehicules",
            "Appeler les pompiers (18) EN PREMIER",
        ],
        "actions_immediates": [
            "APPELER LES POMPIERS (18) IMMEDIATEMENT",
            "Evacuer tous les civils a au moins 200m du foyer",
            "Alerter les habitants aux alentours",
            "Ne PAS tenter d'eteindre soi-meme si le feu est grand",
            "Guider les pompiers sur place a leur arrivee",
        ],
        "materiel_protection": ["masque anti-fumee", "couverture anti-feu", "gants coupe-feu"],
        "vehicules_requis": ["camion-citerne pompiers", "ambulance de secours"],
    },

    # --- INONDATION ---
    "flood or water damage": {
        "type_probleme": "inondation",
        "titre_type": "Zone inondee a traiter",
        "description_template": "Des degats causes par l'eau ont ete identifies. {detail_gravite}",
        "benevoles_base": {"elevee": 12, "moyenne": 8, "faible": 4},
        "nourriture_par_benevole": "1 sandwich + 1 eau",
        "eau_par_benevole": "2 litres + 5 litres pour rinçage",
        "materiel_necessaire": [
            "pompe a eau si disponible",
            "balais et rateaux",
            "seaux",
            "bottes en caoutchouc",
        ],
        "risques_securite": [
            "Eau potentiellement polluee : ne pas la toucher a mains nues",
            "Risque de chute dans les bouchons d'egout ouverts",
            "Electrocution possible si cables sous l'eau",
            "Port de bottes hautes obligatoire",
        ],
        "actions_immediates": [
            "S'assurer que les personnes sont hors de danger",
            "Couper l'electricite du batiment si possible",
            "Installer les pompes si disponibles",
            "Recuperer les objets mobiliers hors de l'eau",
            "Debuter le nettoyage quand le niveau baisse",
        ],
        "materiel_protection": ["bottes en caoutchouc", "gants impermeables"],
        "vehicules_requis": ["pompe a eau", "4x4 ou vehicule tout-terrain"],
    },

    # --- SCENE NORMALE ---
    "normal safe scene": {
        "type_probleme": "autre",
        "titre_type": "Scene normale",
        "description_template": "L'image ne montre pas de probleme necessitant une intervention.",
        "benevoles_base": {"elevee": 0, "moyenne": 0, "faible": 0},
        "nourriture_par_benevole": "",
        "eau_par_benevole": "",
        "materiel_necessaire": [],
        "risques_securite": [],
        "actions_immediates": [],
        "materiel_protection": [],
        "vehicules_requis": [],
    },
}


def _determiner_gravite(confiance: float) -> str:
    """Determine la gravite selon le score de confiance."""
    if confiance >= 0.8:
        return "elevee"
    elif confiance >= 0.5:
        return "moyenne"
    else:
        return "faible"


def _determiner_urgence(classe: str, gravite: str) -> str:
    """
    Determine le niveau d'urgence : "faible", "moyen" ou "grand".
    - grand = danger immediat pour des vies humaines
    - moyen = situation dangereuse mais pas de danger immediatement
    - faible = probleme gereable, pas de danger vital
    """
    # Incendie = toujours grand urgence
    if classe == "fire or smoke" and gravite in ("elevee", "moyenne"):
        return "grand"
    if classe == "fire or smoke":
        return "moyen"

    # Inondation = grand si grave, moyen sinon
    if classe == "flood or water damage" and gravite == "elevee":
        return "grand"
    if classe == "flood or water damage":
        return "moyen"

    # Infrastructure degradee = moyen si instable
    if classe == "damaged public infrastructure" and gravite == "elevee":
        return "moyen"

    # Le reste suit la gravite
    if gravite == "elevee":
        return "moyen"
    if gravite == "moyenne":
        return "moyen"
    return "faible"


def _determiner_delai(urgence: str) -> str:
    """Retourne le delai d'intervention selon l'urgence."""
    delais = {
        "grand": "IMMEDIAT - appeler les secours maintenant",
        "moyen": "dans les 6h maximum",
        "faible": "dans la semaine",
    }
    return delais.get(urgence, "a determiner")


def _generer_description(regle: dict, gravite: str, confiance: float) -> str:
    """Genere une description en remplissant le template."""
    details = {
        "elevee": f"La situation est jugee grave (confiance : {confiance:.0%}). Intervention recommandee en priorite.",
        "moyenne": f"La situation est moderement preoccupante (confiance : {confiance:.0%}). Intervention souhaitable.",
        "faible": f"La situation est incertaine (confiance : {confiance:.0%}). Une verification humaine est recommandee.",
    }
    detail = details.get(gravite, details["faible"])
    return regle["description_template"].format(detail_gravite=detail)


def _calculer_logistique(regle: dict, nb_benevoles: int) -> dict:
    """
    Calcule la logistique exacte en fonction du nombre de benevoles.
    Nourriture et eau sont proportionnelles au nombre de personnes.
    """
    nb = max(nb_benevoles, 1)

    # Nourriture totale
    nourriture_par = regle.get("nourriture_par_benevole", "")
    if nourriture_par:
        nourriture_totale = [f"{nb}x {nourriture_par}"]
    else:
        nourriture_totale = []

    # Eau totale
    eau_par = regle.get("eau_par_benevole", "")
    if eau_par and nb_benevoles > 0:
        eau_totale = f"{nb} personnes x {eau_par}"
    else:
        eau_totale = None

    return {
        "nourriture": nourriture_totale,
        "eau": eau_totale,
        "materiel_necessaire": regle["materiel_necessaire"],
        "materiel_protection": regle["materiel_protection"],
        "vehicules_requis": regle["vehicules_requis"],
    }


def _nb_benevoles(regle: dict, gravite: str) -> int:
    """Retourne le nombre de benevoles selon la gravite."""
    return regle["benevoles_base"].get(gravite, 3)


def generer_mission(classe: str, confiance: float, alternatives: list) -> dict:
    """
    Genere une mission complete a partir du resultat de la classification CLIP.

    Args:
        classe: categorie CLIP detectee
        confiance: score de confiance 0-1
        alternatives: top 3 des autres categories

    Returns:
        dict au format attendu par le frontend
    """
    # --- Cas special : confiance trop basse ---
    if confiance < 0.4:
        return {
            "type_probleme": "autre",
            "titre_court": "Image non exploitable",
            "description": (
                f"Le modele n'a pas pu identifier le probleme "
                f"(meilleure categorie : {classe}, confiance : {confiance:.0%}). "
                "Une verification humaine est necessaire."
            ),
            "gravite": "faible",
            "urgence": "faible",
            "delai_intervention": "a determiner apres verification",
            "benevoles_recommandes": 0,
            "ressources_humaines": {
                "nombre": 0,
                "competences_recherchees": [],
                "description_besoin": "Verification humaine requise",
            },
            "logistique": {"nourriture": [], "eau": None, "materiel_necessaire": [], "materiel_protection": [], "vehicules_requis": []},
            "contacts_urgents": [],
            "actions_immediates": ["Envoyer un observateur sur place pour confirmer la nature du probleme"],
            "materiel_necessaire": [],
            "risques_securite": [],
            "confiance_finale": round(confiance, 4),
            "besoin_verification_humaine": True,
        }

    # --- Cas special : scene normale ---
    if classe == "normal safe scene":
        return {
            "type_probleme": "autre",
            "titre_court": "Scene normale - pas de probleme detecte",
            "description": "L'image montre une scene normale sans probleme necessitant une intervention.",
            "gravite": "faible",
            "urgence": "faible",
            "delai_intervention": "aucune intervention necessaire",
            "benevoles_recommandes": 0,
            "ressources_humaines": {"nombre": 0, "competences_recherchees": [], "description_besoin": "Aucun benevole necessaire"},
            "logistique": {"nourriture": [], "eau": None, "materiel_necessaire": [], "materiel_protection": [], "vehicules_requis": []},
            "contacts_urgents": [],
            "actions_immediates": [],
            "materiel_necessaire": [],
            "risques_securite": [],
            "confiance_finale": round(confiance, 4),
            "besoin_verification_humaine": False,
        }

    # --- Cas normal : probleme detecte ---
    regle = REGLES.get(classe)
    if not regle:
        return generer_mission("normal safe scene", confiance, alternatives)

    gravite = _determiner_gravite(confiance)
    urgence = _determiner_urgence(classe, gravite)
    nb = _nb_benevoles(regle, gravite)

    # Contacts urgents par type de probleme
    contacts = []
    if classe == "fire or smoke":
        contacts = [
            {"service": "POMPIERS", "raison": "Feu actif - APPELER IMMEDIATEMENT", "numero": "18"},
            {"service": "SAMU", "raison": "Victimes potentielles / fumees inhalees", "numero": "15"},
            {"service": "Gendarmerie", "raison": "Securisation de la zone", "numero": "17"},
        ]
    elif classe == "flood or water damage":
        contacts = [
            {"service": "Police/Gendarmerie", "raison": "Zone inondee a baliser", "numero": "17"},
            {"service": "SAMU", "raison": "Personnes isolees ou agees", "numero": "15"},
            {"service": "Mairie / Service technique", "raison": "Debouchage des caniveaux", "numero": None},
        ]
    elif classe == "damaged public infrastructure":
        contacts = [
            {"service": "Mairie / Service technique", "raison": "Infrastructure degradee", "numero": None},
        ]
    elif classe in ("trash and garbage pile", "dirty urban street"):
        contacts = [
            {"service": "Mairie / Service hygiene", "raison": "Dechets sur voie publique", "numero": None},
        ]

    # Competences recherchees par type
    competences = {
        "trash and garbage pile": ["tri et collecte", "sensibilisation"],
        "deforested area needing reforestation": ["jardinage", "plantation"],
        "dirty urban street": ["nettoyage", "entretien"],
        "damaged public infrastructure": ["bricolage", "menuiserie"],
        "fire or smoke": ["secourisme PSE1/PSE2", "gestion du stress"],
        "flood or water damage": ["pompage", "aide aux personnes agees"],
    }

    return {
        "type_probleme": regle["type_probleme"],
        "titre_court": regle["titre_type"],
        "description": _generer_description(regle, gravite, confiance),
        "gravite": gravite,
        "urgence": urgence,
        "delai_intervention": _determiner_delai(urgence),
        "benevoles_recommandes": nb,
        "ressources_humaines": {
            "nombre": nb,
            "competences_recherchees": competences.get(classe, []),
            "description_besoin": f"{nb} benevoles pour {regle['titre_type'].lower()}",
        },
        "logistique": _calculer_logistique(regle, nb),
        "contacts_urgents": contacts,
        "actions_immediates": regle["actions_immediates"],
        "materiel_necessaire": regle["materiel_necessaire"],
        "risques_securite": regle["risques_securite"],
        "confiance_finale": round(confiance, 4),
        "besoin_verification_humaine": gravite == "faible",
    }
