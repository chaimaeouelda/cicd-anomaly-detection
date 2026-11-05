# Résultats des modèles de base

Autoencoder et Isolation Forest, entraînés uniquement sur le trafic normal.

| Image | Ce qu'elle montre | Script |
|---|---|---|
| [ae_loss.png](ae_loss.png) | Courbe d'entraînement de l'autoencoder : l'erreur diminue sur les données d'entraînement et de validation | `src/train_autoencoder.py` |
| [ae_errors.png](ae_errors.png) | Erreur de reconstruction : les exécutions normales et les attaques sont séparées, la ligne pointillée est le seuil (95e percentile du normal) | `src/eval_autoencoder.py` |
| [roc_base.png](roc_base.png) | Courbes ROC de l'autoencoder et de l'Isolation Forest sur le jeu de test | `src/compare_scores.py` |