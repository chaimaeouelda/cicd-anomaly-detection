# Résultats du modèle hybride

Fusion pondérée de l'autoencoder et de l'Isolation Forest : `score = w × AE + (1 − w) × IF`, après normalisation de chaque score par rapport au trafic normal.

| Image | Ce qu'elle montre | Script |
|---|---|---|
| [roc_hybrid.png](roc_hybrid.png) | Courbes ROC : autoencoder, Isolation Forest et hybride (w = 0,5) | `src/fuse.py` |
| [tune_w.png](tune_w.png) | F1 sur la validation selon le poids w : le meilleur compromis est retenu avec son seuil | `src/tune_hybrid.py` |

Configuration retenue : w = 0,8, seuil optimisé sur un jeu de validation, puis mesuré sur un jeu de test séparé.