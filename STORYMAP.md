# Story Map — Veille tech opportuniste

**Méthode** : Jeff Patton, *User Story Mapping*. Backbone = activités du pipeline (colonne vertébrale, de gauche à droite dans l'ordre d'exécution réel). Sous chaque activité, les tâches sont empilées par priorité — la ligne du haut (**Walking Skeleton**) est le chemin minimal bout-en-bout qui produit un digest réel, même dégradé. Les lignes en dessous sont des releases ultérieures.

Backbone dérivé du pipeline défini dans `PRD.md` (section 2).

---

## Backbone (activités)

```
Ingérer → Diffuser les nouvelles → Extraire → Vérifier → Normaliser → Stocker → Digest
```

---

## Walking Skeleton (v0 — chemin bout-en-bout, scope minimal)

| Ingérer | Diffuser les nouvelles | Extraire | Vérifier | Normaliser | Stocker | Digest |
|---|---|---|---|---|---|---|
| Appeler l'API Lever pour **1 boîte** (Scaleway) | Comparer aux ids déjà vus dans l'état local | Appeler **1 SLM** avec un prompt d'extraction ouverte | Vérifier la citation verbatim (substring normalisé) | — (pas de normalisation en v0) | Écrire dans un tracker `.jsonl` append-only | Afficher le tracker brut (pas d'agrégation) |

**Objectif du walking skeleton** : prouver que le pattern extract-then-verify fonctionne de bout en bout sur des données réelles, avant d'élargir les sources ou le nombre de modèles. C'est le seul jalon qui compte pour valider l'hypothèse du PRD — tout le reste est de l'élargissement.

---

## Release 1 — Couverture des sources confirmées

| Ingérer | Diffuser les nouvelles | Extraire | Vérifier | Normaliser | Stocker | Digest |
|---|---|---|---|---|---|---|
| Étendre à Lever (360Learning, Contentsquare, BlaBlaCar) | Diff multi-boîtes (état local par boîte) | Prompt d'extraction stabilisé (issu du protocole d'éval) | Logging des rejets (matière première éval) | — | Tracker consolidé multi-boîtes | Group-by + comptage sur fenêtre glissante |
| Étendre à Ashby (Mistral AI, Alan, Pennylane) | | | | | | |
| Étendre à Greenhouse (Algolia, Doctolib) | | | | | | |

**Sortie de release** : les 9 sources confirmées du PRD sont couvertes, digest hebdomadaire lisible.

---

## Release 2 — Fiabilité et choix du modèle

| Ingérer | Diffuser les nouvelles | Extraire | Vérifier | Normaliser | Stocker | Digest |
|---|---|---|---|---|---|---|
| Gestion des erreurs API (timeout, 404 boîte) | — | Exécuter le protocole d'éval sur 2-3 SLM candidats | Publier le taux de rejet par modèle | Table d'alias (k8s→Kubernetes, etc.) | — | Digest formaté (markdown lisible) |

**Sortie de release** : le SLM en production est choisi sur données, pas par défaut. La normalisation par alias rend le digest lisible sans toucher à la détection.

---

## Release 3 — Extension (si le signal se confirme utile)

| Ingérer | Diffuser les nouvelles | Extraire | Vérifier | Normaliser | Stocker | Digest |
|---|---|---|---|---|---|---|
| OCTO Technology (SmartRecruiters) — après confirmation endpoint | | | | | | |
| PayFit (Teamtailor) — après confirmation slug/token | | | | | | |

**Condition d'entrée** : ne s'attaque à cette release que si le digest des releases 1-2 a effectivement changé une décision de montée en compétences — sinon, ROI douteux d'ajouter des sources pour élargir la couverture sans besoin démontré (cohérent avec la logique GIST : on ne scope l'étape suivante qu'après preuve d'usage de la précédente).

---

## Hors story map (explicitement exclu, cf. PRD section 1)

- OVHcloud, Outscale, Cloud Temple, Numspot, Clever Cloud (pas d'API publique → pas de ticket, veille manuelle ponctuelle).
- Dashboard temps réel, service permanent, scoring/classement des technologies.

---

## Prochaine étape

Découper le Walking Skeleton en tickets/tâches concrètes (fichiers/modules) pour démarrer le pair programming.
