\# Détection d'anomalies dans les pipelines CI/CD



Modèle hybride \*\*Autoencoder + Isolation Forest\*\*, exécuté sous \*\*Docker\*\*, pour détecter et bloquer les exécutions de pipelines suspectes (vol de secrets, cryptomining, commits malveillants).



!\[Progression](https://img.shields.io/badge/progression-75%25-blue)



\## Progression (suivi de certification)



\*\*75 % complété\*\* : semaines 1 et 2 terminées, semaine 3 presque terminée.



| Semaine | Contenu | Poids | État |

|---|---|---|---|

| 1 | Setup Docker + Données | 25 % | ✅ Terminée |

| 2 | Autoencoder + Isolation Forest | 30 % | ✅ Terminée |

| 3 | Modèle hybride + API + intégration CI/CD | 25 % | 🔄 En cours |

| 4 | Évaluation, tests, rapport | 20 % | ⏳ À faire |



Détail des tâches : \[docs/PROGRESS.md](docs/PROGRESS.md)



\## Résultats actuels (jeu de test simulé)



| Modèle | AUC | Précision | Rappel | F1 |

|---|---|---|---|---|

| Autoencoder seul | 1,000 | 1,000 | 0,956 | 0,977 |

| Isolation Forest seule | 0,995 | 0,844 | 0,844 | 0,844 |

| \*\*Hybride (w = 0,8)\*\* | 1,000 | 1,000 | 0,956 | 0,977 |



\## Architecture



```mermaid

flowchart LR

&#x20;   A\[Logs CI/CD] --> B\[Feature engineering]

&#x20;   B --> C\[Normalisation]

&#x20;   C --> D\[Autoencoder<br/>erreur de reconstruction]

&#x20;   C --> E\[Isolation Forest<br/>score d'isolement]

&#x20;   D --> F\[Fusion pondérée<br/>modèle hybride]

&#x20;   E --> F

&#x20;   F --> G\[API FastAPI /predict]

&#x20;   G --> H{Score > seuil ?}

&#x20;   H -- Oui --> I\[Pipeline bloqué]

&#x20;   H -- Non --> J\[Pipeline autorisé]

```



\## Structure du dépôt



```

cicd-anomaly-detection/

├── src/

│   ├── check\_env.py          # vérification de l'environnement

│   ├── generate\_data.py      # génération des logs (normal + 3 attaques)

│   ├── visualize\_data.py     # graphiques du dataset

│   ├── features.py           # feature engineering + normalisation

│   ├── ae\_model.py           # architecture de l'autoencoder

│   ├── train\_autoencoder.py  # entraînement de l'autoencoder

│   ├── eval\_autoencoder.py   # erreur de reconstruction + seuil

│   ├── train\_iforest.py      # entraînement de l'Isolation Forest

│   ├── compare\_scores.py     # comparaison + export des scores

│   ├── hybrid.py             # normalisation et fusion des scores

│   ├── fuse.py               # première fusion (w = 0,5)

│   ├── tune\_hybrid.py        # optimisation du poids et du seuil

│   ├── preprocess.py         # pré-traitement commun à l'API

│   └── api.py                # API FastAPI

├── scripts/gate.py           # contrôle bloquant pour le CI/CD

├── samples/                  # exemples d'exécutions (normal / suspect)

├── .github/workflows/        # workflow GitHub Actions

├── data/  models/  reports/  tests/

├── docs/PROGRESS.md

├── Dockerfile

├── docker-compose.yml

└── requirements.txt

```



\## Démarrage rapide (PowerShell + Docker Desktop)



```powershell

git clone https://github.com/chaimaeouelda/cicd-anomaly-detection.git

cd cicd-anomaly-detection

docker compose build

docker compose run --rm ml python -m src.generate\_data

docker compose run --rm ml python -m src.features

docker compose run --rm ml python -m src.train\_autoencoder

docker compose run --rm ml python -m src.train\_iforest

docker compose run --rm ml python -m src.compare\_scores

docker compose run --rm ml python -m src.tune\_hybrid

docker compose up -d api

```



Tester l'API :



```powershell

$run = @{hour=3;duration\_s=1100;n\_commands=30;n\_secret\_access=14;n\_network\_calls=45;n\_ext\_domains=10;files\_changed=6;failed\_steps=0;new\_ip=1;commits\_24h=3} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8000/predict -Method Post -Body $run -ContentType "application/json"

```



Documentation interactive : http://localhost:8000/docs



\## Données simulées



| Classe | Comportement |

|---|---|

| `normal` | Activité de pipeline habituelle (5000 exécutions) |

| `secret\_exfil` | Nombreux accès aux secrets et domaines externes, de nuit, IP inconnue |

| `crypto\_mining` | Durée anormalement longue, de nuit |

| `malicious\_commit` | Beaucoup de fichiers et de commandes, IP inconnue |



\## Méthode



\- \*\*Autoencoder\*\* (11 → 8 → 4 → 8 → 11) entraîné sur le trafic normal uniquement ; le score est l'erreur de reconstruction.

\- \*\*Isolation Forest\*\* (200 arbres) entraînée sur les mêmes features.

\- \*\*Hybride\*\* : chaque score est normalisé par rapport au trafic normal (0 = médiane, 1 = 95e percentile), puis fusionné : `score = w × AE + (1 − w) × IF`. Le poids `w` et le seuil sont choisis sur un jeu de validation, puis évalués sur un jeu de test distinct.

