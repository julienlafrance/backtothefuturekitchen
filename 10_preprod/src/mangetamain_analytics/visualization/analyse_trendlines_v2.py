"""Module d'analyse des tendances temporelles des recettes Food.com.

Analyse l'évolution des recettes entre 1999 et 2018.
Conversion propre Matplotlib → Plotly Express selon guide pratique.
"""

import warnings
import numpy as np
import polars as pl
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
import statsmodels.api as sm
import streamlit as st
import matplotlib.cm as cm
import matplotlib.colors as mcolors

from mangetamain_data_utils.data_utils_recipes import load_recipes_clean

warnings.filterwarnings("ignore")


# ============================================================================
# FONCTIONS DE CHARGEMENT AVEC CACHE
# ============================================================================

@st.cache_data
def load_and_prepare_data():
    """Charge et prépare les données depuis S3 (avec cache Streamlit)."""
    df = load_recipes_clean()
    # Ajouter complexity_score si nécessaire
    if "complexity_score" not in df.columns:
        df = df.with_columns(
            (
                (pl.col("n_steps") / pl.col("n_steps").max())
                + (pl.col("n_ingredients") / pl.col("n_ingredients").max())
            ).alias("complexity_score")
        )
    return df


# ============================================================================
# ANALYSE 1: VOLUME DE RECETTES
# ============================================================================

def analyse_trendline_volume():
    """Analyse du volume de recettes par année avec Q-Q plot."""
    df = load_and_prepare_data()

    # Agrégation
    recipes_per_year = (
        df.group_by("year")
        .agg(pl.len().alias("n_recipes"))
        .sort("year")
        .to_pandas()
    )

    # Données pour Q-Q plot
    data = recipes_per_year["n_recipes"].values

    # Calcul Q-Q plot
    (osm, osr), (slope, intercept, r) = stats.probplot(data, dist="norm")

    # Créer subplots
    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Nombre de recettes par année", "Q-Q Plot (Test de normalité)"),
    )

    # SUBPLOT 1: Bar chart
    fig.add_trace(
        go.Bar(
            x=recipes_per_year["year"].astype(int),
            y=recipes_per_year["n_recipes"],
            marker=dict(color="steelblue", opacity=0.8),
            text=[f"{val:,}" for val in recipes_per_year["n_recipes"]],
            textposition="outside",
            showlegend=False,
        ),
        row=1,
        col=1,
    )

    # SUBPLOT 2: Q-Q plot - Points
    fig.add_trace(
        go.Scatter(
            x=osm,
            y=osr,
            mode="markers",
            marker=dict(color="steelblue", size=6),
            name="Observations",
            showlegend=False,
        ),
        row=1,
        col=2,
    )

    # SUBPLOT 2: Q-Q plot - Ligne de référence
    fig.add_trace(
        go.Scatter(
            x=[osm.min(), osm.max()],
            y=[slope * osm.min() + intercept, slope * osm.max() + intercept],
            mode="lines",
            line=dict(color="red", dash="dash", width=2),
            name="Loi normale",
            showlegend=False,
        ),
        row=1,
        col=2,
    )

    # Mise en forme des axes
    fig.update_xaxes(
        title_text="Année",
        tickvals=recipes_per_year["year"].astype(int),
        tickangle=45,
        showgrid=True,
        gridcolor="#e0e0e0",
        gridwidth=1,
        row=1,
        col=1,
    )
    fig.update_yaxes(
        title_text="Nombre de recettes",
        showgrid=True,
        gridcolor="#e0e0e0",
        gridwidth=1,
        row=1,
        col=1,
    )
    fig.update_xaxes(
        title_text="Quantiles théoriques (loi normale)",
        showgrid=True,
        gridcolor="#e0e0e0",
        gridwidth=1,
        row=1,
        col=2,
    )
    fig.update_yaxes(
        title_text="Quantiles observés",
        showgrid=True,
        gridcolor="#e0e0e0",
        gridwidth=1,
        row=1,
        col=2,
    )

    # Layout global
    fig.update_layout(
        height=500,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(size=12),
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True)

    # Interprétation
    st.info(
        "📊 **Interprétation**: Nous observons une **forte augmentation du nombre de recettes postées jusqu'en 2007**, "
        "année du **pic d'activité**, suivie d'une **chute marquée** les années suivantes. "
        "Les **tests de normalité** et les **Q-Q plots** montrent que la distribution du **nombre de recettes par an** "
        "**n'est pas parfaitement normale**, avec des **écarts visibles** par rapport à la **loi normale théorique**."
    )


# ============================================================================
# ANALYSE 2: DURÉE DE PRÉPARATION
# ============================================================================

def analyse_trendline_duree():
    """Analyse de l'évolution de la durée de préparation."""
    df = load_and_prepare_data()

    # Agrégation
    minutes_by_year = (
        df.group_by("year")
        .agg(
            [
                pl.mean("minutes").alias("mean_minutes"),
                pl.median("minutes").alias("median_minutes"),
                pl.quantile("minutes", 0.25).alias("q25"),
                pl.quantile("minutes", 0.75).alias("q75"),
                pl.len().alias("n_recipes"),
            ]
        )
        .sort("year")
        .to_pandas()
    )

    # Calcul des régressions WLS
    X = minutes_by_year["year"].values
    w = minutes_by_year["n_recipes"].values

    regressions = {}
    for metric_col in ["mean_minutes", "median_minutes"]:
        y = minutes_by_year[metric_col].values
        X_const = sm.add_constant(X)
        wls_model = sm.WLS(y, X_const, weights=w)
        wls_result = wls_model.fit()
        y_pred = wls_result.predict(X_const)
        r2_w = 1 - np.average((y - y_pred) ** 2, weights=w) / np.average(
            (y - np.average(y, weights=w)) ** 2, weights=w
        )

        regressions[metric_col] = {
            "y_pred": y_pred,
            "slope": wls_result.params[1],
            "r2": r2_w,
            "p_value": wls_result.pvalues[1],
        }

    # Tailles de bulles
    sizes = minutes_by_year["n_recipes"] / minutes_by_year["n_recipes"].max() * 20

    # Création du graphique avec Plotly
    fig = go.Figure()

    # IQR (intervalle interquartile) - zone grise
    fig.add_trace(
        go.Scatter(
            x=minutes_by_year["year"],
            y=minutes_by_year["q25"],
            fill=None,
            mode="lines",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=minutes_by_year["year"],
            y=minutes_by_year["q75"],
            fill="tonexty",
            mode="lines",
            line=dict(width=0),
            name="IQR (Q25-Q75)",
            fillcolor="rgba(200, 200, 200, 0.2)",
        )
    )

    # Moyenne observée (steelblue)
    fig.add_trace(
        go.Scatter(
            x=minutes_by_year["year"],
            y=minutes_by_year["mean_minutes"],
            mode="lines+markers",
            name="Moyenne (observée)",
            line=dict(color="#4682B4", width=2),
            marker=dict(size=sizes, color="#4682B4", opacity=0.6),
        )
    )

    # Régression moyenne (darkblue)
    fig.add_trace(
        go.Scatter(
            x=minutes_by_year["year"],
            y=regressions["mean_minutes"]["y_pred"],
            mode="lines",
            name=f"Régression Moyenne (R²={regressions['mean_minutes']['r2']:.3f})",
            line=dict(color="#00416A", width=2, dash="dash"),
        )
    )

    # Médiane observée (coral)
    fig.add_trace(
        go.Scatter(
            x=minutes_by_year["year"],
            y=minutes_by_year["median_minutes"],
            mode="lines+markers",
            name="Médiane (observée)",
            line=dict(color="#FF7F50", width=2),
            marker=dict(size=sizes, color="#FF7F50", opacity=0.6),
        )
    )

    # Régression médiane (darkred)
    fig.add_trace(
        go.Scatter(
            x=minutes_by_year["year"],
            y=regressions["median_minutes"]["y_pred"],
            mode="lines",
            name=f"Régression Médiane (R²={regressions['median_minutes']['r2']:.3f})",
            line=dict(color="#8B0000", width=2, dash="dash"),
        )
    )

    # Mise en forme
    fig.update_layout(
        title=f"Évolution de la durée de préparation<br><sub>Moyenne: {regressions['mean_minutes']['slope']:+.4f} min/an | Médiane: {regressions['median_minutes']['slope']:+.4f} min/an</sub>",
        xaxis_title="Année",
        yaxis_title="Minutes",
        height=600,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(size=12),
        hovermode="x unified",
        legend=dict(bgcolor="rgba(255, 255, 255, 0.9)", bordercolor="#ddd", borderwidth=1),
    )

    fig.update_xaxes(showgrid=True, gridcolor="#e0e0e0", gridwidth=1)
    fig.update_yaxes(showgrid=True, gridcolor="#e0e0e0", gridwidth=1)

    st.plotly_chart(fig, use_container_width=True)

    # Interprétation
    st.info(
        "⏱️ **Interprétation**: L'analyse de la durée moyenne de préparation montre une **tendance globale à la baisse** "
        f"depuis la création du site. En moyenne, le temps de préparation diminue d'environ "
        f"**{regressions['mean_minutes']['slope']:.2f} min/an**, tandis que la médiane recule de "
        f"**{regressions['median_minutes']['slope']:.2f} min/an**, ce qui traduit une "
        "**légère simplification des recettes** au fil du temps."
    )


# ============================================================================
# ANALYSE 3: COMPLEXITÉ
# ============================================================================

def analyse_trendline_complexite():
    """Analyse de l'évolution de la complexité des recettes."""
    df = load_and_prepare_data()

    # Agrégation
    complexity_by_year = (
        df.group_by("year")
        .agg(
            [
                pl.mean("complexity_score").alias("mean_complexity"),
                pl.mean("n_steps").alias("mean_steps"),
                pl.mean("n_ingredients").alias("mean_ingredients"),
                pl.std("complexity_score").alias("std_complexity"),
                pl.len().alias("count_recipes"),
            ]
        )
        .sort("year")
        .to_pandas()
    )

    # Calcul des régressions WLS
    X = complexity_by_year["year"].values
    w = complexity_by_year["count_recipes"].values

    metrics_config = {
        "mean_complexity": {
            "color": "#9370DB",
            "title": "Score de complexité",
            "ylabel": "Complexity Score",
            "show_std": True,
        },
        "mean_steps": {
            "color": "#FF8C00",
            "title": "Nombre d'étapes",
            "ylabel": "Nombre d'étapes",
            "show_std": False,
        },
        "mean_ingredients": {
            "color": "#2E8B57",
            "title": "Nombre d'ingrédients",
            "ylabel": "Nombre d'ingrédients",
            "show_std": False,
        },
    }

    regressions = {}
    for metric_col in metrics_config.keys():
        y = complexity_by_year[metric_col].values
        X_const = sm.add_constant(X)
        wls_model = sm.WLS(y, X_const, weights=w)
        wls_result = wls_model.fit()
        y_pred = wls_result.predict(X_const)
        r2_w = 1 - np.average((y - y_pred) ** 2, weights=w) / np.average(
            (y - np.average(y, weights=w)) ** 2, weights=w
        )

        regressions[metric_col] = {
            "y_pred": y_pred,
            "slope": wls_result.params[1],
            "r2": r2_w,
            "p_value": wls_result.pvalues[1],
        }

    # Tailles de bulles
    sizes = complexity_by_year["count_recipes"] / complexity_by_year["count_recipes"].max() * 20

    # Création du graphique avec subplots
    fig = make_subplots(
        rows=1,
        cols=3,
        subplot_titles=(
            f"{metrics_config['mean_complexity']['title']}<br>Pente: {regressions['mean_complexity']['slope']:+.4f}/an (p={regressions['mean_complexity']['p_value']:.2e})",
            f"{metrics_config['mean_steps']['title']}<br>Pente: {regressions['mean_steps']['slope']:+.4f}/an (p={regressions['mean_steps']['p_value']:.2e})",
            f"{metrics_config['mean_ingredients']['title']}<br>Pente: {regressions['mean_ingredients']['slope']:+.4f}/an (p={regressions['mean_ingredients']['p_value']:.2e})",
        ),
    )

    for idx, (metric_col, config) in enumerate(metrics_config.items(), 1):
        reg = regressions[metric_col]

        # Bande std pour complexity_score
        if config.get("show_std"):
            fig.add_trace(
                go.Scatter(
                    x=complexity_by_year["year"],
                    y=complexity_by_year["mean_complexity"]
                    - complexity_by_year["std_complexity"],
                    fill=None,
                    mode="lines",
                    line=dict(width=0),
                    showlegend=False,
                    hoverinfo="skip",
                ),
                row=1,
                col=idx,
            )
            fig.add_trace(
                go.Scatter(
                    x=complexity_by_year["year"],
                    y=complexity_by_year["mean_complexity"]
                    + complexity_by_year["std_complexity"],
                    fill="tonexty",
                    mode="lines",
                    line=dict(width=0),
                    name="±1 std",
                    fillcolor=f"rgba({int(config['color'][1:3], 16)}, {int(config['color'][3:5], 16)}, {int(config['color'][5:7], 16)}, 0.15)",
                    showlegend=(idx == 1),
                ),
                row=1,
                col=idx,
            )

        # Courbe observée
        fig.add_trace(
            go.Scatter(
                x=complexity_by_year["year"],
                y=complexity_by_year[metric_col],
                mode="lines+markers",
                name="Tendance observée",
                line=dict(color=config["color"], width=2),
                marker=dict(size=sizes, color=config["color"], opacity=0.6),
                showlegend=(idx == 1),
            ),
            row=1,
            col=idx,
        )

        # Régression
        fig.add_trace(
            go.Scatter(
                x=complexity_by_year["year"],
                y=reg["y_pred"],
                mode="lines",
                name=f"Régression WLS (R²={reg['r2']:.3f})",
                line=dict(color="#E94B3C", width=2, dash="dash"),
                showlegend=(idx == 1),
            ),
            row=1,
            col=idx,
        )

        # Axes
        fig.update_xaxes(
            title_text="Année",
            showgrid=True,
            gridcolor="#e0e0e0",
            gridwidth=1,
            row=1,
            col=idx,
        )
        fig.update_yaxes(
            title_text=config["ylabel"],
            showgrid=True,
            gridcolor="#e0e0e0",
            gridwidth=1,
            row=1,
            col=idx,
        )

    # Mise en forme
    fig.update_layout(
        height=500,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(size=12),
        hovermode="x unified",
    )

    st.plotly_chart(fig, use_container_width=True)

    # Interprétation
    st.info(
        "🔧 **Interprétation**: La **régression linéaire pondérée** met en évidence une **tendance significative à la hausse** "
        f"du **score moyen de complexité** (pente = **{regressions['mean_complexity']['slope']:+.4f}**, "
        f"R² = **{regressions['mean_complexity']['r2']:.2f}**, p = **{regressions['mean_complexity']['p_value']:.2e}**). "
        "Cette évolution indique une **augmentation progressive de la complexité des recettes** au fil du temps, "
        "suggérant des **préparations de plus en plus élaborées**. La tendance est **cohérente** avec l'augmentation "
        "du **nombre d'étapes** et du **nombre d'ingrédients**, confirmant une **complexification globale** des recettes publiées."
    )


# ============================================================================
# ANALYSE 4: NUTRITION
# ============================================================================

def analyse_trendline_nutrition():
    """Analyse de l'évolution des valeurs nutritionnelles."""
    df = load_and_prepare_data()

    # Agrégation
    nutrition_by_year = (
        df.group_by("year")
        .agg(
            [
                pl.mean("calories").alias("mean_calories"),
                pl.mean("carb_pct").alias("mean_carbs"),
                pl.mean("total_fat_pct").alias("mean_fat"),
                pl.mean("protein_pct").alias("mean_protein"),
                pl.len().alias("count_recipes"),
            ]
        )
        .sort("year")
        .to_pandas()
    )

    # Calcul des régressions WLS
    X_year = nutrition_by_year["year"].values
    w = nutrition_by_year["count_recipes"].values

    metrics_config = {
        "mean_calories": {
            "color": "#FF6347",
            "title": "Calories moyennes",
            "ylabel": "Calories",
        },
        "mean_carbs": {
            "color": "#4169E1",
            "title": "Glucides (%)",
            "ylabel": "Carbs %",
        },
        "mean_fat": {"color": "#FF8C00", "title": "Lipides (%)", "ylabel": "Fat %"},
        "mean_protein": {
            "color": "#2E8B57",
            "title": "Protéines (%)",
            "ylabel": "Protein %",
        },
    }

    regressions = {}
    for metric_col in metrics_config.keys():
        y = nutrition_by_year[metric_col].values
        X_const = sm.add_constant(X_year)
        wls_model = sm.WLS(y, X_const, weights=w)
        wls_result = wls_model.fit()
        y_pred = wls_result.predict(X_const)
        r2_w = 1 - np.average((y - y_pred) ** 2, weights=w) / np.average(
            (y - np.average(y, weights=w)) ** 2, weights=w
        )

        regressions[metric_col] = {
            "y_pred": y_pred,
            "slope": wls_result.params[1],
            "r2": r2_w,
            "p_value": wls_result.pvalues[1],
        }

    # Tailles de bulles
    sizes = nutrition_by_year["count_recipes"] / nutrition_by_year["count_recipes"].max() * 20

    # Création du graphique avec subplots
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=tuple(
            f"{config['title']}<br>Pente: {regressions[metric_col]['slope']:+.4f}/an (p={regressions[metric_col]['p_value']:.2e})"
            for metric_col, config in metrics_config.items()
        ),
    )

    positions = [(1, 1), (1, 2), (2, 1), (2, 2)]

    for (row, col), (metric_col, config) in zip(positions, metrics_config.items()):
        reg = regressions[metric_col]

        # Courbe observée
        fig.add_trace(
            go.Scatter(
                x=nutrition_by_year["year"],
                y=nutrition_by_year[metric_col],
                mode="lines+markers",
                name="Tendance observée",
                line=dict(color=config["color"], width=2),
                marker=dict(size=sizes, color=config["color"], opacity=0.6),
                showlegend=(row == 1 and col == 1),
            ),
            row=row,
            col=col,
        )

        # Régression
        fig.add_trace(
            go.Scatter(
                x=nutrition_by_year["year"],
                y=reg["y_pred"],
                mode="lines",
                name=f"Régression WLS (R²={reg['r2']:.3f})",
                line=dict(color="#E94B3C", width=2, dash="dash"),
                showlegend=(row == 1 and col == 1),
            ),
            row=row,
            col=col,
        )

        # Axes
        fig.update_xaxes(
            title_text="Année" if row == 2 else None,
            showgrid=True,
            gridcolor="#e0e0e0",
            gridwidth=1,
            row=row,
            col=col,
        )
        fig.update_yaxes(
            title_text=config["ylabel"],
            showgrid=True,
            gridcolor="#e0e0e0",
            gridwidth=1,
            row=row,
            col=col,
        )

    # Mise en forme
    fig.update_layout(
        height=800,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(size=12),
        hovermode="x unified",
    )

    st.plotly_chart(fig, use_container_width=True)

    # Interprétation
    st.info(
        "🥗 **Interprétation**: Les **régressions linéaires pondérées** montrent une **tendance significative à la baisse** "
        "des valeurs **nutritionnelles moyennes** au fil du temps. Les **calories**, **glucides**, **lipides** et **protéines** "
        "présentent toutes des **pentes négatives**, avec des **R² pondérés entre 0.39 et 0.56**, indiquant une "
        "**bonne part de variance expliquée** et une **diminution mesurable** des apports nutritionnels moyens par recette. "
        "Cette évolution traduit une **orientation progressive vers des recettes plus légères**, moins riches en **calories** "
        "et en **macronutriments**, reflétant probablement une **adaptation aux tendances alimentaires modernes** "
        "(recherche de plats plus équilibrés et moins énergétiques)."
    )


# ============================================================================
# ANALYSE 5: INGRÉDIENTS
# ============================================================================

def analyse_trendline_ingredients(top_n=10):
    """Analyse de l'évolution des ingrédients."""
    df = load_and_prepare_data()

    # Paramètres
    NORMALIZE = True
    MIN_TOTAL_OCC = 50
    TOP_N = top_n
    N_VARIATIONS = min(5, top_n)

    # Exploser et normaliser les ingrédients
    df_ingredients = (
        df.select(["id", "year", "ingredients"])
        .explode("ingredients")
        .with_columns(
            [pl.col("ingredients").str.to_lowercase().str.strip_chars().alias("ingredient_norm")]
        )
    )

    # Fréquence globale
    freq_global = (
        df_ingredients.group_by("ingredient_norm")
        .agg(pl.len().alias("total_count"))
        .filter(pl.col("total_count") >= MIN_TOTAL_OCC)
        .sort("total_count", descending=True)
        .to_pandas()
    )
    top_global = freq_global.head(TOP_N)

    # Fréquence par année
    freq_year_ing = (
        df_ingredients.group_by(["year", "ingredient_norm"])
        .agg(pl.len().alias("count"))
        .to_pandas()
    )

    year_totals = df.group_by("year").agg(pl.len().alias("n_recipes")).to_pandas()
    freq_year_ing = freq_year_ing.merge(year_totals, on="year", how="left")

    if NORMALIZE:
        freq_year_ing["freq"] = freq_year_ing["count"] / freq_year_ing["n_recipes"]
    else:
        freq_year_ing["freq"] = freq_year_ing["count"]

    # Calcul des variations
    min_year = int(df["year"].min())
    max_year = int(df["year"].max())

    first_year_vals = freq_year_ing[freq_year_ing["year"] == min_year][
        ["ingredient_norm", "freq"]
    ].rename(columns={"freq": "first"})
    last_year_vals = freq_year_ing[freq_year_ing["year"] == max_year][
        ["ingredient_norm", "freq"]
    ].rename(columns={"freq": "last"})

    variation = first_year_vals.merge(last_year_vals, on="ingredient_norm", how="outer").fillna(
        0
    )
    variation["delta"] = variation["last"] - variation["first"]
    variation = variation.merge(
        freq_global[["ingredient_norm", "total_count"]], on="ingredient_norm", how="left"
    )
    variation = variation[variation["total_count"] >= MIN_TOTAL_OCC]

    biggest_increase = variation.nlargest(TOP_N, "delta")
    biggest_decrease = variation.nsmallest(TOP_N, "delta")

    # Diversité
    unique_per_year = (
        df_ingredients.group_by("year")
        .agg(pl.n_unique("ingredient_norm").alias("n_unique"))
        .sort("year")
        .to_pandas()
    )

    # Création du graphique avec 6 subplots
    fig = make_subplots(
        rows=3,
        cols=2,
        subplot_titles=(
            f"Top {TOP_N} ingrédients les plus fréquents",
            "Évolution de la diversité des ingrédients",
            f"Top {TOP_N} hausses ({min_year}→{max_year})",
            f"Top {TOP_N} baisses ({min_year}→{max_year})",
            f"Évolution : Top {N_VARIATIONS} hausses",
            f"Évolution : Top {N_VARIATIONS} baisses",
        ),
        specs=[
            [{"type": "bar"}, {"type": "scatter"}],
            [{"type": "bar"}, {"type": "bar"}],
            [{"type": "scatter"}, {"type": "scatter"}],
        ],
    )

    # (1) Top 10 ingrédients
    fig.add_trace(
        go.Bar(
            y=top_global["ingredient_norm"],
            x=top_global["total_count"],
            orientation="h",
            marker=dict(color="#4682B4", opacity=0.8),
            showlegend=False,
        ),
        row=1,
        col=1,
    )

    # (2) Diversité
    w_div = year_totals["n_recipes"].values
    sizes_div = (w_div / w_div.max()) * 15

    fig.add_trace(
        go.Scatter(
            x=unique_per_year["year"],
            y=unique_per_year["n_unique"],
            mode="lines+markers",
            line=dict(color="#9370DB", width=2),
            marker=dict(size=sizes_div, color="#9370DB", opacity=0.6),
            showlegend=False,
        ),
        row=1,
        col=2,
    )

    # (3) Top hausses
    fig.add_trace(
        go.Bar(
            y=biggest_increase["ingredient_norm"],
            x=biggest_increase["delta"],
            orientation="h",
            marker=dict(color="#2E8B57", opacity=0.8),
            showlegend=False,
        ),
        row=2,
        col=1,
    )

    # (4) Top baisses
    fig.add_trace(
        go.Bar(
            y=biggest_decrease["ingredient_norm"],
            x=biggest_decrease["delta"],
            orientation="h",
            marker=dict(color="#E94B3C", opacity=0.8),
            showlegend=False,
        ),
        row=2,
        col=2,
    )

    # (5) Évolution hausses
    greens = cm.Greens(np.linspace(0.4, 0.9, N_VARIATIONS))
    for idx, (_, row_data) in enumerate(biggest_increase.head(N_VARIATIONS).iterrows()):
        ing = row_data["ingredient_norm"]
        data_ing = freq_year_ing[freq_year_ing["ingredient_norm"] == ing].sort_values("year")
        color = mcolors.rgb2hex(greens[idx])
        fig.add_trace(
            go.Scatter(
                x=data_ing["year"],
                y=data_ing["freq"],
                mode="lines+markers",
                name=ing,
                line=dict(color=color, width=2),
                marker=dict(size=6),
                showlegend=True,
                legendgroup="hausses",
            ),
            row=3,
            col=1,
        )

    # (6) Évolution baisses
    reds = cm.Reds(np.linspace(0.4, 0.9, N_VARIATIONS))
    for idx, (_, row_data) in enumerate(biggest_decrease.head(N_VARIATIONS).iterrows()):
        ing = row_data["ingredient_norm"]
        data_ing = freq_year_ing[freq_year_ing["ingredient_norm"] == ing].sort_values("year")
        color = mcolors.rgb2hex(reds[idx])
        fig.add_trace(
            go.Scatter(
                x=data_ing["year"],
                y=data_ing["freq"],
                mode="lines+markers",
                name=ing,
                line=dict(color=color, width=2),
                marker=dict(size=6),
                showlegend=True,
                legendgroup="baisses",
            ),
            row=3,
            col=2,
        )

    # Axes
    fig.update_xaxes(title_text="Occurrences totales", row=1, col=1)
    fig.update_yaxes(showgrid=True, gridcolor="#e0e0e0", row=1, col=1)

    fig.update_xaxes(
        title_text="Année", showgrid=True, gridcolor="#e0e0e0", row=1, col=2
    )
    fig.update_yaxes(
        title_text="Nombre d'ingrédients uniques",
        showgrid=True,
        gridcolor="#e0e0e0",
        row=1,
        col=2,
    )

    label_delta = "Variation (normalisée)" if NORMALIZE else "Variation (occurrences)"
    fig.update_xaxes(title_text=label_delta, row=2, col=1)
    fig.update_yaxes(showgrid=True, gridcolor="#e0e0e0", row=2, col=1)

    fig.update_xaxes(title_text=label_delta, row=2, col=2)
    fig.update_yaxes(showgrid=True, gridcolor="#e0e0e0", row=2, col=2)

    ylabel_freq = "Fréquence" if NORMALIZE else "Occurrences"
    fig.update_xaxes(
        title_text="Année", showgrid=True, gridcolor="#e0e0e0", row=3, col=1
    )
    fig.update_yaxes(
        title_text=ylabel_freq, showgrid=True, gridcolor="#e0e0e0", row=3, col=1
    )

    fig.update_xaxes(
        title_text="Année", showgrid=True, gridcolor="#e0e0e0", row=3, col=2
    )
    fig.update_yaxes(
        title_text=ylabel_freq, showgrid=True, gridcolor="#e0e0e0", row=3, col=2
    )

    # Mise en forme
    fig.update_layout(
        height=1200,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(size=11),
        showlegend=True,
    )

    st.plotly_chart(fig, use_container_width=True)

    # Interprétation
    st.info(
        "🥘 **Interprétation**: L'analyse révèle une **transformation profonde** de l'usage des ingrédients au fil du temps. "
        "**Tendances montantes**: Des ingrédients comme *kosher salt*, *garlic cloves*, *olive oil* et *unsalted butter* "
        "connaissent une forte progression, reflétant peut-être un virage vers une cuisine plus communautaire ou méditerranéenne. "
        "**Tendances descendantes**: Les ingrédients traditionnels comme *sugar*, *butter*, *eggs* et *vanilla* sont en net recul, "
        "suggérant une diminution des recettes de pâtisserie classique et une recherche de recettes moins sucrées. "
        "**Chute de la diversité**: Le nombre d'ingrédients uniques chute drastiquement, passant du maximum en début de période "
        "à un minimum en fin de période. Cette baisse significative s'explique par la diminution du volume de recettes postées "
        "après 2007, entraînant une concentration sur des ingrédients plus courants et une perte d'innovation culinaire."
    )


# ============================================================================
# ANALYSE 6: TAGS
# ============================================================================

def analyse_trendline_tags(top_n=10):
    """Analyse de l'évolution des tags."""
    df = load_and_prepare_data()

    # Paramètres
    NORMALIZE = True
    MIN_TOTAL_OCC = 50
    TOP_N = top_n
    N_VARIATIONS = min(5, top_n)

    # Exploser et normaliser les tags
    df_tags = (
        df.select(["id", "year", "tags"])
        .explode("tags")
        .with_columns([pl.col("tags").str.to_lowercase().str.strip_chars().alias("tag_norm")])
    )

    # Fréquence globale
    freq_global_tags = (
        df_tags.group_by("tag_norm")
        .agg(pl.len().alias("total_count"))
        .filter(pl.col("total_count") >= MIN_TOTAL_OCC)
        .sort("total_count", descending=True)
        .to_pandas()
    )
    top_global_tags = freq_global_tags.head(TOP_N)

    # Fréquence par année
    freq_year_tag = (
        df_tags.group_by(["year", "tag_norm"]).agg(pl.len().alias("count")).to_pandas()
    )

    year_totals_tags = df.group_by("year").agg(pl.len().alias("n_recipes")).to_pandas()
    freq_year_tag = freq_year_tag.merge(year_totals_tags, on="year", how="left")

    if NORMALIZE:
        freq_year_tag["freq"] = freq_year_tag["count"] / freq_year_tag["n_recipes"]
    else:
        freq_year_tag["freq"] = freq_year_tag["count"]

    # Calcul des variations
    min_year_tags = int(df["year"].min())
    max_year_tags = int(df["year"].max())

    first_year_vals_tags = freq_year_tag[freq_year_tag["year"] == min_year_tags][
        ["tag_norm", "freq"]
    ].rename(columns={"freq": "first"})
    last_year_vals_tags = freq_year_tag[freq_year_tag["year"] == max_year_tags][
        ["tag_norm", "freq"]
    ].rename(columns={"freq": "last"})

    variation_tags = first_year_vals_tags.merge(
        last_year_vals_tags, on="tag_norm", how="outer"
    ).fillna(0)
    variation_tags["delta"] = variation_tags["last"] - variation_tags["first"]
    variation_tags = variation_tags.merge(
        freq_global_tags[["tag_norm", "total_count"]], on="tag_norm", how="left"
    )
    variation_tags = variation_tags[variation_tags["total_count"] >= MIN_TOTAL_OCC]

    biggest_increase_tags = variation_tags.nlargest(TOP_N, "delta")
    biggest_decrease_tags = variation_tags.nsmallest(TOP_N, "delta")

    # Diversité
    unique_per_year_tags = (
        df_tags.group_by("year")
        .agg(pl.n_unique("tag_norm").alias("n_unique"))
        .sort("year")
        .to_pandas()
    )

    # Création du graphique avec 6 subplots
    fig = make_subplots(
        rows=3,
        cols=2,
        subplot_titles=(
            f"Top {TOP_N} tags les plus fréquents",
            "Évolution de la diversité des tags",
            f"Top {TOP_N} hausses ({min_year_tags}→{max_year_tags})",
            f"Top {TOP_N} baisses ({min_year_tags}→{max_year_tags})",
            f"Évolution : Top {N_VARIATIONS} hausses",
            f"Évolution : Top {N_VARIATIONS} baisses",
        ),
        specs=[
            [{"type": "bar"}, {"type": "scatter"}],
            [{"type": "bar"}, {"type": "bar"}],
            [{"type": "scatter"}, {"type": "scatter"}],
        ],
    )

    # (1) Top 10 tags
    fig.add_trace(
        go.Bar(
            y=top_global_tags["tag_norm"],
            x=top_global_tags["total_count"],
            orientation="h",
            marker=dict(color="#4682B4", opacity=0.8),
            showlegend=False,
        ),
        row=1,
        col=1,
    )

    # (2) Diversité
    w_div_tags = year_totals_tags["n_recipes"].values
    sizes_div_tags = (w_div_tags / w_div_tags.max()) * 15

    fig.add_trace(
        go.Scatter(
            x=unique_per_year_tags["year"],
            y=unique_per_year_tags["n_unique"],
            mode="lines+markers",
            line=dict(color="#9370DB", width=2),
            marker=dict(size=sizes_div_tags, color="#9370DB", opacity=0.6),
            showlegend=False,
        ),
        row=1,
        col=2,
    )

    # (3) Top hausses
    fig.add_trace(
        go.Bar(
            y=biggest_increase_tags["tag_norm"],
            x=biggest_increase_tags["delta"],
            orientation="h",
            marker=dict(color="#2E8B57", opacity=0.8),
            showlegend=False,
        ),
        row=2,
        col=1,
    )

    # (4) Top baisses
    fig.add_trace(
        go.Bar(
            y=biggest_decrease_tags["tag_norm"],
            x=biggest_decrease_tags["delta"],
            orientation="h",
            marker=dict(color="#E94B3C", opacity=0.8),
            showlegend=False,
        ),
        row=2,
        col=2,
    )

    # (5) Évolution hausses
    greens = cm.Greens(np.linspace(0.4, 0.9, N_VARIATIONS))
    for idx, (_, row_data) in enumerate(biggest_increase_tags.head(N_VARIATIONS).iterrows()):
        tag = row_data["tag_norm"]
        data_tag = freq_year_tag[freq_year_tag["tag_norm"] == tag].sort_values("year")
        color = mcolors.rgb2hex(greens[idx])
        fig.add_trace(
            go.Scatter(
                x=data_tag["year"],
                y=data_tag["freq"],
                mode="lines+markers",
                name=tag,
                line=dict(color=color, width=2),
                marker=dict(size=6),
                showlegend=True,
                legendgroup="hausses_tags",
            ),
            row=3,
            col=1,
        )

    # (6) Évolution baisses
    reds = cm.Reds(np.linspace(0.4, 0.9, N_VARIATIONS))
    for idx, (_, row_data) in enumerate(biggest_decrease_tags.head(N_VARIATIONS).iterrows()):
        tag = row_data["tag_norm"]
        data_tag = freq_year_tag[freq_year_tag["tag_norm"] == tag].sort_values("year")
        color = mcolors.rgb2hex(reds[idx])
        fig.add_trace(
            go.Scatter(
                x=data_tag["year"],
                y=data_tag["freq"],
                mode="lines+markers",
                name=tag,
                line=dict(color=color, width=2),
                marker=dict(size=6),
                showlegend=True,
                legendgroup="baisses_tags",
            ),
            row=3,
            col=2,
        )

    # Axes
    fig.update_xaxes(title_text="Occurrences totales", row=1, col=1)
    fig.update_yaxes(showgrid=True, gridcolor="#e0e0e0", row=1, col=1)

    fig.update_xaxes(
        title_text="Année", showgrid=True, gridcolor="#e0e0e0", row=1, col=2
    )
    fig.update_yaxes(
        title_text="Nombre de tags uniques",
        showgrid=True,
        gridcolor="#e0e0e0",
        row=1,
        col=2,
    )

    label_delta_tags = "Variation (normalisée)" if NORMALIZE else "Variation (occurrences)"
    fig.update_xaxes(title_text=label_delta_tags, row=2, col=1)
    fig.update_yaxes(showgrid=True, gridcolor="#e0e0e0", row=2, col=1)

    fig.update_xaxes(title_text=label_delta_tags, row=2, col=2)
    fig.update_yaxes(showgrid=True, gridcolor="#e0e0e0", row=2, col=2)

    ylabel_freq_tags = "Fréquence" if NORMALIZE else "Occurrences"
    fig.update_xaxes(
        title_text="Année", showgrid=True, gridcolor="#e0e0e0", row=3, col=1
    )
    fig.update_yaxes(
        title_text=ylabel_freq_tags, showgrid=True, gridcolor="#e0e0e0", row=3, col=1
    )

    fig.update_xaxes(
        title_text="Année", showgrid=True, gridcolor="#e0e0e0", row=3, col=2
    )
    fig.update_yaxes(
        title_text=ylabel_freq_tags, showgrid=True, gridcolor="#e0e0e0", row=3, col=2
    )

    # Mise en forme
    fig.update_layout(
        height=1200,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(size=11),
        showlegend=True,
    )

    st.plotly_chart(fig, use_container_width=True)

    # Interprétation
    st.info(
        "🏷️ **Interprétation**: L'analyse des tags révèle les **évolutions thématiques** des recettes au fil du temps. "
        "Comme pour les ingrédients, on observe une **chute de la diversité** des tags, passant d'un maximum en début "
        "de période à un minimum en fin de période, reflétant la diminution du volume de recettes postées après 2007. "
        "Les **tendances montantes et descendantes** des tags permettent d'identifier les **thématiques culinaires** "
        "qui gagnent ou perdent en popularité, offrant un aperçu des **préférences alimentaires** et des **modes culinaires** "
        "qui caractérisent chaque période."
    )
