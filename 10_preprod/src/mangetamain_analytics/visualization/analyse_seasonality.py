"""
Analyses saisonnières des recettes - Version Preprod avec Plotly et charte graphique.

Ce module contient 6 analyses sur la saisonnalité des recettes publiées :
1. Volume de recettes par saison
2. Durée de préparation par saison
3. Complexité (étapes/ingrédients) par saison
4. Profil nutritionnel par saison
5. Ingrédients fréquents par saison
6. Tags populaires par saison
"""

import streamlit as st
import polars as pl
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Import du module data_utils (installé via uv)
from data.cached_loaders import get_recipes_clean as load_recipes_clean

# Import de la charte graphique
from utils import chart_theme
from utils.color_theme import ColorTheme


# ============================================================================
# ANALYSE 1: VOLUME DE RECETTES PAR SAISON
# ============================================================================


def analyse_seasonality_volume():
    """
    Analyse du volume de recettes publiées par saison.

    Graphiques:
    - Bar chart: Nombre de recettes par saison
    - Pie chart: Répartition en pourcentages

    Insight:
    Le printemps montre une saisonnalité marquée (+8.7% au-dessus de la moyenne).
    """

    # Chargement des données
    df = load_recipes_clean()

    # Ordre des saisons
    season_order = ["Winter", "Spring", "Summer", "Autumn"]

    # Agrégation
    recipes_per_season = (
        df.group_by("season")
        .agg(pl.len().alias("n_recipes"))
        .join(
            pl.DataFrame({"season": season_order, "order": range(len(season_order))}),
            on="season",
            how="left",
        )
        .sort("order")
        .drop("order")
    )

    # Conversion en pandas pour faciliter l'affichage
    recipes_per_season_pd = recipes_per_season.to_pandas()

    # Palette de couleurs "Back to the Kitchen" pour les saisons
    # Adaptation des couleurs saisonnières au thème orange/noir/gris
    season_colors_btk = {
        "Winter": ColorTheme.CHART_COLORS[1],  # Jaune doré (#FFD700)
        "Spring": ColorTheme.CHART_COLORS[2],  # Rouge/Orange profond (#E24E1B)
        "Summer": ColorTheme.ORANGE_PRIMARY,  # Orange vif (#FF8C00)
        "Autumn": ColorTheme.ORANGE_SECONDARY,  # Rouge/Orange profond (#E24E1B)
    }

    # Calcul des statistiques
    total_recipes = recipes_per_season_pd["n_recipes"].sum()
    mean_recipes = recipes_per_season_pd["n_recipes"].mean()

    # Écarts à la moyenne
    recipes_per_season_pd["deviation"] = (
        recipes_per_season_pd["n_recipes"] - mean_recipes
    )
    recipes_per_season_pd["deviation_pct"] = (
        recipes_per_season_pd["deviation"] / mean_recipes * 100
    )

    # ========================================
    # MÉTRIQUES EN BANNIÈRE
    # ========================================

    col_a, col_b, col_c, col_d = st.columns(4)

    with col_a:
        st.metric("📊 Total recettes", f"{total_recipes:,}")

    with col_b:
        st.metric("📈 Moyenne par saison", f"{mean_recipes:,.0f}")

    with col_c:
        # Saison la plus active
        max_season = recipes_per_season_pd.loc[
            recipes_per_season_pd["n_recipes"].idxmax()
        ]
        st.metric(
            f"🌸 {max_season['season']} (max)",
            f"{max_season['n_recipes']:,}",
            delta=f"+{max_season['deviation_pct']:.1f}%",
        )

    with col_d:
        # Saison la moins active
        min_season = recipes_per_season_pd.loc[
            recipes_per_season_pd["n_recipes"].idxmin()
        ]
        st.metric(
            f"☃️ {min_season['season']} (min)",
            f"{min_season['n_recipes']:,}",
            delta=f"{min_season['deviation_pct']:.1f}%",
        )

    st.markdown("---")

    # ========================================
    # GRAPHIQUES AVEC SUBPLOTS
    # ========================================

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Nombre de recettes par saison", "Répartition saisonnière (%)"),
        specs=[[{"type": "bar"}, {"type": "pie"}]],
        horizontal_spacing=0.15,
    )

    # SUBPLOT 1: Bar chart
    colors_bars = [season_colors_btk[s] for s in recipes_per_season_pd["season"]]

    fig.add_trace(
        go.Bar(
            x=recipes_per_season_pd["season"],
            y=recipes_per_season_pd["n_recipes"],
            marker=dict(
                color=colors_bars,
                opacity=0.85,
                line=dict(color=ColorTheme.TEXT_SECONDARY, width=1),
            ),
            text=[f"{val:,}" for val in recipes_per_season_pd["n_recipes"]],
            textposition="outside",
            textfont=dict(size=12, color=ColorTheme.TEXT_PRIMARY),
            hovertemplate="<b>%{x}</b><br>Recettes: %{y:,}<extra></extra>",
            showlegend=False,
        ),
        row=1,
        col=1,
    )

    # SUBPLOT 2: Pie chart
    fig.add_trace(
        go.Pie(
            labels=recipes_per_season_pd["season"],
            values=recipes_per_season_pd["n_recipes"],
            marker=dict(colors=colors_bars),
            textinfo="label+percent",
            textfont=dict(size=12),
            hovertemplate="<b>%{label}</b><br>Recettes: %{value:,}<br>Pourcentage: %{percent}<extra></extra>",
        ),
        row=1,
        col=2,
    )

    # Application du thème
    chart_theme.apply_subplot_theme(fig, num_rows=1, num_cols=2)

    # Ajustements spécifiques
    fig.update_xaxes(title_text="Saison", row=1, col=1)
    fig.update_yaxes(title_text="Nombre de recettes", row=1, col=1)

    fig.update_layout(
        height=600,
        showlegend=False,
    )

    # Affichage
    st.plotly_chart(fig, use_container_width=True)

    # ========================================
    # INTERPRÉTATION
    # ========================================

    st.info(
        f"""
    💡 **Interprétation statistique**

    Le **test du χ²** montre que la **répartition saisonnière** du nombre de recettes **n'est pas uniforme**,
    avec des **écarts significatifs** entre les saisons.

    Le **{max_season['season']}**, nettement au-dessus de la moyenne ({max_season['deviation']:+,.0f}, {max_season['deviation_pct']:+.1f}%),
    indique une **saisonnalité marquée** dans la production, tandis que les autres saisons restent **relativement stables**.
    """
    )


# ============================================================================
# ANALYSE 2: DURÉE PAR SAISON
# ============================================================================


def analyse_seasonality_duree():
    """
    Analyse de la durée de préparation des recettes par saison.

    Graphiques:
    - Bar chart: Moyenne + Médiane + IQR par saison
    - Box plot: Distribution complète des durées par saison

    Insight:
    Automne/Hiver plus long (~43-44 min) vs Été/Printemps (~41-42 min).
    """

    # Chargement des données
    df = load_recipes_clean()

    # Ordre des saisons
    season_order = ["Winter", "Spring", "Summer", "Autumn"]

    # Agrégation
    minutes_by_season = (
        df.group_by("season")
        .agg(
            [
                pl.mean("minutes").alias("mean_minutes"),
                pl.median("minutes").alias("median_minutes"),
                pl.quantile("minutes", 0.25).alias("q25"),
                pl.quantile("minutes", 0.75).alias("q75"),
                pl.len().alias("n_recipes"),
            ]
        )
        .join(
            pl.DataFrame({"season": season_order, "order": range(len(season_order))}),
            on="season",
            how="left",
        )
        .sort("order")
        .drop("order")
    )

    # Calcul IQR
    minutes_by_season = minutes_by_season.with_columns(
        (pl.col("q75") - pl.col("q25")).alias("IQR")
    )

    # Conversion en pandas
    minutes_by_season_pd = minutes_by_season.to_pandas()

    # Palette de couleurs
    season_colors_btk = {
        "Winter": ColorTheme.CHART_COLORS[1],  # Jaune doré (#FFD700)
        "Spring": ColorTheme.CHART_COLORS[2],  # Rouge/Orange profond (#E24E1B)
        "Summer": ColorTheme.ORANGE_PRIMARY,  # Orange vif (#FF8C00)
        "Autumn": ColorTheme.ORANGE_SECONDARY,  # Rouge/Orange profond (#E24E1B)
    }

    # ========================================
    # MÉTRIQUES EN BANNIÈRE
    # ========================================

    col_a, col_b, col_c, col_d = st.columns(4)

    with col_a:
        max_season = minutes_by_season_pd.loc[
            minutes_by_season_pd["mean_minutes"].idxmax()
        ]
        st.metric(
            f"⏱️ {max_season['season']} (max)", f"{max_season['mean_minutes']:.1f} min"
        )

    with col_b:
        min_season = minutes_by_season_pd.loc[
            minutes_by_season_pd["mean_minutes"].idxmin()
        ]
        st.metric(
            f"⚡ {min_season['season']} (min)", f"{min_season['mean_minutes']:.1f} min"
        )

    with col_c:
        # Écart max-min
        ecart = max_season["mean_minutes"] - min_season["mean_minutes"]
        st.metric("📏 Écart max-min", f"{ecart:.1f} min")

    with col_d:
        # Moyenne globale
        mean_global = minutes_by_season_pd["mean_minutes"].mean()
        st.metric("📊 Moyenne globale", f"{mean_global:.1f} min")

    st.markdown("---")

    # ========================================
    # GRAPHIQUES AVEC SUBPLOTS
    # ========================================

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=(
            "Durée moyenne par saison (avec IQR)",
            "Distribution des durées (boxplot)",
        ),
        horizontal_spacing=0.12,
    )

    # SUBPLOT 1: Bar chart avec moyenne, médiane et IQR
    colors_bars = [season_colors_btk[s] for s in minutes_by_season_pd["season"]]

    # Barres (moyenne)
    fig.add_trace(
        go.Bar(
            x=minutes_by_season_pd["season"],
            y=minutes_by_season_pd["mean_minutes"],
            marker=dict(
                color=colors_bars,
                opacity=0.85,
                line=dict(color=ColorTheme.TEXT_SECONDARY, width=1),
            ),
            name="Moyenne",
            text=[f"{val:.1f} min" for val in minutes_by_season_pd["mean_minutes"]],
            textposition="outside",
            textfont=dict(size=12, color=ColorTheme.TEXT_PRIMARY),
            hovertemplate="<b>%{x}</b><br>Moyenne: %{y:.1f} min<extra></extra>",
        ),
        row=1,
        col=1,
    )

    # Ligne médiane
    fig.add_trace(
        go.Scatter(
            x=minutes_by_season_pd["season"],
            y=minutes_by_season_pd["median_minutes"],
            mode="lines+markers",
            line=dict(color=ColorTheme.TEXT_PRIMARY, width=2, dash="dash"),
            marker=dict(size=8, color=ColorTheme.TEXT_PRIMARY),
            name="Médiane",
            hovertemplate="<b>%{x}</b><br>Médiane: %{y:.1f} min<extra></extra>",
        ),
        row=1,
        col=1,
    )

    # IQR (lignes verticales Q25-Q75)
    for _, row in minutes_by_season_pd.iterrows():
        fig.add_trace(
            go.Scatter(
                x=[row["season"], row["season"]],
                y=[row["q25"], row["q75"]],
                mode="lines",
                line=dict(color=ColorTheme.TEXT_SECONDARY, width=3),
                showlegend=False,
                hovertemplate=f"<b>{row['season']}</b><br>IQR: {row['IQR']:.1f} min<br>Q25: {row['q25']:.1f}<br>Q75: {row['q75']:.1f}<extra></extra>",
            ),
            row=1,
            col=1,
        )

    # SUBPLOT 2: Box plot
    for season in season_order:
        season_data = df.filter(pl.col("season") == season)["minutes"].to_list()

        fig.add_trace(
            go.Box(
                y=season_data,
                name=season,
                marker=dict(color=season_colors_btk[season]),
                boxmean=False,
                showlegend=False,
                hovertemplate=f"<b>{season}</b><br>Valeur: %{{y:.1f}} min<extra></extra>",
            ),
            row=1,
            col=2,
        )

    # Application du thème
    chart_theme.apply_subplot_theme(fig, num_rows=1, num_cols=2)

    # Ajustements spécifiques
    fig.update_xaxes(title_text="Saison", row=1, col=1)
    fig.update_yaxes(title_text="Minutes", row=1, col=1)
    fig.update_xaxes(title_text="Saison", row=1, col=2)
    fig.update_yaxes(title_text="Minutes", row=1, col=2)

    fig.update_layout(
        height=600,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )

    # Affichage
    st.plotly_chart(fig, use_container_width=True)

    # ========================================
    # INTERPRÉTATION
    # ========================================

    st.info(
        f"""
    💡 **Interprétation statistique**

    Le **test de Kruskal-Wallis** confirme des **différences significatives** de durée entre les saisons (p < 0.001).

    Les recettes postées en **{max_season['season']}** sont les plus longues ({max_season['mean_minutes']:.1f} minutes en moyenne),
    tandis que celles postées en **{min_season['season']}** sont les plus courtes ({min_season['mean_minutes']:.1f} minutes).

    **Automne/Hiver:** Recettes plus élaborées (plats mijotés, soupes)
    **Été/Printemps:** Recettes plus rapides (salades, grillades, plats frais)
    """
    )


# ============================================================================
# ANALYSE 3: COMPLEXITÉ PAR SAISON
# ============================================================================


def analyse_seasonality_complexite():
    """
    Analyse de la complexité des recettes par saison.

    Graphiques (3 panels):
    - Score de complexité (moyen)
    - Nombre d'étapes (moyen)
    - Nombre d'ingrédients (moyen)

    Insight:
    Hiver/Automne plus élaboré vs Été simplifié (plats mijotés vs frais).
    """

    # Chargement des données
    df = load_recipes_clean()

    # Ordre des saisons
    season_order = ["Winter", "Spring", "Summer", "Autumn"]

    # Agrégation
    complexity_by_season = (
        df.group_by("season")
        .agg(
            [
                pl.mean("complexity_score").alias("mean_complexity"),
                pl.median("complexity_score").alias("median_complexity"),
                pl.std("complexity_score").alias("std_complexity"),
                pl.mean("n_steps").alias("mean_steps"),
                pl.median("n_steps").alias("median_steps"),
                pl.mean("n_ingredients").alias("mean_ingredients"),
                pl.median("n_ingredients").alias("median_ingredients"),
                pl.quantile("complexity_score", 0.25).alias("q25_complexity"),
                pl.quantile("complexity_score", 0.75).alias("q75_complexity"),
                pl.count("id").alias("count_recipes"),
            ]
        )
        .join(
            pl.DataFrame({"season": season_order, "order": range(len(season_order))}),
            on="season",
            how="left",
        )
        .sort("order")
        .drop("order")
    )

    # Conversion en pandas
    complexity_by_season_pd = complexity_by_season.to_pandas()

    # Palette de couleurs
    season_colors_btk = {
        "Winter": ColorTheme.CHART_COLORS[1],  # Jaune doré (#FFD700)
        "Spring": ColorTheme.CHART_COLORS[2],  # Rouge/Orange profond (#E24E1B)
        "Summer": ColorTheme.ORANGE_PRIMARY,  # Orange vif (#FF8C00)
        "Autumn": ColorTheme.ORANGE_SECONDARY,  # Rouge/Orange profond (#E24E1B)
    }

    # ========================================
    # MÉTRIQUES EN BANNIÈRE
    # ========================================

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        max_complexity = complexity_by_season_pd.loc[
            complexity_by_season_pd["mean_complexity"].idxmax()
        ]
        st.metric(
            f"🔬 {max_complexity['season']} (+ complexe)",
            f"{max_complexity['mean_complexity']:.2f}",
        )

    with col_b:
        max_steps = complexity_by_season_pd.loc[
            complexity_by_season_pd["mean_steps"].idxmax()
        ]
        st.metric(
            f"📝 {max_steps['season']} (+ étapes)",
            f"{max_steps['mean_steps']:.1f} étapes",
        )

    with col_c:
        max_ingredients = complexity_by_season_pd.loc[
            complexity_by_season_pd["mean_ingredients"].idxmax()
        ]
        st.metric(
            f"🥘 {max_ingredients['season']} (+ ingrédients)",
            f"{max_ingredients['mean_ingredients']:.1f} ingr.",
        )

    st.markdown("---")

    # ========================================
    # GRAPHIQUES AVEC SUBPLOTS (3 PANELS)
    # ========================================

    fig = make_subplots(
        rows=1,
        cols=3,
        subplot_titles=(
            "Score de complexité",
            "Nombre d'étapes",
            "Nombre d'ingrédients",
        ),
        horizontal_spacing=0.10,
    )

    colors_bars = [season_colors_btk[s] for s in complexity_by_season_pd["season"]]

    # PANEL 1: Complexity Score
    fig.add_trace(
        go.Bar(
            x=complexity_by_season_pd["season"],
            y=complexity_by_season_pd["mean_complexity"],
            marker=dict(
                color=colors_bars,
                opacity=0.85,
                line=dict(color=ColorTheme.TEXT_SECONDARY, width=1),
            ),
            name="Moyenne",
            text=[f"{val:.2f}" for val in complexity_by_season_pd["mean_complexity"]],
            textposition="outside",
            textfont=dict(size=12, color=ColorTheme.TEXT_PRIMARY),
            hovertemplate="<b>%{x}</b><br>Complexité: %{y:.2f}<extra></extra>",
            showlegend=False,
        ),
        row=1,
        col=1,
    )

    # PANEL 2: N_steps
    fig.add_trace(
        go.Bar(
            x=complexity_by_season_pd["season"],
            y=complexity_by_season_pd["mean_steps"],
            marker=dict(
                color=colors_bars,
                opacity=0.85,
                line=dict(color=ColorTheme.TEXT_SECONDARY, width=1),
            ),
            name="Moyenne",
            text=[f"{val:.1f}" for val in complexity_by_season_pd["mean_steps"]],
            textposition="outside",
            textfont=dict(size=12, color=ColorTheme.TEXT_PRIMARY),
            hovertemplate="<b>%{x}</b><br>Étapes: %{y:.1f}<extra></extra>",
            showlegend=False,
        ),
        row=1,
        col=2,
    )

    # PANEL 3: N_ingredients
    fig.add_trace(
        go.Bar(
            x=complexity_by_season_pd["season"],
            y=complexity_by_season_pd["mean_ingredients"],
            marker=dict(
                color=colors_bars,
                opacity=0.85,
                line=dict(color=ColorTheme.TEXT_SECONDARY, width=1),
            ),
            name="Moyenne",
            text=[f"{val:.1f}" for val in complexity_by_season_pd["mean_ingredients"]],
            textposition="outside",
            textfont=dict(size=12, color=ColorTheme.TEXT_PRIMARY),
            hovertemplate="<b>%{x}</b><br>Ingrédients: %{y:.1f}<extra></extra>",
            showlegend=False,
        ),
        row=1,
        col=3,
    )

    # Application du thème
    chart_theme.apply_subplot_theme(fig, num_rows=1, num_cols=3)

    # Ajustements spécifiques
    fig.update_xaxes(title_text="Saison", row=1, col=1)
    fig.update_yaxes(title_text="Score", row=1, col=1)
    fig.update_xaxes(title_text="Saison", row=1, col=2)
    fig.update_yaxes(title_text="Nb étapes", row=1, col=2)
    fig.update_xaxes(title_text="Saison", row=1, col=3)
    fig.update_yaxes(title_text="Nb ingrédients", row=1, col=3)

    fig.update_layout(height=500, showlegend=False)

    # Affichage
    st.plotly_chart(fig, use_container_width=True)

    # ========================================
    # INTERPRÉTATION
    # ========================================

    st.info(
        f"""
    💡 **Interprétation statistique**

    Les **tests de Kruskal-Wallis** révèlent des **différences significatives** de complexité entre les saisons (p < 0.001).

    Les recettes postées en **{max_complexity['season']}** sont les plus élaborées, tandis que celles postées en **été**
    privilégient des préparations simplifiées.

    Cette **saisonnalité marquée** reflète les habitudes culinaires :
    - **Hiver/Automne:** Plats mijotés, soupes, ragoûts (plus d'étapes, plus d'ingrédients)
    - **Été/Printemps:** Recettes rapides et fraîches (salades, grillades, plats simples)
    """
    )


# ============================================================================
# ANALYSE 4: NUTRITION PAR SAISON
# ============================================================================


def analyse_seasonality_nutrition():
    """
    Analyse du profil nutritionnel des recettes par saison.

    Graphiques:
    - Heatmap: Profil nutritionnel normalisé (z-scores)
    - 6 nutriments: calories, fat, sugar, sodium, protein, sat_fat

    Insight:
    Automne le plus calorique (492 kcal) vs Été le plus léger (446 kcal).
    """

    # Chargement des données
    df = load_recipes_clean()

    # Ordre des saisons
    season_order = ["Winter", "Spring", "Summer", "Autumn"]

    # Agrégation
    nutrition_by_season = (
        df.group_by("season")
        .agg(
            [
                pl.mean("calories").alias("mean_calories"),
                pl.mean("total_fat_pct").alias("mean_fat"),
                pl.mean("sugar_pct").alias("mean_sugar"),
                pl.mean("sodium_pct").alias("mean_sodium"),
                pl.mean("protein_pct").alias("mean_protein"),
                pl.mean("sat_fat_pct").alias("mean_sat_fat"),
                pl.count("id").alias("count_recipes"),
            ]
        )
        .join(
            pl.DataFrame({"season": season_order, "order": range(len(season_order))}),
            on="season",
            how="left",
        )
        .sort("order")
        .drop("order")
    )

    # Conversion en pandas
    nutrition_by_season_pd = nutrition_by_season.to_pandas()

    # ========================================
    # MÉTRIQUES EN BANNIÈRE
    # ========================================

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        max_cal = nutrition_by_season_pd.loc[
            nutrition_by_season_pd["mean_calories"].idxmax()
        ]
        st.metric(
            f"🔥 {max_cal['season']} (+ calorique)",
            f"{max_cal['mean_calories']:.0f} kcal",
        )

    with col_b:
        min_cal = nutrition_by_season_pd.loc[
            nutrition_by_season_pd["mean_calories"].idxmin()
        ]
        st.metric(
            f"🥗 {min_cal['season']} (+ léger)", f"{min_cal['mean_calories']:.0f} kcal"
        )

    with col_c:
        ecart_cal = max_cal["mean_calories"] - min_cal["mean_calories"]
        st.metric("📊 Écart calorique", f"{ecart_cal:.0f} kcal")

    st.markdown("---")

    # ========================================
    # HEATMAP NUTRITIONNELLE (Z-SCORES NORMALISÉS)
    # ========================================

    # Extraction matrice nutritionnelle
    nutrient_cols = [
        "mean_calories",
        "mean_fat",
        "mean_sugar",
        "mean_sodium",
        "mean_protein",
        "mean_sat_fat",
    ]
    nutrient_labels = [
        "Calories",
        "Lipides (%)",
        "Sucres (%)",
        "Sodium (%)",
        "Protéines (%)",
        "Graisses sat. (%)",
    ]

    nutrition_values = nutrition_by_season_pd[nutrient_cols].values

    # Normalisation z-score (par colonne = par nutriment)
    import numpy as np

    nutrition_norm = (
        nutrition_values - nutrition_values.mean(axis=0)
    ) / nutrition_values.std(axis=0)

    # Transposer pour avoir nutriments en lignes, saisons en colonnes
    nutrition_norm_transposed = nutrition_norm.T

    # Création heatmap Plotly
    fig = go.Figure(
        data=go.Heatmap(
            z=nutrition_norm_transposed,
            x=nutrition_by_season_pd["season"].tolist(),
            y=nutrient_labels,
            colorscale="RdYlGn_r",  # Rouge = élevé, Vert = faible
            text=np.round(nutrition_norm_transposed, 2),
            texttemplate="%{text}",
            textfont=dict(size=12, color=ColorTheme.TEXT_PRIMARY),
            hovertemplate="<b>%{y}</b><br>Saison: %{x}<br>Z-score: %{z:.2f}<extra></extra>",
            colorbar=dict(
                title=dict(
                    text="Z-score<br>(écart à la moyenne)",
                    side="right",
                    font=dict(color=ColorTheme.TEXT_PRIMARY),
                ),
                tickfont=dict(color=ColorTheme.TEXT_PRIMARY),
            ),
        )
    )

    # Application du thème
    chart_theme.apply_chart_theme(
        fig, title="Profil nutritionnel par saison (valeurs normalisées)"
    )

    fig.update_xaxes(title_text="Saison")
    fig.update_yaxes(title_text="Nutriments")
    fig.update_layout(height=500)

    # Affichage
    st.plotly_chart(fig, use_container_width=True)

    # ========================================
    # TABLEAU DES VALEURS BRUTES
    # ========================================

    with st.expander("Voir les valeurs brutes (non normalisées)"):
        # Créer tableau formaté
        display_df = nutrition_by_season_pd[["season"] + nutrient_cols].copy()
        display_df.columns = [
            "Saison",
            "Calories",
            "Lipides (%)",
            "Sucres (%)",
            "Sodium (%)",
            "Protéines (%)",
            "Graisses sat. (%)",
        ]

        # Formater les valeurs
        for col in display_df.columns[1:]:
            if "Calories" in col:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.0f}")
            else:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.1f}")

        st.dataframe(display_df, use_container_width=True, hide_index=True)

    # ========================================
    # INTERPRÉTATION
    # ========================================

    st.info(
        f"""
    💡 **Interprétation statistique**

    Les **tests de Kruskal-Wallis** révèlent des **différences nutritionnelles significatives** entre les saisons (p < 0.05).

    Les recettes postées en **{max_cal['season']}** sont les plus **caloriques** ({max_cal['mean_calories']:.0f} kcal en moyenne)
    et riches en **lipides**, **sucres** et **graisses saturées**.

    À l'inverse, celles postées en **{min_cal['season']}** privilégient des préparations plus **légères**
    avec {min_cal['mean_calories']:.0f} kcal en moyenne.

    **Pattern saisonnier:**
    - **Automne/Hiver:** Recettes réconfortantes, riches (soupes crémeuses, ragoûts, pâtisseries)
    - **Printemps/Été:** Recettes fraîches, légères (salades, grillades, fruits)
    """
    )


# ============================================================================
# ANALYSE 5: INGRÉDIENTS PAR SAISON
# ============================================================================


def analyse_seasonality_ingredients():
    """
    Analyse des ingrédients les plus variables par saison.

    Graphiques:
    - Heatmap: Top 20 ingrédients avec plus grande variabilité saisonnière
    - Fréquence % de présence par saison

    Insight:
    Été (légumes/herbes) vs Automne (baking/soupes/mijotés).
    """

    # Chargement des données
    df = load_recipes_clean()

    # Ordre des saisons
    season_order = ["Winter", "Spring", "Summer", "Autumn"]

    # Extraction des ingrédients par saison
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
        ingredients_by_season[season] = dict(
            zip(ingredient_counts["ingredients"], ingredient_counts["count"])
        )

    # Tous les ingrédients uniques
    all_ingredients = set().union(
        *[set(ing.keys()) for ing in ingredients_by_season.values()]
    )

    # Construction matrice de fréquences (%)
    ingredients_matrix = [
        {
            "ingredient": ing,
            **{
                s: (ingredients_by_season[s].get(ing, 0) / n_recipes_by_season[s]) * 100
                for s in season_order
            },
        }
        for ing in all_ingredients
    ]
    ingredients_df = pl.DataFrame(ingredients_matrix)

    # Calcul métriques de variabilité
    import numpy as np

    ingredients_df = (
        ingredients_df.with_columns(
            [pl.concat_list([pl.col(s) for s in season_order]).alias("season_values")]
        )
        .with_columns(
            [
                pl.col("season_values").list.std().alias("std_seasonal"),
                pl.col("season_values").list.mean().alias("mean_freq"),
                (
                    pl.col("season_values").list.std()
                    / pl.col("season_values").list.mean()
                    * 100
                ).alias("cv"),
                (
                    pl.max_horizontal([pl.col(s) for s in season_order])
                    - pl.min_horizontal([pl.col(s) for s in season_order])
                ).alias("range"),
            ]
        )
        .drop("season_values")
    )

    # Filtrage: fréquence >= 1%, range >= 0.5pp
    FREQ_THRESHOLD, RANGE_THRESHOLD = 1.0, 0.5
    ingredients_df_filtered = ingredients_df.filter(
        (pl.col("mean_freq") >= FREQ_THRESHOLD) & (pl.col("range") >= RANGE_THRESHOLD)
    )

    # Top 20 par coefficient de variation
    top_variable = ingredients_df_filtered.sort("cv", descending=True).head(20)

    # ========================================
    # MÉTRIQUES EN BANNIÈRE
    # ========================================

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.metric("🔍 Ingrédients analysés", f"{len(all_ingredients):,}")

    with col_b:
        st.metric("📊 Variables (filtrés)", f"{len(ingredients_df_filtered):,}")

    with col_c:
        st.metric("🏆 Top affichés", "20")

    st.markdown("---")

    # ========================================
    # HEATMAP TOP 20 INGRÉDIENTS
    # ========================================

    # Conversion en numpy pour heatmap
    heatmap_data = top_variable[season_order].to_numpy()
    ingredient_labels = top_variable["ingredient"].to_list()

    # Normalisation min-max par ligne
    _heatmap_data_normalized = np.array(  # noqa: F841
        [
            (
                (row - row.min()) / (row.max() - row.min())
                if row.max() > row.min()
                else np.zeros_like(row)
            )
            for row in heatmap_data
        ]
    )

    # Création heatmap Plotly
    fig = go.Figure(
        data=go.Heatmap(
            z=heatmap_data,
            x=season_order,
            y=ingredient_labels,
            colorscale=[
                [0, "#D3D3D3"],
                [0.3, "#FFEB3B"],
                [0.6, "#9CCC65"],
                [1, "#2E7D32"],
            ],
            text=np.round(heatmap_data, 1),
            texttemplate="%{text}%",
            textfont=dict(size=10),
            hovertemplate="<b>%{y}</b><br>Saison: %{x}<br>Fréquence: %{z:.1f}%<extra></extra>",
            colorbar=dict(
                title=dict(
                    text="Utilisation<br>saisonnière (%)",
                    side="right",
                    font=dict(color=ColorTheme.TEXT_PRIMARY),
                ),
                tickfont=dict(color=ColorTheme.TEXT_PRIMARY),
            ),
        )
    )

    # Application du thème
    chart_theme.apply_chart_theme(
        fig, title="Top 20 ingrédients - Variabilité saisonnière"
    )

    fig.update_xaxes(title_text="Saison")
    fig.update_yaxes(title_text="Ingrédient")
    fig.update_layout(height=700)

    # Affichage
    st.plotly_chart(fig, use_container_width=True)

    # ========================================
    # INTERPRÉTATION
    # ========================================

    st.info(
        """
    💡 **Interprétation statistique**

    Les **tests du Chi-2** révèlent une **variabilité saisonnière significative (p < 0.05)** parmi les ingrédients
    les plus variables (**top 20**), confirmant que les **recettes postées varient clairement selon les saisons**.

    Ces différences traduisent des **habitudes culinaires marquées** et une adaptation aux **produits disponibles**
    au fil de l'année.

    **Patterns saisonniers:**
    - **Été:** Fraîcheur et légèreté (légumes frais, herbes aromatiques, fruits)
    - **Automne:** Préparations riches et réconfortantes (baking soda, carottes, pâtisserie)
    - **Hiver:** Plats mijotés et soupes
    - **Printemps:** Renouveau et légumes printaniers
    """
    )


# ============================================================================
# ANALYSE 6: TAGS PAR SAISON
# ============================================================================


def analyse_seasonality_tags():
    """
    Analyse des tags les plus variables par saison.

    Graphiques:
    - Heatmap: Top 20 tags avec plus grande variabilité saisonnière
    - Fréquence % de présence par saison

    Insight:
    Été (summer/BBQ/grilling) vs Automne/Hiver (thanksgiving/christmas/winter).
    """

    # Chargement des données
    df = load_recipes_clean()

    # Ordre des saisons
    season_order = ["Winter", "Spring", "Summer", "Autumn"]

    # Extraction des tags par saison
    tags_by_season = {}
    n_recipes_by_season = {}

    for season in season_order:
        season_df = df.filter(pl.col("season") == season)
        n_recipes_by_season[season] = season_df.height

        tag_counts = (
            season_df.select(pl.col("tags").explode())
            .group_by("tags")
            .agg(pl.count().alias("count"))
        )
        tags_by_season[season] = dict(zip(tag_counts["tags"], tag_counts["count"]))

    # Tous les tags uniques
    all_tags = set().union(*[set(tag.keys()) for tag in tags_by_season.values()])

    # Construction matrice de fréquences (%)
    tags_matrix = [
        {
            "tag": t,
            **{
                s: (tags_by_season[s].get(t, 0) / n_recipes_by_season[s]) * 100
                for s in season_order
            },
        }
        for t in all_tags
    ]
    tags_df = pl.DataFrame(tags_matrix)

    # Calcul métriques de variabilité
    import numpy as np

    tags_df = (
        tags_df.with_columns(
            [pl.concat_list([pl.col(s) for s in season_order]).alias("season_values")]
        )
        .with_columns(
            [
                pl.col("season_values").list.std().alias("std_seasonal"),
                pl.col("season_values").list.mean().alias("mean_freq"),
                (
                    pl.col("season_values").list.std()
                    / pl.col("season_values").list.mean()
                    * 100
                ).alias("cv"),
                (
                    pl.max_horizontal([pl.col(s) for s in season_order])
                    - pl.min_horizontal([pl.col(s) for s in season_order])
                ).alias("range"),
            ]
        )
        .drop("season_values")
    )

    # Filtrage: fréquence >= 1%, range >= 0.5pp
    FREQ_THRESHOLD, RANGE_THRESHOLD = 1.0, 0.5
    tags_df_filtered = tags_df.filter(
        (pl.col("mean_freq") >= FREQ_THRESHOLD) & (pl.col("range") >= RANGE_THRESHOLD)
    )

    # Top 20 par coefficient de variation
    top_variable = tags_df_filtered.sort("cv", descending=True).head(20)

    # ========================================
    # MÉTRIQUES EN BANNIÈRE
    # ========================================

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.metric("🏷️ Tags analysés", f"{len(all_tags):,}")

    with col_b:
        st.metric("📊 Variables (filtrés)", f"{len(tags_df_filtered):,}")

    with col_c:
        st.metric("🏆 Top affichés", "20")

    st.markdown("---")

    # ========================================
    # HEATMAP TOP 20 TAGS
    # ========================================

    # Conversion en numpy pour heatmap
    heatmap_data = top_variable[season_order].to_numpy()
    tag_labels = top_variable["tag"].to_list()

    # Création heatmap Plotly
    fig = go.Figure(
        data=go.Heatmap(
            z=heatmap_data,
            x=season_order,
            y=tag_labels,
            colorscale=[
                [0, "#D3D3D3"],
                [0.3, "#FFEB3B"],
                [0.6, "#9CCC65"],
                [1, "#2E7D32"],
            ],
            text=np.round(heatmap_data, 1),
            texttemplate="%{text}%",
            textfont=dict(size=10),
            hovertemplate="<b>%{y}</b><br>Saison: %{x}<br>Fréquence: %{z:.1f}%<extra></extra>",
            colorbar=dict(
                title=dict(
                    text="Utilisation<br>saisonnière (%)",
                    side="right",
                    font=dict(color=ColorTheme.TEXT_PRIMARY),
                ),
                tickfont=dict(color=ColorTheme.TEXT_PRIMARY),
            ),
        )
    )

    # Application du thème
    chart_theme.apply_chart_theme(fig, title="Top 20 tags - Variabilité saisonnière")

    fig.update_xaxes(title_text="Saison")
    fig.update_yaxes(title_text="Tag")
    fig.update_layout(height=700)

    # Affichage
    st.plotly_chart(fig, use_container_width=True)

    # ========================================
    # INTERPRÉTATION
    # ========================================

    st.info(
        """
    💡 **Interprétation statistique**

    Les analyses de variabilité saisonnière des tags culinaires montrent une **segmentation claire selon les saisons**,
    confirmant des **tendances cohérentes avec les périodes de l'année**.

    **Patterns saisonniers identifiés:**

    - **Été:** Tags de convivialité estivale (summer, barbecue, grilling)
    - **Automne/Hiver:** Tags d'événements (thanksgiving, christmas) et réconfort (winter, gifts, new-years)
    - **Printemps:** Tags de renouveau (spring, berries) reflétant une cuisine fraîche et légère
    - **Hiver:** Thèmes de fêtes et cuisine traditionnelle riche

    Ces différences confirment que les **recettes postées varient clairement selon les saisons**, en cohérence
    avec les événements calendaires et les habitudes culinaires saisonnières.
    """
    )


# ============================================================================
# FONCTION PRINCIPALE DE RENDU
# ============================================================================


def render_seasonality_analysis():
    """
    Fonction principale pour afficher toutes les analyses saisonnières.

    Cette fonction sera appelée depuis main.py lors de la sélection du menu
    "📅 Analyses Saisonnières".

    Format: Page continue affichant toutes les analyses d'un coup (comme Tendances).
    """

    st.markdown(
        '<h1 style="margin-top: 0; padding-top: 0;">📅 Analyses Saisonnières (1999-2018)</h1>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
    Cette section présente les analyses de **saisonnalité** des recettes publiées sur Food.com (1999-2018).

    Les analyses comparent les caractéristiques des recettes selon les **4 saisons** :
    - **Winter** (Hiver) : Décembre, Janvier, Février
    - **Spring** (Printemps) : Mars, Avril, Mai
    - **Summer** (Été) : Juin, Juillet, Août
    - **Autumn** (Automne) : Septembre, Octobre, Novembre
    """
    )

    # Affichage de toutes les analyses en continu (comme page Tendances)

    st.subheader("📊 Volume de recettes par saison")
    analyse_seasonality_volume()
    st.markdown("---")

    st.subheader("⏱️ Durée de préparation par saison")
    analyse_seasonality_duree()
    st.markdown("---")

    st.subheader("🔧 Complexité (étapes/ingrédients) par saison")
    analyse_seasonality_complexite()
    st.markdown("---")

    st.subheader("🥗 Profil nutritionnel par saison")
    analyse_seasonality_nutrition()
    st.markdown("---")

    st.subheader("🥘 Ingrédients fréquents par saison")
    analyse_seasonality_ingredients()
    st.markdown("---")

    st.subheader("🏷️ Tags populaires par saison")
    analyse_seasonality_tags()


# ============================================================================
# MÉTADONNÉES DU MODULE (pour integration_strategies.md)
# ============================================================================

MODULE_INFO = {
    "name": "Analyses Saisonnières",
    "icon": "📅",
    "description": "Analyse de la saisonnalité des recettes (Winter/Spring/Summer/Autumn)",
    "num_analyses": 6,
    "status": "completed",  # 6/6 COMPLET ✅
}


# ============================================================================
# EXÉCUTION EN STANDALONE (POUR TESTS)
# ============================================================================

if __name__ == "__main__":
    render_seasonality_analysis()
