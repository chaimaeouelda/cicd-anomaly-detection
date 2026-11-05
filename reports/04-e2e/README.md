# Tests de bout en bout

290 exécutions **inconnues du modèle** (autre graine aléatoire) sont envoyées à l'API. Chaque décision (`ALLOW` ou `BLOCK`) est comparée à la réponse attendue.

| Fichier | Contenu |
|---|---|
| [e2e_scenarios.png](e2e_scenarios.png) | Taux de bonne décision par scénario (bleu : cas *core*, orange : cas *stress*) |
| [e2e_confusion.png](e2e_confusion.png) | Matrice de confusion globale |
| [e2e_report.json](e2e_report.json) | Résultats détaillés |

**Critères de réussite (scénarios core)** : au moins 85 % des attaques bloquées et au plus 10 % de faux positifs sur le trafic normal.

**Cas stress** : attaque d'exfiltration discrète, attaque de chaîne d'approvisionnement d'un type jamais vu, build nocturne et jour de livraison légitimes. Ils servent à repérer les limites du modèle et n'entraînent pas l'échec du test.

Scripts : `scripts/make_e2e_logs.py`, `scripts/e2e_run.py`, `src/e2e_report.py`