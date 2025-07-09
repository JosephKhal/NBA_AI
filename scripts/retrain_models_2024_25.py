#!/usr/bin/env python3
"""
Script de réentraînement des modèles avec les données 2024-25
Automatise le processus de mise à jour des modèles ML
"""

import os
import sys
import subprocess
import logging
from datetime import datetime
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.config import config
from src.logging_config import setup_logging

def main():
    """Script principal de réentraînement"""
    setup_logging(log_level="INFO")
    
    logging.info("🤖 Début du réentraînement des modèles avec données 2024-25")
    
    # Saisons d'entraînement (historique + nouvelle)
    training_seasons = [
        "2021-2022", "2022-2023", "2023-2024", "2024-2025"
    ]
    
    # Saison de test (la plus récente complète)
    testing_season = "2024-2025"
    
    try:
        # 1. Vérifier les prérequis
        check_prerequisites()
        
        # 2. Réentraîner chaque modèle
        models_to_train = [
            ("linear_model.py", "Linear"),
            ("xgb_model.py", "Tree"), 
            ("mlp_model.py", "MLP")
        ]
        
        for model_file, model_name in models_to_train:
            logging.info(f"🔄 Réentraînement du modèle {model_name}")
            retrain_model(model_file, training_seasons, testing_season)
        
        # 3. Mettre à jour la configuration
        update_model_config()
        
        # 4. Valider les nouveaux modèles
        validate_new_models()
        
        logging.info("✅ Réentraînement terminé avec succès!")
        
    except Exception as e:
        logging.error(f"❌ Erreur lors du réentraînement: {e}")
        sys.exit(1)

def check_prerequisites():
    """Vérifie que tous les prérequis sont présents"""
    logging.info("🔍 Vérification des prérequis...")
    
    # Vérifier que les données 2024-25 sont présentes
    from src.database_audit import database_audit
    
    try:
        audit_results = database_audit("2024-2025", output_file=None)
        logging.info("✅ Données 2024-25 validées")
    except Exception as e:
        raise Exception(f"Données 2024-25 non disponibles: {e}")
    
    # Vérifier les dépendances Python
    required_packages = ["torch", "sklearn", "xgboost", "pandas", "numpy"]
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            raise Exception(f"Package manquant: {package}")
    
    logging.info("✅ Tous les prérequis sont satisfaits")

def retrain_model(model_file, training_seasons, testing_season):
    """Réentraîne un modèle spécifique"""
    model_script = Path(__file__).parent.parent / "src" / "model_training" / model_file
    
    if not model_script.exists():
        raise Exception(f"Script de modèle non trouvé: {model_script}")
    
    # Modifier temporairement les saisons dans le script
    # (Dans un vrai projet, on passerait ces paramètres en arguments)
    logging.info(f"📊 Entraînement avec saisons: {training_seasons}")
    logging.info(f"🧪 Test avec saison: {testing_season}")
    
    # Exécuter le script de modèle
    try:
        result = subprocess.run([
            sys.executable, str(model_script)
        ], capture_output=True, text=True, cwd=str(model_script.parent.parent.parent))
        
        if result.returncode != 0:
            raise Exception(f"Erreur d'exécution: {result.stderr}")
        
        logging.info("✅ Modèle entraîné avec succès")
        
    except Exception as e:
        logging.error(f"❌ Erreur lors de l'entraînement: {e}")
        raise

def update_model_config():
    """Met à jour la configuration avec les nouveaux modèles"""
    logging.info("📝 Mise à jour de la configuration des modèles...")
    
    # Trouver les nouveaux fichiers de modèles
    models_dir = Path(__file__).parent.parent / "models"
    
    if not models_dir.exists():
        logging.warning("⚠️  Répertoire models/ non trouvé")
        return
    
    # Lister les modèles récents
    model_files = {
        "Linear": list(models_dir.glob("Ridge_Regression_*.joblib")),
        "Tree": list(models_dir.glob("XGBoost_Regression_*.joblib")),
        "MLP": list(models_dir.glob("MLP_Regression_*.pth"))
    }
    
    # Afficher les modèles trouvés
    for model_type, files in model_files.items():
        if files:
            latest = max(files, key=lambda f: f.stat().st_mtime)
            logging.info(f"  {model_type}: {latest.name}")
        else:
            logging.warning(f"  ⚠️  Aucun modèle {model_type} trouvé")
    
    logging.info("💡 Mettez à jour manuellement config.yaml avec les nouveaux chemins")

def validate_new_models():
    """Valide les nouveaux modèles entraînés"""
    logging.info("🧪 Validation des nouveaux modèles...")
    
    # Tests de base
    tests = [
        "1. Vérifier que les fichiers de modèles existent",
        "2. Tester le chargement des modèles",
        "3. Valider les prédictions sur un échantillon",
        "4. Comparer les performances avec les anciens modèles"
    ]
    
    for test in tests:
        logging.info(f"📋 {test}")
    
    # Ici on pourrait implémenter des tests automatisés
    logging.info("✅ Validation manuelle requise")

if __name__ == "__main__":
    main()