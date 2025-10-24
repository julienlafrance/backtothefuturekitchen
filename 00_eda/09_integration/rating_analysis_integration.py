# =============================================================================
# HEADER: IMPORTS ET CONFIGURATION GLOBALE
# =============================================================================

import sys
import warnings
import importlib
from pathlib import Path
from collections import Counter
from typing import Dict, List, Tuple, Optional, Union

# Ajout du chemin du module personnalisé
sys.path.append('../../')

# Import des modules internes
try:
    from _data_utils import *
    from _data_utils.data_utils_ratings import *
except ImportError:
    print("Attention: _data_utils non trouvés. Assurez-vous que le sys.path est correct.")
    # Définition de fonctions de secours si l'import échoue
    def load_clean_interactions():
        print("ERREUR: Impossible de charger 'load_clean_interactions'")
        return pl.DataFrame()
    def load_ratings_for_longterm_analysis(min_interactions=100, return_metadata=True, verbose=False):
        print("ERREUR: Impossible de charger 'load_ratings_for_longterm_analysis'")
        return pd.DataFrame(), {}

# Bibliothèques data science
import pandas as pd
import polars as pl
import numpy as np

# Visualisation
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from matplotlib.gridspec import GridSpec

# Statistiques
from scipy import stats
from scipy.stats import (
    mannwhitneyu, chi2_contingency, kruskal, f_oneway,
    spearmanr, kendalltau, linregress, rankdata
)

# Modèles statistiques
import statsmodels.api as sm

# Configuration globale
warnings.filterwarnings('ignore')
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 6)
plt.rcParams['font.size'] = 10


# =============================================================================
# FONCTIONS UTILITAIRES SPÉCIFIQUES (si nécessaire)
# =============================================================================

def weighted_spearman(x, y, w):
    """Corrélation de Spearman pondérée"""
    rx = rankdata(x)
    ry = rankdata(y)
    mx = np.average(rx, weights=w)
    my = np.average(ry, weights=w)
    cov_xy = np.average((rx - mx) * (ry - my), weights=w)
    sx = np.sqrt(np.average((rx - mx)**2, weights=w))
    sy = np.sqrt(np.average((ry - my)**2, weights=w))
    return cov_xy / (sx * sy)


# =============================================================================
# BLOC 1: ANALYSE DES TENDANCES (TRENDLINE)
# =============================================================================

def analyse_trendline_1():
    """
    Validation méthodologique - Tests pondérés vs non-pondérés
    """
    print("Chargement des statistiques mensuelles...")
    monthly_stats, metadata = load_ratings_for_longterm_analysis(
        min_interactions=100, 
        return_metadata=True, 
        verbose=False
    )
    
    # Préparation du DataFrame
    monthly_df = monthly_stats.copy()
    monthly_df['date'] = pd.to_datetime(monthly_df['date'])
    monthly_df = monthly_df.sort_values('date')
    monthly_df['mean_rating'] = pd.to_numeric(monthly_df['mean_rating'], errors='coerce')
    monthly_df['std_rating'] = pd.to_numeric(monthly_df.get('std_rating', 0), errors='coerce').fillna(0)
    monthly_df['n_interactions'] = pd.to_numeric(monthly_df['n_interactions'], errors='coerce').fillna(0)
    monthly_df = monthly_df.dropna(subset=['mean_rating'])

    # Variables pour tests statistiques
    monthly_sorted = monthly_df.sort_values('date')
    time_index = range(len(monthly_sorted))
    ratings = monthly_sorted['mean_rating'].values
    volumes = monthly_sorted['n_interactions'].values
    weights = np.sqrt(monthly_df['n_interactions'].values)
    weights_normalized = weights / weights.sum()

    # Analyse de l'hétérogénéité
    cv_volumes = np.std(monthly_df['n_interactions'])/np.mean(monthly_df['n_interactions'])
    
    # --- VISUALISATION : Comparaison des méthodes de pondération ---
    print("Comparaison des effets de pondération...")
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

    # Distribution des volumes (log scale)
    ax1.hist(monthly_df['n_interactions'], bins=20, alpha=0.7, color='steelblue', edgecolor='black')
    ax1.set_title('Distribution des volumes mensuels', fontsize=14)
    ax1.set_xlabel('Nombre d\'interactions')
    ax1.set_ylabel('Fréquence')
    ax1.set_yscale('log')
    ax1.grid(True, alpha=0.3)

    # Poids calculés dans le temps
    ax2.plot(monthly_df['date'], weights_normalized, 'ro-', linewidth=2, markersize=4, label='Poids normalisés')
    ax2.set_title('Évolution des poids dans le temps', fontsize=14)
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Poids normalisé')
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    # Ratings avec taille proportionnelle au poids
    sizes = weights_normalized * 1000
    scatter = ax3.scatter(monthly_df['date'], monthly_df['mean_rating'], 
                         s=sizes, c=monthly_df['n_interactions'], 
                         cmap='viridis', alpha=0.7, edgecolors='black', linewidth=0.5)
    ax3.set_title('Ratings pondérés par volume', fontsize=14)
    ax3.set_xlabel('Date')
    ax3.set_ylabel('Rating moyen')
    ax3.grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=ax3, label='Volume interactions')

    # Comparaison variance pondérée vs non-pondérée
    var_unweighted = np.var(monthly_df['mean_rating'])
    var_weighted = np.average((monthly_df['mean_rating'] - np.average(monthly_df['mean_rating'], weights=weights))**2, weights=weights)

    bars = ax4.bar(['Non pondérée', 'Pondérée'], [var_unweighted, var_weighted], 
                   color=['lightcoral', 'lightgreen'], alpha=0.8, edgecolor='black')
    ax4.set_title('Variance des ratings', fontsize=14)
    ax4.set_ylabel('Variance')
    ax4.grid(True, alpha=0.3, axis='y')
    for bar, val in zip(bars, [var_unweighted, var_weighted]):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
                 f'{val:.4f}', ha='center', va='bottom')

    plt.suptitle('Impact de la pondération par volume sur l\'analyse', fontsize=16)
    plt.tight_layout()
    plt.show()

    # --- TESTS STATISTIQUES ---
    print("=" * 60)
    print("COMPARAISON TESTS PONDÉRÉS vs NON-PONDÉRÉS")
    print("=" * 60)
    
    # Tests non-pondérés
    tau, p_value_kendall = kendalltau(time_index, ratings)
    slope, intercept, r_value, p_value_reg, std_err = linregress(time_index, ratings)
    corr_spearman, p_corr_spearman = spearmanr(volumes, ratings)

    # Données pour tests pondérés
    x = time_index
    y = ratings
    w = weights

    print(f"COMPARAISON CORRÉLATIONS TEMPORELLES:")
    print(f"Non-pondérée (Kendall): τ = {tau:.4f}, p = {p_value_kendall:.4f}")
    spearman_weighted = weighted_spearman(x, y, w)
    print(f"Pondérée (Spearman): ρ = {spearman_weighted:.4f}")

    print(f"\nCOMPARAISON RÉGRESSIONS LINÉAIRES:")
    print(f"Non-pondérée: pente = {slope:.6f}, R² = {r_value**2:.4f}")

    # Régression pondérée (WLS)
    X_const = sm.add_constant(x)
    wls_model = sm.WLS(y, X_const, weights=w)
    wls_result = wls_model.fit()
    y_pred_weighted = wls_result.predict(X_const)
    y_mean_weighted = np.average(y, weights=w)
    r2_weighted = 1 - np.average((y - y_pred_weighted)**2, weights=w) / np.average((y - y_mean_weighted)**2, weights=w)

    print(f"Pondérée (WLS): pente = {wls_result.params[1]:.6f}, R² = {r2_weighted:.4f}")
    print(f"P-value pondérée: {wls_result.pvalues[1]:.6f}")

    bias_slope = abs(wls_result.params[1] - slope) / abs(slope) * 100
    bias_corr = abs(spearman_weighted - tau) / abs(tau) * 100 if tau != 0 else 0
    print(f"\nBIAIS DE PONDÉRATION: Pente {bias_slope:.1f}%, Corrélation {bias_corr:.1f}%")
    print("=" * 60)

    # <INTERPRÉTATION>
    # L'analyse méthodologique révèle une **hétérogénéité extrême des volumes d'interactions** mensuels (Coefficient de variation = **1.11**, Ratio max/min = **30.6:1**), ce qui rend les tests statistiques standards **non fiables**.
    # Les tests non-pondérés s'avèrent **fortement biaisés** (biais de pente de **+35.4%**), car ils donnent une importance disproportionnée aux périodes de **très forte activité** (comme 2008-2009), écrasant l'influence des autres périodes.
    # L'utilisation de **méthodes pondérées** (comme la régression WLS et le Spearman pondéré) est donc **indispensable** pour corriger ce biais et obtenir une **interprétation juste et robuste** des tendances réelles du comportement utilisateur.
    # </INTERPRÉTATION>


def analyse_trendline_2():
    """
    Tendance temporelle des ratings (Méthodes pondérées)
    """
    print("Chargement des statistiques mensuelles...")
    monthly_stats, _ = load_ratings_for_longterm_analysis(min_interactions=100, return_metadata=True)
    
    # Préparation du DataFrame
    monthly_df = monthly_stats.copy()
    monthly_df['date'] = pd.to_datetime(monthly_df['date'])
    monthly_df = monthly_df.sort_values('date')
    monthly_df = monthly_df.dropna(subset=['mean_rating'])
    
    # Variables pour tests
    time_index = range(len(monthly_df))
    ratings = monthly_df['mean_rating'].values
    volumes = monthly_df['n_interactions'].values
    weights = np.sqrt(volumes)
    weights_normalized = weights / weights.sum()

    # --- CALCUL TENDANCE PONDÉRÉE ---
    X_trend = np.arange(len(monthly_df))
    X_const_trend = sm.add_constant(X_trend)
    wls_trend = sm.WLS(ratings, X_const_trend, weights=weights)
    wls_trend_result = wls_trend.fit()
    trend_line_weighted = wls_trend_result.predict(X_const_trend)
    
    # R² pondéré
    y_mean_weighted = np.average(ratings, weights=weights)
    r2_weighted = 1 - np.average((ratings - trend_line_weighted)**2, weights=weights) / np.average((ratings - y_mean_weighted)**2, weights=weights)

    # --- VISUALISATION : Tendance temporelle pondérée ---
    print("Création des visualisations temporelles pondérées...")
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

    # 1. Tendance des ratings
    ax1.plot(monthly_df['date'], ratings, 'bo-', linewidth=2, markersize=4, label='Rating moyen')
    ax1.plot(monthly_df['date'], trend_line_weighted, 'r--', linewidth=2, 
             label=f'Tendance pondérée ({wls_trend_result.params[1]:.4f}/mois)')
    ax1.set_title("Évolution des ratings - Tendance pondérée", fontsize=14)
    ax1.set_ylabel("Rating moyen")
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    # 2. Volume d'interactions
    ax2.scatter(monthly_df['date'], volumes, 
               s=weights_normalized*500, alpha=0.7, color='green', edgecolors='black')
    ax2.set_title("Volume d'interactions", fontsize=14)
    ax2.set_ylabel("Nombre d'interactions")
    ax2.grid(True, alpha=0.3)

    # 3. Stabilité (écart-type)
    weighted_std = np.sqrt(np.average((ratings - np.average(ratings, weights=weights))**2, weights=weights))
    ax3.plot(monthly_df['date'], monthly_df['std_rating'], 'o-', color='orange', linewidth=2, markersize=4, label='Écart-type brut')
    ax3.axhline(y=weighted_std, color='red', linestyle='--', linewidth=2, label=f'Écart-type pondéré ({weighted_std:.3f})')
    ax3.set_title("Stabilité des ratings", fontsize=14)
    ax3.set_ylabel("Écart-type des ratings")
    ax3.set_xlabel("Date")
    ax3.grid(True, alpha=0.3)
    ax3.legend()

    # 4. Relation volume vs qualité
    scatter = ax4.scatter(volumes, ratings, 
                         s=weights_normalized*300, c=weights_normalized, cmap='viridis',
                         alpha=0.7, edgecolors='black')
    ax4.set_title("Corrélation volume-qualité", fontsize=14)
    ax4.set_xlabel("Nombre d'interactions")
    ax4.set_ylabel("Rating moyen")
    ax4.grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=ax4, label='Poids normalisé')
    
    # Ligne de corrélation sur le scatter
    X_vol_const = sm.add_constant(volumes)
    wls_vol = sm.WLS(ratings, X_vol_const, weights=weights)
    wls_vol_result = wls_vol.fit()
    vol_pred = wls_vol_result.predict(X_vol_const)
    ax4.plot(volumes, vol_pred, "r--", alpha=0.8, linewidth=2, label='Régression pondérée')
    ax4.legend()

    plt.suptitle(f"Analyse Temporelle - Pente: {wls_trend_result.params[1]:+.4f}/mois", fontsize=16)
    plt.tight_layout()
    plt.show()

    # --- TESTS STATISTIQUES ---
    print("=" * 60)
    print("TESTS STATISTIQUES - TENDANCE TEMPORELLE")
    print("=" * 60)
    print(f"\nRégression temporelle pondérée (WLS):")
    print(f"Pente pondérée: {wls_trend_result.params[1]:.6f} points/mois")
    print(f"R² pondéré: {r2_weighted:.4f}")
    print(f"P-value pondérée: {wls_trend_result.pvalues[1]:.6f}")
    print(f"Évolution annuelle: {wls_trend_result.params[1] * 12:.4f} points/an")

    vol_qual_weighted = weighted_spearman(volumes, ratings, weights)
    print(f"\nCorrélation Volume-Rating (pondérée):")
    print(f"ρ de Spearman pondéré: {vol_qual_weighted:.3f}")
    print("=" * 60)

    # <INTERPRÉTATION>
    # L'analyse temporelle pondérée révèle une **stabilité remarquable des notes moyennes** sur le long terme, contredisant l'intuition d'une éventuelle dégradation ou amélioration.
    # La tendance observée est **statistiquement non significative** (pente annuelle = **-0.0005 points/an**, p-value = **0.29**). Le R² pondéré de **0.008** confirme que le temps n'explique quasiment **aucune variance** dans les notes.
    # On observe également une **faible corrélation négative** entre le **volume** d'interactions et la **qualité** perçue (ρ = **-0.125**), suggérant que les mois de **plus forte activité** sont associés à des **notes moyennes très légèrement plus basses**.
    # Cette stabilité globale confirme que le **comportement de notation des utilisateurs** est **extrêmement constant** depuis 2005.
    # </INTERPRÉTATION>


def analyse_trendline_3():
    """
    Évolution détaillée et corrélations (bandes de confiance)
    """
    print("Chargement des statistiques mensuelles...")
    monthly_stats, _ = load_ratings_for_longterm_analysis(min_interactions=100, return_metadata=True)
    
    # Préparation du DataFrame
    monthly_df = monthly_stats.copy()
    monthly_df['date'] = pd.to_datetime(monthly_df['date'])
    monthly_df = monthly_df.sort_values('date')
    monthly_df = monthly_df.dropna(subset=['mean_rating'])
    
    # Variables pour tests
    ratings = monthly_df['mean_rating'].values
    volumes = monthly_df['n_interactions'].values
    weights = np.sqrt(volumes)
    weights_normalized = weights / weights.sum()

    # --- CALCUL TENDANCE ET IC ---
    mean_rating_weighted = np.average(ratings, weights=weights)
    std_rating_weighted = np.sqrt(np.average((ratings - mean_rating_weighted)**2, weights=weights))
    
    # IC 95%
    upper_bound_weighted = mean_rating_weighted + 1.96 * std_rating_weighted / np.sqrt(np.sum(weights))
    lower_bound_weighted = mean_rating_weighted - 1.96 * std_rating_weighted / np.sqrt(np.sum(weights))

    # Tendance (WLS)
    X_trend = np.arange(len(monthly_df))
    X_const_trend = sm.add_constant(X_trend)
    wls_trend = sm.WLS(ratings, X_const_trend, weights=weights)
    wls_trend_result = wls_trend.fit()
    trend_weighted_detailed = wls_trend_result.predict(X_const_trend)

    # --- VISUALISATION : Analyse détaillée avec bandes de confiance ---
    print("Création des visualisations détaillées...")
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(16, 18))

    # 1. Évolution ratings - Vue d'ensemble
    ax1.plot(monthly_df['date'], ratings, 'o-', 
            color='#1f77b4', linewidth=2, markersize=4, label='Rating moyen mensuel')
    ax1.fill_between(monthly_df['date'], 
                    lower_bound_weighted, upper_bound_weighted,
                    alpha=0.2, color='red', label=f'IC 95% (±{1.96 * std_rating_weighted / np.sqrt(np.sum(weights)):.3f})')
    ax1.plot(monthly_df['date'], trend_weighted_detailed, '--', 
             color='red', linewidth=2, label=f'Tendance ({wls_trend_result.params[1]*12:.4f}/an)')
    ax1.axhline(y=mean_rating_weighted, color='orange', linestyle='-', linewidth=2,
               label=f'Moyenne ({mean_rating_weighted:.3f})')
    ax1.set_title('Évolution temporelle - Vue d\'ensemble', fontsize=16)
    ax1.set_ylabel('Rating moyen', fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    ax1.tick_params(axis='x', rotation=45)

    # 2. Évolution ratings - Vue zoomée
    ax2.plot(monthly_df['date'], ratings, 'o-', 
            color='#1f77b4', linewidth=2, markersize=6, label='Rating moyen mensuel')
    ax2.fill_between(monthly_df['date'], 
                    lower_bound_weighted, upper_bound_weighted,
                    alpha=0.3, color='red', label=f'IC 95% (±{1.96 * std_rating_weighted / np.sqrt(np.sum(weights)):.4f})')
    ax2.plot(monthly_df['date'], trend_weighted_detailed, '--', 
             color='red', linewidth=3, label=f'Tendance ({wls_trend_result.params[1]*12:.4f}/an)')
    ax2.axhline(y=mean_rating_weighted, color='orange', linestyle='-', linewidth=2,
               label=f'Moyenne ({mean_rating_weighted:.3f})')
    ax2.set_title('Évolution temporelle - Vue zoomée', fontsize=16)
    ax2.set_ylabel('Rating moyen', fontsize=12)
    ax2.set_ylim(4.65, 4.72)  # Zoom
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    ax2.tick_params(axis='x', rotation=45)

    # 3. Corrélation volume-qualité
    sizes_detailed = weights_normalized * 800
    colors_c = monthly_df['n_interactions']
    scatter = ax3.scatter(volumes, ratings, 
                         s=sizes_detailed, c=colors_c, cmap='viridis',
                         alpha=0.7, edgecolors='black', linewidth=1)
    
    # Ligne de régression
    X_vol_detailed = sm.add_constant(volumes)
    wls_vol_detailed = sm.WLS(ratings, X_vol_detailed, weights=weights)
    wls_vol_detailed_result = wls_vol_detailed.fit()
    vol_pred_detailed = wls_vol_detailed_result.predict(X_vol_detailed)
    vol_qual_weighted = weighted_spearman(volumes, ratings, weights)

    ax3.plot(volumes, vol_pred_detailed, "r--", linewidth=3, 
             label=f'Régression pondérée (ρ={vol_qual_weighted:.3f})')
    ax3.set_title('Corrélation Volume-Qualité', fontsize=16)
    ax3.set_xlabel('Nombre d\'interactions mensuelles', fontsize=12)
    ax3.set_ylabel('Rating moyen', fontsize=12)
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    plt.colorbar(scatter, ax=ax3, label='Volume interactions')

    plt.tight_layout()
    plt.show()

    # <INTERPRÉTATION>
    # L'analyse détaillée confirme la **très forte stabilité** des ratings, avec une **moyenne pondérée** se situant à **4.696**.
    # Les **bandes de confiance à 95%** calculées sur la moyenne pondérée sont **extrêmement resserrées** (IC 95% = **±0.0001**), ce qui démontre une **variance globale très faible** et une **grande prévisibilité** du comportement de notation.
    # Visuellement, bien que les notes mensuelles individuelles fluctuent légèrement, elles restent **constamment groupées** autour de cette moyenne stable, renforçant la conclusion d'une **absence totale de tendance significative** à long terme.
    # </INTERPRÉTATION>


# =============================================================================
# BLOC 2: ANALYSE DE LA SAISONNALITÉ
# =============================================================================

def analyse_seasonality_1():
    """
    Statistiques descriptives des données saisonnières
    """
    print("=" * 60)
    print("STATISTIQUES DESCRIPTIVES PAR SAISON")
    print("=" * 60)
    
    df_clean = load_clean_interactions()
    df_pandas = df_clean.to_pandas()

    # Calcul des statistiques par saison
    seasonal_stats = df_pandas.groupby('season').agg({
        'rating': ['mean', 'std', 'count'],
        'user_id': 'nunique',
        'recipe_id': 'nunique'
    }).round(4)

    seasonal_stats.columns = ['mean_rating', 'std_rating', 'count_ratings', 'unique_users', 'unique_recipes']
    seasonal_stats = seasonal_stats.reset_index()

    print("Statistiques par saison:")
    print(seasonal_stats)

    # Informations sur les volumes
    volumes = seasonal_stats['count_ratings'].values
    cv_volumes = np.std(volumes) / np.mean(volumes)
    ratio_max_min = volumes.max() / volumes.min()

    print(f"\nDistribution des interactions:")
    print(f"Coefficient de variation: {cv_volumes:.3f}")
    print(f"Ratio max/min: {ratio_max_min:.2f}:1")
    print(f"Volume total: {volumes.sum():,} interactions")
    print("=" * 60)

    # <INTERPRÉTATION>
    # Les statistiques descriptives confirment la **validité de l'analyse saisonnière**.
    # Le volume d'interactions est **remarquablement bien équilibré** entre les quatre saisons, chacune représentant environ **25%** du total.
    # Le **Coefficient de Variation (0.012)** et le **ratio max/min (1.03:1)** des volumes sont **extrêmement faibles**, indiquant qu'aucune saison ne pèse indûment sur l'analyse. Les comparaisons entre saisons seront donc **fiables et robustes**.
    # </INTERPRÉTATION>


def analyse_seasonality_2():
    """
    Variations saisonnières des ratings (Stats et Visualisations)
    """
    df_clean = load_clean_interactions()

    # --- PRÉPARATION ET STATS ---
    seasonal_ratings = df_clean.group_by("season").agg([
        pl.col("rating").mean().alias("mean_rating"),
        pl.col("rating").median().alias("median_rating"),
        pl.col("rating").std().alias("std_rating"),
        pl.len().alias("n_interactions"),
        pl.col("rating").quantile(0.25).alias("q25"),
        pl.col("rating").quantile(0.75).alias("q75")
    ]).to_pandas()

    # Ordre logique des saisons
    season_order = ["Spring", "Summer", "Autumn", "Winter"]
    seasonal_ratings = seasonal_ratings.set_index('season').loc[season_order].reset_index()

    print("Statistiques par saisons:")
    print(seasonal_ratings)

    # Tests statistiques
    season_groups = [df_clean.filter(pl.col("season") == season)["rating"].to_pandas().tolist() 
                    for season in season_order]
    f_stat, p_anova = f_oneway(*season_groups)
    h_stat, p_kruskal = kruskal(*season_groups)

    print(f"\nTest ANOVA: F={f_stat:.3f}, p={p_anova:.4f}")
    print(f"Test Kruskal-Wallis: H={h_stat:.3f}, p={p_kruskal:.4f}")

    # --- VISUALISATION : Dashboard Saisonnier ---
    fig = plt.figure(figsize=(18, 8))
    gs = GridSpec(2, 3, figure=fig, hspace=0.35, wspace=0.3)

    # 1. Radar chart
    ax1 = fig.add_subplot(gs[0, 0], projection='polar')
    theta = np.linspace(0, 2*np.pi, len(seasonal_ratings), endpoint=False)
    theta = np.concatenate((theta, [theta[0]]))
    values = np.concatenate((seasonal_ratings["mean_rating"].values, [seasonal_ratings["mean_rating"].values[0]]))

    ax1.plot(theta, values, 'o-', linewidth=3, color='crimson', markersize=8)
    ax1.fill(theta, values, alpha=0.25, color='crimson')
    ax1.set_xticks(theta[:-1])
    ax1.set_xticklabels(seasonal_ratings["season"], fontsize=9)
    ax1.set_title("Variations saisonnières", fontsize=11, pad=15)
    ax1.set_ylim([4.5, 4.8])
    ax1.grid(True, alpha=0.3)

    # 2. Moyenne par saison (échelle zoomée)
    ax2 = fig.add_subplot(gs[0, 1])
    colors = ['#90EE90', '#FFD700', '#FFA500', '#87CEEB']
    bars = ax2.bar(seasonal_ratings['season'], seasonal_ratings['mean_rating'], 
                   color=colors, edgecolor='black', linewidth=1.5, alpha=0.8)
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.003, f'{height:.4f}', ha='center', va='bottom', fontsize=10)
    ax2.set_title('Rating moyen par saison', fontsize=11)
    ax2.set_ylabel('Rating moyen', fontsize=10)
    ax2.set_ylim([4.60, 4.70])
    ax2.grid(True, alpha=0.3, axis='y')

    # 3. Pourcentage de ratings parfaits (5★)
    ax3 = fig.add_subplot(gs[0, 2])
    seasonal_perfect = df_clean.group_by("season").agg([
        (pl.col("rating") == 5).sum().alias("count_5"),
        pl.len().alias("total")
    ]).with_columns(
        (pl.col("count_5") / pl.col("total") * 100).alias("pct_5_stars")
    ).to_pandas().set_index('season').loc[season_order].reset_index()

    bars = ax3.bar(seasonal_perfect['season'], seasonal_perfect['pct_5_stars'], 
                   color=colors, edgecolor='darkgreen', linewidth=1.5, alpha=0.8)
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 0.15, f'{height:.2f}%', ha='center', va='bottom', fontsize=10)
    ax3.set_title('% Ratings parfaits (5★)', fontsize=11)
    ax3.set_ylabel('% de ratings = 5', fontsize=10)
    ax3.set_ylim([74, 78])
    ax3.grid(True, alpha=0.3, axis='y')

    # 4. Pourcentage de ratings négatifs (1-2★)
    ax4 = fig.add_subplot(gs[1, 0])
    seasonal_negative = df_clean.group_by("season").agg([
        (pl.col("rating") <= 2).sum().alias("count_negative"),
        pl.len().alias("total")
    ]).with_columns(
        (pl.col("count_negative") / pl.col("total") * 100).alias("pct_negative")
    ).to_pandas().set_index('season').loc[season_order].reset_index()

    bars = ax4.bar(seasonal_negative['season'], seasonal_negative['pct_negative'], 
                   color=colors, edgecolor='darkred', linewidth=1.5, alpha=0.8)
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 0.05, f'{height:.2f}%', ha='center', va='bottom', fontsize=10)
    ax4.set_title('% Ratings négatifs (1-2★)', fontsize=11)
    ax4.set_ylabel('% de ratings ≤ 2', fontsize=10)
    ax4.set_ylim([0, 4])
    ax4.grid(True, alpha=0.3, axis='y')

    # 5. Écart-type (dispersion)
    ax5 = fig.add_subplot(gs[1, 1])
    bars = ax5.bar(seasonal_ratings['season'], seasonal_ratings['std_rating'], 
                   color=colors, edgecolor='purple', linewidth=1.5, alpha=0.8)
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width()/2., height + 0.005, f'{height:.3f}', ha='center', va='bottom', fontsize=10)
    ax5.set_title('Écart-type des ratings', fontsize=11)
    ax5.set_ylabel('Écart-type', fontsize=10)
    ax5.set_ylim([0.0, 0.70])
    ax5.grid(True, alpha=0.3, axis='y')

    # 6. Volume d'interactions
    ax6 = fig.add_subplot(gs[1, 2])
    bars = ax6.bar(seasonal_ratings['season'], seasonal_ratings['n_interactions']/1000, 
                   color=colors, edgecolor='navy', linewidth=1.5, alpha=0.8)
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax6.text(bar.get_x() + bar.get_width()/2., height + 3, f'{int(height)}K', ha='center', va='bottom', fontsize=10)
    ax6.set_title('Volume d\'interactions', fontsize=11)
    ax6.set_ylabel('Nombre (milliers)', fontsize=10)
    ax6.grid(True, alpha=0.3, axis='y')

    plt.suptitle("Analyse des variations saisonnières des ratings", fontsize=16, y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()

    # <INTERPRÉTATION>
    # Les tests statistiques (ANOVA et Kruskal-Wallis) révèlent des **différences statistiquement significatives** entre les saisons (p < 0.0001), **confirmant l'existence d'une variation saisonnière**.
    # Cependant, l'**ampleur de cette différence est infime** : l'écart entre la meilleure saison (Été, **4.676**) et la moins bonne (Hiver, **4.648**) n'est que de **0.028 points** sur une échelle de 5.
    # L'analyse visuelle confirme la **stabilité globale**, mais révèle un **schéma saisonnier cohérent** :
    # * **Tendance Générale** : L'**été** est la saison la **plus positive** (Moyenne: **4.676**, % 5★: **76.91%**, % Négatifs: **2.55%**). L'**hiver** est la saison la **moins positive** (Moyenne: **4.648**, % 5★: **75.83%**, % Négatifs: **2.83%**).
    # * **Comportement de vote** : L'hiver est aussi la plus **polarisée**, avec la **dispersion la plus élevée** (σ = 0.748).
    # * **Conclusion** : Malgré une **significativité statistique irréfutable**, l'**impact pratique de cette saisonnalité est nul**.
    # </INTERPRÉTATION>


# =============================================================================
# BLOC 3: ANALYSE DE L'EFFET WEEK-END
# =============================================================================

def analyse_weekend_effect_1():
    """
    Vérification et répartition des données (Weekend vs Semaine)
    """
    print("=" * 70)
    print("Vérification des données : weekend vs semaine")
    print("=" * 70)
    
    df_clean = load_clean_interactions()

    # Répartition weekend/semaine
    weekend_split = df_clean.group_by("is_weekend").agg([
        pl.len().alias("count"),
        (pl.len() / df_clean.shape[0] * 100).alias("percentage"),
        pl.col("rating").mean().alias("mean_rating"),
        pl.col("rating").std().alias("std_rating")
    ]).sort("is_weekend").to_pandas()
    weekend_split['category'] = ['Semaine', 'Weekend']
    
    print("Répartition Semaine vs Weekend :")
    print(weekend_split)

    # Répartition par jour
    weekday_dist = df_clean.group_by("weekday").agg([
        pl.len().alias("count"),
        pl.col("rating").mean().alias("mean_rating")
    ]).sort("weekday").to_pandas()
    
    weekday_names = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    day_mapping = {val: weekday_names[i] for i, val in enumerate(sorted(weekday_dist['weekday'].unique()))}
    weekday_dist['jour'] = weekday_dist['weekday'].map(day_mapping)

    print("\nRépartition par jour :")
    print(weekday_dist[['jour', 'count', 'mean_rating']])
    print("=" * 70)
    
    # <INTERPRÉTATION>
    # L'analyse de la répartition confirme la **validité des données** : l'activité est **conforme au calendrier**, avec **71.0%** des interactions en semaine (5 jours) et **29.0%** le week-end (2 jours).
    # Un premier aperçu montre une **stabilité remarquable** des notes moyennes, avec un écart quasi nul entre la semaine (**4.6599**) et le week-end (**4.6687**).
    # </INTERPRÉTATION>

def analyse_weekend_effect_2():
    """
    Comparaison statistique et visuelle : Weekend vs Semaine
    """
    print("=" * 70)
    print("Analyse statistique et visuelle : weekend vs semaine")
    print("=" * 70)
    
    df_clean = load_clean_interactions()

    # --- PRÉPARATION ET STATS ---
    weekend_ratings = df_clean.filter(pl.col("is_weekend") == 1)["rating"].to_numpy()
    weekday_ratings = df_clean.filter(pl.col("is_weekend") == 0)["rating"].to_numpy()

    statistic, p_value = mannwhitneyu(weekend_ratings, weekday_ratings, alternative='two-sided')
    print(f"Test Mann-Whitney U : stat={statistic:.0f}, p={p_value:.6f}")

    mean_diff = np.mean(weekend_ratings) - np.mean(weekday_ratings)
    pooled_std = np.sqrt((np.std(weekend_ratings, ddof=1)**2 + np.std(weekday_ratings, ddof=1)**2) / 2)
    cohens_d = mean_diff / pooled_std
    print(f"Différence de moyennes: {mean_diff:.4f}, Cohen's d: {cohens_d:.4f}")
    
    # --- VISUALISATION : Dashboard Binaire ---
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Analyse Comparative: Weekend vs Semaine', fontsize=16, fontweight='bold')

    weekend_data = pd.Series(weekend_ratings)
    weekday_data = pd.Series(weekday_ratings)
    categories = ["Semaine", "Weekend"]
    colors = ["#87CEEB", "#FFD700"]

    # 1. COMPARAISON DES MOYENNES
    ax1 = axes[0, 0]
    weekend_mean = weekend_data.mean()
    weekday_mean = weekday_data.mean()
    means = [weekday_mean, weekend_mean]
    bars = ax1.bar(categories, means, color=colors, edgecolor='black', linewidth=1.5, alpha=0.8)
    for i, (bar, mean) in enumerate(zip(bars, means)):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.003, f'{mean:.4f}', ha='center', va='bottom', fontsize=10)
    ax1.set_title(f'Rating Moyen\n(Δ = {mean_diff:+.4f} points)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Rating moyen', fontsize=10)
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.set_ylim([4.60, 4.70])

    # 2. DISTRIBUTION (VIOLIN PLOT)
    ax2 = axes[0, 1]
    violin_parts = ax2.violinplot([weekday_data, weekend_data], positions=[0, 1], showmeans=True, showmedians=True, widths=0.7)
    for i, pc in enumerate(violin_parts['bodies']):
        pc.set_facecolor(colors[i])
        pc.set_alpha(0.7)
        pc.set_edgecolor('black')
    ax2.set_xticks([0, 1])
    ax2.set_xticklabels(categories, fontsize=10)
    ax2.set_title('Distribution des Ratings', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Rating', fontsize=10)
    ax2.grid(True, alpha=0.3, axis='y')

    # 3. POURCENTAGE RATINGS PARFAITS (5★)
    ax3 = axes[1, 0]
    pct_5_weekend = (weekend_data == 5).sum() / len(weekend_data) * 100
    pct_5_weekday = (weekday_data == 5).sum() / len(weekday_data) * 100
    pct_5_values = [pct_5_weekday, pct_5_weekend]
    bars = ax3.bar(categories, pct_5_values, color=colors, edgecolor='darkgreen', linewidth=1.5, alpha=0.8)
    for i, (bar, pct) in enumerate(zip(bars, pct_5_values)):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 0.15, f'{pct:.2f}%', ha='center', va='bottom', fontsize=10)
    ax3.set_title(f'% Ratings Parfaits (5★)\n(Δ = {pct_5_weekend-pct_5_weekday:+.2f}%)', fontsize=11, fontweight='bold')
    ax3.set_ylabel('% de ratings = 5', fontsize=10)
    ax3.grid(True, alpha=0.3, axis='y')
    ax3.set_ylim([74, 78])

    # 4. VOLATILITÉ (ÉCART-TYPE)
    ax4 = axes[1, 1]
    std_weekend = weekend_data.std()
    std_weekday = weekday_data.std()
    std_values = [std_weekday, std_weekend]
    bars = ax4.bar(categories, std_values, color=colors, edgecolor='purple', linewidth=1.5, alpha=0.8)
    for i, (bar, std) in enumerate(zip(bars, std_values)):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 0.005, f'{std:.3f}', ha='center', va='bottom', fontsize=10)
    ax4.set_title(f'Volatilité (σ)\n(Δ = {std_weekend-std_weekday:+.3f})', fontsize=11, fontweight='bold')
    ax4.set_ylabel('Écart-type', fontsize=10)
    ax4.grid(True, alpha=0.3, axis='y')
    ax4.set_ylim([0.0, 0.70])

    plt.tight_layout()
    plt.show()

    # <INTERPRÉTATION>
    # Le test Mann-Whitney U confirme une **différence statistiquement significative** (p < 0.0001), un résultat attendu étant donné le **très grand volume de données**.
    # Cependant, la **taille de l'effet (Cohen's d = 0.0123)** est **extrêmement faible**, indiquant une **absence totale d'impact pratique**. L'écart de moyenne de **+0.0088 points** est **négligeable**.
    # L'analyse visuelle confirme :
    # * **Stabilité des Moyennes** : Les notes moyennes (**Δ = +0.0088**) et la proportion de 5★ (**Δ = +0.31%**) sont **quasi identiques**.
    # * **Volatilité** : Les notes du week-end (σ = **0.704**) sont **très légèrement moins dispersées** que celles de la semaine (σ = **0.726**), suggérant un **consensus marginalement plus fort**.
    # * **Conclusion** : L'effet week-end sur la note moyenne est **inexistant** d'un point de vue comportemental.
    # </INTERPRÉTATION>


def analyse_weekend_effect_3():
    """
    Analyse détaillée par jour de la semaine (Stats et Visualisations)
    """
    print("=" * 70)
    print("Analyse détaillée par jour de la semaine")
    print("=" * 70)
    
    df_clean = load_clean_interactions()
    pdf_clean = df_clean.to_pandas()

    # --- PRÉPARATION ET STATS ---
    unique_weekdays = sorted(pdf_clean['weekday'].unique())
    weekday_names = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    day_mapping = {val: weekday_names[i] for i, val in enumerate(unique_weekdays) if i < len(weekday_names)}
    pdf_clean['jour'] = pdf_clean['weekday'].map(day_mapping)
    day_order = weekday_names

    ratings_per_day = pdf_clean.groupby(['weekday', 'jour'], as_index=False).agg({
        'rating': ['count', 'mean', 'std'],
        'is_weekend': 'first'
    })
    ratings_per_day.columns = ['weekday', 'jour', 'n_ratings', 'mean_rating', 'std_rating', 'is_weekend']
    ratings_per_day = ratings_per_day.set_index('jour').loc[day_order].reset_index()

    # Tests statistiques (ANOVA)
    groups = [pdf_clean[pdf_clean['jour'] == day]['rating'].tolist() for day in day_order]
    f_stat, p_value_anova = stats.f_oneway(*groups)
    print(f"\nTest ANOVA (7 jours): F={f_stat:.3f}, p={p_value_anova:.4f}")

    best_day = ratings_per_day.loc[ratings_per_day['mean_rating'].idxmax()]
    worst_day = ratings_per_day.loc[ratings_per_day['mean_rating'].idxmin()]
    print(f"Jour le plus généreux: {best_day['jour']} ({best_day['mean_rating']:.4f})")
    print(f"Jour le plus sévère: {worst_day['jour']} ({worst_day['mean_rating']:.4f})")
    
    # --- VISUALISATION : Dashboard 7 Jours ---
    weekday_patterns = ratings_per_day.rename(columns={'jour': 'day_name', 'n_ratings': 'n_interactions'})
    fig = plt.figure(figsize=(18, 8))
    gs = GridSpec(2, 3, figure=fig, hspace=0.35, wspace=0.3)
    day_colors = ['#87CEEB', '#87CEEB', '#87CEEB', '#87CEEB', '#87CEEB', '#FFD700', '#FFD700']

    # Calcul % 5★ et % Négatifs
    pct_5_by_day = []
    pct_neg_by_day = []
    for day in range(7): # Assumant 0=Lundi..6=Dimanche ou 0..6 mapping
        day_data = df_clean.filter(pl.col("weekday") == day)["rating"].to_pandas()
        pct_5_by_day.append((day_data == 5).sum() / len(day_data) * 100)
        pct_neg_by_day.append((day_data <= 2).sum() / len(day_data) * 100)

    # 1. RATING MOYEN PAR JOUR (échelle zoomée)
    ax1 = fig.add_subplot(gs[0, 0])
    bars = ax1.bar(weekday_patterns["day_name"], weekday_patterns["mean_rating"], color=day_colors, edgecolor='black', alpha=0.8)
    for bar, val in zip(bars, weekday_patterns["mean_rating"]):
        ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.003, f'{val:.4f}', ha='center', va='bottom', fontsize=9)
    ax1.set_title("Rating Moyen par Jour (zoomé)", fontsize=11, fontweight='bold')
    ax1.set_ylim([4.60, 4.70])
    ax1.tick_params(axis='x', rotation=45, labelsize=9)

    # 2. % RATINGS PARFAITS (5★)
    ax2 = fig.add_subplot(gs[0, 1])
    bars = ax2.bar(weekday_patterns["day_name"], pct_5_by_day, color=day_colors, edgecolor='darkgreen', alpha=0.8)
    for bar, val in zip(bars, pct_5_by_day):
        ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.15, f'{val:.2f}%', ha='center', va='bottom', fontsize=9)
    ax2.set_title("% Ratings Parfaits (5★)", fontsize=11, fontweight='bold')
    ax2.set_ylim([74, 78])
    ax2.tick_params(axis='x', rotation=45, labelsize=9)

    # 3. % RATINGS NÉGATIFS (1-2★)
    ax3 = fig.add_subplot(gs[0, 2])
    bars = ax3.bar(weekday_patterns["day_name"], pct_neg_by_day, color=day_colors, edgecolor='darkred', alpha=0.8)
    for bar, val in zip(bars, pct_neg_by_day):
        ax3.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.05, f'{val:.2f}%', ha='center', va='bottom', fontsize=9)
    ax3.set_title("% Ratings Négatifs (1-2★)", fontsize=11, fontweight='bold')
    ax3.set_ylim([0, 4])
    ax3.tick_params(axis='x', rotation=45, labelsize=9)

    # 4. VOLATILITÉ PAR JOUR
    ax4 = fig.add_subplot(gs[1, 0])
    bars = ax4.bar(weekday_patterns["day_name"], weekday_patterns["std_rating"], color=day_colors, edgecolor='purple', alpha=0.8)
    for bar, val in zip(bars, weekday_patterns["std_rating"]):
        ax4.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.005, f'{val:.3f}', ha='center', va='bottom', fontsize=9)
    ax4.set_title("Volatilité (σ)", fontsize=11, fontweight='bold')
    ax4.set_ylim([0.65, 0.80])
    ax4.tick_params(axis='x', rotation=45, labelsize=9)

    # 5. VOLUME D'ACTIVITÉ
    ax5 = fig.add_subplot(gs[1, 1])
    bars = ax5.bar(weekday_patterns["day_name"], weekday_patterns["n_interactions"]/1000, color=day_colors, edgecolor='navy', alpha=0.8)
    for bar, val in zip(bars, weekday_patterns["n_interactions"]/1000):
        ax5.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 3, f'{int(val)}K', ha='center', va='bottom', fontsize=9)
    ax5.set_title("Volume d'Activité", fontsize=11, fontweight='bold')
    ax5.tick_params(axis='x', rotation=45, labelsize=9)

    # 6. RADAR CHART
    ax6 = fig.add_subplot(gs[1, 2], projection='polar')
    theta = np.linspace(0, 2*np.pi, len(weekday_patterns), endpoint=False)
    theta = np.concatenate((theta, [theta[0]]))
    values = np.concatenate((weekday_patterns["mean_rating"].values, [weekday_patterns["mean_rating"].values[0]]))
    ax6.plot(theta, values, 'o-', linewidth=3, color='crimson', markersize=8)
    ax6.fill(theta, values, alpha=0.25, color='crimson')
    ax6.set_xticks(theta[:-1])
    ax6.set_xticklabels([name[:3] for name in weekday_patterns["day_name"]], fontsize=9)
    ax6.set_title("Pattern Hebdomadaire (Radar)", fontsize=11, fontweight='bold', pad=15)
    ax6.set_ylim([4.5, 4.8])

    plt.suptitle(f"Analyse par Jour de la Semaine (ANOVA p={p_value_anova:.4f})", fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()

    # <INTERPRÉTATION>
    # L'analyse par jour (ANOVA) montre aussi des **différences statistiquement significatives** (p < 0.0001), mais l'**amplitude reste négligeable** (écart max de **0.0176 points**).
    # L'analyse détaillée révèle des **patterns comportementaux distincts** :
    # * **Volume d'Activité** : L'activité de notation est **maximale le week-end**, en particulier le **samedi** et le **dimanche**.
    # * **Le Pattern du Dimanche** : Le **dimanche** est le jour le plus positif : **note moyenne la plus élevée** (**4.6710**), **plus haut taux de 5★** (**76.73%**) et **plus faible taux de notes négatives** (**2.52%**).
    # * **Le Pattern du Jeudi** : Le **jeudi** est le plus "sévère" : **note moyenne la plus basse** (**4.6534**) et **taux de notes négatives le plus élevé** (**2.86%**).
    # * **Consensus du Week-end** : La **volatilité (écart-type)** est **visiblement plus faible le week-end** (Samedi: 0.700, Dimanche: 0.709), suggérant un **consensus plus marqué**.
    # </INTERPRÉTATION>


# =============================================================================
# FOOTER: EXÉCUTION PRINCIPALE
# =============================================================================

def main():
    """
    Fonction principale pour exécuter les analyses des ratings.
    """
    
    print("--- DÉBUT DE L'ANALYSE DES TENDANCES (TRENDLINE) ---")
    analyse_trendline_1()
    analyse_trendline_2()
    analyse_trendline_3()
    print("--- FIN DE L'ANALYSE DES TENDANCES ---")

    print("\n--- DÉBUT DE L'ANALYSE DE LA SAISONNALITÉ ---")
    analyse_seasonality_1()
    analyse_seasonality_2()
    print("--- FIN DE L'ANALYSE DE LA SAISONNALITÉ ---")

    print("\n--- DÉBUT DE L'ANALYSE DE L'EFFET WEEK-END ---")
    analyse_weekend_effect_1()
    analyse_weekend_effect_2()
    analyse_weekend_effect_3()
    print("--- FIN DE L'ANALYSE DE L'EFFET WEEK-END ---")

    print("\n✅ Analyse complète des ratings terminée avec succès !")

if __name__ == "__main__":
    main()