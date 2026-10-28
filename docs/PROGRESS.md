\# D�tection d'anomalies dans les pipelines CI/CD



Mod�le hybride \*\*Autoencoder + Isolation Forest\*\*, ex�cut� sous \*\*Docker\*\*, pour d�tecter et bloquer les ex�cutions de pipelines suspectes (vol de secrets, cryptomining, commits malveillants).



!\[Progression](https://img.shields.io/badge/progression-75%25-blue)



\## Progression (suivi de certification)



\*\*75 % compl�t�\*\* : semaines 1 et 2 termin�es, semaine 3 presque termin�e.



| Semaine | Contenu | Poids | �tat |

|---|---|---|---|

| 1 | Setup Docker + Donn�es | 25 % | ? Termin�e |

| 2 | Autoencoder + Isolation Forest | 30 % | ? Termin�e |

| 3 | Mod�le hybride + API + int�gration CI/CD | 25 % | ?? En cours |

| 4 | �valuation, tests, rapport | 20 % | ? � faire |



D�tail des t�ches : \[docs/PROGRESS.md](docs/PROGRESS.md)



\## R�sultats actuels (jeu de test simul�)



| Mod�le | AUC | Pr�cision | Rappel | F1 |

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

&#x20;   D --> F\[Fusion pond�r�e<br/>mod�le hybride]

&#x20;   E --> F

&#x20;   F --> G\[API FastAPI /predict]

&#x20;   G --> H{Score > seuil ?}

&#x20;   H -- Oui --> I\[Pipeline bloqu�]

&#x20;   H -- Non --> J\[Pipeline autoris�]

```



\## Structure du d�p�t



```

cicd-anomaly-detection/

+-- src/

�   +-- check\_env.py          # v�rification de l'environnement

�   +-- generate\_data.py      # g�n�ration des logs (normal + 3 attaques)

�   +-- visualize\_data.py     # graphiques du dataset

�   +-- features.py           # feature engineering + normalisation

�   +-- ae\_model.py           # architecture de l'autoencoder

�   +-- train\_autoencoder.py  # entra�nement de l'autoencoder

�   +-- eval\_autoencoder.py   # erreur de reconstruction + seuil

�   +-- train\_iforest.py      # entra�nement de l'Isolation Forest

�   +-- compare\_scores.py     # comparaison + export des scores

�   +-- hybrid.py             # normalisation et fusion des scores

�   +-- fuse.py               # premi�re fusion (w = 0,5)

�   +-- tune\_hybrid.py        # optimisation du poids et du seuil

�   +-- preprocess.py         # pr�-traitement commun � l'API

�   +-- api.py                # API FastAPI

+-- scripts/gate.py           # contr�le bloquant pour le CI/CD

+-- samples/                  # exemples d'ex�cutions (normal / suspect)

+-- .github/workflows/        # workflow GitHub Actions

+-- data/  models/  reports/  tests/

+-- docs/PROGRESS.md

+-- Dockerfile

+-- docker-compose.yml

+-- requirements.txt

```



\## D�marrage rapide (PowerShell + Docker Desktop)



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



\## Donn�es simul�es



| Classe | Comportement |

|---|---|

| `normal` | Activit� de pipeline habituelle (5000 ex�cutions) |

| `secret\_exfil` | Nombreux acc�s aux secrets et domaines externes, de nuit, IP inconnue |

| `crypto\_mining` | Dur�e anormalement longue, de nuit |

| `malicious\_commit` | Beaucoup de fichiers et de commandes, IP inconnue |



\## M�thode



\- \*\*Autoencoder\*\* (11 ? 8 ? 4 ? 8 ? 11) entra�n� sur le trafic normal uniquement ; le score est l'erreur de reconstruction.

\- \*\*Isolation Forest\*\* (200 arbres) entra�n�e sur les m�mes features.

\- \*\*Hybride\*\* : chaque score est normalis� par rapport au trafic normal (0 = m�diane, 1 = 95e percentile), puis fusionn� : `score = w � AE + (1 - w) � IF`. Le poids `w` et le seuil sont choisis sur un jeu de validation, puis �valu�s sur un jeu de test distinct.

