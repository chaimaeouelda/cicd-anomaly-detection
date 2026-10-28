# DÃ©tection d'anomalies dans les pipelines CI/CD

ModÃ¨le hybride **Autoencoder + Isolation Forest**, exÃ©cutÃ© sous **Docker**, pour dÃ©tecter et bloquer les exÃ©cutions de pipelines suspectes (vol de secrets, cryptomining, commits malveillants).

![Progression](https://img.shields.io/badge/progression-80%25-blue)

## Progression (suivi de certification)

**55 % complÃ©tÃ©** : semaines 1 et 2 terminÃ©es.

| Semaine | Contenu | Poids | Ã‰tat |
|---|---|---|---|
| 1 | Setup Docker + DonnÃ©es | 25 % | âœ… TerminÃ©e |
| 2 | Autoencoder + Isolation Forest | 30 % | âœ… TerminÃ©e |
| 3 | ModÃ¨le hybride + API + intÃ©gration CI/CD | 25 % | â³ Ã€ faire |
| 4 | Ã‰valuation, tests, rapport | 20 % | â³ Ã€ faire |

DÃ©tail des tÃ¢ches : [docs/PROGRESS.md](docs/PROGRESS.md)

## Architecture

```mermaid
flowchart LR
    A[Logs CI/CD] --> B[Feature engineering]
    B --> C[Normalisation]
    C --> D[Autoencoder<br/>erreur de reconstruction]
    C --> E[Isolation Forest<br/>score d'isolement]
    D --> F[Fusion pondÃ©rÃ©e<br/>modÃ¨le hybride]
    E --> F
    F --> G{Score > seuil ?}
    G -- Oui --> H[Pipeline bloquÃ©]
    G -- Non --> I[Pipeline autorisÃ©]
    style F stroke-dasharray: 5 5
    style G stroke-dasharray: 5 5
    style H stroke-dasharray: 5 5
    style I stroke-dasharray: 5 5
```

Les blocs en pointillÃ©s (hybride, API, blocage) correspondent Ã  la semaine 3.

## Structure du dÃ©pÃ´t

```
cicd-anomaly-detection/
â”œâ”€â”€ src/
â”‚   â”œâ”€â”€ check_env.py          # vÃ©rification de l'environnement
â”‚   â”œâ”€â”€ generate_data.py      # gÃ©nÃ©ration des logs (normal + 3 attaques)
â”‚   â”œâ”€â”€ features.py           # feature engineering + normalisation
â”‚   â”œâ”€â”€ ae_model.py           # architecture de l'autoencoder
â”‚   â”œâ”€â”€ train_autoencoder.py  # entraÃ®nement de l'autoencoder
â”‚   â”œâ”€â”€ eval_autoencoder.py   # erreur de reconstruction + seuil
â”‚   â”œâ”€â”€ train_iforest.py      # entraÃ®nement de l'Isolation Forest
â”‚   â””â”€â”€ compare_scores.py     # comparaison + export des scores
â”œâ”€â”€ data/  models/  reports/  tests/
â”œâ”€â”€ docs/PROGRESS.md
â”œâ”€â”€ Dockerfile
â”œâ”€â”€ docker-compose.yml
â”œâ”€â”€ requirements.txt
â””â”€â”€ run_all.ps1               # exÃ©cute tout le pipeline
```

## DÃ©marrage rapide (PowerShell + Docker Desktop)

```powershell
git clone https://github.com/chaimaeouelda/cicd-anomaly-detection.git
cd cicd-anomaly-detection
.\run_all.ps1
```

Ou Ã©tape par Ã©tape :

```powershell
docker compose build
docker compose run --rm ml python -m src.generate_data
docker compose run --rm ml python -m src.features
docker compose run --rm ml python -m src.train_autoencoder
docker compose run --rm ml python -m src.eval_autoencoder
docker compose run --rm ml python -m src.train_iforest
docker compose run --rm ml python -m src.compare_scores
```

## DonnÃ©es simulÃ©es

| Classe | Comportement |
|---|---|
| `normal` | ActivitÃ© de pipeline habituelle (5000 exÃ©cutions) |
| `secret_exfil` | Nombreux accÃ¨s aux secrets et domaines externes, de nuit, IP inconnue |
| `crypto_mining` | DurÃ©e anormalement longue, de nuit |
| `malicious_commit` | Beaucoup de fichiers et de commandes, IP inconnue |

## MÃ©thode

- **Autoencoder** (11 â†’ 8 â†’ 4 â†’ 8 â†’ 11) entraÃ®nÃ© sur le trafic normal uniquement ; le score est l'erreur de reconstruction, le seuil est le 95e percentile du normal.
- **Isolation Forest** (200 arbres) entraÃ®nÃ© sur les mÃªmes features.
- **Hybride** (semaine 3) : fusion pondÃ©rÃ©e des deux scores normalisÃ©s.
