import sys
import warnings
import importlib
from collections import Counter
from typing import Dict, List, Tuple, Optional, Union
from configparser import ConfigParser

# Ajout du chemin du module personnalisé
sys.path.append('../../')

# Import du module interne
from _data_utils import *

# Bibliothèques data science
import pandas as pd
import polars as pl
import numpy as np

# Visualisation
import matplotlib.pyplot as plt
import seaborn as sns

# Statistiques
from scipy import stats
from scipy.stats import (
    spearmanr, kendalltau, kruskal,
    chi2_contingency, chisquare, kstest
)

# Machine Learning
from sklearn.linear_model import LinearRegression, TheilSenRegressor

# Modèles statistiques
import statsmodels.api as sm
from statsmodels.stats.anova import anova_lm
from statsmodels.formula.api import ols

# Configuration globale
warnings.filterwarnings('ignore')

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 6)
plt.rcParams['font.size'] = 10


def analyse_trendline_1():
    df = load_recipes_clean()
    recipes_per_year = (df.group_by("year").agg(pl.len().alias("n_recipes")).sort("year").to_pandas())

    # Préparation des données pour le Q-Q plot
    data = recipes_per_year['n_recipes'].values
    mean_data = np.mean(data)
    std_data = np.std(data, ddof=1)

    # --- VISUALISATION : Fréquence + Q-Q Plot ---
    fig, (ax1, ax0) = plt.subplots(1, 2, figsize=(15, 6))

    # (1) Graphique de fréquence (barres)
    bars = ax1.bar(recipes_per_year['year'].astype(int), recipes_per_year['n_recipes'], 
                color='steelblue', alpha=0.8)
    ax1.set_title('Nombre de recettes par année', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Année')
    ax1.set_ylabel('Nombre de recettes')
    ax1.set_xticks(recipes_per_year['year'].astype(int))
    ax1.set_xticklabels(recipes_per_year['year'].astype(int), rotation=45)
    ax1.grid(axis='y', alpha=0.3)

    # Annotations des valeurs
    for bar, val in zip(bars, recipes_per_year['n_recipes']):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                    f'{val:,}', ha='center', va='bottom', fontsize=9)

    # (2) Q-Q Plot (test de normalité)
    stats.probplot(data, dist="norm", plot=ax0)
    ax0.set_title('Q-Q Plot (Test de normalité)', fontsize=14, fontweight='bold')
    ax0.set_xlabel('Quantiles théoriques (loi normale)')
    ax0.set_ylabel('Quantiles observés')
    ax0.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

    # <INTERPRÉTATION>
    # > Nous observons une **forte augmentation du nombre de recettes postées jusqu’en 2007**, année du **pic d’activité**, suivie d’une **chute marquée** les années suivantes. 
    # Les **tests de normalité** et les **Q-Q plots** montrent que la distribution du **nombre de recettes par an** **n’est pas parfaitement normale**, avec des **écarts visibles** par rapport à la **loi normale théorique**. 
    # </INTERPRÉTATION>

def analyse_trendline_2():
    df = load_recipes_clean()
# 📊 Agrégation durée par année
    minutes_by_year = (
        df.group_by("year")
        .agg([
            pl.mean("minutes").alias("mean_minutes"), 
            pl.median("minutes").alias("median_minutes"),
            pl.quantile("minutes", 0.25).alias("q25"), 
            pl.quantile("minutes", 0.75).alias("q75"), 
            pl.len().alias("n_recipes")
        ])
        .sort("year").to_pandas()
    )

    # --- CALCUL DES RÉGRESSIONS WLS POUR MEAN ET MEDIAN ---
    X = minutes_by_year['year'].values
    w = minutes_by_year['n_recipes'].values

    metrics_config = {
        'mean_minutes': {
            'color': 'steelblue', 
            'label': 'Moyenne',
            'ylabel': 'minutes/an'
        },
        'median_minutes': {
            'color': 'coral',
            'label': 'Médiane',
            'ylabel': 'minutes/an'
        }
    }

    regressions = {}
    for metric_col in metrics_config.keys():
        y = minutes_by_year[metric_col].values
        X_const = sm.add_constant(X)
        wls_model = sm.WLS(y, X_const, weights=w)
        wls_result = wls_model.fit()
        y_pred = wls_result.predict(X_const)
        r2_w = 1 - np.average((y - y_pred)**2, weights=w) / np.average((y - np.average(y, weights=w))**2, weights=w)
        
        regressions[metric_col] = {
            'y_pred': y_pred,
            'slope': wls_result.params[1],
            'intercept': wls_result.params[0],
            'r2': r2_w,
            'p_value': wls_result.pvalues[1]
        }

    # --- VISUALISATION AVEC RÉGRESSIONS ---
    fig, ax1 = plt.subplots(1, 1, figsize=(12, 6))

    sizes = minutes_by_year['n_recipes'] / minutes_by_year['n_recipes'].max() * 350

    # Moyenne : courbe + bulles + régression
    ax1.plot(minutes_by_year['year'], minutes_by_year['mean_minutes'], 
            color='steelblue', linewidth=2, alpha=0.7, label='Moyenne (observée)', zorder=1)
    ax1.scatter(minutes_by_year['year'], minutes_by_year['mean_minutes'], 
                s=sizes, color='steelblue', alpha=0.6, edgecolors='black', linewidths=0.5, zorder=3)
    ax1.plot(minutes_by_year['year'], regressions['mean_minutes']['y_pred'],
            color='darkblue', linewidth=2, linestyle='--', alpha=0.8,
            label=f"Régression Moyenne (R²={regressions['mean_minutes']['r2']:.3f})", zorder=2)

    # Médiane : courbe + bulles + régression
    ax1.plot(minutes_by_year['year'], minutes_by_year['median_minutes'], 
            color='coral', linewidth=1.5, alpha=0.7, label='Médiane (observée)', zorder=1)
    ax1.scatter(minutes_by_year['year'], minutes_by_year['median_minutes'], 
                s=sizes, color='coral', alpha=0.6, edgecolors='black', linewidths=0.5, zorder=3)
    ax1.plot(minutes_by_year['year'], regressions['median_minutes']['y_pred'],
            color='darkred', linewidth=2, linestyle='--', alpha=0.8,
            label=f"Régression Médiane (R²={regressions['median_minutes']['r2']:.3f})", zorder=2)

    # IQR (intervalle interquartile)
    ax1.fill_between(minutes_by_year['year'], minutes_by_year['q25'], minutes_by_year['q75'], 
                    alpha=0.15, color='steelblue', label='IQR (Q25-Q75)', zorder=0)

    # Titres et légendes
    title_text = (f"Évolution de la durée (minutes)\n"
                f"Moyenne: {regressions['mean_minutes']['slope']:+.4f} min/an | "
                f"Médiane: {regressions['median_minutes']['slope']:+.4f} min/an")
    ax1.set_title(title_text, fontsize=12, fontweight='bold')
    ax1.set_xlabel('Année', fontsize=12)
    ax1.set_ylabel('Minutes', fontsize=12)
    ax1.legend(loc='best', fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(minutes_by_year['year'])
    ax1.set_xticklabels([int(y) for y in minutes_by_year['year']], rotation=45)

    plt.tight_layout()
    plt.show()

    # <INTERPRÉTATION>
    # **L’analyse de la durée moyenne de préparation** montre une **tendance globale à la baisse** depuis la création du site.    
    # En moyenne, le temps de préparation diminue d’environ **−0.46/min par an**, tandis que la médiane recule de **−0.26/min par an**, ce qui traduit une **légère simplification des recettes** au fil du temps.  
    # </INTERPRÉTATION>

def analyse_trendline_3():
    df = load_recipes_clean()
    # 📊 Agrégation des données de complexité par année
    complexity_by_year = (
        df.group_by("year")
        .agg([
            pl.mean("complexity_score").alias("mean_complexity"),
            pl.mean("n_steps").alias("mean_steps"),
            pl.mean("n_ingredients").alias("mean_ingredients"),
            pl.std("complexity_score").alias("std_complexity"),
            pl.count("id").alias("count_recipes")
        ])
        .sort("year").to_pandas()
    )

    # --- CALCUL DES RÉGRESSIONS WLS POUR LES 3 MÉTRIQUES ---
    X = complexity_by_year['year'].values
    w = complexity_by_year['count_recipes'].values

    metrics_config = {
        'mean_complexity': {
            'color': 'purple', 'marker': 'o', 
            'title': 'Score de complexité', 
            'ylabel': 'Complexity Score',
            'show_std': True
        },
        'mean_steps': {
            'color': 'orange', 'marker': 's',
            'title': 'Nombre d\'étapes',
            'ylabel': 'Nombre d\'étapes',
            'show_std': False
        },
        'mean_ingredients': {
            'color': 'forestgreen', 'marker': '^',
            'title': 'Nombre d\'ingrédients',
            'ylabel': 'Nombre d\'ingrédients',
            'show_std': False
        }
    }

    # Calcul des régressions
    regressions = {}
    for metric_col in metrics_config.keys():
        y = complexity_by_year[metric_col].values
        X_const = sm.add_constant(X)
        wls_model = sm.WLS(y, X_const, weights=w)
        wls_result = wls_model.fit()
        y_pred = wls_result.predict(X_const)
        r2_w = 1 - np.average((y - y_pred)**2, weights=w) / np.average((y - np.average(y, weights=w))**2, weights=w)
        
        regressions[metric_col] = {
            'y_pred': y_pred,
            'slope': wls_result.params[1],
            'r2': r2_w,
            'p_value': wls_result.pvalues[1]
        }

    # --- VISUALISATION AVEC RÉGRESSIONS ---
    sizes = (w / w.max()) * 400
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    for ax, (metric_col, config) in zip(axes, metrics_config.items()):
        reg = regressions[metric_col]
        
        # Courbe observée
        ax.plot(complexity_by_year['year'], complexity_by_year[metric_col],
                linewidth=2.5, color=config['color'], alpha=0.7,
                label='Tendance observée', zorder=1)
        
        # Bulles proportionnelles
        ax.scatter(complexity_by_year['year'], complexity_by_year[metric_col],
                s=sizes, alpha=0.6, color=config['color'],
                edgecolors='black', linewidths=0.5,
                label='Observations (taille ~ count_recipes)', zorder=3)
        
        # Ligne de régression
        ax.plot(complexity_by_year['year'], reg['y_pred'],
                color='red', linewidth=2, linestyle='--', alpha=0.8,
                label=f'Régression WLS (R²={reg["r2"]:.3f})', zorder=2)
        
        # Bande de std pour complexity_score
        if config.get('show_std'):
            ax.fill_between(complexity_by_year['year'],
                            complexity_by_year['mean_complexity'] - complexity_by_year['std_complexity'],
                            complexity_by_year['mean_complexity'] + complexity_by_year['std_complexity'],
                            alpha=0.15, color=config['color'], label='±1 std', zorder=0)

        title_text = f"{config['title']}\n Pente: {reg['slope']:+.4f}/an (p={reg['p_value']:.2e})"
        ax.set_title(title_text, fontsize=11, fontweight='bold')
        
        ax.set_xlabel('Année')
        ax.set_ylabel(config['ylabel'])
        ax.grid(True, alpha=0.3)
        ax.set_xticks(complexity_by_year['year'])
        ax.set_xticklabels([int(y) for y in complexity_by_year['year']], rotation=45)
        ax.legend(loc='best', fontsize=8)

    plt.tight_layout()
    plt.show()
    # <INTERPRÉTATION>
    # La **régression linéaire pondérée** (pente = **+0.10**, R² = **0.56**, p = **1.59×10⁻⁴**) met en évidence une **tendance significative à la hausse** du **score moyen de complexité** au fil du temps.  
    # Cette évolution indique une **augmentation progressive de la complexité des recettes**, d’environ **+0.10 point par an**, suggérant des **préparations de plus en plus élaborées** au cours des années.  
    # La tendance observée est **cohérente** avec la corrélation positive entre le **nombre d’étapes** et le **nombre d’ingrédients**, confirmant une **complexification globale** des recettes publiées.

    # </INTERPRÉTATION>

def analyse_trendline_4():
    df = load_recipes_clean()

    # 📊 Agrégation nutrition par année (Calories, Glucides, Lipides, Protéines)
    nutrition_by_year = (
        df.group_by("year")
        .agg([pl.mean("calories").alias("mean_calories"), pl.mean("carb_pct").alias("mean_carbs"), 
            pl.mean("total_fat_pct").alias("mean_fat"), pl.mean("protein_pct").alias("mean_protein"),
            pl.count("id").alias("count_recipes")])
        .sort("year").to_pandas())

    # --- CALCUL DES RÉGRESSIONS WLS POUR CHAQUE MÉTRIQUE ---
    X_year = nutrition_by_year['year'].values
    w = nutrition_by_year['count_recipes'].values

    metrics_config = {
        'mean_calories': {'color': 'tomato', 'marker': 'o', 'title': 'Calories moyennes', 'ylabel': 'Calories'},
        'mean_carbs': {'color': 'royalblue', 'marker': 's', 'title': 'Glucides (%)', 'ylabel': 'Carbs %'},
        'mean_fat': {'color': 'orange', 'marker': '^', 'title': 'Lipides (%)', 'ylabel': 'Fat %'},
        'mean_protein': {'color': 'green', 'marker': 'd', 'title': 'Protéines (%)', 'ylabel': 'Protein %'}
    }

    regressions = {}
    for metric_col in metrics_config.keys():
        y = nutrition_by_year[metric_col].values
        X_const = sm.add_constant(X_year)
        wls_model = sm.WLS(y, X_const, weights=w)
        wls_result = wls_model.fit()
        y_pred = wls_result.predict(X_const)
        r2_w = 1 - np.average((y - y_pred)**2, weights=w) / np.average((y - np.average(y, weights=w))**2, weights=w)
        
        regressions[metric_col] = {
            'y_pred': y_pred,
            'slope': wls_result.params[1],
            'intercept': wls_result.params[0],
            'r2': r2_w,
            'p_value': wls_result.pvalues[1]
        }

    # --- CALCUL DES TAILLES DE BULLES ---
    sizes = (w / w.max()) * 500  # Taille max = 500

    # --- VISUALISATION AVEC COURBES + BULLES + RÉGRESSIONS ---
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    axes_flat = [axes[0,0], axes[0,1], axes[1,0], axes[1,1]]

    for ax, (metric_col, config) in zip(axes_flat, metrics_config.items()):
        reg = regressions[metric_col]
        
        # Courbe originale (ligne continue)
        ax.plot(nutrition_by_year['year'], nutrition_by_year[metric_col], 
                linewidth=2.5, color=config['color'], alpha=0.7,
                label='Tendance observée', zorder=1)
        
        # Bulles (scatter) proportionnelles à count_recipes
        ax.scatter(nutrition_by_year['year'], nutrition_by_year[metric_col], 
                s=sizes, alpha=0.6, color=config['color'], 
                edgecolors='black', linewidths=0.5,
                label='Observations (taille ~ count_recipes)', zorder=3)
        
        # Ligne de régression
        ax.plot(nutrition_by_year['year'], reg['y_pred'], 
                color='red', linewidth=2, linestyle='--', alpha=0.8,
                label=f'Régression WLS (R²={reg["r2"]:.3f})', zorder=2)
        
        # Titre avec significativité
        title_text = f"{config['title']}\n Pente: {reg['slope']:+.4f}/an (p={reg['p_value']:.2e})"
        ax.set_title(title_text, fontsize=11, fontweight='bold')
        
        ax.set_ylabel(config['ylabel'])
        if ax in [axes[1,0], axes[1,1]]:
            ax.set_xlabel('Année')
        
        ax.grid(True, alpha=0.3)
        ax.set_xticks(nutrition_by_year['year'])
        ax.set_xticklabels([int(y) for y in nutrition_by_year['year']], rotation=45)
        ax.legend(loc='best', fontsize=8)

    plt.tight_layout()
    plt.show()
    # <INTERPRÉTATION>
    # Les **régressions linéaires pondérées** montrent une **tendance significative à la baisse** des valeurs **nutritionnelles moyennes** au fil du temps.  
    # Les **calories**, **glucides**, **lipides** et **protéines** présentent toutes des **pentes négatives**, avec des **R² pondérés entre 0.39 et 0.56**, indiquant une **bonne part de variance expliquée** et une **diminution mesurable** des apports nutritionnels moyens par recette.  
    # Cette évolution traduit une **orientation progressive vers des recettes plus légères**, moins riches en **calories** et en **macronutriments**, reflétant probablement une **adaptation aux tendances alimentaires modernes** (recherche de plats plus équilibrés et moins énergétiques).  
    # </INTERPRÉTATION>

def analyse_trendline_5():
    df = load_recipes_clean()
    # 📊 ANALYSE DES INGRÉDIENTS PAR ANNÉE

    # --- PARAMÈTRES ---
    NORMALIZE = True  # Normaliser par le nb de recettes de l'année
    MIN_TOTAL_OCC = 50  # Seuil min d'occurrences globales
    TOP_N = 10  # Top hausses/baisses à afficher
    N_VARIATIONS = 5  # Nombre d'ingrédients à tracer

    # --- 0. PRÉPARATION : NORMALISATION DES INGRÉDIENTS ---
    print("🔄 Normalisation des ingrédients en cours...")

    # Exploser la liste d'ingrédients et normaliser (lowercase + strip)
    df_ingredients = (
        df.select(['id', 'year', 'ingredients'])
        .explode('ingredients')
        .with_columns([
            pl.col('ingredients').str.to_lowercase().str.strip_chars().alias('ingredient_norm')
        ])
    )

    print(f"✅ {df_ingredients.shape[0]:,} ingrédients individuels extraits")

    # --- 1. FRÉQUENCE GLOBALE DES INGRÉDIENTS ---
    freq_global = (
        df_ingredients
        .group_by('ingredient_norm')
        .agg(pl.count('id').alias('total_count'))
        .filter(pl.col('total_count') >= MIN_TOTAL_OCC)
        .sort('total_count', descending=True)
        .to_pandas()
    )

    top_global = freq_global.head(TOP_N)

    # --- 2. FRÉQUENCE PAR ANNÉE ---
    freq_year_ing = (
        df_ingredients
        .group_by(['year', 'ingredient_norm'])
        .agg(pl.count('ingredient_norm').alias('count'))
        .to_pandas()
    )

    # Nombre de recettes par année
    year_totals = df.group_by('year').agg(pl.count('id').alias('n_recipes')).to_pandas()

    # Joindre et normaliser
    freq_year_ing = freq_year_ing.merge(year_totals, on='year', how='left')
    if NORMALIZE:
        freq_year_ing['freq'] = freq_year_ing['count'] / freq_year_ing['n_recipes']
    else:
        freq_year_ing['freq'] = freq_year_ing['count']

    # --- 3. CALCUL DES VARIATIONS ---
    min_year = int(df['year'].min())
    max_year = int(df['year'].max())

    first_year_vals = freq_year_ing[freq_year_ing['year'] == min_year][['ingredient_norm', 'freq']].rename(columns={'freq': 'first'})
    last_year_vals = freq_year_ing[freq_year_ing['year'] == max_year][['ingredient_norm', 'freq']].rename(columns={'freq': 'last'})

    variation = first_year_vals.merge(last_year_vals, on='ingredient_norm', how='outer').fillna(0)
    variation['delta'] = variation['last'] - variation['first']

    # Filtrer pour avoir suffisamment d'occurrences
    variation = variation.merge(freq_global[['ingredient_norm', 'total_count']], on='ingredient_norm', how='left')
    variation = variation[variation['total_count'] >= MIN_TOTAL_OCC]

    biggest_increase = variation.nlargest(TOP_N, 'delta')
    biggest_decrease = variation.nsmallest(TOP_N, 'delta')

    # --- 4. DIVERSITÉ (NOMBRE D'INGRÉDIENTS UNIQUES) ---
    unique_per_year = (
        df_ingredients
        .group_by('year')
        .agg(pl.n_unique('ingredient_norm').alias('n_unique'))
        .sort('year')
        .to_pandas()
    )

    # --- VISUALISATION ---
    fig = plt.figure(figsize=(18, 12))

    # (1) Top 10 ingrédients (barres horizontales)
    ax1 = plt.subplot(3, 2, 1)
    ax1.barh(range(len(top_global)), top_global['total_count'], color='steelblue', alpha=0.8)
    ax1.set_yticks(range(len(top_global)))
    ax1.set_yticklabels(top_global['ingredient_norm'])
    ax1.invert_yaxis()
    ax1.set_xlabel('Occurrences totales')
    ax1.set_title(f'Top {TOP_N} ingrédients les plus fréquents', fontweight='bold', fontsize=11)
    ax1.grid(axis='x', alpha=0.3)

    # (2) Évolution de la diversité
    ax2 = plt.subplot(3, 2, 2)
    w_div = year_totals['n_recipes'].values
    sizes_div = (w_div / w_div.max()) * 300
    ax2.plot(unique_per_year['year'], unique_per_year['n_unique'], 
            color='purple', linewidth=2, alpha=0.7, label='Diversité observée', zorder=1)
    ax2.scatter(unique_per_year['year'], unique_per_year['n_unique'],
                s=sizes_div, color='purple', alpha=0.6, 
                edgecolors='black', linewidths=0.5, zorder=3)
    ax2.set_xlabel('Année')
    ax2.set_ylabel('Nombre d\'ingrédients uniques')
    ax2.set_title('Évolution de la diversité des ingrédients', fontweight='bold', fontsize=11)
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks(unique_per_year['year'])
    ax2.set_xticklabels([int(y) for y in unique_per_year['year']], rotation=45)

    # (3) Top hausses (barres horizontales)
    ax3 = plt.subplot(3, 2, 3)
    label_delta = 'Variation (normalisée)' if NORMALIZE else 'Variation (occurrences)'
    ax3.barh(range(len(biggest_increase)), biggest_increase['delta'], color='green', alpha=0.8)
    ax3.set_yticks(range(len(biggest_increase)))
    ax3.set_yticklabels(biggest_increase['ingredient_norm'])
    ax3.invert_yaxis()
    ax3.set_xlabel(label_delta)
    ax3.set_title(f'Top {TOP_N} hausses ({min_year}→{max_year})', fontweight='bold', fontsize=11)
    ax3.grid(axis='x', alpha=0.3)

    # (4) Top baisses (barres horizontales)
    ax4 = plt.subplot(3, 2, 4)
    ax4.barh(range(len(biggest_decrease)), biggest_decrease['delta'], color='red', alpha=0.8)
    ax4.set_yticks(range(len(biggest_decrease)))
    ax4.set_yticklabels(biggest_decrease['ingredient_norm'])
    ax4.invert_yaxis()
    ax4.set_xlabel(label_delta)
    ax4.set_title(f'Top {TOP_N} baisses ({min_year}→{max_year})', fontweight='bold', fontsize=11)
    ax4.grid(axis='x', alpha=0.3)

    # (5) Évolution de quelques ingrédients en hausse
    ax_inc = plt.subplot(3, 2, 5)
    colors = plt.cm.Greens(np.linspace(0.4, 0.9, N_VARIATIONS))
    for idx, (_, row) in enumerate(biggest_increase.head(N_VARIATIONS).iterrows()):
        ing = row['ingredient_norm']
        data_ing = freq_year_ing[freq_year_ing['ingredient_norm'] == ing].sort_values('year')
        ax_inc.plot(data_ing['year'], data_ing['freq'], 
                    marker='o', linewidth=2, alpha=0.7, color=colors[idx],
                    label=ing)
    ax_inc.set_xlabel('Année')
    ax_inc.set_ylabel('Fréquence' if NORMALIZE else 'Occurrences')
    ax_inc.set_title(f'Évolution : Top {N_VARIATIONS} hausses', fontweight='bold', fontsize=11)
    ax_inc.legend(loc='best', fontsize=8)
    ax_inc.grid(True, alpha=0.3)
    ax_inc.set_xticks(unique_per_year['year'])
    ax_inc.set_xticklabels([int(y) for y in unique_per_year['year']], rotation=45)

    # (6) Évolution de quelques ingrédients en baisse
    ax_dec = plt.subplot(3, 2, 6)
    colors = plt.cm.Reds(np.linspace(0.4, 0.9, N_VARIATIONS))
    for idx, (_, row) in enumerate(biggest_decrease.head(N_VARIATIONS).iterrows()):
        ing = row['ingredient_norm']
        data_ing = freq_year_ing[freq_year_ing['ingredient_norm'] == ing].sort_values('year')
        ax_dec.plot(data_ing['year'], data_ing['freq'], 
                    marker='s', linewidth=2, alpha=0.7, color=colors[idx],
                    label=ing)
    ax_dec.set_xlabel('Année')
    ax_dec.set_ylabel('Fréquence' if NORMALIZE else 'Occurrences')
    ax_dec.set_title(f'Évolution : Top {N_VARIATIONS} baisses', fontweight='bold', fontsize=11)
    ax_dec.legend(loc='best', fontsize=8)
    ax_dec.grid(True, alpha=0.3)
    ax_dec.set_xticks(unique_per_year['year'])
    ax_dec.set_xticklabels([int(y) for y in unique_per_year['year']], rotation=45)

    plt.tight_layout()
    plt.show()
    # <INTERPRÉTATION>
    #  L'analyse révèle une **transformation profonde** de l'usage des ingrédients au fil du temps.
    # **Tendances montantes** : Des ingrédients comme *kosher salt*, *garlic cloves*, *olive oil* et *unsalted butter* connaissent une forte progression, reflétant peut-être un virage vers une cuisine plus communautaire ou méditerranéenne.
    # **Tendances descendantes** : Les ingrédients traditionnels comme *sugar*, *butter*, *eggs* et *vanilla* sont en net recul, suggérant une diminution des recettes de pâtisserie classique et une recherche de recettes moins sucrées.
    # **Chute de la diversité** : Le nombre d'ingrédients uniques chute drastiquement, passant du maximum en début de période à un minimum en fin de période. Cette baisse significative s'explique par la diminution du volume de recettes postées après 2007, entraînant une concentration sur des ingrédients plus courants et une perte d'innovation culinaire.
    # </INTERPRÉTATION>

def analyse_trendline_6():
    df = load_recipes_clean()
    # 📊 ANALYSE DES TAGS PAR ANNÉE

    # --- PARAMÈTRES ---
    NORMALIZE = True  # Normaliser par le nb de recettes de l'année
    MIN_TOTAL_OCC = 50  # Seuil min d'occurrences globales
    TOP_N = 10  # Top hausses/baisses à afficher
    N_VARIATIONS = 5  # Nombre de tags à tracer

    # --- 0. PRÉPARATION : NORMALISATION DES TAGS ---
    print("🔄 Normalisation des tags en cours...")

    # Exploser la liste de tags et normaliser (lowercase + strip)
    df_tags = (
        df.select(['id', 'year', 'tags'])
        .explode('tags')
        .with_columns([
            pl.col('tags').str.to_lowercase().str.strip_chars().alias('tag_norm')
        ])
    )

    print(f"✅ {df_tags.shape[0]:,} tags individuels extraits")

    # --- 1. FRÉQUENCE GLOBALE DES TAGS ---
    freq_global_tags = (
        df_tags
        .group_by('tag_norm')
        .agg(pl.count('id').alias('total_count'))
        .filter(pl.col('total_count') >= MIN_TOTAL_OCC)
        .sort('total_count', descending=True)
        .to_pandas()
    )

    top_global_tags = freq_global_tags.head(TOP_N)

    # --- 2. FRÉQUENCE PAR ANNÉE ---
    freq_year_tag = (
        df_tags
        .group_by(['year', 'tag_norm'])
        .agg(pl.count('tag_norm').alias('count'))
        .to_pandas()
    )

    # Nombre de recettes par année
    year_totals_tags = df.group_by('year').agg(pl.count('id').alias('n_recipes')).to_pandas()

    # Joindre et normaliser
    freq_year_tag = freq_year_tag.merge(year_totals_tags, on='year', how='left')
    if NORMALIZE:
        freq_year_tag['freq'] = freq_year_tag['count'] / freq_year_tag['n_recipes']
    else:
        freq_year_tag['freq'] = freq_year_tag['count']

    # --- 3. CALCUL DES VARIATIONS ---
    min_year_tags = int(df['year'].min())
    max_year_tags = int(df['year'].max())

    first_year_vals_tags = freq_year_tag[freq_year_tag['year'] == min_year_tags][['tag_norm', 'freq']].rename(columns={'freq': 'first'})
    last_year_vals_tags = freq_year_tag[freq_year_tag['year'] == max_year_tags][['tag_norm', 'freq']].rename(columns={'freq': 'last'})

    variation_tags = first_year_vals_tags.merge(last_year_vals_tags, on='tag_norm', how='outer').fillna(0)
    variation_tags['delta'] = variation_tags['last'] - variation_tags['first']

    # Filtrer pour avoir suffisamment d'occurrences
    variation_tags = variation_tags.merge(freq_global_tags[['tag_norm', 'total_count']], on='tag_norm', how='left')
    variation_tags = variation_tags[variation_tags['total_count'] >= MIN_TOTAL_OCC]

    biggest_increase_tags = variation_tags.nlargest(TOP_N, 'delta')
    biggest_decrease_tags = variation_tags.nsmallest(TOP_N, 'delta')

    # --- 4. DIVERSITÉ (NOMBRE DE TAGS UNIQUES) ---
    unique_per_year_tags = (
        df_tags
        .group_by('year')
        .agg(pl.n_unique('tag_norm').alias('n_unique'))
        .sort('year')
        .to_pandas()
    )

    # --- VISUALISATION ---
    fig = plt.figure(figsize=(18, 12))

    # (1) Top 10 tags (barres horizontales)
    ax1 = plt.subplot(3, 2, 1)
    ax1.barh(range(len(top_global_tags)), top_global_tags['total_count'], color='steelblue', alpha=0.8)
    ax1.set_yticks(range(len(top_global_tags)))
    ax1.set_yticklabels(top_global_tags['tag_norm'])
    ax1.invert_yaxis()
    ax1.set_xlabel('Occurrences totales')
    ax1.set_title(f'Top {TOP_N} tags les plus fréquents', fontweight='bold', fontsize=11)
    ax1.grid(axis='x', alpha=0.3)

    # (2) Évolution de la diversité
    ax2 = plt.subplot(3, 2, 2)
    w_div_tags = year_totals_tags['n_recipes'].values
    sizes_div_tags = (w_div_tags / w_div_tags.max()) * 300
    ax2.plot(unique_per_year_tags['year'], unique_per_year_tags['n_unique'], 
            color='purple', linewidth=2, alpha=0.7, label='Diversité observée', zorder=1)
    ax2.scatter(unique_per_year_tags['year'], unique_per_year_tags['n_unique'],
                s=sizes_div_tags, color='purple', alpha=0.6, 
                edgecolors='black', linewidths=0.5, zorder=3)
    ax2.set_xlabel('Année')
    ax2.set_ylabel('Nombre de tags uniques')
    ax2.set_title('Évolution de la diversité des tags', fontweight='bold', fontsize=11)
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks(unique_per_year_tags['year'])
    ax2.set_xticklabels([int(y) for y in unique_per_year_tags['year']], rotation=45)

    # (3) Top hausses (barres horizontales)
    ax3 = plt.subplot(3, 2, 3)
    label_delta_tags = 'Variation (normalisée)' if NORMALIZE else 'Variation (occurrences)'
    ax3.barh(range(len(biggest_increase_tags)), biggest_increase_tags['delta'], color='green', alpha=0.8)
    ax3.set_yticks(range(len(biggest_increase_tags)))
    ax3.set_yticklabels(biggest_increase_tags['tag_norm'])
    ax3.invert_yaxis()
    ax3.set_xlabel(label_delta_tags)
    ax3.set_title(f'Top {TOP_N} hausses ({min_year_tags}→{max_year_tags})', fontweight='bold', fontsize=11)
    ax3.grid(axis='x', alpha=0.3)

    # (4) Top baisses (barres horizontales)
    ax4 = plt.subplot(3, 2, 4)
    ax4.barh(range(len(biggest_decrease_tags)), biggest_decrease_tags['delta'], color='red', alpha=0.8)
    ax4.set_yticks(range(len(biggest_decrease_tags)))
    ax4.set_yticklabels(biggest_decrease_tags['tag_norm'])
    ax4.invert_yaxis()
    ax4.set_xlabel(label_delta_tags)
    ax4.set_title(f'Top {TOP_N} baisses ({min_year_tags}→{max_year_tags})', fontweight='bold', fontsize=11)
    ax4.grid(axis='x', alpha=0.3)

    # (5) Évolution de quelques tags en hausse
    ax_inc = plt.subplot(3, 2, 5)
    colors = plt.cm.Greens(np.linspace(0.4, 0.9, N_VARIATIONS))
    for idx, (_, row) in enumerate(biggest_increase_tags.head(N_VARIATIONS).iterrows()):
        tag = row['tag_norm']
        data_tag = freq_year_tag[freq_year_tag['tag_norm'] == tag].sort_values('year')
        ax_inc.plot(data_tag['year'], data_tag['freq'], 
                    marker='o', linewidth=2, alpha=0.7, color=colors[idx],
                    label=tag)
    ax_inc.set_xlabel('Année')
    ax_inc.set_ylabel('Fréquence' if NORMALIZE else 'Occurrences')
    ax_inc.set_title(f'Évolution : Top {N_VARIATIONS} hausses', fontweight='bold', fontsize=11)
    ax_inc.legend(loc='best', fontsize=8)
    ax_inc.grid(True, alpha=0.3)
    ax_inc.set_xticks(unique_per_year_tags['year'])
    ax_inc.set_xticklabels([int(y) for y in unique_per_year_tags['year']], rotation=45)

    # (6) Évolution de quelques tags en baisse
    ax_dec = plt.subplot(3, 2, 6)
    colors = plt.cm.Reds(np.linspace(0.4, 0.9, N_VARIATIONS))
    for idx, (_, row) in enumerate(biggest_decrease_tags.head(N_VARIATIONS).iterrows()):
        tag = row['tag_norm']
        data_tag = freq_year_tag[freq_year_tag['tag_norm'] == tag].sort_values('year')
        ax_dec.plot(data_tag['year'], data_tag['freq'], 
                    marker='s', linewidth=2, alpha=0.7, color=colors[idx],
                    label=tag)
    ax_dec.set_xlabel('Année')
    ax_dec.set_ylabel('Fréquence' if NORMALIZE else 'Occurrences')
    ax_dec.set_title(f'Évolution : Top {N_VARIATIONS} baisses', fontweight='bold', fontsize=11)
    ax_dec.legend(loc='best', fontsize=8)
    ax_dec.grid(True, alpha=0.3)
    ax_dec.set_xticks(unique_per_year_tags['year'])
    ax_dec.set_xticklabels([int(y) for y in unique_per_year_tags['year']], rotation=45)

    plt.tight_layout()
    plt.show()
    # <INTERPRÉTATION>
    # L'analyse des tags révèle une **évolution des pratiques de catégorisation** des recettes au fil du temps.
    # **Tendances montantes** : Les catégories en hausse concernent surtout les repas rapides (*60-minutes-or-less*, *for-1-or-2*), les plats principaux (*main-dish*), ainsi que des moments spécifiques comme le petit-déjeuner ou les en-cas. On observe aussi une progression des recettes à base de fruits de mer (*seafood*, *shrimp*) et des inspirations internationales (*mexican*, *pizza*, *cocktails*).
    # **Tendances descendantes** : Les baisses marquées touchent des catégories techniques ou structurantes (*dietary*, *equipment*, *oven*, *occasion*, *number-of-servings*), ainsi que des étiquettes génériques (*north-american*, *cuisine*, *american*, *main-ingredient*, *desserts*), suggérant une simplification de la catégorisation au profit de tags plus concrets et orientés usage.
    # **Évolution de la diversité** : Le nombre de tags uniques suit une trajectoire similaire à celle des ingrédients, avec une diminution significative après 2007. Cette standardisation progressive traduit à la fois la baisse du volume de recettes et une convergence vers un vocabulaire de catégorisation plus homogène.   # </INTERPRÉTATION>
    # </INTERPRÉTATION>
def main():
    """
    Fonction principale pour exécuter les analyses de tendances.
    """

    analyse_trendline_1()
    analyse_trendline_3()    
    
    print("\n✅ Analyse terminée avec succès !")

if __name__ == "__main__":
    main()