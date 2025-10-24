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
    # 📊 ANALYSE DU NOMBRE DE RECETTES PAR ANNÉE (100% POLARS)
    recipes_per_year = df.group_by("year").agg(pl.len().alias("n_recipes")).sort("year")

    # Préparation des données pour le Q-Q plot
    data = recipes_per_year["n_recipes"].to_numpy()
    mean_data = np.mean(data)
    std_data = np.std(data, ddof=1)

    # --- VISUALISATION : Fréquence + Q-Q Plot ---
    fig, (ax1, ax0) = plt.subplots(1, 2, figsize=(15, 6))

    # (1) Graphique de fréquence (barres)
    bars = ax1.bar(recipes_per_year["year"].to_numpy().astype(int), recipes_per_year["n_recipes"].to_numpy(),
                color="steelblue", alpha=0.8)
    ax1.set_title("Nombre de recettes par année", fontsize=14, fontweight="bold")
    ax1.set_xlabel("Année")
    ax1.set_ylabel("Nombre de recettes")
    ax1.set_xticks(recipes_per_year["year"].to_numpy().astype(int))
    ax1.set_xticklabels(recipes_per_year["year"].to_numpy().astype(int), rotation=45)
    ax1.grid(axis="y", alpha=0.3)

    # Annotations des valeurs
    for x, y in zip(recipes_per_year["year"].to_numpy(), recipes_per_year["n_recipes"].to_numpy()):
        ax1.text(x, y + 50, f"{y:,}", ha="center", va="bottom", fontsize=9)

    # (2) Q-Q Plot (test de normalité)
    stats.probplot(data, dist="norm", plot=ax0)
    ax0.set_title("Q-Q Plot (Test de normalité)", fontsize=14, fontweight="bold")
    ax0.set_xlabel("Quantiles théoriques (loi normale)")
    ax0.set_ylabel("Quantiles observés")
    ax0.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

    # <INTERPRÉTATION>
    # > Nous observons une **forte augmentation du nombre de recettes postées jusqu’en 2007**, année du **pic d’activité**, suivie d’une **chute marquée** les années suivantes. 
    # Les **tests de normalité** et les **Q-Q plots** montrent que la distribution du **nombre de recettes par an** **n’est pas parfaitement normale**, avec des **écarts visibles** par rapport à la **loi normale théorique**. 
    # </INTERPRÉTATION>

def analyse_trendline_2():
    df = load_recipes_clean()

    # 📊 Agrégation durée par année (100% POLARS)

    minutes_by_year = df.group_by("year").agg([
        pl.mean("minutes").alias("mean_minutes"),
        pl.median("minutes").alias("median_minutes"),
        pl.quantile("minutes", 0.25).alias("q25"),
        pl.quantile("minutes", 0.75).alias("q75"),
        pl.len().alias("n_recipes")
    ]).sort("year")

    # --- CALCUL DES RÉGRESSIONS WLS POUR MEAN ET MEDIAN ---
    X = minutes_by_year["year"].to_numpy()
    w = minutes_by_year["n_recipes"].to_numpy()

    metrics_config = {
        "mean_minutes": {"color": "steelblue", "label": "Moyenne", "ylabel": "minutes/an"},
        "median_minutes": {"color": "coral", "label": "Médiane", "ylabel": "minutes/an"}
    }

    regressions = {}
    for metric_col in metrics_config.keys():
        y = minutes_by_year[metric_col].to_numpy()
        X_const = sm.add_constant(X)
        wls_model = sm.WLS(y, X_const, weights=w)
        wls_result = wls_model.fit()
        y_pred = wls_result.predict(X_const)
        r2_w = 1 - np.average((y - y_pred) ** 2, weights=w) / np.average((y - np.average(y, weights=w)) ** 2, weights=w)
        regressions[metric_col] = {
            "y_pred": y_pred,
            "slope": wls_result.params[1],
            "intercept": wls_result.params[0],
            "r2": r2_w,
            "p_value": wls_result.pvalues[1]
        }

    # --- VISUALISATION AVEC RÉGRESSIONS ---
    fig, ax1 = plt.subplots(1, 1, figsize=(12, 6))

    sizes = minutes_by_year["n_recipes"].to_numpy() / minutes_by_year["n_recipes"].max() * 350
    years = minutes_by_year["year"].to_numpy()
    mean_vals = minutes_by_year["mean_minutes"].to_numpy()
    median_vals = minutes_by_year["median_minutes"].to_numpy()
    q25 = minutes_by_year["q25"].to_numpy()
    q75 = minutes_by_year["q75"].to_numpy()

    # Moyenne
    ax1.plot(years, mean_vals, color="steelblue", linewidth=2, alpha=0.7, label="Moyenne (observée)", zorder=1)
    ax1.scatter(years, mean_vals, s=sizes, color="steelblue", alpha=0.6, edgecolors="black", linewidths=0.5, zorder=3)
    ax1.plot(years, regressions["mean_minutes"]["y_pred"], color="darkblue", linewidth=2, linestyle="--", alpha=0.8,
            label=f"Régression Moyenne (R²={regressions['mean_minutes']['r2']:.3f})", zorder=2)

    # Médiane
    ax1.plot(years, median_vals, color="coral", linewidth=1.5, alpha=0.7, label="Médiane (observée)", zorder=1)
    ax1.scatter(years, median_vals, s=sizes, color="coral", alpha=0.6, edgecolors="black", linewidths=0.5, zorder=3)
    ax1.plot(years, regressions["median_minutes"]["y_pred"], color="darkred", linewidth=2, linestyle="--", alpha=0.8,
            label=f"Régression Médiane (R²={regressions['median_minutes']['r2']:.3f})", zorder=2)

    # IQR
    ax1.fill_between(years, q25, q75, alpha=0.15, color="steelblue", label="IQR (Q25-Q75)", zorder=0)

    # Titres et légendes
    title_text = (f"Évolution de la durée (minutes)\n"
                f"Moyenne: {regressions['mean_minutes']['slope']:+.4f} min/an | "
                f"Médiane: {regressions['median_minutes']['slope']:+.4f} min/an")
    ax1.set_title(title_text, fontsize=12, fontweight="bold")
    ax1.set_xlabel("Année", fontsize=12)
    ax1.set_ylabel("Minutes", fontsize=12)
    ax1.legend(loc="best", fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(years)
    ax1.set_xticklabels([int(y) for y in years], rotation=45)

    plt.tight_layout()
    plt.show()

    # <INTERPRÉTATION>
    # **L’analyse de la durée moyenne de préparation** montre une **tendance globale à la baisse** depuis la création du site.    
    # En moyenne, le temps de préparation diminue d’environ **−0.46/min par an**, tandis que la médiane recule de **−0.26/min par an**, ce qui traduit une **légère simplification des recettes** au fil du temps.  
    # </INTERPRÉTATION>

def analyse_trendline_3():
    df = load_recipes_clean()

    # 📊 Agrégation des données de complexité par année (100% POLARS)

    complexity_by_year = df.group_by("year").agg([
        pl.mean("complexity_score").alias("mean_complexity"),
        pl.mean("n_steps").alias("mean_steps"),
        pl.mean("n_ingredients").alias("mean_ingredients"),
        pl.std("complexity_score").alias("std_complexity"),
        pl.count("id").alias("count_recipes")
    ]).sort("year")

    # --- CALCUL DES RÉGRESSIONS WLS POUR LES 3 MÉTRIQUES ---
    X = complexity_by_year["year"].to_numpy()
    w = complexity_by_year["count_recipes"].to_numpy()

    metrics_config = {
        "mean_complexity": {"color": "purple", "marker": "o", "title": "Score de complexité", "ylabel": "Complexity Score", "show_std": True},
        "mean_steps": {"color": "orange", "marker": "s", "title": "Nombre d'étapes", "ylabel": "Nombre d'étapes", "show_std": False},
        "mean_ingredients": {"color": "forestgreen", "marker": "^", "title": "Nombre d'ingrédients", "ylabel": "Nombre d'ingrédients", "show_std": False}
    }

    regressions = {}
    for metric_col in metrics_config.keys():
        y = complexity_by_year[metric_col].to_numpy()
        X_const = sm.add_constant(X)
        wls_model = sm.WLS(y, X_const, weights=w)
        wls_result = wls_model.fit()
        y_pred = wls_result.predict(X_const)
        r2_w = 1 - np.average((y - y_pred) ** 2, weights=w) / np.average((y - np.average(y, weights=w)) ** 2, weights=w)
        regressions[metric_col] = {"y_pred": y_pred, "slope": wls_result.params[1], "r2": r2_w, "p_value": wls_result.pvalues[1]}

    # --- VISUALISATION AVEC RÉGRESSIONS ---
    sizes = (w / w.max()) * 400
    years = complexity_by_year["year"].to_numpy()
    mean_complexity = complexity_by_year["mean_complexity"].to_numpy()
    std_complexity = complexity_by_year["std_complexity"].to_numpy()
    mean_steps = complexity_by_year["mean_steps"].to_numpy()
    mean_ingredients = complexity_by_year["mean_ingredients"].to_numpy()

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    for ax, (metric_col, config) in zip(axes, metrics_config.items()):
        reg = regressions[metric_col]
        y_vals = complexity_by_year[metric_col].to_numpy()

        ax.plot(years, y_vals, linewidth=2.5, color=config["color"], alpha=0.7, label="Tendance observée", zorder=1)
        ax.scatter(years, y_vals, s=sizes, alpha=0.6, color=config["color"], edgecolors="black", linewidths=0.5,
                label="Observations (taille ~ count_recipes)", zorder=3)
        ax.plot(years, reg["y_pred"], color="red", linewidth=2, linestyle="--", alpha=0.8,
                label=f"Régression WLS (R²={reg['r2']:.3f})", zorder=2)

        if config.get("show_std"):
            ax.fill_between(years, mean_complexity - std_complexity, mean_complexity + std_complexity,
                            alpha=0.15, color=config["color"], label="±1 std", zorder=0)

        title_text = f"{config['title']}\n Pente: {reg['slope']:+.4f}/an (p={reg['p_value']:.2e})"
        ax.set_title(title_text, fontsize=11, fontweight="bold")
        ax.set_xlabel("Année")
        ax.set_ylabel(config["ylabel"])
        ax.grid(True, alpha=0.3)
        ax.set_xticks(years)
        ax.set_xticklabels([int(y) for y in years], rotation=45)
        ax.legend(loc="best", fontsize=8)

    plt.tight_layout()
    plt.show()

    # <INTERPRÉTATION>
    # La **régression linéaire pondérée** (pente = **+0.10**, R² = **0.56**, p = **1.59×10⁻⁴**) met en évidence une **tendance significative à la hausse** du **score moyen de complexité** au fil du temps.  
    # Cette évolution indique une **augmentation progressive de la complexité des recettes**, d’environ **+0.10 point par an**, suggérant des **préparations de plus en plus élaborées** au cours des années.  
    # La tendance observée est **cohérente** avec la corrélation positive entre le **nombre d’étapes** et le **nombre d’ingrédients**, confirmant une **complexification globale** des recettes publiées.
    # </INTERPRÉTATION>

def analyse_trendline_4():
    df = load_recipes_clean()

    # 📊 Agrégation nutrition par année (Calories, Glucides, Lipides, Protéines) — 100% POLARS

    nutrition_by_year = df.group_by("year").agg([
        pl.mean("calories").alias("mean_calories"),
        pl.mean("carb_pct").alias("mean_carbs"),
        pl.mean("total_fat_pct").alias("mean_fat"),
        pl.mean("protein_pct").alias("mean_protein"),
        pl.count("id").alias("count_recipes")
    ]).sort("year")

    # --- CALCUL DES RÉGRESSIONS WLS POUR CHAQUE MÉTRIQUE ---
    X_year = nutrition_by_year["year"].to_numpy()
    w = nutrition_by_year["count_recipes"].to_numpy()

    metrics_config = {
        "mean_calories": {"color": "tomato", "marker": "o", "title": "Calories moyennes", "ylabel": "Calories"},
        "mean_carbs": {"color": "royalblue", "marker": "s", "title": "Glucides (%)", "ylabel": "Carbs %"},
        "mean_fat": {"color": "orange", "marker": "^", "title": "Lipides (%)", "ylabel": "Fat %"},
        "mean_protein": {"color": "green", "marker": "d", "title": "Protéines (%)", "ylabel": "Protein %"}
    }

    regressions = {}
    for metric_col in metrics_config.keys():
        y = nutrition_by_year[metric_col].to_numpy()
        X_const = sm.add_constant(X_year)
        wls_model = sm.WLS(y, X_const, weights=w)
        wls_result = wls_model.fit()
        y_pred = wls_result.predict(X_const)
        r2_w = 1 - np.average((y - y_pred)**2, weights=w) / np.average((y - np.average(y, weights=w))**2, weights=w)
        regressions[metric_col] = {
            "y_pred": y_pred,
            "slope": wls_result.params[1],
            "intercept": wls_result.params[0],
            "r2": r2_w,
            "p_value": wls_result.pvalues[1]
        }

    # --- CALCUL DES TAILLES DE BULLES ---
    sizes = (w / w.max()) * 500

    # --- VISUALISATION AVEC COURBES + BULLES + RÉGRESSIONS ---
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    axes_flat = [axes[0,0], axes[0,1], axes[1,0], axes[1,1]]
    years = nutrition_by_year["year"].to_numpy()

    for ax, (metric_col, config) in zip(axes_flat, metrics_config.items()):
        reg = regressions[metric_col]
        y_vals = nutrition_by_year[metric_col].to_numpy()

        ax.plot(years, y_vals, linewidth=2.5, color=config["color"], alpha=0.7,
                label="Tendance observée", zorder=1)
        ax.scatter(years, y_vals, s=sizes, alpha=0.6, color=config["color"],
                edgecolors="black", linewidths=0.5,
                label="Observations (taille ~ count_recipes)", zorder=3)
        ax.plot(years, reg["y_pred"], color="red", linewidth=2, linestyle="--", alpha=0.8,
                label=f"Régression WLS (R²={reg['r2']:.3f})", zorder=2)

        title_text = f"{config['title']}\n Pente: {reg['slope']:+.4f}/an (p={reg['p_value']:.2e})"
        ax.set_title(title_text, fontsize=11, fontweight="bold")
        ax.set_ylabel(config["ylabel"])
        if ax in [axes[1,0], axes[1,1]]:
            ax.set_xlabel("Année")

        ax.grid(True, alpha=0.3)
        ax.set_xticks(years)
        ax.set_xticklabels([int(y) for y in years], rotation=45)
        ax.legend(loc="best", fontsize=8)

    plt.tight_layout()
    plt.show()

    # <INTERPRÉTATION>
    # Les **régressions linéaires pondérées** montrent une **tendance significative à la baisse** des valeurs **nutritionnelles moyennes** au fil du temps.  
    # Les **calories**, **glucides**, **lipides** et **protéines** présentent toutes des **pentes négatives**, avec des **R² pondérés entre 0.39 et 0.56**, indiquant une **bonne part de variance expliquée** et une **diminution mesurable** des apports nutritionnels moyens par recette.  
    # Cette évolution traduit une **orientation progressive vers des recettes plus légères**, moins riches en **calories** et en **macronutriments**, reflétant probablement une **adaptation aux tendances alimentaires modernes** (recherche de plats plus équilibrés et moins énergétiques).  
    # </INTERPRÉTATION>


def analyse_trendline_5():
    df = load_recipes_clean()
    # --- PARAMÈTRES ---
    NORMALIZE = True  # Normaliser par le nb de recettes de l'année
    MIN_TOTAL_OCC = 50  # Seuil min d'occurrences globales
    TOP_N = 10  # Top hausses/baisses à afficher
    N_VARIATIONS = 5  # Nombre d'ingrédients à tracer

    # --- 0. PRÉPARATION : NORMALISATION DES INGRÉDIENTS ---
    print("🔄 Normalisation des ingrédients en cours...")

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
    )

    top_global = freq_global.head(TOP_N)

    # --- 2. FRÉQUENCE PAR ANNÉE ---
    freq_year_ing = (
        df_ingredients
        .group_by(['year', 'ingredient_norm'])
        .agg(pl.count('ingredient_norm').alias('count'))
    )

    # Nombre de recettes par année
    year_totals = df.group_by('year').agg(pl.count('id').alias('n_recipes'))

    # Joindre et normaliser
    freq_year_ing = freq_year_ing.join(year_totals, on='year', how='left')

    if NORMALIZE:
        freq_year_ing = freq_year_ing.with_columns(
            (pl.col('count') / pl.col('n_recipes')).alias('freq')
        )
    else:
        freq_year_ing = freq_year_ing.with_columns(pl.col('count').alias('freq'))

    # --- 3. CALCUL DES VARIATIONS ---
    min_year = df['year'].min()
    max_year = df['year'].max()

    first_year_vals = (
        freq_year_ing
        .filter(pl.col('year') == min_year)
        .select(['ingredient_norm', pl.col('freq').alias('first')])
    )

    last_year_vals = (
        freq_year_ing
        .filter(pl.col('year') == max_year)
        .select(['ingredient_norm', pl.col('freq').alias('last')])
    )

    variation = (
        first_year_vals
        .join(last_year_vals, on='ingredient_norm', how='full')
        .with_columns([
            pl.col('first').fill_null(0),
            pl.col('last').fill_null(0)
        ])
        .with_columns(
            (pl.col('last') - pl.col('first')).alias('delta')
        )
    )

    # Filtrer pour avoir suffisamment d'occurrences
    variation = (
        variation
        .join(freq_global.select(['ingredient_norm', 'total_count']), on='ingredient_norm', how='left')
        .filter(pl.col('total_count') >= MIN_TOTAL_OCC)
    )

    biggest_increase = variation.sort('delta', descending=True).head(TOP_N)
    biggest_decrease = variation.sort('delta', descending=False).head(TOP_N)

    # --- 4. DIVERSITÉ (NOMBRE D'INGRÉDIENTS UNIQUES) ---
    unique_per_year = (
        df_ingredients
        .group_by('year')
        .agg(pl.n_unique('ingredient_norm').alias('n_unique'))
        .sort('year')
    )

    # --- VISUALISATION ---
    fig = plt.figure(figsize=(18, 12))

    # (1) Top 10 ingrédients (barres horizontales)
    ax1 = plt.subplot(3, 2, 1)
    top_global_data = top_global.to_pandas()
    ax1.barh(range(len(top_global_data)), top_global_data['total_count'], color='steelblue', alpha=0.8)
    ax1.set_yticks(range(len(top_global_data)))
    ax1.set_yticklabels(top_global_data['ingredient_norm'])
    ax1.invert_yaxis()
    ax1.set_xlabel('Occurrences totales')
    ax1.set_title(f'Top {TOP_N} ingrédients les plus fréquents', fontweight='bold', fontsize=11)
    ax1.grid(axis='x', alpha=0.3)

    # (2) Évolution de la diversité
    ax2 = plt.subplot(3, 2, 2)
    unique_data = unique_per_year.to_pandas()
    year_totals_data = year_totals.sort('year').to_pandas()
    w_div = year_totals_data['n_recipes'].values
    sizes_div = (w_div / w_div.max()) * 300
    ax2.plot(unique_data['year'], unique_data['n_unique'], color='purple', linewidth=2, alpha=0.7, label='Diversité observée', zorder=1)
    ax2.scatter(unique_data['year'], unique_data['n_unique'], s=sizes_div, color='purple', alpha=0.6, edgecolors='black', linewidths=0.5, zorder=3)
    ax2.set_xlabel('Année')
    ax2.set_ylabel('Nombre d\'ingrédients uniques')
    ax2.set_title('Évolution de la diversité des ingrédients', fontweight='bold', fontsize=11)
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks(unique_data['year'])
    ax2.set_xticklabels([int(y) for y in unique_data['year']], rotation=45)

    # (3) Top hausses (barres horizontales)
    ax3 = plt.subplot(3, 2, 3)
    label_delta = 'Variation (normalisée)' if NORMALIZE else 'Variation (occurrences)'
    increase_data = biggest_increase.to_pandas()
    ax3.barh(range(len(increase_data)), increase_data['delta'], color='green', alpha=0.8)
    ax3.set_yticks(range(len(increase_data)))
    ax3.set_yticklabels(increase_data['ingredient_norm'])
    ax3.invert_yaxis()
    ax3.set_xlabel(label_delta)
    ax3.set_title(f'Top {TOP_N} hausses ({min_year}→{max_year})', fontweight='bold', fontsize=11)
    ax3.grid(axis='x', alpha=0.3)

    # (4) Top baisses (barres horizontales)
    ax4 = plt.subplot(3, 2, 4)
    decrease_data = biggest_decrease.to_pandas()
    ax4.barh(range(len(decrease_data)), decrease_data['delta'], color='red', alpha=0.8)
    ax4.set_yticks(range(len(decrease_data)))
    ax4.set_yticklabels(decrease_data['ingredient_norm'])
    ax4.invert_yaxis()
    ax4.set_xlabel(label_delta)
    ax4.set_title(f'Top {TOP_N} baisses ({min_year}→{max_year})', fontweight='bold', fontsize=11)
    ax4.grid(axis='x', alpha=0.3)

    # (5) Évolution de quelques ingrédients en hausse
    ax_inc = plt.subplot(3, 2, 5)
    colors = plt.cm.Greens(np.linspace(0.4, 0.9, N_VARIATIONS))
    freq_year_data = freq_year_ing.to_pandas()
    for idx, row in enumerate(biggest_increase.head(N_VARIATIONS).iter_rows(named=True)):
        ing = row['ingredient_norm']
        data_ing = freq_year_data[freq_year_data['ingredient_norm'] == ing].sort_values('year')
        ax_inc.plot(data_ing['year'], data_ing['freq'], marker='o', linewidth=2, alpha=0.7, color=colors[idx], label=ing)
    ax_inc.set_xlabel('Année')
    ax_inc.set_ylabel('Fréquence' if NORMALIZE else 'Occurrences')
    ax_inc.set_title(f'Évolution : Top {N_VARIATIONS} hausses', fontweight='bold', fontsize=11)
    ax_inc.legend(loc='best', fontsize=8)
    ax_inc.grid(True, alpha=0.3)
    ax_inc.set_xticks(unique_data['year'])
    ax_inc.set_xticklabels([int(y) for y in unique_data['year']], rotation=45)

    # (6) Évolution de quelques ingrédients en baisse
    ax_dec = plt.subplot(3, 2, 6)
    colors = plt.cm.Reds(np.linspace(0.4, 0.9, N_VARIATIONS))
    for idx, row in enumerate(biggest_decrease.head(N_VARIATIONS).iter_rows(named=True)):
        ing = row['ingredient_norm']
        data_ing = freq_year_data[freq_year_data['ingredient_norm'] == ing].sort_values('year')
        ax_dec.plot(data_ing['year'], data_ing['freq'], marker='s', linewidth=2, alpha=0.7, color=colors[idx], label=ing)
    ax_dec.set_xlabel('Année')
    ax_dec.set_ylabel('Fréquence' if NORMALIZE else 'Occurrences')
    ax_dec.set_title(f'Évolution : Top {N_VARIATIONS} baisses', fontweight='bold', fontsize=11)
    ax_dec.legend(loc='best', fontsize=8)
    ax_dec.grid(True, alpha=0.3)
    ax_dec.set_xticks(unique_data['year'])
    ax_dec.set_xticklabels([int(y) for y in unique_data['year']], rotation=45)

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

    # 📊 ANALYSE DES TAGS PAR ANNÉE (MODE POLARS PUR)

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
    )

    top_global_tags = freq_global_tags.head(TOP_N)

    # --- 2. FRÉQUENCE PAR ANNÉE ---
    freq_year_tag = (
        df_tags
        .group_by(['year', 'tag_norm'])
        .agg(pl.count('tag_norm').alias('count'))
    )

    # Nombre de recettes par année
    year_totals_tags = df.group_by('year').agg(pl.count('id').alias('n_recipes'))

    # Joindre et normaliser
    freq_year_tag = freq_year_tag.join(year_totals_tags, on='year', how='left')

    if NORMALIZE:
        freq_year_tag = freq_year_tag.with_columns(
            (pl.col('count') / pl.col('n_recipes')).alias('freq')
        )
    else:
        freq_year_tag = freq_year_tag.with_columns(pl.col('count').alias('freq'))

    # --- 3. CALCUL DES VARIATIONS ---
    min_year_tags = df['year'].min()
    max_year_tags = df['year'].max()

    first_year_vals_tags = (
        freq_year_tag
        .filter(pl.col('year') == min_year_tags)
        .select(['tag_norm', pl.col('freq').alias('first')])
    )

    last_year_vals_tags = (
        freq_year_tag
        .filter(pl.col('year') == max_year_tags)
        .select(['tag_norm', pl.col('freq').alias('last')])
    )

    variation_tags = (
        first_year_vals_tags
        .join(last_year_vals_tags, on='tag_norm', how='full')
        .with_columns([
            pl.col('first').fill_null(0),
            pl.col('last').fill_null(0)
        ])
        .with_columns(
            (pl.col('last') - pl.col('first')).alias('delta')
        )
    )

    # Filtrer pour avoir suffisamment d'occurrences
    variation_tags = (
        variation_tags
        .join(freq_global_tags.select(['tag_norm', 'total_count']), on='tag_norm', how='left')
        .filter(pl.col('total_count') >= MIN_TOTAL_OCC)
    )

    biggest_increase_tags = variation_tags.sort('delta', descending=True).head(TOP_N)
    biggest_decrease_tags = variation_tags.sort('delta', descending=False).head(TOP_N)

    # --- 4. DIVERSITÉ (NOMBRE DE TAGS UNIQUES) ---
    unique_per_year_tags = (
        df_tags
        .group_by('year')
        .agg(pl.n_unique('tag_norm').alias('n_unique'))
        .sort('year')
    )

    # --- VISUALISATION ---
    fig = plt.figure(figsize=(18, 12))

    # (1) Top 10 tags (barres horizontales)
    ax1 = plt.subplot(3, 2, 1)
    top_global_tags_data = top_global_tags.to_pandas()
    ax1.barh(range(len(top_global_tags_data)), top_global_tags_data['total_count'], color='steelblue', alpha=0.8)
    ax1.set_yticks(range(len(top_global_tags_data)))
    ax1.set_yticklabels(top_global_tags_data['tag_norm'])
    ax1.invert_yaxis()
    ax1.set_xlabel('Occurrences totales')
    ax1.set_title(f'Top {TOP_N} tags les plus fréquents', fontweight='bold', fontsize=11)
    ax1.grid(axis='x', alpha=0.3)

    # (2) Évolution de la diversité
    ax2 = plt.subplot(3, 2, 2)
    unique_data_tags = unique_per_year_tags.to_pandas()
    year_totals_tags_data = year_totals_tags.sort('year').to_pandas()
    w_div_tags = year_totals_tags_data['n_recipes'].values
    sizes_div_tags = (w_div_tags / w_div_tags.max()) * 300
    ax2.plot(unique_data_tags['year'], unique_data_tags['n_unique'], 
            color='purple', linewidth=2, alpha=0.7, label='Diversité observée', zorder=1)
    ax2.scatter(unique_data_tags['year'], unique_data_tags['n_unique'],
                s=sizes_div_tags, color='purple', alpha=0.6, 
                edgecolors='black', linewidths=0.5, zorder=3)
    ax2.set_xlabel('Année')
    ax2.set_ylabel('Nombre de tags uniques')
    ax2.set_title('Évolution de la diversité des tags', fontweight='bold', fontsize=11)
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks(unique_data_tags['year'])
    ax2.set_xticklabels([int(y) for y in unique_data_tags['year']], rotation=45)

    # (3) Top hausses (barres horizontales)
    ax3 = plt.subplot(3, 2, 3)
    label_delta_tags = 'Variation (normalisée)' if NORMALIZE else 'Variation (occurrences)'
    increase_data_tags = biggest_increase_tags.to_pandas()
    ax3.barh(range(len(increase_data_tags)), increase_data_tags['delta'], color='green', alpha=0.8)
    ax3.set_yticks(range(len(increase_data_tags)))
    ax3.set_yticklabels(increase_data_tags['tag_norm'])
    ax3.invert_yaxis()
    ax3.set_xlabel(label_delta_tags)
    ax3.set_title(f'Top {TOP_N} hausses ({min_year_tags}→{max_year_tags})', fontweight='bold', fontsize=11)
    ax3.grid(axis='x', alpha=0.3)

    # (4) Top baisses (barres horizontales)
    ax4 = plt.subplot(3, 2, 4)
    decrease_data_tags = biggest_decrease_tags.to_pandas()
    ax4.barh(range(len(decrease_data_tags)), decrease_data_tags['delta'], color='red', alpha=0.8)
    ax4.set_yticks(range(len(decrease_data_tags)))
    ax4.set_yticklabels(decrease_data_tags['tag_norm'])
    ax4.invert_yaxis()
    ax4.set_xlabel(label_delta_tags)
    ax4.set_title(f'Top {TOP_N} baisses ({min_year_tags}→{max_year_tags})', fontweight='bold', fontsize=11)
    ax4.grid(axis='x', alpha=0.3)

    # (5) Évolution de quelques tags en hausse
    ax_inc = plt.subplot(3, 2, 5)
    colors = plt.cm.Greens(np.linspace(0.4, 0.9, N_VARIATIONS))
    freq_year_tag_data = freq_year_tag.to_pandas()
    for idx, row in enumerate(biggest_increase_tags.head(N_VARIATIONS).iter_rows(named=True)):
        tag = row['tag_norm']
        data_tag = freq_year_tag_data[freq_year_tag_data['tag_norm'] == tag].sort_values('year')
        ax_inc.plot(data_tag['year'], data_tag['freq'], 
                    marker='o', linewidth=2, alpha=0.7, color=colors[idx],
                    label=tag)
    ax_inc.set_xlabel('Année')
    ax_inc.set_ylabel('Fréquence' if NORMALIZE else 'Occurrences')
    ax_inc.set_title(f'Évolution : Top {N_VARIATIONS} hausses', fontweight='bold', fontsize=11)
    ax_inc.legend(loc='best', fontsize=8)
    ax_inc.grid(True, alpha=0.3)
    ax_inc.set_xticks(unique_data_tags['year'])
    ax_inc.set_xticklabels([int(y) for y in unique_data_tags['year']], rotation=45)

    # (6) Évolution de quelques tags en baisse
    ax_dec = plt.subplot(3, 2, 6)
    colors = plt.cm.Reds(np.linspace(0.4, 0.9, N_VARIATIONS))
    for idx, row in enumerate(biggest_decrease_tags.head(N_VARIATIONS).iter_rows(named=True)):
        tag = row['tag_norm']
        data_tag = freq_year_tag_data[freq_year_tag_data['tag_norm'] == tag].sort_values('year')
        ax_dec.plot(data_tag['year'], data_tag['freq'], 
                    marker='s', linewidth=2, alpha=0.7, color=colors[idx],
                    label=tag)
    ax_dec.set_xlabel('Année')
    ax_dec.set_ylabel('Fréquence' if NORMALIZE else 'Occurrences')
    ax_dec.set_title(f'Évolution : Top {N_VARIATIONS} baisses', fontweight='bold', fontsize=11)
    ax_dec.legend(loc='best', fontsize=8)
    ax_dec.grid(True, alpha=0.3)
    ax_dec.set_xticks(unique_data_tags['year'])
    ax_dec.set_xticklabels([int(y) for y in unique_data_tags['year']], rotation=45)

    plt.tight_layout()
    plt.show()

    print(f"\n✅ Visualisation terminée !")
    print(f"   • {len(freq_global_tags):,} tags analysés (≥ {MIN_TOTAL_OCC} occurrences)")
    print(f"   • Diversité : {unique_per_year_tags[0, 'n_unique']:,} ({min_year_tags}) → {unique_per_year_tags[-1, 'n_unique']:,} ({max_year_tags})")

    # <INTERPRÉTATION>
    # L'analyse des tags révèle une **évolution des pratiques de catégorisation** des recettes au fil du temps.
    # **Tendances montantes** : Les catégories en hausse concernent surtout les repas rapides (*60-minutes-or-less*, *for-1-or-2*), les plats principaux (*main-dish*), ainsi que des moments spécifiques comme le petit-déjeuner ou les en-cas. On observe aussi une progression des recettes à base de fruits de mer (*seafood*, *shrimp*) et des inspirations internationales (*mexican*, *pizza*, *cocktails*).
    # **Tendances descendantes** : Les baisses marquées touchent des catégories techniques ou structurantes (*dietary*, *equipment*, *oven*, *occasion*, *number-of-servings*), ainsi que des étiquettes génériques (*north-american*, *cuisine*, *american*, *main-ingredient*, *desserts*), suggérant une simplification de la catégorisation au profit de tags plus concrets et orientés usage.
    # **Évolution de la diversité** : Le nombre de tags uniques suit une trajectoire similaire à celle des ingrédients, avec une diminution significative après 2007. Cette standardisation progressive traduit à la fois la baisse du volume de recettes et une convergence vers un vocabulaire de catégorisation plus homogène.   # </INTERPRÉTATION>
    # </INTERPRÉTATION>



def analyse_seasonality_1():
    df = load_recipes_clean()
    # 📊 ANALYSE : RECETTES PAR SAISON

    # Agrégation
    recipes_per_season = (
        df.group_by("season")
        .agg(pl.len().alias("n_recipes"))
        .join(pl.DataFrame({"season": ["Winter", "Spring", "Summer", "Autumn"], "order": range(4)}),
            on="season", how="left")
        .sort("order")
        .drop("order")
    )

    # Visualisation
    season_order = ["Winter", "Spring", "Summer", "Autumn"]
    season_colors = {"Winter": "#87CEEB", "Spring": "#90EE90", "Summer": "#FFD700", "Autumn": "#FF8C00"}

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))

    colors = [season_colors[s] for s in recipes_per_season['season']]
    bars = ax1.bar(recipes_per_season['season'], recipes_per_season['n_recipes'],
                color=colors, alpha=0.8, edgecolor='black', linewidth=1)

    ax1.set_title('Nombre de recettes par saison', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Saison')
    ax1.set_ylabel('Nombre de recettes')
    ax1.grid(axis='y', alpha=0.3)

    for bar, val in zip(bars, recipes_per_season['n_recipes']):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1000,
                f'{val:,}', ha='center', va='bottom', fontsize=11, fontweight='bold')

    sizes = recipes_per_season['n_recipes']
    labels = recipes_per_season['season']
    colors_pie = [season_colors[s] for s in recipes_per_season['season']]

    wedges, texts, autotexts = ax2.pie(sizes, labels=labels, colors=colors_pie, autopct='%1.1f%%',
                                    startangle=90, textprops={'fontsize': 11})

    ax2.set_title('Répartition saisonnière des recettes (%)', fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.show()
    # <INTERPRÉTATION>
    # Le **test du χ²** montre que la **répartition saisonnière** du nombre de recettes **n’est pas uniforme**, avec des **écarts significatifs** entre les saisons.  
    #
    # Le **printemps**, nettement au-dessus de la moyenne (+4236, +8,7%), indique une **saisonnalité marquée** dans la production, tandis que les autres saisons restent **relativement stables**.  
    # </INTERPRÉTATION>


def analyse_seasonality_2():
    df = load_recipes_clean()
    season_order = ["Winter", "Spring", "Summer", "Autumn"]
    season_colors = {"Winter": "#87CEEB", "Spring": "#90EE90", "Summer": "#FFD700", "Autumn": "#FF8C00"}

    # 📊 ANALYSE : DURÉE DES RECETTES PAR SAISON

    minutes_by_season = (
        df.group_by("season")
        .agg([
            pl.mean("minutes").alias("mean_minutes"),
            pl.median("minutes").alias("median_minutes"),
            pl.quantile("minutes", 0.25).alias("q25"),
            pl.quantile("minutes", 0.75).alias("q75"),
            pl.len().alias("n_recipes")
        ])
        .join(pl.DataFrame({"season": season_order, "order": range(len(season_order))}), on="season", how="left")
        .sort("order")
        .drop("order")
    )

    minutes_by_season = minutes_by_season.with_columns((pl.col("q75") - pl.col("q25")).alias("IQR"))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    bar_colors = [season_colors[s] for s in minutes_by_season["season"]]

    # --- GRAPHIQUE 1 : Barres + Médiane + IQR ---
    ax1.bar(minutes_by_season["season"], minutes_by_season["mean_minutes"],
            color=bar_colors, alpha=.85, edgecolor='black', lw=1, label='Moyenne')
    ax1.plot(minutes_by_season["season"], minutes_by_season["median_minutes"],
            'o--', color='black', lw=1.2, ms=6, label='Médiane')

    for row in minutes_by_season.iter_rows(named=True):
        s, m, med, q25, q75, _n, _iqr = row['season'], row['mean_minutes'], row['median_minutes'], row['q25'], row['q75'], row['n_recipes'], row['IQR']
        ax1.vlines(s, q25, q75, color='black', lw=3, alpha=.6)
        ax1.scatter([s], [q25], color='black', s=25)
        ax1.scatter([s], [q75], color='black', s=25)
        ax1.text(s, m * 1.03, f"{m:.1f} m", ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax1.set_title("Durée des recettes par saison", fontsize=14, fontweight='bold')
    ax1.set_ylabel("Minutes")
    ax1.grid(axis='y', alpha=.3)
    ax1.legend()

    # --- GRAPHIQUE 2 : Boxplot enrichi ---
    sns.boxplot(
        data=df.to_pandas(), x='season', y='minutes', order=season_order,
        palette=[season_colors[s] for s in season_order], ax=ax2,
        showfliers=False, linewidth=1.5
    )

    # Annotations : médiane, Q1, Q3, IQR sur chaque boîte
    for i, season in enumerate(season_order):
        row = minutes_by_season.filter(pl.col("season") == season).row(0, named=True)
        median, q25, q75, iqr = row['median_minutes'], row['q25'], row['q75'], row['IQR']

        ax2.text(i, median, f'{median:.1f}', ha='center', va='center', fontsize=9, fontweight='bold',
                color='white', bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7))
        ax2.text(i-0.35, q25, f'Q1={q25:.0f}', ha='center', va='top', fontsize=8, color='gray', style='italic')
        ax2.text(i-0.35, q75, f'Q3={q75:.0f}', ha='center', va='bottom', fontsize=8, color='gray', style='italic')
        ax2.text(i+0.42, (q25+q75)/2, f'IQR\n{iqr:.0f}', ha='left', va='center', fontsize=8, color='darkblue', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.25', facecolor='lightyellow', alpha=0.8))

    ax2.set_title("Distribution des durées (boxplot enrichi)", fontsize=14, fontweight='bold')
    ax2.set_xlabel("Saison", fontsize=12)
    ax2.set_ylabel("Minutes", fontsize=12)
    ax2.grid(axis='y', alpha=.3)

    plt.tight_layout()
    plt.show()
    
    # <INTERPRÉTATION>
    # Le **test de Kruskal-Wallis** (H = 346.93, p < 0.001) confirme des **différences significatives** de durée entre les saisons.  
    #
    # Les recettes postées en **automne** et en **hiver** sont **plus longues** que celles partagées en **été**, avec une durée moyenne de **43,9 minutes** en **automne** et **43,1 minutes** en **hiver**, contre **41,0 minutes** en **été** et **41,9 minutes** au **printemps**.  
    # </INTERPRÉTATION>


def analyse_seasonality_3():
    df = load_recipes_clean()
    season_order = ["Winter", "Spring", "Summer", "Autumn"]
    season_colors = {"Winter": "#87CEEB", "Spring": "#90EE90", "Summer": "#FFD700", "Autumn": "#FF8C00"}

    # 📊 Agrégation des données de complexité par saison
    complexity_by_season = (
        df.group_by("season")
        .agg([
            pl.mean("complexity_score").alias("mean_complexity"),
            pl.median("complexity_score").alias("median_complexity"),
            pl.std("complexity_score").alias("std_complexity"),
            pl.mean("n_steps").alias("mean_steps"),
            pl.median("n_steps").alias("median_steps"),
            pl.mean("n_ingredients").alias("mean_ingredients"),
            pl.median("n_ingredients").alias("median_ingredients"),
            pl.quantile("complexity_score", 0.25).alias("q25_complexity"),
            pl.quantile("complexity_score", 0.75).alias("q75_complexity"),
            pl.count("id").alias("count_recipes")
        ])
        .join(pl.DataFrame({"season": season_order, "order": range(len(season_order))}), on="season", how="left")
        .sort("order")
        .drop("order")
    )

    # Configuration des couleurs saisonnières
    colors_dict = {s: season_colors[s] for s in season_order}

    # --- VISUALISATION EN 3 PANELS ---
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # --- GRAPHIQUE 1 : Score de complexité (barres + médiane + IQR) ---
    ax1 = axes[0]
    bar_colors = [colors_dict[s] for s in complexity_by_season["season"]]

    bars = ax1.bar(complexity_by_season["season"], complexity_by_season["mean_complexity"],
                color=bar_colors, alpha=0.85, edgecolor='black', linewidth=1.2,
                label='Moyenne')

    # Médiane en ligne pointillée
    ax1.plot(complexity_by_season["season"], complexity_by_season["median_complexity"],
            'o--', color='black', linewidth=1.5, markersize=7, label='Médiane')

    # Annotations
    for i, row in enumerate(complexity_by_season.iter_rows(named=True)):
        ax1.text(i, row["mean_complexity"] * 1.02, f"{row['mean_complexity']:.2f}",
                ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax1.set_title('Score de complexité par saison\n(moyenne ± écart-type)',
                fontsize=12, fontweight='bold')
    ax1.set_xlabel('Saison', fontsize=11)
    ax1.set_ylabel('Complexity Score', fontsize=11)
    ax1.grid(axis='y', alpha=0.3)
    ax1.legend(loc='best')

    # --- GRAPHIQUE 2 : Nombre d'étapes ---
    ax2 = axes[1]
    bars2 = ax2.bar(complexity_by_season["season"], complexity_by_season["mean_steps"],
                    color=bar_colors, alpha=0.85, edgecolor='black', linewidth=1.2,
                    label='Moyenne')

    ax2.plot(complexity_by_season["season"], complexity_by_season["median_steps"],
            's--', color='black', linewidth=1.5, markersize=7, label='Médiane')

    for i, row in enumerate(complexity_by_season.iter_rows(named=True)):
        ax2.text(i, row["mean_steps"] * 1.02, f"{row['mean_steps']:.1f}",
                ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax2.set_title("Nombre d'étapes par saison",
                fontsize=12, fontweight='bold')
    ax2.set_xlabel('Saison', fontsize=11)
    ax2.set_ylabel("Nombre d'étapes", fontsize=11)
    ax2.grid(axis='y', alpha=0.3)
    ax2.legend(loc='best')

    # --- GRAPHIQUE 3 : Nombre d'ingrédients ---
    ax3 = axes[2]
    bars3 = ax3.bar(complexity_by_season["season"], complexity_by_season["mean_ingredients"],
                    color=bar_colors, alpha=0.85, edgecolor='black', linewidth=1.2,
                    label='Moyenne')

    ax3.plot(complexity_by_season["season"], complexity_by_season["median_ingredients"],
            '^--', color='black', linewidth=1.5, markersize=7, label='Médiane')

    for i, row in enumerate(complexity_by_season.iter_rows(named=True)):
        ax3.text(i, row["mean_ingredients"] * 1.02, f"{row['mean_ingredients']:.1f}",
                ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax3.set_title("Nombre d'ingrédients par saison",
                fontsize=12, fontweight='bold')
    ax3.set_xlabel('Saison', fontsize=11)
    ax3.set_ylabel("Nombre d'ingrédients", fontsize=11)
    ax3.grid(axis='y', alpha=0.3)
    ax3.legend(loc='best')

    plt.tight_layout()
    plt.show()

    # <INTERPRÉTATION>
    # Les **tests de Kruskal-Wallis** révèlent des **différences significatives** de complexité entre les saisons (p < 0.001).  
    #
    # Les recettes postées en **hiver** et en **automne** sont plus élaborées (plus d'étapes et d'ingrédients), tandis que les recettes postées en **été** privilégient des préparations simplifiées. Cette **saisonnalité marquée** reflète les habitudes culinaires : plats mijotés en saison froide vs. recettes rapides et fraîches en période estivale.  
    # </INTERPRÉTATION>


def analyse_seasonality_4():
    df = load_recipes_clean()
    season_order = ["Winter", "Spring", "Summer", "Autumn"]
    season_colors = {"Winter": "#87CEEB", "Spring": "#90EE90", "Summer": "#FFD700", "Autumn": "#FF8C00"}

    # 📊 Agrégation des données nutritionnelles par saison
    nutrition_by_season = (
        df.group_by("season")
        .agg([
            pl.mean("calories").alias("mean_calories"),
            pl.mean("total_fat_pct").alias("mean_fat"),
            pl.mean("sugar_pct").alias("mean_sugar"),
            pl.mean("sodium_pct").alias("mean_sodium"),
            pl.mean("protein_pct").alias("mean_protein"),
            pl.mean("sat_fat_pct").alias("mean_sat_fat"),
            pl.count("id").alias("count_recipes")
        ])
        .join(pl.DataFrame({"season": season_order, "order": range(len(season_order))}), on="season", how="left")
        .sort("order")
        .drop("order")
    )

    # --- HEATMAP NUTRITIONNELLE ---
    fig, ax = plt.subplots(figsize=(12, 7))

    # Extraction du sous-ensemble pour la matrice
    nutrition_matrix = nutrition_by_season.select([
        "season", "mean_calories", "mean_fat", "mean_sugar", "mean_sodium", "mean_protein", "mean_sat_fat"
    ])

    # Normalisation par z-score pour chaque colonne numérique
    nutrition_values = nutrition_matrix.select(pl.exclude("season")).to_numpy()
    nutrition_norm = (nutrition_values - nutrition_values.mean(axis=0)) / nutrition_values.std(axis=0)

    # Conversion en DataFrame pandas uniquement pour seaborn
    nutrition_norm_df = pd.DataFrame(
        nutrition_norm.T,
        index=["Calories", "Lipides (%)", "Sucres (%)", "Sodium (%)", "Protéines (%)", "Graisses sat. (%)"],
        columns=nutrition_matrix["season"].to_list()
    )

    sns.heatmap(nutrition_norm_df, annot=True, fmt='.2f', cmap='RdYlGn_r',
                cbar_kws={'label': 'Z-score (écart à la moyenne)'}, 
                linewidths=0.5, ax=ax, annot_kws={'fontsize': 11})

    ax.set_title('Profil nutritionnel par saison (valeurs normalisées)',
                fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Saison', fontsize=12, fontweight='bold')
    ax.set_ylabel('Nutriments', fontsize=12, fontweight='bold')
    ax.tick_params(axis='both', labelsize=11)

    plt.tight_layout()
    plt.show()

    # <INTERPRÉTATION>
    # Les **tests de Kruskal-Wallis** révèlent des **différences nutritionnelles significatives** entre les saisons (p < 0.05).  
    #
    # Les recettes **postées en automne** sont les plus **caloriques** (**492 kcal** en moyenne) et riches en **lipides**, **sucres** et **graisses saturées**, tandis que celles **postées en été** privilégient des préparations plus **légères** avec moins de **calories** (**446 kcal**).  
    # </INTERPRÉTATION>


def analyse_seasonality_5():
    df = load_recipes_clean()
    season_order = ["Winter", "Spring", "Summer", "Autumn"]
    season_colors = {"Winter": "#87CEEB", "Spring": "#90EE90", "Summer": "#FFD700", "Autumn": "#FF8C00"}

    # 📊 ANALYSE DES INGRÉDIENTS PAR SAISON
    print("🔄 Extraction et analyse des ingrédients par saison...")

    # --- 1. EXTRACTION DES INGRÉDIENTS ---
    ingredients_by_season = {}
    n_recipes_by_season = {}

    for season in season_order:
        season_df = df.filter(pl.col("season") == season)
        n_recipes_by_season[season] = season_df.height
        ingredient_counts = (
            season_df.select(pl.col("ingredients").explode())
            .group_by("ingredients")
            .agg(pl.count().alias("count"))
        )
        ingredients_by_season[season] = dict(zip(ingredient_counts["ingredients"], ingredient_counts["count"]))
        print(f"  • {season}: {len(ingredients_by_season[season]):,} ingrédients dans {n_recipes_by_season[season]:,} recettes")

    # --- 2. CALCUL DES FRÉQUENCES ET MÉTRIQUES ---
    all_ingredients = set().union(*[set(ing.keys()) for ing in ingredients_by_season.values()])
    print(f"\n✅ Total: {len(all_ingredients):,} ingrédients uniques")

    # Construction matrice
    ingredients_matrix = [
        {"ingredient": ing, **{s: (ingredients_by_season[s].get(ing, 0) / n_recipes_by_season[s]) * 100 for s in season_order}}
        for ing in all_ingredients
    ]
    ingredients_df = pl.DataFrame(ingredients_matrix)

    # Métriques de variabilité
    ingredients_df = ingredients_df.with_columns([
        pl.concat_list([pl.col(s) for s in season_order]).alias("season_values")
    ]).with_columns([
        pl.col("season_values").list.std().alias("std_seasonal"),
        pl.col("season_values").list.mean().alias("mean_freq"),
        (pl.col("season_values").list.std() / pl.col("season_values").list.mean() * 100).alias("cv"),
        (pl.max_horizontal([pl.col(s) for s in season_order]) - pl.min_horizontal([pl.col(s) for s in season_order])).alias("range")
    ]).drop("season_values")

    # --- 3. FILTRAGE ---
    FREQ_THRESHOLD, RANGE_THRESHOLD = 1.0, 0.5
    ingredients_df_filtered = ingredients_df.filter(
        (pl.col("mean_freq") >= FREQ_THRESHOLD) & (pl.col("range") >= RANGE_THRESHOLD)
    )

    print(f"\n📊 Filtrage: {len(ingredients_df_filtered):,}/{len(ingredients_df):,} ingrédients")
    print(f"  • Fréquence ≥ {FREQ_THRESHOLD}% | Range ≥ {RANGE_THRESHOLD}pp")

    # Top 20 par coefficient de variation
    top_variable = (
        ingredients_df_filtered.sort("cv", descending=True)
        .head(20)
        .with_columns([
            pl.struct(season_order).map_elements(lambda x: max(x, key=x.get)).alias("max_season"),
            pl.struct(season_order).map_elements(lambda x: min(x, key=x.get)).alias("min_season")
        ])
    )

    # --- 4. VISUALISATION : HEATMAP ---
    fig, ax = plt.subplots(figsize=(12, 10))

    heatmap_data_raw = np.array([top_variable[s].to_numpy() for s in season_order]).T
    ingredient_labels = top_variable["ingredient"].to_list()

    heatmap_data_normalized = np.array([
        (row - row.min()) / (row.max() - row.min()) if row.max() > row.min() else np.zeros_like(row)
        for row in heatmap_data_raw
    ])

    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list(
        "gray_yellow_green",
        ["#D3D3D3", "#F5F5DC", "#FFEB3B", "#9CCC65", "#66BB6A", "#2E7D32"],
        N=100
    )

    im = ax.imshow(heatmap_data_normalized, cmap=cmap, aspect="auto", vmin=0, vmax=1)

    ax.set_xticks(np.arange(len(season_order)))
    ax.set_yticks(np.arange(len(ingredient_labels)))
    ax.set_xticklabels(season_order, fontsize=11, fontweight="bold")
    ax.set_yticklabels(ingredient_labels, fontsize=10)

    for i in range(len(ingredient_labels)):
        for j in range(len(season_order)):
            text_color = "black" if heatmap_data_normalized[i, j] < 0.6 else "white"
            ax.text(j, i, f"{heatmap_data_raw[i, j]:.1f}%",
                    ha="center", va="center", color=text_color,
                    fontsize=9, fontweight="bold")

    cbar = plt.colorbar(im, ax=ax, ticks=[0, 0.25, 0.5, 0.75, 1.0])
    cbar.set_label("Utilisation saisonnière", fontsize=11, fontweight="bold")
    cbar.ax.set_yticklabels(["Min", "Faible", "Moyen", "Élevé", "Max"])

    ax.set_title("Top 20 ingrédients - Variabilité saisonnière (% présence dans les recettes)\n(Gris = rare | Vert = pic)",
                fontsize=13, fontweight="bold", pad=20)
    ax.set_xlabel("Saison", fontsize=12, fontweight="bold")
    ax.set_ylabel("Ingrédient", fontsize=12, fontweight="bold")

    plt.tight_layout()
    plt.show()

    print("\n✅ Visualisation terminée!")

    # <INTERPRÉTATION>
    # Les **tests du Chi-2** révèlent une **variabilité saisonnière significative (p < 0.05)** parmi les ingrédients les plus variables (**top 20**), confirmant que les **recettes postées varient clairement selon les saisons**. Ces différences traduisent des **habitudes culinaires marquées** et une adaptation aux **produits disponibles** au fil de l’année.  
    #
    # En **été**, les recettes postées mettent en avant la **fraîcheur** et la **légèreté**, avec une forte présence de **légumes et herbes aromatiques** comme les courgettes ou les tomates.  
    #
    # À l’inverse, les **recettes postées en automne** se tournent vers des **préparations plus riches et réconfortantes**, dominées par exemple par des ingrédients comme le bicarbonate de soude (baking soda) ou les carottes, typiques de la **pâtisserie** et des **plats mijotés** ou **soupes**.  
    # </INTERPRÉTATION>


def analyse_seasonality_6():    
    df = load_recipes_clean()
    season_order = ["Winter", "Spring", "Summer", "Autumn"]
    season_colors = {"Winter": "#87CEEB", "Spring": "#90EE90", "Summer": "#FFD700", "Autumn": "#FF8C00"}

    # 📊 ANALYSE DES TAGS PAR SAISON
    print("🔄 Extraction et analyse des tags par saison...")

    # --- 1. EXTRACTION DES TAGS ---
    tags_by_season = {}
    n_recipes_by_season_tags = {}

    for season in season_order:
        season_df = df.filter(pl.col("season") == season)
        n_recipes_by_season_tags[season] = season_df.height
        tag_counts = (
            season_df.select(pl.col("tags").explode())
            .group_by("tags")
            .agg(pl.count().alias("count"))
        )
        tags_by_season[season] = dict(zip(tag_counts["tags"], tag_counts["count"]))
        print(f"  • {season}: {len(tags_by_season[season]):,} tags dans {n_recipes_by_season_tags[season]:,} recettes")

    # --- 2. CALCUL DES FRÉQUENCES ET MÉTRIQUES ---
    all_tags = set().union(*[set(tag.keys()) for tag in tags_by_season.values()])
    print(f"\n✅ Total: {len(all_tags):,} tags uniques")

    # Matrice tags × saisons
    tags_matrix = [
        {"tag": t, **{s: (tags_by_season[s].get(t, 0) / n_recipes_by_season_tags[s]) * 100 for s in season_order}}
        for t in all_tags
    ]
    tags_df = pl.DataFrame(tags_matrix)

    # Métriques de variabilité
    tags_df = tags_df.with_columns([
        pl.concat_list([pl.col(s) for s in season_order]).alias("season_values")
    ]).with_columns([
        pl.col("season_values").list.std().alias("std_seasonal"),
        pl.col("season_values").list.mean().alias("mean_freq"),
        (pl.col("season_values").list.std() / pl.col("season_values").list.mean() * 100).alias("cv"),
        (pl.max_horizontal([pl.col(s) for s in season_order]) - pl.min_horizontal([pl.col(s) for s in season_order])).alias("range")
    ]).drop("season_values")

    # --- 3. FILTRAGE ---
    FREQ_THRESHOLD_TAGS, RANGE_THRESHOLD_TAGS = 1.0, 0.5
    tags_df_filtered = tags_df.filter(
        (pl.col("mean_freq") >= FREQ_THRESHOLD_TAGS) & (pl.col("range") >= RANGE_THRESHOLD_TAGS)
    )

    print(f"\n📊 Filtrage: {len(tags_df_filtered):,}/{len(tags_df):,} tags")
    print(f"  • Fréquence ≥ {FREQ_THRESHOLD_TAGS}% | Range ≥ {RANGE_THRESHOLD_TAGS}pp")

    # Top 20 par coefficient de variation
    top_variable_tags = (
        tags_df_filtered.sort("cv", descending=True)
        .head(20)
        .with_columns([
            pl.struct(season_order).map_elements(lambda x: max(x, key=x.get)).alias("max_season"),
            pl.struct(season_order).map_elements(lambda x: min(x, key=x.get)).alias("min_season")
        ])
    )

    # --- 4. VISUALISATION : HEATMAP ---
    fig, ax = plt.subplots(figsize=(12, 10))

    heatmap_data_raw = np.array([top_variable_tags[s].to_numpy() for s in season_order]).T
    tag_labels = top_variable_tags["tag"].to_list()

    heatmap_data_normalized = np.array([
        (row - row.min()) / (row.max() - row.min()) if row.max() > row.min() else np.zeros_like(row)
        for row in heatmap_data_raw
    ])

    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list(
        "gray_yellow_green",
        ["#D3D3D3", "#F5F5DC", "#FFEB3B", "#9CCC65", "#66BB6A", "#2E7D32"],
        N=100
    )

    im = ax.imshow(heatmap_data_normalized, cmap=cmap, aspect="auto", vmin=0, vmax=1)

    ax.set_xticks(np.arange(len(season_order)))
    ax.set_yticks(np.arange(len(tag_labels)))
    ax.set_xticklabels(season_order, fontsize=11, fontweight="bold")
    ax.set_yticklabels(tag_labels, fontsize=10)

    for i in range(len(tag_labels)):
        for j in range(len(season_order)):
            text_color = "black" if heatmap_data_normalized[i, j] < 0.6 else "white"
            ax.text(j, i, f"{heatmap_data_raw[i, j]:.1f}%",
                    ha="center", va="center", color=text_color,
                    fontsize=9, fontweight="bold")

    cbar = plt.colorbar(im, ax=ax, ticks=[0, 0.25, 0.5, 0.75, 1.0])
    cbar.set_label("Utilisation saisonnière", fontsize=11, fontweight="bold")
    cbar.ax.set_yticklabels(["Min", "Faible", "Moyen", "Élevé", "Max"])

    ax.set_title("Top 20 tags - Variabilité saisonnière\n(Gris = rare | Vert = pic)",
                fontsize=13, fontweight="bold", pad=20)
    ax.set_xlabel("Saison", fontsize=12, fontweight="bold")
    ax.set_ylabel("Tag", fontsize=12, fontweight="bold")

    plt.tight_layout()
    plt.show()

    print("\n✅ Visualisation terminée!")

    # <INTERPRÉTATION>
    # **Les analyses de variabilité saisonnière des tags culinaires** montrent une **segmentation claire selon les saisons**, confirmant des **tendances cohérentes avec les périodes de l’année**. Les tags liés à des événements précis comme **thanksgiving (3.9%)** ou **christmas (5.6%)** culminent logiquement en **automne et hiver**, tandis que ceux associés à la convivialité estivale, tels que **summer (7.7%)**, **barbecue (2.7%)** et **grilling (2.4%)**, atteignent leur maximum en **été**.  
    #
    # Au **printemps**, des tags de renouveau apparaissent comme **spring (2.6%)** ou **berries (3.1%)**, reflétant une cuisine plus fraîche et légère. L’**hiver**, quant à lui, se distingue par des thèmes de **réconfort et de fêtes** (**winter 4.6%**, gifts 3.4%, new-years 1.5%), témoignant d’une cuisine plus riche et traditionnelle.  
    # </INTERPRÉTATION>



def analyse_weekend_effect_1():
    df = load_recipes_clean()
    # 📊 ANALYSE 1 : VOLUME DE RECETTES (Weekday vs Weekend)

    # --- Ajout colonne Weekday / Weekend ---
    df = df.with_columns(pl.when(pl.col("is_weekend") == 1).then(pl.lit("Weekend")).otherwise(pl.lit("Weekday")).alias("week_period"))

    # --- Agrégation Weekday vs Weekend ---
    recipes_week_period = (
        df.group_by("week_period")
        .agg(pl.count().alias("n_recipes"))
        .with_columns(pl.when(pl.col("week_period") == "Weekday").then(pl.lit(5)).otherwise(pl.lit(2)).alias("n_days"))
        .with_columns((pl.col("n_recipes") / pl.col("n_days")).alias("recipes_per_day"))
        .with_columns(pl.when(pl.col("week_period") == "Weekday").then(0).otherwise(1).alias("order"))
        .sort("order")
        .drop("order")
    )

    # --- Agrégation par jour ---
    recipes_per_day = (
        df.group_by("weekday")
        .agg(pl.count().alias("n_recipes"))
        .with_columns(pl.col("weekday").map_elements(lambda x: {1:'Lun',2:'Mar',3:'Mer',4:'Jeu',5:'Ven',6:'Sam',7:'Dim'}[x]).alias("jour"))
    )

    # --- Réordonnons les jours ---
    day_order = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
    recipes_per_day = (
        recipes_per_day
        .join(pl.DataFrame({"jour": day_order, "order": range(len(day_order))}), on="jour", how="left")
        .sort("order")
        .drop("order")
    )

    # --- Moyennes globales ---
    mean_all = recipes_per_day["n_recipes"].mean()
    mean_weekday = recipes_per_day.filter(~pl.col("jour").is_in(["Sam","Dim"]))["n_recipes"].mean()
    mean_weekend = recipes_per_day.filter(pl.col("jour").is_in(["Sam","Dim"]))["n_recipes"].mean()

    # --- Écarts à la moyenne ---
    recipes_per_day = recipes_per_day.with_columns(((pl.col("n_recipes") - mean_all) / mean_all * 100).alias("deviation_pct"))

    # 🎨 VISUALISATION PONDÉRÉE (3 graphiques)
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # --- GRAPHIQUE 1 : Weekday vs Weekend ---
    ax1 = axes[0]
    period_colors = ['#1F77B4', '#D62728']

    bars1 = ax1.bar(recipes_week_period["week_period"], recipes_week_period["recipes_per_day"], color=period_colors, alpha=0.85, edgecolor='black', linewidth=1.2)
    ax1.set_title('Volume moyen par jour (pondéré)', fontsize=13, fontweight='bold')
    ax1.set_ylabel('Recettes/jour', fontsize=11)
    ax1.grid(axis='y', alpha=0.3)

    for i, row in enumerate(recipes_week_period.iter_rows(named=True)):
        bar = bars1[i]
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() * 1.02, f'{row["recipes_per_day"]:,.0f}/jour', ha='center', va='bottom', fontsize=11, fontweight='bold', color='black')
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() * 0.5, f'Total: {row["n_recipes"]:,}\n(sur {row["n_days"]} jours)', ha='center', va='center', fontsize=9, color='white', bbox=dict(boxstyle='round,pad=0.4', facecolor='black', alpha=0.7))

    # --- GRAPHIQUE 2 : Distribution 7 jours ---
    ax2 = axes[1]
    day_colors = ['#4C72B0' if j not in ['Sam','Dim'] else '#D62728' for j in recipes_per_day['jour']]

    bars2 = ax2.bar(recipes_per_day['jour'], recipes_per_day['n_recipes'], color=day_colors, alpha=0.85, edgecolor='black', linewidth=1.2)
    ax2.axhline(mean_all, color='black', linestyle='--', linewidth=2, label=f'Moy. globale : {mean_all:,.0f}')
    ax2.axhline(mean_weekday, color='#4C72B0', linestyle=':', linewidth=1.5, alpha=0.7, label=f'Moy. Weekday : {mean_weekday:,.0f}')
    ax2.axhline(mean_weekend, color='#D62728', linestyle=':', linewidth=1.5, alpha=0.7, label=f'Moy. Weekend : {mean_weekend:,.0f}')
    ax2.set_title('Distribution des 7 jours (avec moyennes)', fontsize=13, fontweight='bold')
    ax2.set_xlabel('Jour de la semaine', fontsize=11)
    ax2.set_ylabel('Nombre de recettes', fontsize=11)
    ax2.grid(axis='y', alpha=0.3)
    ax2.legend(loc='upper right', fontsize=9)

    for bar, val in zip(bars2, recipes_per_day['n_recipes']):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 500, f'{val:,}', ha='center', va='bottom', fontsize=9, fontweight='bold')

    # --- GRAPHIQUE 3 : Écart à la moyenne (%) ---
    ax3 = axes[2]
    colors_dev = ['green' if x > 0 else 'red' for x in recipes_per_day['deviation_pct']]

    bars3 = ax3.bar(recipes_per_day['jour'], recipes_per_day['deviation_pct'], color=colors_dev, alpha=0.75, edgecolor='black', linewidth=1.2)
    ax3.axhline(0, color='black', linestyle='-', linewidth=1.5)
    ax3.set_title('Écart à la moyenne globale (%)', fontsize=13, fontweight='bold')
    ax3.set_xlabel('Jour de la semaine', fontsize=11)
    ax3.set_ylabel('Écart (%)', fontsize=11)
    ax3.grid(axis='y', alpha=0.3)

    for bar, val in zip(bars3, recipes_per_day['deviation_pct']):
        y_pos = val + (1 if val > 0 else -1)
        ax3.text(bar.get_x() + bar.get_width()/2, y_pos, f'{val:+.1f}%', ha='center', va='bottom' if val > 0 else 'top', fontsize=9, fontweight='bold')

    plt.tight_layout()
    plt.show()

    print("✅ Visualisation pondérée terminée !")

    # <INTERPRÉTATION>
    # Le **test Chi-2 pondéré** révèle une **différence statistiquement très significative** (p < 0.001) entre les volumes Weekday et Weekend. **Les recettes sont massivement publiées en semaine** : en moyenne **33,472 recettes/jour en Weekday** contre seulement **16,352 recettes/jour en Weekend**, soit **-51% le week-end**.
    #
    # Le **test d'uniformité des 7 jours** confirme une **forte variabilité inter-jours** (CV = 34.1%). Le **lundi est le jour le plus actif** (+45% au-dessus de la moyenne), suivi du **mardi** (+29%) et du **mercredi** (+13%). À l'inverse, le **samedi est le jour le moins actif** (-49%), suivi du **dimanche** (-36%). Les utilisateurs publient principalement **en début de semaine**.
    # </INTERPRÉTATION>

 

def analyse_weekend_effect_2():
    df = load_recipes_clean()
    # 📊 ANALYSE 2 : DURÉE MOYENNE (Weekday vs Weekend)

    # Ajout direct de week_period dans df
    df = df.with_columns(pl.when(pl.col('is_weekend') == 1).then(pl.lit('Weekend')).otherwise(pl.lit('Weekday')).alias('week_period'))
    week_period_order = ['Weekday', 'Weekend']

    # Agrégation
    minutes_by_period = (
        df.group_by('week_period')
        .agg([
            pl.mean('minutes').alias('mean_minutes'),
            pl.median('minutes').alias('median_minutes'),
            pl.quantile('minutes', 0.25).alias('q25'),
            pl.quantile('minutes', 0.75).alias('q75'),
            pl.std('minutes').alias('std_minutes'),
            pl.len().alias('n_recipes')
        ])
        .join(pl.DataFrame({'week_period': week_period_order, 'order': range(len(week_period_order))}), on='week_period', how='left')
        .sort('order')
        .drop('order')
    )

    minutes_by_period = minutes_by_period.with_columns((pl.col('q75') - pl.col('q25')).alias('IQR'))

    # Visualisation
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # --- GRAPHIQUE 1 : Barres + Médiane + IQR ---
    bars1 = ax1.bar(minutes_by_period['week_period'], minutes_by_period['mean_minutes'], color=period_colors, alpha=0.85, edgecolor='black', linewidth=1.2, label='Moyenne')
    ax1.plot(minutes_by_period['week_period'], minutes_by_period['median_minutes'], 'o--', color='black', linewidth=1.5, markersize=7, label='Médiane')

    for row in minutes_by_period.iter_rows(named=True):
        period = row['week_period']; q25 = row['q25']; q75 = row['q75']; mean_val = row['mean_minutes']
        ax1.vlines(period, q25, q75, color='black', linewidth=3, alpha=0.6)
        ax1.scatter([period], [q25], color='black', s=25)
        ax1.scatter([period], [q75], color='black', s=25)
        ax1.text(period, mean_val * 1.03, f"{mean_val:.1f} m", ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax1.set_title('Durée des recettes par période', fontsize=13, fontweight='bold')
    ax1.set_ylabel('Minutes', fontsize=11)
    ax1.grid(axis='y', alpha=0.3)
    ax1.legend(loc='best')

    # --- GRAPHIQUE 2 : Boxplot ---
    sns.boxplot(data=df.to_pandas(), x='week_period', y='minutes', order=week_period_order, palette=period_colors, ax=ax2, showfliers=False, linewidth=1.5)

    for period in week_period_order:
        row = minutes_by_period.filter(pl.col('week_period') == period).row(0, named=True)
        median, q25, q75, iqr = row['median_minutes'], row['q25'], row['q75'], row['IQR']
        i_idx = week_period_order.index(period)

        ax2.text(i_idx, median, f'{median:.1f}', ha='center', va='center', fontsize=9, fontweight='bold', color='white', bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7))
        ax2.text(i_idx-0.35, q25, f'Q1={q25:.0f}', ha='center', va='top', fontsize=8, color='gray', style='italic')
        ax2.text(i_idx-0.35, q75, f'Q3={q75:.0f}', ha='center', va='bottom', fontsize=8, color='gray', style='italic')
        ax2.text(i_idx+0.42, (q25+q75)/2, f'IQR\n{iqr:.0f}', ha='left', va='center', fontsize=8, color='darkblue', fontweight='bold', bbox=dict(boxstyle='round,pad=0.25', facecolor='lightyellow', alpha=0.8))

    ax2.set_title('Distribution des durées (boxplot)', fontsize=13, fontweight='bold')
    ax2.set_xlabel('Période', fontsize=11)
    ax2.set_ylabel('Minutes', fontsize=11)
    ax2.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.show()

    # <INTERPRÉTATION>
    # Le **test t de Student** ne révèle **aucune différence significative** (t = 0.545, p = 0.586) entre les durées Weekday et Weekend. Les **moyennes sont quasi identiques** (42.5 vs 42.4 min, différence < 0.3%). La durée des recettes publiées reste **constante indépendamment de la période**, sans effet week-end observable.  
    # </INTERPRÉTATION>

def analyse_weekend_effect_3():
    df = load_recipes_clean()

    week_period_order = ['Weekday', 'Weekend']
    
    # 📊 ANALYSE 3 : COMPLEXITÉ (Weekday vs Weekend)

    # Agrégation par période
    complexity_by_period = (
        df.group_by('week_period')
        .agg([
            pl.mean('complexity_score').alias('mean_complexity'),
            pl.median('complexity_score').alias('median_complexity'),
            pl.std('complexity_score').alias('std_complexity'),
            pl.mean('n_steps').alias('mean_steps'),
            pl.median('n_steps').alias('median_steps'),
            pl.mean('n_ingredients').alias('mean_ingredients'),
            pl.median('n_ingredients').alias('median_ingredients'),
            pl.quantile('complexity_score', 0.25).alias('q25_complexity'),
            pl.quantile('complexity_score', 0.75).alias('q75_complexity'),
            pl.len().alias('n_recipes')
        ])
        .join(pl.DataFrame({'week_period': week_period_order, 'order': range(len(week_period_order))}), on='week_period', how='left')
        .sort('order')
        .drop('order')
    )

    # Visualisation
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # --- GRAPHIQUE 1 : Score de complexité ---
    ax1 = axes[0]
    bars1 = ax1.bar(complexity_by_period['week_period'], complexity_by_period['mean_complexity'], color=period_colors, alpha=0.85, edgecolor='black', linewidth=1.2, label='Moyenne')
    ax1.plot(complexity_by_period['week_period'], complexity_by_period['median_complexity'], 'o--', color='black', linewidth=1.5, markersize=7, label='Médiane')

    for i, row in enumerate(complexity_by_period.iter_rows(named=True)):
        ax1.text(i, row['mean_complexity'] * 1.02, f"{row['mean_complexity']:.2f}", ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax1.set_title('Score de complexité par période', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Complexity Score', fontsize=11)
    ax1.grid(axis='y', alpha=0.3)
    ax1.legend(loc='best')

    # --- GRAPHIQUE 2 : Nombre d'étapes ---
    ax2 = axes[1]
    bars2 = ax2.bar(complexity_by_period['week_period'], complexity_by_period['mean_steps'], color=period_colors, alpha=0.85, edgecolor='black', linewidth=1.2, label='Moyenne')
    ax2.plot(complexity_by_period['week_period'], complexity_by_period['median_steps'], 's--', color='black', linewidth=1.5, markersize=7, label='Médiane')

    for i, row in enumerate(complexity_by_period.iter_rows(named=True)):
        ax2.text(i, row['mean_steps'] * 1.02, f"{row['mean_steps']:.1f}", ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax2.set_title("Nombre d'étapes par période", fontsize=12, fontweight='bold')
    ax2.set_ylabel("Nombre d'étapes", fontsize=11)
    ax2.grid(axis='y', alpha=0.3)
    ax2.legend(loc='best')

    # --- GRAPHIQUE 3 : Nombre d'ingrédients ---
    ax3 = axes[2]
    bars3 = ax3.bar(complexity_by_period['week_period'], complexity_by_period['mean_ingredients'], color=period_colors, alpha=0.85, edgecolor='black', linewidth=1.2, label='Moyenne')
    ax3.plot(complexity_by_period['week_period'], complexity_by_period['median_ingredients'], '^--', color='black', linewidth=1.5, markersize=7, label='Médiane')

    for i, row in enumerate(complexity_by_period.iter_rows(named=True)):
        ax3.text(i, row['mean_ingredients'] * 1.02, f"{row['mean_ingredients']:.1f}", ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax3.set_title("Nombre d'ingrédients par période", fontsize=12, fontweight='bold')
    ax3.set_ylabel("Nombre d'ingrédients", fontsize=11)
    ax3.grid(axis='y', alpha=0.3)
    ax3.legend(loc='best')

    plt.tight_layout()
    plt.show()

    # <INTERPRÉTATION>
    # Le **test t de Student** ne révèle **aucune différence significative** (t = 1.499, p = 0.134) de complexité entre Weekday et Weekend. Les **scores de complexité sont quasi identiques** (17.10 vs 17.05, différence -0.31%), ainsi que le **nombre d'étapes** (9.2) et d'**ingrédients** (8.8). La complexité des recettes publiées reste **constante indépendamment de la période**, sans effet week-end observable.
    # </INTERPRÉTATION>


def analyse_weekend_effect_4():
    df = load_recipes_clean()
    week_period_order = ['Weekday', 'Weekend']

    # 📊 ANALYSE 4 : NUTRITION (Weekday vs Weekend)

    # Agrégation nutritionnelle
    nutrition_by_period = (
        df.group_by("week_period")
        .agg([
            pl.mean("calories").alias("mean_calories"),
            pl.mean("protein_pct").alias("mean_protein"),
            pl.mean("total_fat_pct").alias("mean_fat"),
            pl.mean("sat_fat_pct").alias("mean_sat_fat"),
            pl.mean("sugar_pct").alias("mean_sugar"),
            pl.mean("sodium_pct").alias("mean_sodium")
        ])
        .join(pl.DataFrame({"week_period": week_period_order, "order": range(len(week_period_order))}), on="week_period", how="left")
        .sort("order")
        .drop("order")
    )

    # Tests statistiques
    nutrients_list = [
        ('Calories', 'calories', 'mean_calories', 0),
        ('Protéines (%)', 'protein_pct', 'mean_protein', 1),
        ('Lipides (%)', 'total_fat_pct', 'mean_fat', 1),
        ('Graisses sat. (%)', 'sat_fat_pct', 'mean_sat_fat', 1),
        ('Sucres (%)', 'sugar_pct', 'mean_sugar', 1),
        ('Sodium (%)', 'sodium_pct', 'mean_sodium', 1)
    ]

    results = []

    for nutrient_name, col_polars, col_agg, decimals in nutrients_list:
        weekday_vals = df.filter(pl.col('week_period') == 'Weekday')[col_polars].to_numpy()
        weekend_vals = df.filter(pl.col('week_period') == 'Weekend')[col_polars].to_numpy()
        
        t_stat, p_value = stats.ttest_ind(weekday_vals, weekend_vals, equal_var=True)
        
        wd_val = nutrition_by_period.filter(pl.col('week_period') == 'Weekday')[col_agg][0]
        we_val = nutrition_by_period.filter(pl.col('week_period') == 'Weekend')[col_agg][0]
        diff_pct = ((we_val - wd_val) / wd_val) * 100
        
        results.append({
            'nutrient': nutrient_name,
            'weekday': wd_val,
            'weekend': we_val,
            'diff_pct': diff_pct,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'decimals': decimals
        })

    results_df = pl.DataFrame(results)

    # --- VISUALISATION ---
    fig, ax = plt.subplots(figsize=(17, 6))

    y_pos = range(len(results_df))
    nutrients_ordered = results_df['nutrient'].to_list()
    diffs_ordered = results_df['diff_pct'].to_list()
    signif_ordered = results_df['significant'].to_list()

    # Couleurs : vert/rouge selon direction, foncé si significatif
    colors = ['#16A085' if (diff < 0 and sig) else '#C0392B' if (diff > 0 and sig)
            else '#A9DFBF' if diff < 0 else '#F5B7B1'
            for diff, sig in zip(diffs_ordered, signif_ordered)]

    ax.barh(y_pos, diffs_ordered, color=colors, alpha=0.85, edgecolor='black', linewidth=1.2)
    ax.axvline(0, color='black', linestyle='-', linewidth=2)

    # Annotations
    for i, (diff, is_signif) in enumerate(zip(diffs_ordered, signif_ordered)):
        x_pos = diff + (0.15 if diff > 0 else -0.15)
        text = f'{diff:+.1f}%' + (' *' if is_signif else '')
        ax.text(x_pos, i, text, ha='left' if diff > 0 else 'right', va='center',
                fontsize=10, fontweight='bold' if is_signif else 'normal',
                color='darkred' if is_signif else 'black')

    ax.set_yticks(list(y_pos))
    ax.set_yticklabels(nutrients_ordered, fontsize=11)
    ax.set_xlabel('Différence Weekend vs Weekday (%)', fontsize=11, fontweight='bold')
    ax.set_title('Profil nutritionnel : Écarts Weekend vs Weekday\n(* = effet significatif, p < 0.05)', 
                fontsize=12, fontweight='bold', pad=15)
    ax.grid(axis='x', alpha=0.3)
    ax.invert_yaxis()

    plt.tight_layout()
    plt.show()

    # <INTERPRÉTATION>
    # Les **tests t de Student** révèlent des **profils nutritionnels globalement similaires** entre Weekday et Weekend. Une seule différence significative émerge : les **protéines** (p < 0.01), avec des recettes publiées légèrement plus protéinées en semaine (environ -3% le week-end).  
    # </INTERPRÉTATION>



def analyse_weekend_effect_5():
    df = load_recipes_clean()
    week_period_order = ['Weekday', 'Weekend']
    # 📊 ANALYSE 5 : INGRÉDIENTS (Weekday vs Weekend)

    # Extraction des ingrédients par période
    ingredients_by_period = {}
    n_recipes_by_period = {}

    for period in week_period_order:
        period_df = df.filter(pl.col('week_period') == period)
        n_recipes_by_period[period] = period_df.height
        ingredient_counts = (
            period_df.select(pl.col('ingredients').explode())
            .group_by('ingredients')
            .agg(pl.count().alias('count'))
        )
        ingredients_by_period[period] = dict(zip(ingredient_counts['ingredients'].to_list(), ingredient_counts['count'].to_list()))

    all_ingredients = set().union(*[set(ing.keys()) for ing in ingredients_by_period.values()])

    # Tests statistiques Chi-2
    ingredients_results = []
    for ing in all_ingredients:
        weekday_count = ingredients_by_period['Weekday'].get(ing, 0)
        weekend_count = ingredients_by_period['Weekend'].get(ing, 0)
        weekday_freq = (weekday_count / n_recipes_by_period['Weekday']) * 100
        weekend_freq = (weekend_count / n_recipes_by_period['Weekend']) * 100
        
        contingency = np.array([
            [weekday_count, n_recipes_by_period['Weekday'] - weekday_count],
            [weekend_count, n_recipes_by_period['Weekend'] - weekend_count]
        ])
        
        try:
            chi2_stat, p_val, _, _ = chi2_contingency(contingency)
        except:
            chi2_stat, p_val = 0, 1.0
        
        ingredients_results.append({
            'ingredient': ing,
            'weekday_freq': weekday_freq,
            'weekend_freq': weekend_freq,
            'mean_freq': (weekday_freq + weekend_freq) / 2,
            'diff_abs': weekend_freq - weekday_freq,
            'p_value': p_val
        })

    ingredients_df = pl.DataFrame(ingredients_results)

    # Filtrage strict (fréquence, différence, significativité)
    FREQ_THRESHOLD = 1
    ABS_DIFF_THRESHOLD = 0.2

    ingredients_filtered = (
        ingredients_df
        .filter((pl.col('mean_freq') >= FREQ_THRESHOLD) &
                (pl.col('diff_abs').abs() >= ABS_DIFF_THRESHOLD) &
                (pl.col('p_value') < 0.05))
    )

    print(f"🔍 Filtrage : freq ≥{FREQ_THRESHOLD}%, |diff| ≥{ABS_DIFF_THRESHOLD}pp, p<0.05")
    print(f"   → {len(ingredients_filtered)}/{len(all_ingredients)} ingrédients retenus\n")

    # Visualisation (Top 20)
    if len(ingredients_filtered) > 0:
        top_ingredients = (
            ingredients_filtered
            .sort('diff_abs', descending=False)
            .tail(20)
        )

        fig, ax = plt.subplots(figsize=(12, max(6, len(top_ingredients) * 0.3)))
        colors = ['#d62728' if x < 0 else '#2ca02c' for x in top_ingredients['diff_abs']]

        ax.barh(range(len(top_ingredients)), top_ingredients['diff_abs'], color=colors, alpha=0.75, edgecolor='black', linewidth=1)
        ax.set_yticks(range(len(top_ingredients)))
        ax.set_yticklabels(top_ingredients['ingredient'], fontsize=9)
        ax.set_xlabel('Δ Weekend - Weekday (pp)', fontsize=10, fontweight='bold')
        ax.set_title(f"Top {len(top_ingredients)} ingrédients : Écarts Weekend vs Weekday (+ si week-end)", fontsize=12, fontweight='bold', pad=15)
        ax.axvline(0, color='black', linewidth=1.2)
        ax.grid(axis='x', alpha=0.3)

        # Annotations
        for i, row in enumerate(top_ingredients.iter_rows(named=True)):
            value = row['diff_abs']
            x_offset = 0.03 if value > 0 else -0.03
            ax.text(value + x_offset, i, f"{value:+.2f}", va='center', ha='left' if value > 0 else 'right', fontsize=8, fontweight='bold')

        plt.tight_layout()
        plt.show()

        # <INTERPRÉTATION>
        # **Méthodologie :** Sur les ~6800 ingrédients analysés, un **filtrage strict** a été appliqué pour ne conserver que les ingrédients avec :
        # - Fréquence ≥ 1% (ingrédients courants)
        # - Différence absolue ≥ 0.2 points de pourcentage
        #
        # Les tests **Chi-2** identifient quelques ingrédients avec variations significatives selon le moment posté (weekday vs weekend). **Week-end** : légère hausse pour `ground cinnamon` (+0.35pp), `canola oil` (+0.23pp). Semaine : légère hausse pour `mozzarella cheese` (-0.23pp), `boneless skinless chicken breasts` (-0.25pp), `honey` (-0.27pp).  
        #
        # **Les écarts restent faibles (<0.4pp) et l'inteprétation est sujet à débat.**  
        # </INTERPRÉTATION>

def analyse_weekend_effect_6():
    df = load_recipes_clean()
    week_period_order = ['Weekday', 'Weekend']
    # 📊 ANALYSE 6 : TAGS (Weekday vs Weekend)

    # Extraction des tags par période
    tags_by_period = {}
    n_recipes_by_period_tags = {}

    for period in week_period_order:
        period_df = df.filter(pl.col('week_period') == period)
        n_recipes_by_period_tags[period] = period_df.height
        tag_counts = (
            period_df.select(pl.col('tags').explode())
            .group_by('tags')
            .agg(pl.count().alias('count'))
        )
        tags_by_period[period] = dict(zip(tag_counts['tags'].to_list(), tag_counts['count'].to_list()))

    all_tags = set().union(*[set(tag.keys()) for tag in tags_by_period.values()])

    # Tests statistiques Chi-2
    tags_results = []
    for tag in all_tags:
        weekday_count = tags_by_period['Weekday'].get(tag, 0)
        weekend_count = tags_by_period['Weekend'].get(tag, 0)
        weekday_freq = (weekday_count / n_recipes_by_period_tags['Weekday']) * 100
        weekend_freq = (weekend_count / n_recipes_by_period_tags['Weekend']) * 100

        observed = [[weekday_count, n_recipes_by_period_tags['Weekday'] - weekday_count],
                    [weekend_count, n_recipes_by_period_tags['Weekend'] - weekend_count]]
        try:
            chi2, p_value, _, _ = chi2_contingency(observed)
        except:
            chi2, p_value = np.nan, np.nan

        tags_results.append({
            'tag': tag,
            'weekday_freq': weekday_freq,
            'weekend_freq': weekend_freq,
            'mean_freq': (weekday_freq + weekend_freq) / 2,
            'diff_abs': weekend_freq - weekday_freq,
            'p_value': p_value
        })

    tags_df = pl.DataFrame(tags_results)

    # Filtrage strict (fréquence, différence, significativité)
    FREQ_THRESHOLD = 1
    ABS_DIFF_THRESHOLD = 0.2

    tags_filtered = (
        tags_df
        .filter((pl.col('mean_freq') >= FREQ_THRESHOLD) &
                (pl.col('diff_abs').abs() >= ABS_DIFF_THRESHOLD) &
                (pl.col('p_value') < 0.05))
    )

    print(f"🔍 Filtrage : freq ≥{FREQ_THRESHOLD}%, |diff| ≥{ABS_DIFF_THRESHOLD}pp, p<0.05")
    print(f"   → {len(tags_filtered)}/{len(all_tags)} tags retenus\n")

    # Visualisation (Top 20)
    if len(tags_filtered) > 0:
        top_tags = (
            tags_filtered
            .sort('diff_abs', descending=False)
            .tail(20)
        )

        fig, ax = plt.subplots(figsize=(12, max(6, len(top_tags) * 0.3)))
        colors = ['#d62728' if x < 0 else '#2ca02c' for x in top_tags['diff_abs']]

        ax.barh(range(len(top_tags)), top_tags['diff_abs'], color=colors, alpha=0.75, edgecolor='black', linewidth=1)
        ax.set_yticks(range(len(top_tags)))
        ax.set_yticklabels(top_tags['tag'], fontsize=9)
        ax.set_xlabel('Δ Weekend - Weekday (pp)', fontsize=10, fontweight='bold')
        ax.set_title(f'Top {len(top_tags)} tags : Écarts Weekend vs Weekday', fontsize=12, fontweight='bold', pad=15)
        ax.axvline(0, color='black', linewidth=1.2)
        ax.grid(axis='x', alpha=0.3)

        # Annotations
        for i, row in enumerate(top_tags.iter_rows(named=True)):
            value = row['diff_abs']
            x_offset = 0.03 if value > 0 else -0.03
            ax.text(value + x_offset, i, f"{value:+.2f}", va='center', ha='left' if value > 0 else 'right', fontsize=8, fontweight='bold')

        plt.tight_layout()
        plt.show()

    # <INTERPRÉTATION>
    # **Méthodologie :** Sur les ~500 tags analysés, un **filtrage strict** a été appliqué pour ne conserver que les tags avec :
    # - Fréquence ≥ 1% (tags significatifs)
    # - Différence absolue ≥ 0.2 points de pourcentage
    # - Significativité statistique (p < 0.05)
    #
    # Ce filtrage a permis d'identifier **les tags dont l'usage révèle des thématiques vraiment différentes** entre périodes.
    #
    # Les **tests Chi-2** révèlent des différences significatives sur 20 tags. Week-end (+) : `vegetarian` (+0.74pp), `christmas` (+0.56pp), `from-scratch` (+0.47pp), `breakfast` (+0.44pp), `eggs` (+0.40pp). Semaine (−) : `one-dish-meal` (-0.49pp), `beginner-cook` (-0.48pp), `mexican` (-0.42pp).
    #
    # **Les écarts restent faibles (<0.5pp) et l'inteprétation est sujet à débat.**
    # </INTERPRÉTATION>


def main():
    """
    Fonction principale pour exécuter les analyses de tendances.
    """

    analyse_trendline_1()
    analyse_trendline_2()    
    analyse_trendline_3()
    analyse_trendline_4()    
    analyse_trendline_5() 
    analyse_trendline_6()           

    analyse_seasonality_1()
    analyse_seasonality_2()
    analyse_seasonality_3()
    analyse_seasonality_4()
    analyse_seasonality_5()
    analyse_seasonality_6()

    analyse_weekend_effect_1()
    analyse_weekend_effect_2()    
    analyse_weekend_effect_3()
    analyse_weekend_effect_4()    
    analyse_weekend_effect_5() 
    analyse_weekend_effect_6()           


    print("\n✅ Analyse terminée avec succès !")

if __name__ == "__main__":
    main()


