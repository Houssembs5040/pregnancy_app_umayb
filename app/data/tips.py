"""Module 5 — Conseils content, organized by category and trimester."""

TIPS: dict[str, dict] = {
    "nutrition": {
        "title": "Nutrition",
        "description": "Aliments recommandés par trimestre",
        1: [
            "Prenez 400 µg d'acide folique par jour",
            "Évitez le fromage cru, la charcuterie et le poisson cru",
            "Consommez des légumes verts feuillus (épinards, brocoli)",
            "Hydratez-vous : au moins 1,5 L d'eau par jour",
            "Fractionnez les repas en cas de nausées",
        ],
        2: [
            "Augmentez l'apport en fer : viande rouge, légumineuses, lentilles",
            "Le calcium est essentiel : produits laitiers, amandes, sardines",
            "Continuez les vitamines prénatales",
            "Privilégiez les glucides complexes : riz complet, pain complet",
            "Limitez la caféine à moins de 200 mg/jour",
        ],
        3: [
            "Mangez des petits repas fréquents pour éviter la gêne gastrique",
            "Favorisez les aliments riches en oméga-3 : noix, poisson gras cuit",
            "Continuez l'hydratation même si les mictions sont fréquentes",
            "Réduisez le sel pour limiter les œdèmes",
            "Consommez des aliments riches en vitamine K : épinards, brocoli",
        ],
    },
    "activity": {
        "title": "Activité Physique",
        "description": "Exercices doux adaptés à chaque mois",
        1: [
            "Marche légère 20–30 min/jour",
            "Yoga prénatal adapté au 1er trimestre",
            "Évitez les sports de contact et les chutes",
            "Écoutez votre corps : réduisez si fatiguée",
        ],
        2: [
            "Natation ou aquagym prénatal : idéal pour soulager le dos",
            "Marche douce 30 min/jour",
            "Exercices de Kegel pour renforcer le périnée",
            "Pilates prénatal avec moniteur qualifié",
        ],
        3: [
            "Marche courte et régulière",
            "Exercices de respiration et relaxation",
            "Préparation à l'accouchement (sophrologie, haptonomie)",
            "Évitez rester debout trop longtemps",
            "Exercices de balancement sur ballon de grossesse",
        ],
    },
    "supplements": {
        "title": "Suppléments et Médicaments",
        "description": "Vitamines recommandées pour bébé",
        1: [
            "Acide folique (vitamine B9) : 400–800 µg/jour — indispensable",
            "Vitamine D : 1000–2000 UI/jour si insuffisance",
            "Iode : important pour le développement neurologique",
            "Ne prenez aucun médicament sans avis médical",
        ],
        2: [
            "Fer : si anémie détectée (NFS), prescription médicale",
            "Calcium : 1000 mg/jour via alimentation ou supplément",
            "Continuez acide folique et vitamine D",
            "Omega-3 DHA : important pour le développement cérébral",
        ],
        3: [
            "Continuez tous les suppléments prescrits",
            "Magnésium : peut aider les crampes nocturnes (avis médical)",
            "Vitamine K : important pour la coagulation du bébé",
            "Ne stoppez pas les suppléments sans avis médical",
        ],
    },
    "mental_health": {
        "title": "Santé Mentale et Bien-être",
        "description": "Conseils relaxation et gestion du stress",
        1: [
            "Parlez de vos angoisses à votre médecin ou sage-femme",
            "Dormez autant que nécessaire",
            "Pratiquez la respiration abdominale profonde",
            "Entourez-vous de personnes positives",
        ],
        2: [
            "Prenez du temps pour vous : bains chauds (pas trop chauds), lecture",
            "Commencez un journal de grossesse",
            "Pratiquez la méditation ou la pleine conscience",
            "Partagez vos émotions avec votre partenaire",
        ],
        3: [
            "Préparez-vous mentalement à l'accouchement : cours de préparation",
            "Gérez l'anxiété par la respiration et la sophrologie",
            "Restez connectée à vos proches",
            "Il est normal d'avoir peur : parlez-en à votre médecin",
        ],
    },
    "birth_prep": {
        "title": "Préparation à l'Accouchement",
        "description": "Check-list et signes du travail",
        1: [
            "Choisissez votre maternité",
            "Planifiez vos consultations prénatales",
            "Commencez à vous informer sur les options d'accouchement",
        ],
        2: [
            "Visitez la maternité choisie",
            "Inscrivez-vous aux cours de préparation à l'accouchement",
            "Commencez à préparer la chambre du bébé",
            "Rédigez votre projet de naissance",
        ],
        3: [
            "Préparez la valise de maternité (dès 36 SA)",
            "Apprenez les signes du travail : contractions régulières, perte du bouchon muqueux, rupture de la poche des eaux",
            "Notez les numéros utiles : maternité, médecin, urgences",
            "Reposez-vous et faites confiance à votre corps",
            "Signes nécessitant un départ immédiat : contractions toutes les 5 min, rupture de la poche des eaux",
        ],
    },
}


def get_tips_by_trimester(trimester: int) -> dict:
    """Return all tip categories with content filtered for the given trimester."""
    result = {}
    for category, data in TIPS.items():
        tips_for_trimester = data.get(trimester, [])
        result[category] = {
            "title": data["title"],
            "description": data["description"],
            "tips": tips_for_trimester,
        }
    return result


def get_tips_by_category(category: str, trimester: int) -> dict | None:
    """Return tips for a specific category and trimester."""
    data = TIPS.get(category)
    if not data:
        return None
    return {
        "category": category,
        "title": data["title"],
        "description": data["description"],
        "trimester": trimester,
        "tips": data.get(trimester, []),
    }


AVAILABLE_CATEGORIES = list(TIPS.keys())
