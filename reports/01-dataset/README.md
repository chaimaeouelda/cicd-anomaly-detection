# Visualisation du dataset

Exploration du fichier `cicd_logs.csv` (5 300 exécutions : 5 000 normales et 300 attaques).

| Image | Ce qu'elle montre |
|---|---|
| [data_classes.png](data_classes.png) | Répartition des classes : 5 000 exécutions normales et 100 de chaque attaque |
| [data_distributions.png](data_distributions.png) | Distribution des variables clés par type d'exécution : les attaques se démarquent du trafic normal (accès aux secrets, domaines externes, durée, fichiers modifiés) |
| [data_hours.png](data_hours.png) | Nombre d'exécutions par heure : le trafic normal se concentre en journée, les attaques surtout la nuit |

Script : `src/visualize_data.py`