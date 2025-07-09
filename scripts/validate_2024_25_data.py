#!/usr/bin/env python3
"""
Script de validation des données 2024-25
Vérifie la qualité et la cohérence des données intégrées
"""

import sqlite3
import pandas as pd
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.config import config
from src.logging_config import setup_logging

DB_PATH = config["database"]["path"]

def validate_2024_25_data():
    """Validation complète des données 2024-25"""
    setup_logging(log_level="INFO")
    
    print("🔍 Validation des données NBA 2024-25")
    print("=" * 50)
    
    with sqlite3.connect(DB_PATH) as conn:
        # 1. Statistiques générales
        print("\n📊 STATISTIQUES GÉNÉRALES")
        stats = get_season_stats(conn, "2024-2025")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # 2. Vérification de la couverture temporelle
        print("\n📅 COUVERTURE TEMPORELLE")
        coverage = check_temporal_coverage(conn, "2024-2025")
        print(f"  Première date: {coverage['first_date']}")
        print(f"  Dernière date: {coverage['last_date']}")
        print(f"  Jours couverts: {coverage['days_covered']}")
        
        # 3. Qualité des données
        print("\n✅ QUALITÉ DES DONNÉES")
        quality = check_data_quality(conn, "2024-2025")
        for check, result in quality.items():
            status = "✅" if result['passed'] else "❌"
            print(f"  {status} {check}: {result['message']}")
        
        # 4. État des prédictions
        print("\n🤖 ÉTAT DES PRÉDICTIONS")
        predictions = check_predictions_status(conn, "2024-2025")
        for predictor, count in predictions.items():
            print(f"  {predictor}: {count} prédictions")
        
        # 5. Recommandations
        print("\n💡 RECOMMANDATIONS")
        recommendations = generate_recommendations(stats, quality, predictions)
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")

def get_season_stats(conn, season):
    """Obtient les statistiques de base pour une saison"""
    cursor = conn.cursor()
    
    # Nombre total de jeux
    cursor.execute("SELECT COUNT(*) FROM Games WHERE season = ?", (season,))
    total_games = cursor.fetchone()[0]
    
    # Jeux par statut
    cursor.execute("""
        SELECT status, COUNT(*) 
        FROM Games 
        WHERE season = ? 
        GROUP BY status
    """, (season,))
    status_counts = dict(cursor.fetchall())
    
    # Jeux avec données finalisées
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN pre_game_data_finalized = 1 THEN 1 ELSE 0 END) as pre_game_final,
            SUM(CASE WHEN game_data_finalized = 1 THEN 1 ELSE 0 END) as game_final
        FROM Games 
        WHERE season = ?
    """, (season,))
    finalized = cursor.fetchone()
    
    return {
        "Total des jeux": total_games,
        "Jeux terminés": status_counts.get("Completed", 0),
        "Jeux en cours": status_counts.get("In Progress", 0),
        "Jeux à venir": status_counts.get("Not Started", 0),
        "Données pré-jeu finalisées": finalized[0],
        "Données de jeu finalisées": finalized[1]
    }

def check_temporal_coverage(conn, season):
    """Vérifie la couverture temporelle"""
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            MIN(date(date_time_est)) as first_date,
            MAX(date(date_time_est)) as last_date,
            COUNT(DISTINCT date(date_time_est)) as days_covered
        FROM Games 
        WHERE season = ?
    """, (season,))
    
    result = cursor.fetchone()
    return {
        "first_date": result[0],
        "last_date": result[1], 
        "days_covered": result[2]
    }

def check_data_quality(conn, season):
    """Vérifie la qualité des données"""
    cursor = conn.cursor()
    quality_checks = {}
    
    # 1. Cohérence des GameStates
    cursor.execute("""
        SELECT COUNT(*) 
        FROM Games g
        LEFT JOIN GameStates gs ON g.game_id = gs.game_id AND gs.is_final_state = 1
        WHERE g.season = ? AND g.status = 'Completed' AND gs.game_id IS NULL
    """, (season,))
    
    missing_final_states = cursor.fetchone()[0]
    quality_checks["États finaux manquants"] = {
        "passed": missing_final_states == 0,
        "message": f"{missing_final_states} jeux terminés sans état final"
    }
    
    # 2. Cohérence PbP vs GameStates
    cursor.execute("""
        SELECT 
            g.game_id,
            COUNT(DISTINCT p.play_id) as pbp_count,
            COUNT(DISTINCT gs.play_id) as gs_count
        FROM Games g
        LEFT JOIN PbP_Logs p ON g.game_id = p.game_id
        LEFT JOIN GameStates gs ON g.game_id = gs.game_id
        WHERE g.season = ? AND g.status = 'Completed'
        GROUP BY g.game_id
        HAVING pbp_count != gs_count OR pbp_count < 300 OR pbp_count > 800
    """, (season,))
    
    inconsistent_counts = len(cursor.fetchall())
    quality_checks["Cohérence PbP/GameStates"] = {
        "passed": inconsistent_counts == 0,
        "message": f"{inconsistent_counts} jeux avec des comptages incohérents"
    }
    
    # 3. Features manquantes
    cursor.execute("""
        SELECT COUNT(*)
        FROM Games g
        LEFT JOIN Features f ON g.game_id = f.game_id
        WHERE g.season = ? AND g.pre_game_data_finalized = 1 AND f.game_id IS NULL
    """, (season,))
    
    missing_features = cursor.fetchone()[0]
    quality_checks["Features manquantes"] = {
        "passed": missing_features == 0,
        "message": f"{missing_features} jeux sans features malgré données finalisées"
    }
    
    return quality_checks

def check_predictions_status(conn, season):
    """Vérifie l'état des prédictions"""
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT predictor, COUNT(*)
        FROM Predictions p
        JOIN Games g ON p.game_id = g.game_id
        WHERE g.season = ?
        GROUP BY predictor
    """, (season,))
    
    return dict(cursor.fetchall())

def generate_recommendations(stats, quality, predictions):
    """Génère des recommandations basées sur l'analyse"""
    recommendations = []
    
    # Recommandations basées sur les statistiques
    if stats["Jeux à venir"] > 0:
        recommendations.append(f"Surveiller {stats['Jeux à venir']} jeux à venir pour mise à jour automatique")
    
    if stats["Données pré-jeu finalisées"] < stats["Total des jeux"]:
        missing = stats["Total des jeux"] - stats["Données pré-jeu finalisées"]
        recommendations.append(f"Finaliser les données pré-jeu pour {missing} jeux")
    
    # Recommandations basées sur la qualité
    for check, result in quality.items():
        if not result['passed']:
            recommendations.append(f"Corriger: {result['message']}")
    
    # Recommandations basées sur les prédictions
    expected_predictors = ["Baseline", "Linear", "Tree", "MLP"]
    for predictor in expected_predictors:
        if predictor not in predictions:
            recommendations.append(f"Générer des prédictions pour le modèle {predictor}")
        elif predictions[predictor] < stats["Données pré-jeu finalisées"]:
            missing = stats["Données pré-jeu finalisées"] - predictions[predictor]
            recommendations.append(f"Compléter {missing} prédictions pour {predictor}")
    
    if not recommendations:
        recommendations.append("Toutes les données semblent en bon état ✅")
    
    return recommendations

if __name__ == "__main__":
    validate_2024_25_data()