# PRD — Veille tech opportuniste via offres d'emploi

**Statut** : draft v0.1 — 16/09/2026
**Auteur** : Dorian Erkens (PM/AI/EdTech)
**Mode de travail** : pair programming, pas de livraison clé en main

---

## 1. Problème et hypothèse

**Hypothèse à tester** (format Confidence Meter, Gilad) : *si on extrait automatiquement les outils/frameworks mentionnés dans les nouvelles offres d'emploi tech françaises, on obtient un signal de priorisation de montée en compétences plus fiable qu'une veille manuelle ad hoc.*

Ce n'est pas un produit à discovery classique (pas d'utilisateur externe, pas de marché) — c'est un outil de veille personnelle. Le PRD sert ici de garde-fou pour ne pas sur-construire : le risque principal n'est pas "est-ce que ça a de la valeur" mais "est-ce que l'extraction est fiable et est-ce que le scope reste minimal".

**Non-objectifs explicites** :
- Pas de dashboard temps réel, pas de service permanent.
- Pas de couverture exhaustive du marché (dépendant des ATS avec API publique).
- Pas de classement/scoring des technologies — juste comptage et tendance.

---

## 2. Pipeline

```
[Cron hebdo]
   │
   ▼
1. Ingestion — APIs ATS confirmées (Lever, Ashby, Greenhouse)
   → stockage brut : {id, entreprise, titre, url, date_publication, texte_offre}
   │
   ▼
2. Diff — comparaison avec l'état local (fichier JSON)
   → isole les offres nouvelles (par id d'offre, pas de re-traitement)
   │
   ▼
3. Extraction (SLM local, Ollama/CPU)
   → pour chaque offre nouvelle : [{terme, citation_exacte}]
   → prompt : extraction ouverte, pas de liste de référence
   │
   ▼
4. Vérification déterministe (code, pas de LLM)
   → citation_exacte doit apparaître verbatim (normalisée : casse, espaces) dans texte_offre
   → rejet + log si non trouvée
   │
   ▼
5. Normalisation légère (table d'alias, affichage seulement)
   → k8s → Kubernetes ; ne modifie pas la détection en amont
   │
   ▼
6. Stockage append-only (tracker.json ou .jsonl)
   → {entreprise, poste, date, lien, outils_valides[]}
   │
   ▼
7. Digest hebdomadaire (group-by + comptage, déterministe)
   → pas de LLM — agrégation pure sur le tracker
```

**Sources confirmées (Phase 1)** : Scaleway, Mistral AI, Alan, Pennylane, 360Learning, Algolia, Doctolib, Contentsquare, BlaBlaCar (9 boîtes, 3 ATS : Lever, Ashby, Greenhouse).

**À confirmer avant intégration (Phase 2)** : OCTO Technology (SmartRecruiters), PayFit (Teamtailor).

**Hors scope (pas d'API publique)** : OVHcloud, Outscale, Cloud Temple, Numspot, Clever Cloud — veille manuelle ponctuelle si besoin, pas automatisée.

### Garde-fous anti-hallucination

Le point critique du pipeline est l'étape 3→4 (extract-then-verify). C'est un pattern connu en eval de systèmes LLM à sortie structurée : ne jamais faire confiance à une extraction non vérifiable mécaniquement. Ici :
- Le SLM ne fait **que** proposer des paires (terme, citation).
- La vérification est **100% déterministe** (substring match normalisé) — aucun jugement LLM sur la validité.
- Toute extraction rejetée est loguée (pas silencieusement droppée) → sert de matière première au protocole d'eval (section 3).

---

## 3. Protocole d'éval — choix du SLM

Objectif : choisir un modèle local (candidat Ollama/CPU) de façon empirique, pas sur la réputation du modèle. C'est un exercice d'eval coding, un des objectifs prioritaires identifiés.

### Métriques

| Métrique | Définition | Type |
|---|---|---|
| **Taux de rejet** | % d'extractions proposées par le SLM rejetées à l'étape 4 (citation non verbatim) | Automatique, déterministe |
| **Taux de couverture** | % d'outils "évidents" (relecture manuelle d'un échantillon) effectivement extraits | Semi-manuel |
| **Qualité perçue** | Revue manuelle sur un échantillon fixe d'offres (ex. 20 offres, mêmes offres pour tous les modèles) — les termes extraits sont-ils pertinents et non bruités ? | Manuel, grille simple (pertinent / bruit / manqué) |
| **Latence** | Temps d'extraction moyen par offre, CPU local | Automatique |

### Méthode

1. Fixer un jeu de test = les N premières offres nouvelles de la première semaine réelle (pas de dataset synthétique — on veut du signal sur les vraies offres FR tech).
2. Faire tourner chaque SLM candidat sur ce même jeu, dans les mêmes conditions.
3. Calculer taux de rejet + latence automatiquement.
4. Faire une revue manuelle rapide (grille 3 colonnes ci-dessus) sur le même échantillon pour les 2-3 candidats.
5. Trancher sur le couple (taux de rejet bas + qualité perçue correcte), pas sur la latence seule — c'est un job hebdo, pas temps réel.

Ce protocole est volontairement léger (pas de framework d'eval externe) car le volume est faible (une fois/semaine, ~10 boîtes). Réévaluable si le pipeline scale.

---

## 4. Stockage et état

- **État local** (fichier JSON) : sert uniquement au diff — liste des ids d'offres déjà vues par boîte.
- **Tracker** (append-only) : la donnée de valeur — historique complet des offres + outils validés. Ne doit jamais être écrasé, seulement complété.
- Pas de base de données — cohérent avec la contrainte "minimaliste, pas de service permanent".

---

## 5. Digest hebdomadaire

Agrégation pure sur le tracker (group-by outil, comptage sur fenêtre glissante ex. 4 ou 12 semaines). Pas de LLM nécessaire à cette étape — évite d'introduire de la variance/coût là où un simple `groupby` suffit. Sortie possible : markdown ou JSON, à trancher en fonction de l'usage (lecture rapide vs réinjection dans un autre outil).

---

## 6. Questions ouvertes à trancher

1. **Emplacement du code** : nouveau repo dédié vs intégration dans un repo existant ? Ce repo (`veille-opportuniste`) est actuellement vide — a priori il *est* la réponse, mais à confirmer si l'intention était différente (ex. repo monolithique existant avec d'autres outils perso).
2. **Format exact du fichier d'état** : JSON simple `{boite: [ids_vus]}` suffit pour le diff, mais faut-il fusionner état + tracker dans un seul fichier (source de vérité unique) ou les garder séparés (état = cache jetable, tracker = donnée durable) ? Recommandation par défaut : séparés, pour pouvoir reconstruire l'état sans perdre le tracker.
3. **Liste initiale de SLM candidats à tester** : à définir — candidats plausibles sur Ollama/CPU pour extraction structurée légère (ex. modèles 3B-8B). Le choix final doit sortir du protocole d'éval (section 3), pas d'une présélection arbitraire.

---

## 7. Prochaines étapes (pair programming)

- [ ] Trancher les 3 questions ouvertes (section 6).
- [ ] Scaffolder le repo (structure minimale : ingestion / extraction / vérification / digest).
- [ ] Implémenter l'ingestion pour les 9 sources confirmées.
- [ ] Implémenter extract-then-verify avec logging des rejets.
- [ ] Lancer le protocole d'éval sur le premier jeu réel d'offres.
- [ ] Planifier l'exécution hebdomadaire.

---

*Références de méthode : ICE Score / Confidence Meter (Itamar Gilad) pour le cadrage de l'hypothèse ; pattern extract-then-verify pour la fiabilité de l'extraction LLM sur sortie structurée.*
