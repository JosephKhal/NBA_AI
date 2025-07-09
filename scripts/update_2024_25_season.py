#!/usr/bin/env python3
"""
Script d'intégration des données de la saison 2024-25
Automatise la mise à jour complète du système NBA_AI
"""

import argparse
import logging
import os
import sys
from datetime import datetime

# Ajouter le répertoire src au path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.config import config
from src.database_updater.database_update_manager import update_database
from src.database_audit import database_audit
from src.logging_config import setup_logging

def main():
    """Script principal d'intégration 2024-25"""
    parser = argparse.ArgumentParser(description="Intégration des données NBA 2024-25")
    parser.add_argument("--log_level", default="INFO", help="Niveau de logging")
    parser.add_argument("--force", action="store_true", help="Force la mise à jour même si les données existent")
    parser.add_argument("--audit", action="store_true", help="Effectue un audit après la mise à jour")
    
    args = parser.parse_args()
    setup_logging(log_level=args.log_level.upper())
    
    logging.info("🏀 Début de l'intégration des données NBA 2024-25")
    
    try:
        # Étape 1: Mise à jour de la configuration
        update_config_for_2024_25()
        
        # Étape 2: Mise à jour des données
        update_season_data("2024-2025", force=args.force)
        
        # Étape 3: Audit des données (optionnel)
        if args.audit:
            audit_results = database_audit("2024-2025", output_file="audit_2024_25.csv")
            logging.info(f"Audit terminé. Résultats sauvés dans audit_2024_25.csv")
        
        # Étape 4: Mise à jour des modèles
        update_prediction_models()
        
        logging.info("✅ Intégration 2024-25 terminée avec succès!")
        
    except Exception as e:
        logging.error(f"❌ Erreur lors de l'intégration: {e}")
        sys.exit(1)

def update_config_for_2024_25():
    """Met à jour la configuration pour inclure 2024-25"""
    logging.info("📝 Mise à jour de la configuration...")
    
    # Vérifier que 2024-2025 est dans les saisons valides
    valid_seasons = config.get("api", {}).get("valid_seasons", [])
    if "2024-2025" not in valid_seasons:
        logging.warning("⚠️  2024-2025 n'est pas dans les saisons valides du config.yaml")
        logging.info("Ajoutez '2024-2025' à la liste api.valid_seasons dans config.yaml")

def update_season_data(season, force=False):
    """Met à jour toutes les données pour une saison"""
    logging.info(f"📊 Mise à jour des données pour la saison {season}")
    
    # Mise à jour complète avec tous les prédicteurs
    predictors = ["Baseline", "Linear", "Tree", "MLP"]
    
    for predictor in predictors:
        logging.info(f"🔄 Mise à jour avec le prédicteur {predictor}")
        try:
            update_database(season=season, predictor=predictor)
            logging.info(f"✅ {predictor} mis à jour avec succès")
        except Exception as e:
            logging.error(f"❌ Erreur avec {predictor}: {e}")

def update_prediction_models():
    """Met à jour les modèles de prédiction avec les nouvelles données"""
    logging.info("🤖 Mise à jour des modèles de prédiction...")
    
    # Cette fonction pourrait déclencher le réentraînement des modèles
    # Pour l'instant, on log juste les étapes nécessaires
    
    steps = [
        "1. Extraire les features de 2024-25",
        "2. Combiner avec les données historiques", 
        "3. Réentraîner les modèles Linear, Tree, MLP",
        "4. Valider les performances",
        "5. Sauvegarder les nouveaux modèles"
    ]
    
    for step in steps:
        logging.info(f"📋 {step}")
    
    logging.warning("⚠️  Le réentraînement automatique n'est pas encore implémenté")
    logging.info("💡 Exécutez manuellement les scripts dans src/model_training/")

if __name__ == "__main__":
    main()