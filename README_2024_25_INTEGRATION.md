# Guide d'intégration NBA 2024-25

## 🎯 Objectif
Intégrer les données de la saison NBA 2024-25 et mettre à jour les modèles de prédiction pour disposer de prédictions actualisées.

## 📋 Étapes d'intégration

### 1. Préparation de l'environnement

```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Vérifier les dépendances
pip install -r requirements.txt

# Sauvegarder la base de données actuelle
cp data/NBA_AI_BASE.sqlite data/NBA_AI_BASE_backup_$(date +%Y%m%d).sqlite
```

### 2. Mise à jour de la configuration

```bash
# Éditer config.yaml pour ajouter 2024-2025 aux saisons valides
# Voir config_updates.yaml pour les modifications suggérées
```

### 3. Intégration des données

```bash
# Exécuter le script d'intégration automatique
python scripts/update_2024_25_season.py --log_level=INFO --audit

# OU mise à jour manuelle étape par étape
python -m src.database_updater.database_update_manager --season=2024-2025 --predictor=Baseline
python -m src.database_updater.database_update_manager --season=2024-2025 --predictor=Linear
python -m src.database_updater.database_update_manager --season=2024-2025 --predictor=Tree
python -m src.database_updater.database_update_manager --season=2024-2025 --predictor=MLP
```

### 4. Validation des données

```bash
# Valider la qualité des données intégrées
python scripts/validate_2024_25_data.py

# Audit complet de la base de données
python -m src.database_audit --season=2024-2025
```

### 5. Réentraînement des modèles

```bash
# Réentraîner automatiquement tous les modèles
python scripts/retrain_models_2024_25.py

# OU réentraînement manuel
cd src/model_training
python linear_model.py    # Modèle Ridge Regression
python xgb_model.py       # Modèle XGBoost  
python mlp_model.py       # Modèle MLP
```

### 6. Mise à jour de la configuration des modèles

```bash
# Mettre à jour config.yaml avec les nouveaux chemins de modèles
# Voir la section predictors dans config_updates.yaml
```

### 7. Test de l'application

```bash
# Tester l'application web avec les nouvelles données
python start_app.py --predictor=Linear --log_level=INFO

# Tester l'API
curl "http://localhost:5000/api/games?date=2024-12-19&predictor=Linear"
```

## 🔍 Vérifications importantes

### Données intégrées
- [ ] Saison 2024-2025 présente dans la table Games
- [ ] GameStates générés pour tous les matchs terminés
- [ ] Features calculées pour tous les matchs éligibles
- [ ] Prédictions générées pour tous les prédicteurs

### Qualité des données
- [ ] Pas d'états finaux manquants pour les matchs terminés
- [ ] Cohérence entre PbP_Logs et GameStates (300-800 actions par match)
- [ ] Toutes les équipes NBA 2024-25 présentes
- [ ] Dates cohérentes (octobre 2024 - avril 2025)

### Modèles mis à jour
- [ ] Nouveaux fichiers de modèles générés dans models/
- [ ] Configuration mise à jour avec les nouveaux chemins
- [ ] Performances des modèles validées (MAE < 12 points)
- [ ] Prédictions cohérentes sur des échantillons de test

## 📊 Métriques de performance attendues

Après intégration, les modèles devraient maintenir ces performances :

| Modèle | MAE Home Score | MAE Away Score | MAE Home Margin | Log Loss Win % |
|--------|----------------|----------------|-----------------|----------------|
| Baseline | ~9.65 | ~9.83 | ~11.61 | ~0.65 |
| Linear | ~9.47 | ~9.46 | ~11.25 | ~0.62 |
| Tree | ~9.62 | ~9.61 | ~11.30 | ~0.64 |
| MLP | ~9.41 | ~9.45 | ~11.22 | ~0.63 |

## 🚨 Résolution de problèmes

### Erreur "Saison non valide"
```bash
# Vérifier que 2024-2025 est dans config.yaml
grep -A 5 "valid_seasons" config.yaml
```

### Données manquantes
```bash
# Vérifier la connectivité à l'API NBA
python -m src.database_updater.schedule --season=2024-2025 --log_level=DEBUG
```

### Modèles non chargés
```bash
# Vérifier les chemins dans config.yaml
ls -la models/
```

### Performances dégradées
```bash
# Comparer avec les métriques de référence
python scripts/validate_2024_25_data.py
```

## 📈 Monitoring continu

Une fois l'intégration terminée, configurez un monitoring pour :

1. **Mise à jour quotidienne** des données en cours de saison
2. **Alertes** en cas d'échec de prédiction
3. **Métriques de performance** en temps réel
4. **Sauvegarde automatique** avant chaque mise à jour

```bash
# Exemple de tâche cron pour mise à jour quotidienne
# 0 6 * * * /path/to/venv/bin/python /path/to/scripts/update_2024_25_season.py --log_level=WARNING
```

## 🎉 Validation finale

L'intégration est réussie quand :
- ✅ L'application web affiche les matchs 2024-25
- ✅ Les prédictions sont générées pour tous les modèles
- ✅ Les performances sont dans les plages attendues
- ✅ L'audit de base de données ne remonte aucune erreur

---

**Note**: Ce processus peut prendre 30-60 minutes selon la quantité de données à traiter et la puissance de calcul disponible.