"""
Static maternal symptoms and motivational messages by trimester.
"""

SYMPTOMS_BY_TRIMESTER: dict[int, dict] = {
    1: {
        "symptoms": [
            "Nausées matinales", "Fatigue intense", "Seins sensibles",
            "Envies fréquentes d'uriner", "Sautes d'humeur", "Aversions alimentaires",
        ],
        "normal_note": "Ces symptômes sont normaux au 1er trimestre et s'atténuent vers la 12e semaine.",
        "motivational_message": "Votre corps travaille dur pour créer une nouvelle vie. Reposez-vous bien. 💛",
        "weekly_tip": "Prenez de l'acide folique chaque jour et évitez les aliments crus.",
    },
    2: {
        "symptoms": [
            "Fatigue réduite", "Douleurs lombaires", "Vertiges légers",
            "Constipation", "Brûlures d'estomac", "Premiers mouvements du bébé",
        ],
        "normal_note": "Le 2ème trimestre est souvent le plus confortable. L'énergie revient progressivement.",
        "motivational_message": "Votre corps fait un travail merveilleux. Votre bébé grandit magnifiquement. 🌸",
        "weekly_tip": "Hydratez-vous bien et surveillez régulièrement votre tension artérielle.",
    },
    3: {
        "symptoms": [
            "Essoufflement", "Œdèmes", "Contractions de Braxton Hicks",
            "Difficultés à dormir", "Douleurs pelviennes", "Mictions fréquentes",
        ],
        "normal_note": "Ces symptômes sont normaux en fin de grossesse. Le bébé prend de la place.",
        "motivational_message": "Vous approchez du but ! Restez forte et confiante. 💪🤰",
        "weekly_tip": "Préparez votre valise de maternité et repérez les signes du travail.",
    },
}

ALERT_SIGNS: dict[str, list] = {
    "urgent": [
        "Saignement abondant",
        "Douleur abdominale intense et persistante",
        "Convulsions ou perte de conscience",
        "Absence de mouvements fœtaux depuis plus de 12h",
        "Fuite de liquide amniotique",
    ],
    "consultation_rapide": [
        "Œdème brutal des mains ou du visage",
        "Céphalée intense et persistante",
        "Fièvre supérieure à 38°C",
        "Vomissements sévères et répétés",
        "Vision trouble ou mouches volantes",
    ],
}


def get_maternal_state(trimester: int) -> dict:
    data = SYMPTOMS_BY_TRIMESTER.get(trimester)
    if not data:
        return {}
    return data


def get_alert_signs() -> dict:
    return ALERT_SIGNS
