"""
Static baby development data per gestational week.
Values are median estimates based on standard obstetric references.
The frontend can interpolate between defined weeks for unlisted ones.
"""

BABY_BY_WEEK: dict[int, dict] = {
    4:  {"size_cm": 0.2,  "weight_g": None, "fruit": "graine de pavot",     "milestones": ["Implantation dans l'utérus", "Formation du tube neural"]},
    5:  {"size_cm": 0.4,  "weight_g": None, "fruit": "graine de sésame",    "milestones": ["Début formation du cœur", "Ébauche du cerveau"]},
    6:  {"size_cm": 0.6,  "weight_g": None, "fruit": "lentille",             "milestones": ["Battements cardiaques", "Bourgeons des bras et jambes"]},
    7:  {"size_cm": 1.0,  "weight_g": None, "fruit": "myrtille",             "milestones": ["Formation des organes majeurs", "Ébauche du visage"]},
    8:  {"size_cm": 1.6,  "weight_g": 1,    "fruit": "framboise",            "milestones": ["Doigts visibles", "Formation des yeux"]},
    9:  {"size_cm": 2.3,  "weight_g": 2,    "fruit": "cerise",               "milestones": ["Tous les organes formés", "Mouvements spontanés"]},
    10: {"size_cm": 3.1,  "weight_g": 4,    "fruit": "fraise",               "milestones": ["Ongles en formation", "Cordes vocales"]},
    11: {"size_cm": 4.1,  "weight_g": 7,    "fruit": "citron vert",          "milestones": ["Foie fonctionnel", "Réflexes se développent"]},
    12: {"size_cm": 5.4,  "weight_g": 14,   "fruit": "citron",               "milestones": ["Fin du 1er trimestre", "Risque fausse couche diminue", "Échographie du 1er trimestre"]},
    13: {"size_cm": 7.4,  "weight_g": 23,   "fruit": "pêche",                "milestones": ["Empreintes digitales", "Formation des os"]},
    14: {"size_cm": 8.7,  "weight_g": 43,   "fruit": "citron jaune",         "milestones": ["Début 2ème trimestre", "Pouce sucé"]},
    15: {"size_cm": 10.1, "weight_g": 70,   "fruit": "pomme",                "milestones": ["Duvet (lanugo) apparaît", "Système squelettique se solidifie"]},
    16: {"size_cm": 11.6, "weight_g": 100,  "fruit": "avocat",               "milestones": ["Premiers mouvements perçus", "Échographie morphologique recommandée"]},
    17: {"size_cm": 13.0, "weight_g": 140,  "fruit": "poire",                "milestones": ["Graisse sous-cutanée", "Réflexes de succion"]},
    18: {"size_cm": 14.2, "weight_g": 190,  "fruit": "poivron",              "milestones": ["Oreilles fonctionnelles", "Réagit aux sons"]},
    19: {"size_cm": 15.3, "weight_g": 240,  "fruit": "tomate",               "milestones": ["Sens du goût se développe", "Vernix caseosa apparaît"]},
    20: {"size_cm": 16.4, "weight_g": 300,  "fruit": "banane",               "milestones": ["Moitié de la grossesse", "Cheveux apparaissent", "Déglutit du liquide amniotique"]},
    21: {"size_cm": 26.7, "weight_g": 360,  "fruit": "mangue",               "milestones": ["Formation des poumons", "Mouvements coordonnés", "Développement du système nerveux"]},
    22: {"size_cm": 27.8, "weight_g": 430,  "fruit": "noix de coco",         "milestones": ["Lèvres et sourcils visibles", "Sens du toucher développé"]},
    23: {"size_cm": 28.9, "weight_g": 501,  "fruit": "mangue (grande)",      "milestones": ["Poumons développent surfactant", "Rythme veille/sommeil"]},
    24: {"size_cm": 30.0, "weight_g": 600,  "fruit": "épi de maïs",          "milestones": ["Viabilité (avec assistance médicale)", "HGPO recommandé", "Papilles gustatives développées"]},
    25: {"size_cm": 34.6, "weight_g": 660,  "fruit": "navet",                "milestones": ["Réponses aux stimuli externes", "Graisses accumulées"]},
    26: {"size_cm": 35.6, "weight_g": 760,  "fruit": "oignon",               "milestones": ["Yeux s'ouvrent", "Réflexes de préhension"]},
    27: {"size_cm": 36.6, "weight_g": 875,  "fruit": "chou-fleur",           "milestones": ["Fin 2ème trimestre", "Cerveau en développement rapide"]},
    28: {"size_cm": 37.6, "weight_g": 1005, "fruit": "aubergine",            "milestones": ["Début 3ème trimestre", "Yeux pleinement ouverts", "Suivre les mouvements activé"]},
    29: {"size_cm": 38.6, "weight_g": 1153, "fruit": "butternut",            "milestones": ["Prise de poids rapide", "Os se solidifient"]},
    30: {"size_cm": 39.9, "weight_g": 1319, "fruit": "chou",                 "milestones": ["Cerveau forme des circonvolutions", "Ongles complets"]},
    31: {"size_cm": 41.1, "weight_g": 1502, "fruit": "asperge (bouquet)",    "milestones": ["Capacité à réguler la température", "Iris coloré"]},
    32: {"size_cm": 42.4, "weight_g": 1702, "fruit": "ananas",               "milestones": ["Présentation fœtale à vérifier", "Poumons presque matures", "4ème consultation recommandée"]},
    33: {"size_cm": 43.7, "weight_g": 1918, "fruit": "ananas (grand)",       "milestones": ["Ongles atteignent le bout des doigts", "Développement immunitaire"]},
    34: {"size_cm": 45.0, "weight_g": 2146, "fruit": "melon vert",           "milestones": ["Position tête en bas souvent", "Stockage de fer et calcium"]},
    35: {"size_cm": 46.2, "weight_g": 2383, "fruit": "nid d'abeille (melon)","milestones": ["Poumons fonctionnels", "Graisse sous-cutanée abondante"]},
    36: {"size_cm": 47.4, "weight_g": 2622, "fruit": "melon (grand)",        "milestones": ["Presque à terme", "Début engagement dans le bassin", "5ème consultation recommandée"]},
    37: {"size_cm": 48.6, "weight_g": 2859, "fruit": "poireau",              "milestones": ["À terme précoce", "Prêt à naître à tout moment", "Signes du travail à surveiller"]},
    38: {"size_cm": 49.8, "weight_g": 3083, "fruit": "poireau (grand)",      "milestones": ["À terme", "Système digestif prêt", "Tous les organes matures"]},
    39: {"size_cm": 50.7, "weight_g": 3288, "fruit": "pastèque (petite)",    "milestones": ["À terme complet", "Mouvements actifs attendus"]},
    40: {"size_cm": 51.2, "weight_g": 3462, "fruit": "pastèque",             "milestones": ["Date prévue d'accouchement", "Prêt à naître", "Présentation définitive confirmée"]},
}


def get_baby_data(gestational_week: int) -> dict:
    """
    Return baby development data for a given gestational week.
    If the exact week is not in the database, returns the closest previous week.
    """
    if gestational_week <= 0:
        return {
            "size_cm": None, "weight_g": None,
            "fruit": None, "milestones": ["Grossesse tout juste confirmée"],
            "week": gestational_week,
        }

    # Find closest defined week (floor)
    available = sorted(BABY_BY_WEEK.keys())
    week_key = max((w for w in available if w <= gestational_week), default=available[0])

    data = BABY_BY_WEEK[week_key].copy()
    data["week"] = gestational_week
    data["reference_week"] = week_key  # which entry was actually used
    return data
