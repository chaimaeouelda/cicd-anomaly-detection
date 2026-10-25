# Execute le pipeline complet (semaines 1 et 2) depuis la racine du projet
$ErrorActionPreference = "Stop"
docker compose build
foreach ($m in "check_env","generate_data","features","train_autoencoder","eval_autoencoder","train_iforest","compare_scores") {
    Write-Host "`n>>> $m" -ForegroundColor Cyan
    docker compose run --rm ml python -m "src.$m"
}
