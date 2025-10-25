"""Module d'analyse des tendances temporelles des recettes Food.com.

Analyse l'évolution des recettes entre 1999 et 2018:
- Volume de recettes par année
- Durée de préparation
- Complexité
- Valeurs nutritionnelles
- Ingrédients
- Tags/catégories

Utilise WLS (Weighted Least Squares) pour les régressions.
"""

import warnings

import polars as pl
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
import statsmodels.api as sm
import streamlit as st

from data.cached_loaders import get_recipes_clean as load_recipes_clean
from .plotly_config import COLORS, apply_theme

warnings.filterwarnings("ignore")

# Les couleurs sont maintenant importées depuis plotly_config
# COLORS = {
#     "primary": "#00416A",  # darkblue
#     "secondary": "#E94B3C",  # red
#     "success": "#2E8B57",  # green
#     "warning": "#FF8C00",  # orange
#     "info": "#4682B4",  # steelblue
#     "purple": "#8B008B",
#     "coral": "#FF7F50",
# }
# La fonction apply_white_theme est maintenant importée depuis plotly_config (renommée apply_theme)


def analyse_trendline_volume():
    """Analyse du volume de recettes par année.

    Affiche:
        - Graphique en barres du nombre de recettes
        - Q-Q plot pour test de normalité
        - Interprétation des tendances
    """
    if load_recipes_clean is None:
        st.error("❌ Impossible de charger les données")
        return

    df = load_recipes_clean()
    recipes_per_year = (
        df.group_by("year").agg(pl.len().alias("n_recipes")).sort("year").to_pandas()
    )

    # Préparation Q-Q plot
    data = recipes_per_year["n_recipes"].values

    # Création des subplots
    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Nombre de recettes par année", "Q-Q Plot (Test de normalité)"),
        specs=[[{"type": "bar"}, {"type": "scatter"}]],
    )

    # (1) Graphique de fréquence
    fig.add_trace(
        go.Bar(
            x=recipes_per_year["year"].astype(int),
            y=recipes_per_year["n_recipes"],
            marker=dict(color=COLORS["primary"], opacity=0.8),
            text=recipes_per_year["n_recipes"].apply(lambda x: f"{x:,}"),
            textposition="outside",
            name="Recettes",
        ),
        row=1,
        col=1,
    )

    # (2) Q-Q Plot
    theoretical_quantiles, ordered_values = stats.probplot(data, dist="norm")
    fig.add_trace(
        go.Scatter(
            x=theoretical_quantiles[0],
            y=ordered_values,
            mode="markers",
            marker=dict(color=COLORS["primary"], size=8),
            name="Observations",
        ),
        row=1,
        col=2,
    )

    # Ligne de référence Q-Q plot
    slope = theoretical_quantiles[1]
    intercept = theoretical_quantiles[0]
    x_ref = theoretical_quantiles[0]
    y_ref = slope * x_ref + intercept
    fig.add_trace(
        go.Scatter(
            x=x_ref,
            y=y_ref,
            mode="lines",
            line=dict(color=COLORS["secondary"], dash="dash"),
            name="Loi normale théorique",
        ),
        row=1,
        col=2,
    )

    # Mise en page avec grilles
    fig.update_xaxes(
        title_text="Année",
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

    fig.update_layout(
        height=500,
        showlegend=True,
        title_text="Volume de recettes par année (1999-2018)",
    )

    st.plotly_chart(apply_theme(fig), use_container_width=True)

    # Interprétation
    st.info(
        "📊 **Interprétation**: Nous observons une **forte augmentation du nombre de recettes postées jusqu'en 2007**, "
        "année du **pic d'activité**, suivie d'une **chute marquée** les années suivantes. "
        "Les **tests de normalité** et les **Q-Q plots** montrent que la distribution du **nombre de recettes par an** "
        "**n'est pas parfaitement normale**, avec des **écarts visibles** par rapport à la **loi normale théorique**."
    )


def analyse_trendline_duree():
    """Analyse de l'évolution de la durée de préparation.

    Affiche:
        - Courbe moyenne et médiane
        - Régressions WLS
        - IQR (intervalle interquartile)
        - Statistiques de tendance
    """
    if load_recipes_clean is None:
        st.error("❌ Impossible de charger les données")
        return

    df = load_recipes_clean()
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
    sizes = minutes_by_year["n_recipes"] / minutes_by_year["n_recipes"].max() * 30

    # Création du graphique
    fig = go.Figure()

    # IQR (intervalle interquartile)
    fig.add_trace(
        go.Scatter(
            x=minutes_by_year["year"],
            y=minutes_by_year["q25"],
            fill=None,
            mode="lines",
            line=dict(color=COLORS["primary"], width=0),
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
            line=dict(color=COLORS["primary"], width=0),
            name="IQR (Q25-Q75)",
            fillcolor="rgba(70, 130, 180, 0.15)",
        )
    )

    # Moyenne observée
    fig.add_trace(
        go.Scatter(
            x=minutes_by_year["year"],
            y=minutes_by_year["mean_minutes"],
            mode="lines+markers",
            name="Moyenne (observée)",
            line=dict(color=COLORS["primary"], width=2),
            marker=dict(size=sizes, color=COLORS["primary"], opacity=0.6),
        )
    )

    # Régression moyenne
    fig.add_trace(
        go.Scatter(
            x=minutes_by_year["year"],
            y=regressions["mean_minutes"]["y_pred"],
            mode="lines",
            name=f"Régression Moyenne (R²={regressions['mean_minutes']['r2']:.3f})",
            line=dict(color=COLORS["primary"], width=2, dash="dash"),
        )
    )

    # Médiane observée
    fig.add_trace(
        go.Scatter(
            x=minutes_by_year["year"],
            y=minutes_by_year["median_minutes"],
            mode="lines+markers",
            name="Médiane (observée)",
            line=dict(color=COLORS["coral"], width=2),
            marker=dict(size=sizes, color=COLORS["coral"], opacity=0.6),
        )
    )

    # Régression médiane
    fig.add_trace(
        go.Scatter(
            x=minutes_by_year["year"],
            y=regressions["median_minutes"]["y_pred"],
            mode="lines",
            name=f"Régression Médiane (R²={regressions['median_minutes']['r2']:.3f})",
            line=dict(color=COLORS["secondary"], width=2, dash="dash"),
        )
    )

    # Mise en page
    fig.update_layout(
        title=f"Évolution de la durée (minutes)<br>"
        f"<sub>Moyenne: {regressions['mean_minutes']['slope']:+.4f} min/an | "
        f"Médiane: {regressions['median_minutes']['slope']:+.4f} min/an</sub>",
        xaxis_title="Année",
        yaxis_title="Minutes",
        height=600,
        hovermode="x unified",
    )

    st.plotly_chart(apply_theme(fig), use_container_width=True)

    # Interprétation
    st.info(
        "⏱️ **Interprétation**: L'analyse de la durée moyenne de préparation montre une **tendance globale à la baisse** "
        f"depuis la création du site. En moyenne, le temps de préparation diminue d'environ "
        f"**{regressions['mean_minutes']['slope']:.2f} min/an**, tandis que la médiane recule de "
        f"**{regressions['median_minutes']['slope']:.2f} min/an**, ce qui traduit une "
        "**légère simplification des recettes** au fil du temps."
    )


def analyse_trendline_complexite():
    """Analyse de l'évolution de la complexité des recettes.

    Affiche:
        - Score de complexité
        - Nombre d'étapes
        - Nombre d'ingrédients
        - Régressions WLS pour chaque métrique
    """
    if load_recipes_clean is None:
        st.error("❌ Impossible de charger les données")
        return

    df = load_recipes_clean()
    complexity_by_year = (
        df.group_by("year")
        .agg(
            [
                pl.mean("complexity_score").alias("mean_complexity"),
                pl.mean("n_steps").alias("mean_steps"),
                pl.mean("n_ingredients").alias("mean_ingredients"),
                pl.std("complexity_score").alias("std_complexity"),
                pl.count("id").alias("count_recipes"),
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
            "color": "purple",
            "title": "Score de complexité",
            "ylabel": "Complexity Score",
        },
        "mean_steps": {
            "color": "orange",
            "title": "Nombre d'étapes",
            "ylabel": "Nombre d'étapes",
        },
        "mean_ingredients": {
            "color": "forestgreen",
            "title": "Nombre d'ingrédients",
            "ylabel": "Nombre d'ingrédients",
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
    sizes = (w / w.max()) * 30

    # Création des subplots
    fig = make_subplots(
        rows=1,
        cols=3,
        subplot_titles=[config["title"] for config in metrics_config.values()],
        specs=[[{"type": "scatter"}] * 3],
    )

    for idx, (metric_col, config) in enumerate(metrics_config.items(), 1):
        reg = regressions[metric_col]

        # Courbe observée
        fig.add_trace(
            go.Scatter(
                x=complexity_by_year["year"],
                y=complexity_by_year[metric_col],
                mode="lines+markers",
                name=f"{config['title']} (observée)",
                line=dict(color=config["color"], width=2),
                marker=dict(size=sizes, color=config["color"], opacity=0.6),
                legendgroup=f"group{idx}",
            ),
            row=1,
            col=idx,
        )

        # Ligne de régression
        fig.add_trace(
            go.Scatter(
                x=complexity_by_year["year"],
                y=reg["y_pred"],
                mode="lines",
                name=f"Régression (R²={reg['r2']:.3f})",
                line=dict(color=COLORS["secondary"], width=2, dash="dash"),
                legendgroup=f"group{idx}",
            ),
            row=1,
            col=idx,
        )

        # Titre avec pente
        fig.layout.annotations[idx - 1].update(
            text=f"{config['title']}<br><sub>Pente: {reg['slope']:+.4f}/an (p={reg['p_value']:.2e})</sub>"
        )

        # Axes
        fig.update_xaxes(title_text="Année", row=1, col=idx)
        fig.update_yaxes(title_text=config["ylabel"], row=1, col=idx)

    fig.update_layout(
        height=500,
        showlegend=True,
        title_text="Évolution de la complexité des recettes",
    )

    st.plotly_chart(apply_theme(fig), use_container_width=True)

    # Interprétation
    slope_complexity = regressions["mean_complexity"]["slope"]
    r2_complexity = regressions["mean_complexity"]["r2"]
    p_complexity = regressions["mean_complexity"]["p_value"]

    st.info(
        f"🔧 **Interprétation**: La **régression linéaire pondérée** (pente = **{slope_complexity:+.2f}**, "
        f"R² = **{r2_complexity:.2f}**, p = **{p_complexity:.2e}**) met en évidence une **tendance significative à la hausse** "
        "du **score moyen de complexité** au fil du temps. Cette évolution indique une **augmentation progressive de la complexité "
        f"des recettes**, d'environ **{slope_complexity:+.2f} point par an**, suggérant des **préparations de plus en plus élaborées** "
        "au cours des années."
    )


def analyse_trendline_nutrition():
    """Analyse de l'évolution des valeurs nutritionnelles.

    Affiche:
        - Calories
        - Glucides (%)
        - Lipides (%)
        - Protéines (%)
        - Régressions WLS pour chaque métrique
    """
    if load_recipes_clean is None:
        st.error("❌ Impossible de charger les données")
        return

    df = load_recipes_clean()
    nutrition_by_year = (
        df.group_by("year")
        .agg(
            [
                pl.mean("calories").alias("mean_calories"),
                pl.mean("carb_pct").alias("mean_carbs"),
                pl.mean("total_fat_pct").alias("mean_fat"),
                pl.mean("protein_pct").alias("mean_protein"),
                pl.count("id").alias("count_recipes"),
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
            "color": "tomato",
            "title": "Calories moyennes",
            "ylabel": "Calories",
        },
        "mean_carbs": {
            "color": "royalblue",
            "title": "Glucides (%)",
            "ylabel": "Carbs %",
        },
        "mean_fat": {"color": "orange", "title": "Lipides (%)", "ylabel": "Fat %"},
        "mean_protein": {
            "color": "green",
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
    sizes = (w / w.max()) * 30

    # Création des subplots
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=[config["title"] for config in metrics_config.values()],
        specs=[[{"type": "scatter"}] * 2] * 2,
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
                name=f"{config['title']} (observée)",
                line=dict(color=config["color"], width=2),
                marker=dict(size=sizes, color=config["color"], opacity=0.6),
                legendgroup=f"group{row}{col}",
            ),
            row=row,
            col=col,
        )

        # Ligne de régression
        fig.add_trace(
            go.Scatter(
                x=nutrition_by_year["year"],
                y=reg["y_pred"],
                mode="lines",
                name=f"Régression (R²={reg['r2']:.3f})",
                line=dict(color=COLORS["secondary"], width=2, dash="dash"),
                legendgroup=f"group{row}{col}",
            ),
            row=row,
            col=col,
        )

        # Titre avec pente
        idx = (row - 1) * 2 + col - 1
        fig.layout.annotations[idx].update(
            text=f"{config['title']}<br><sub>Pente: {reg['slope']:+.4f}/an (p={reg['p_value']:.2e})</sub>"
        )

        # Axes
        fig.update_xaxes(title_text="Année", row=row, col=col)
        fig.update_yaxes(title_text=config["ylabel"], row=row, col=col)

    fig.update_layout(
        height=800, showlegend=True, title_text="Évolution des valeurs nutritionnelles"
    )

    st.plotly_chart(apply_theme(fig), use_container_width=True)

    # Interprétation
    st.info(
        "🥗 **Interprétation**: Les **régressions linéaires pondérées** montrent une **tendance significative à la baisse** "
        "des valeurs **nutritionnelles moyennes** au fil du temps. Les **calories**, **glucides**, **lipides** et **protéines** "
        "présentent toutes des **pentes négatives**, avec des **R² pondérés entre 0.39 et 0.56**, indiquant une **bonne part "
        "de variance expliquée** et une **diminution mesurable** des apports nutritionnels moyens par recette. Cette évolution "
        "traduit une **orientation progressive vers des recettes plus légères**, moins riches en **calories** et en **macronutriments**, "
        "reflétant probablement une **adaptation aux tendances alimentaires modernes** (recherche de plats plus équilibrés et moins "
        "énergétiques)."
    )


def analyse_trendline_ingredients(top_n=10):
    """Analyse de l'évolution des ingrédients.

    Args:
        top_n: Nombre d'ingrédients à afficher dans les tops

    Affiche:
        - Top ingrédients globaux
        - Diversité des ingrédients
        - Top hausses/baisses
        - Évolution temporelle
    """
    if load_recipes_clean is None:
        st.error("❌ Impossible de charger les données")
        return

    df = load_recipes_clean()

    # Paramètres
    MIN_TOTAL_OCC = 50
    N_VARIATIONS = 5

    # Normalisation des ingrédients
    df_ingredients = (
        df.select(["id", "year", "ingredients"])
        .explode("ingredients")
        .with_columns(
            [
                pl.col("ingredients")
                .str.to_lowercase()
                .str.strip_chars()
                .alias("ingredient_norm")
            ]
        )
    )

    # Fréquence globale
    freq_global = (
        df_ingredients.group_by("ingredient_norm")
        .agg(pl.count("id").alias("total_count"))
        .filter(pl.col("total_count") >= MIN_TOTAL_OCC)
        .sort("total_count", descending=True)
        .to_pandas()
    )

    top_global = freq_global.head(top_n)

    # Fréquence par année
    freq_year_ing = (
        df_ingredients.group_by(["year", "ingredient_norm"])
        .agg(pl.count("ingredient_norm").alias("count"))
        .to_pandas()
    )

    year_totals = df.group_by("year").agg(pl.count("id").alias("n_recipes")).to_pandas()
    freq_year_ing = freq_year_ing.merge(year_totals, on="year", how="left")
    freq_year_ing["freq"] = freq_year_ing["count"] / freq_year_ing["n_recipes"]

    # Calcul des variations
    min_year = int(df["year"].min())
    max_year = int(df["year"].max())

    first_year_vals = freq_year_ing[freq_year_ing["year"] == min_year][
        ["ingredient_norm", "freq"]
    ].rename(columns={"freq": "first"})
    last_year_vals = freq_year_ing[freq_year_ing["year"] == max_year][
        ["ingredient_norm", "freq"]
    ].rename(columns={"freq": "last"})

    variation = first_year_vals.merge(
        last_year_vals, on="ingredient_norm", how="outer"
    ).fillna(0)
    variation["delta"] = variation["last"] - variation["first"]
    variation = variation.merge(
        freq_global[["ingredient_norm", "total_count"]],
        on="ingredient_norm",
        how="left",
    )
    variation = variation[variation["total_count"] >= MIN_TOTAL_OCC]

    biggest_increase = variation.nlargest(top_n, "delta")
    biggest_decrease = variation.nsmallest(top_n, "delta")

    # Diversité
    unique_per_year = (
        df_ingredients.group_by("year")
        .agg(pl.n_unique("ingredient_norm").alias("n_unique"))
        .sort("year")
        .to_pandas()
    )

    # VISUALISATION - 6 subplots
    fig = make_subplots(
        rows=3,
        cols=2,
        subplot_titles=(
            f"Top {top_n} ingrédients les plus fréquents",
            "Évolution de la diversité des ingrédients",
            f"Top {top_n} hausses ({min_year}→{max_year})",
            f"Top {top_n} baisses ({min_year}→{max_year})",
            f"Évolution : Top {N_VARIATIONS} hausses",
            f"Évolution : Top {N_VARIATIONS} baisses",
        ),
        specs=[
            [{"type": "bar"}, {"type": "scatter"}],
            [{"type": "bar"}, {"type": "bar"}],
            [{"type": "scatter"}, {"type": "scatter"}],
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.1,
    )

    # (1) Top ingrédients globaux
    fig.add_trace(
        go.Bar(
            y=top_global["ingredient_norm"].tolist()[::-1],
            x=top_global["total_count"].tolist()[::-1],
            orientation="h",
            marker=dict(color=COLORS["primary"], opacity=0.8),
            name="Fréquence globale",
        ),
        row=1,
        col=1,
    )

    # (2) Diversité
    w_div = year_totals["n_recipes"].values
    sizes_div = (w_div / w_div.max()) * 20
    fig.add_trace(
        go.Scatter(
            x=unique_per_year["year"],
            y=unique_per_year["n_unique"],
            mode="lines+markers",
            marker=dict(size=sizes_div, color=COLORS["purple"], opacity=0.6),
            line=dict(color=COLORS["purple"], width=2),
            name="Diversité",
        ),
        row=1,
        col=2,
    )

    # (3) Top hausses
    fig.add_trace(
        go.Bar(
            y=biggest_increase["ingredient_norm"].tolist()[::-1],
            x=biggest_increase["delta"].tolist()[::-1],
            orientation="h",
            marker=dict(color=COLORS["success"], opacity=0.8),
            name="Hausses",
        ),
        row=2,
        col=1,
    )

    # (4) Top baisses
    fig.add_trace(
        go.Bar(
            y=biggest_decrease["ingredient_norm"].tolist()[::-1],
            x=biggest_decrease["delta"].tolist()[::-1],
            orientation="h",
            marker=dict(color=COLORS["secondary"], opacity=0.8),
            name="Baisses",
        ),
        row=2,
        col=2,
    )

    # (5) Évolution hausses
    for _, row_data in biggest_increase.head(N_VARIATIONS).iterrows():
        ing = row_data["ingredient_norm"]
        data_ing = freq_year_ing[freq_year_ing["ingredient_norm"] == ing].sort_values(
            "year"
        )
        fig.add_trace(
            go.Scatter(
                x=data_ing["year"],
                y=data_ing["freq"],
                mode="lines+markers",
                name=ing,
                line=dict(width=2),
                legendgroup="hausses",
            ),
            row=3,
            col=1,
        )

    # (6) Évolution baisses
    for _, row_data in biggest_decrease.head(N_VARIATIONS).iterrows():
        ing = row_data["ingredient_norm"]
        data_ing = freq_year_ing[freq_year_ing["ingredient_norm"] == ing].sort_values(
            "year"
        )
        fig.add_trace(
            go.Scatter(
                x=data_ing["year"],
                y=data_ing["freq"],
                mode="lines+markers",
                name=ing,
                line=dict(width=2),
                legendgroup="baisses",
            ),
            row=3,
            col=2,
        )

    # Mise en page
    fig.update_xaxes(title_text="Occurrences totales", row=1, col=1)
    fig.update_xaxes(title_text="Année", row=1, col=2)
    fig.update_xaxes(title_text="Variation (normalisée)", row=2, col=1)
    fig.update_xaxes(title_text="Variation (normalisée)", row=2, col=2)
    fig.update_xaxes(title_text="Année", row=3, col=1)
    fig.update_xaxes(title_text="Année", row=3, col=2)

    fig.update_yaxes(title_text="Ingrédient", row=1, col=1)
    fig.update_yaxes(title_text="Nombre d'ingrédients uniques", row=1, col=2)
    fig.update_yaxes(title_text="Ingrédient", row=2, col=1)
    fig.update_yaxes(title_text="Ingrédient", row=2, col=2)
    fig.update_yaxes(title_text="Fréquence", row=3, col=1)
    fig.update_yaxes(title_text="Fréquence", row=3, col=2)

    fig.update_layout(
        height=1400, title_text="Analyse des ingrédients", showlegend=True
    )

    st.plotly_chart(apply_theme(fig), use_container_width=True)

    # Interprétation
    st.info(
        "🥘 **Interprétation**: L'analyse révèle une **transformation profonde** de l'usage des ingrédients au fil du temps. "
        "**Tendances montantes**: Des ingrédients comme *kosher salt*, *garlic cloves*, *olive oil* et *unsalted butter* "
        "connaissent une forte progression, reflétant peut-être un virage vers une cuisine plus communautaire ou méditerranéenne. "
        "**Tendances descendantes**: Les ingrédients traditionnels comme *sugar*, *butter*, *eggs* et *vanilla* sont en net recul, "
        "suggérant une diminution des recettes de pâtisserie classique et une recherche de recettes moins sucrées. "
        "**Chute de la diversité**: Le nombre d'ingrédients uniques chute drastiquement après 2007, s'expliquant par la diminution "
        "du volume de recettes postées et une concentration sur des ingrédients plus courants."
    )


def analyse_trendline_tags(top_n=10):
    """Analyse de l'évolution des tags/catégories.

    Args:
        top_n: Nombre de tags à afficher dans les tops

    Affiche:
        - Top tags globaux
        - Diversité des tags
        - Top hausses/baisses
        - Évolution temporelle
    """
    if load_recipes_clean is None:
        st.error("❌ Impossible de charger les données")
        return

    df = load_recipes_clean()

    # Paramètres
    MIN_TOTAL_OCC = 50
    N_VARIATIONS = 5

    # Normalisation des tags
    df_tags = (
        df.select(["id", "year", "tags"])
        .explode("tags")
        .with_columns(
            [pl.col("tags").str.to_lowercase().str.strip_chars().alias("tag_norm")]
        )
    )

    # Fréquence globale
    freq_global_tags = (
        df_tags.group_by("tag_norm")
        .agg(pl.count("id").alias("total_count"))
        .filter(pl.col("total_count") >= MIN_TOTAL_OCC)
        .sort("total_count", descending=True)
        .to_pandas()
    )

    top_global_tags = freq_global_tags.head(top_n)

    # Fréquence par année
    freq_year_tag = (
        df_tags.group_by(["year", "tag_norm"])
        .agg(pl.count("tag_norm").alias("count"))
        .to_pandas()
    )

    year_totals_tags = (
        df.group_by("year").agg(pl.count("id").alias("n_recipes")).to_pandas()
    )
    freq_year_tag = freq_year_tag.merge(year_totals_tags, on="year", how="left")
    freq_year_tag["freq"] = freq_year_tag["count"] / freq_year_tag["n_recipes"]

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

    biggest_increase_tags = variation_tags.nlargest(top_n, "delta")
    biggest_decrease_tags = variation_tags.nsmallest(top_n, "delta")

    # Diversité
    unique_per_year_tags = (
        df_tags.group_by("year")
        .agg(pl.n_unique("tag_norm").alias("n_unique"))
        .sort("year")
        .to_pandas()
    )

    # VISUALISATION - 6 subplots
    fig = make_subplots(
        rows=3,
        cols=2,
        subplot_titles=(
            f"Top {top_n} tags les plus fréquents",
            "Évolution de la diversité des tags",
            f"Top {top_n} hausses ({min_year_tags}→{max_year_tags})",
            f"Top {top_n} baisses ({min_year_tags}→{max_year_tags})",
            f"Évolution : Top {N_VARIATIONS} hausses",
            f"Évolution : Top {N_VARIATIONS} baisses",
        ),
        specs=[
            [{"type": "bar"}, {"type": "scatter"}],
            [{"type": "bar"}, {"type": "bar"}],
            [{"type": "scatter"}, {"type": "scatter"}],
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.1,
    )

    # (1) Top tags globaux
    fig.add_trace(
        go.Bar(
            y=top_global_tags["tag_norm"].tolist()[::-1],
            x=top_global_tags["total_count"].tolist()[::-1],
            orientation="h",
            marker=dict(color=COLORS["primary"], opacity=0.8),
            name="Fréquence globale",
        ),
        row=1,
        col=1,
    )

    # (2) Diversité
    w_div_tags = year_totals_tags["n_recipes"].values
    sizes_div_tags = (w_div_tags / w_div_tags.max()) * 20
    fig.add_trace(
        go.Scatter(
            x=unique_per_year_tags["year"],
            y=unique_per_year_tags["n_unique"],
            mode="lines+markers",
            marker=dict(size=sizes_div_tags, color=COLORS["purple"], opacity=0.6),
            line=dict(color=COLORS["purple"], width=2),
            name="Diversité",
        ),
        row=1,
        col=2,
    )

    # (3) Top hausses
    fig.add_trace(
        go.Bar(
            y=biggest_increase_tags["tag_norm"].tolist()[::-1],
            x=biggest_increase_tags["delta"].tolist()[::-1],
            orientation="h",
            marker=dict(color=COLORS["success"], opacity=0.8),
            name="Hausses",
        ),
        row=2,
        col=1,
    )

    # (4) Top baisses
    fig.add_trace(
        go.Bar(
            y=biggest_decrease_tags["tag_norm"].tolist()[::-1],
            x=biggest_decrease_tags["delta"].tolist()[::-1],
            orientation="h",
            marker=dict(color=COLORS["secondary"], opacity=0.8),
            name="Baisses",
        ),
        row=2,
        col=2,
    )

    # (5) Évolution hausses
    for _, row_data in biggest_increase_tags.head(N_VARIATIONS).iterrows():
        tag = row_data["tag_norm"]
        data_tag = freq_year_tag[freq_year_tag["tag_norm"] == tag].sort_values("year")
        fig.add_trace(
            go.Scatter(
                x=data_tag["year"],
                y=data_tag["freq"],
                mode="lines+markers",
                name=tag,
                line=dict(width=2),
                legendgroup="hausses_tags",
            ),
            row=3,
            col=1,
        )

    # (6) Évolution baisses
    for _, row_data in biggest_decrease_tags.head(N_VARIATIONS).iterrows():
        tag = row_data["tag_norm"]
        data_tag = freq_year_tag[freq_year_tag["tag_norm"] == tag].sort_values("year")
        fig.add_trace(
            go.Scatter(
                x=data_tag["year"],
                y=data_tag["freq"],
                mode="lines+markers",
                name=tag,
                line=dict(width=2),
                legendgroup="baisses_tags",
            ),
            row=3,
            col=2,
        )

    # Mise en page
    fig.update_xaxes(title_text="Occurrences totales", row=1, col=1)
    fig.update_xaxes(title_text="Année", row=1, col=2)
    fig.update_xaxes(title_text="Variation (normalisée)", row=2, col=1)
    fig.update_xaxes(title_text="Variation (normalisée)", row=2, col=2)
    fig.update_xaxes(title_text="Année", row=3, col=1)
    fig.update_xaxes(title_text="Année", row=3, col=2)

    fig.update_yaxes(title_text="Tag", row=1, col=1)
    fig.update_yaxes(title_text="Nombre de tags uniques", row=1, col=2)
    fig.update_yaxes(title_text="Tag", row=2, col=1)
    fig.update_yaxes(title_text="Tag", row=2, col=2)
    fig.update_yaxes(title_text="Fréquence", row=3, col=1)
    fig.update_yaxes(title_text="Fréquence", row=3, col=2)

    fig.update_layout(
        height=1400, title_text="Analyse des tags/catégories", showlegend=True
    )

    st.plotly_chart(apply_theme(fig), use_container_width=True)

    # Interprétation
    st.info(
        "🏷️ **Interprétation**: L'analyse des tags révèle une **évolution des pratiques de catégorisation** des recettes au fil du temps. "
        "**Tendances montantes**: Les catégories en hausse concernent surtout les repas rapides (*60-minutes-or-less*, *for-1-or-2*), "
        "les plats principaux (*main-dish*), ainsi que des moments spécifiques comme le petit-déjeuner ou les en-cas. "
        "**Tendances descendantes**: Les baisses marquées touchent des catégories techniques ou structurantes (*dietary*, *equipment*, "
        "*oven*, *occasion*, *number-of-servings*), ainsi que des étiquettes génériques (*north-american*, *cuisine*, *american*), "
        "suggérant une simplification de la catégorisation au profit de tags plus concrets et orientés usage. "
        "**Évolution de la diversité**: Le nombre de tags uniques suit une trajectoire similaire à celle des ingrédients, avec une "
        "diminution significative après 2007, traduisant une convergence vers un vocabulaire de catégorisation plus homogène."
    )
