"""
Module d'analyse de l'effet weekend sur les recettes.

Ce module contient 6 analyses principales explorant les différences
entre recettes publiées en semaine vs. week-end.

Analyses disponibles:
1. Volume de recettes (Weekday vs Weekend)
2. Durée des recettes (minutes)
3. Complexité (score, steps, ingredients)
4. Profil nutritionnel
5. Ingrédients les plus variables
6. Tags les plus variables

Date: 2025-10-24
"""

import streamlit as st
import polars as pl
import numpy as np
from scipy import stats
from scipy.stats import chi2_contingency
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from data.cached_loaders import get_recipes_clean as load_recipes_clean
from utils import chart_theme
from utils.color_theme import ColorTheme
from utils.i18n_helper import t


def analyse_weekend_volume() -> None:
    """
    📊 ANALYSE 1: Volume de recettes (Weekday vs Weekend)

    Insight: Publication massives en semaine (+51% vs weekend).
    Lundi = jour le plus actif (+45%), Samedi le moins actif (-49%).
    """
    df = load_recipes_clean()

    # --- Ajout colonne Weekday / Weekend ---
    df = df.with_columns(
        pl.when(pl.col("is_weekend") == 1)
        .then(pl.lit("Weekend"))
        .otherwise(pl.lit("Weekday"))
        .alias("week_period")
    )

    # --- Agrégation Weekday vs Weekend ---
    recipes_week_period = (
        df.group_by("week_period")
        .agg(pl.count().alias("n_recipes"))
        .with_columns(
            pl.when(pl.col("week_period") == "Weekday")
            .then(pl.lit(5))
            .otherwise(pl.lit(2))
            .alias("n_days")
        )
        .with_columns((pl.col("n_recipes") / pl.col("n_days")).alias("recipes_per_day"))
        .with_columns(
            pl.when(pl.col("week_period") == "Weekday")
            .then(0)
            .otherwise(1)
            .alias("order")
        )
        .sort("order")
        .drop("order")
    )

    # --- Agrégation par jour ---
    recipes_per_day = (
        df.group_by("weekday")
        .agg(pl.count().alias("n_recipes"))
        .with_columns(
            pl.col("weekday")
            .map_elements(
                lambda x: {
                    1: "Lun",
                    2: "Mar",
                    3: "Mer",
                    4: "Jeu",
                    5: "Ven",
                    6: "Sam",
                    7: "Dim",
                }[x],
                return_dtype=pl.Utf8,
            )
            .alias("jour")
        )
    )

    # Réordonner les jours
    day_order = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
    recipes_per_day = (
        recipes_per_day.join(
            pl.DataFrame({"jour": day_order, "order": range(len(day_order))}),
            on="jour",
            how="left",
        )
        .sort("order")
        .drop("order")
    )

    # --- Moyennes globales ---
    mean_all = recipes_per_day["n_recipes"].mean()
    # --- Écarts à la moyenne ---
    recipes_per_day = recipes_per_day.with_columns(
        ((pl.col("n_recipes") - mean_all) / mean_all * 100).alias("deviation_pct")
    )

    # 📊 MÉTRIQUES BANNIÈRE
    weekday_rpd = recipes_week_period.filter(pl.col("week_period") == "Weekday")[
        "recipes_per_day"
    ][0]
    weekend_rpd = recipes_week_period.filter(pl.col("week_period") == "Weekend")[
        "recipes_per_day"
    ][0]
    diff_pct = (weekday_rpd - weekend_rpd) / weekend_rpd * 100
    max_day = recipes_per_day.sort("n_recipes", descending=True).row(0, named=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Semaine (moy/jour)", f"{weekday_rpd:,.0f}")
    with col2:
        st.metric("Week-end (moy/jour)", f"{weekend_rpd:,.0f}")
    with col3:
        st.metric(t("difference"), f"+{diff_pct:.1f}%", delta=t("weekday_gt_weekend", category="weekend"))
    with col4:
        st.metric(f"Jour max: {max_day['jour']}", f"{max_day['n_recipes']:,}")

    # 🎨 VISUALISATION (3 panels)
    period_colors_btk = [
        ColorTheme.CHART_COLORS[1],
        ColorTheme.ORANGE_PRIMARY,
    ]

    fig = make_subplots(
        rows=1,
        cols=3,
        subplot_titles=(
            "Volume moyen par jour (pondéré)",
            "Distribution des 7 jours",
            t("deviation_from_average"),
        ),
        specs=[[{"type": "bar"}, {"type": "bar"}, {"type": "bar"}]],
    )

    # --- PANEL 1: Weekday vs Weekend ---
    fig.add_trace(
        go.Bar(
            x=recipes_week_period["week_period"],
            y=recipes_week_period["recipes_per_day"],
            marker=dict(
                color=period_colors_btk,
                line=dict(color=ColorTheme.TEXT_SECONDARY, width=1),
            ),
            text=[f"{val:,.0f}/jour" for val in recipes_week_period["recipes_per_day"]],
            textposition="outside",
            textfont=dict(size=12, color=ColorTheme.TEXT_PRIMARY),
            name=t("legend_weighted_volume", category="trends"),
            showlegend=False,
        ),
        row=1,
        col=1,
    )

    # --- PANEL 2: Distribution 7 jours avec moyennes ---
    day_colors_btk = [
        (
            ColorTheme.CHART_COLORS[1]
            if j not in ["Sam", "Dim"]
            else ColorTheme.ORANGE_PRIMARY
        )
        for j in recipes_per_day["jour"]
    ]

    fig.add_trace(
        go.Bar(
            x=recipes_per_day["jour"],
            y=recipes_per_day["n_recipes"],
            marker=dict(
                color=day_colors_btk,
                line=dict(color=ColorTheme.TEXT_SECONDARY, width=1),
            ),
            text=[f"{val:,}" for val in recipes_per_day["n_recipes"]],
            textposition="outside",
            textfont=dict(size=11, color=ColorTheme.TEXT_PRIMARY),
            name="Recettes par jour",
            showlegend=False,
        ),
        row=1,
        col=2,
    )

    # Lignes moyennes
    fig.add_hline(
        y=mean_all,
        line=dict(color=ColorTheme.TEXT_PRIMARY, dash="dash", width=2),
        annotation_text=f"Moy. globale: {mean_all:,.0f}",
        annotation_position="top right",
        annotation_font=dict(size=10, color=ColorTheme.TEXT_PRIMARY),
        row=1,
        col=2,
    )

    # --- PANEL 3: Écarts à la moyenne ---
    colors_deviation = [
        (ColorTheme.CHART_COLORS[2] if x > 0 else ColorTheme.ORANGE_PRIMARY)
        for x in recipes_per_day["deviation_pct"]
    ]

    fig.add_trace(
        go.Bar(
            x=recipes_per_day["jour"],
            y=recipes_per_day["deviation_pct"],
            marker=dict(
                color=colors_deviation,
                line=dict(color=ColorTheme.TEXT_SECONDARY, width=1),
            ),
            text=[f"{val:+.1f}%" for val in recipes_per_day["deviation_pct"]],
            textposition="outside",
            textfont=dict(size=11, color=ColorTheme.TEXT_PRIMARY),
            name=t("legend_deviation_pct", category="trends"),
            showlegend=False,
        ),
        row=1,
        col=3,
    )

    fig.add_hline(
        y=0, line=dict(color=ColorTheme.TEXT_PRIMARY, width=1.5), row=1, col=3
    )

    # Axes
    fig.update_yaxes(title_text="Recettes/jour", row=1, col=1)
    fig.update_yaxes(title_text="Nombre de recettes", row=1, col=2)
    fig.update_yaxes(title_text=t("legend_deviation_pct", category="trends"), row=1, col=3)

    fig.update_xaxes(title_text=t("axis_period"), row=1, col=1)
    fig.update_xaxes(title_text="Jour de la semaine", row=1, col=2)
    fig.update_xaxes(title_text="Jour de la semaine", row=1, col=3)

    # Appliquer thème
    chart_theme.apply_subplot_theme(fig, num_rows=1, num_cols=3)
    fig.update_layout(height=500)

    st.plotly_chart(fig, use_container_width=True)

    # 📝 INTERPRÉTATION
    st.info(t('volume_interpretation', category='weekend'))


def analyse_weekend_duree() -> None:
    """
    📊 ANALYSE 2: Durée des recettes (Weekday vs Weekend)

    Insight: Durée quasi identique entre semaine et week-end (42.5 vs 42.4 min).
    Pas d'effet week-end observable sur la durée.
    """
    df = load_recipes_clean()

    # Ajout colonne week_period
    df = df.with_columns(
        pl.when(pl.col("is_weekend") == 1)
        .then(pl.lit("Weekend"))
        .otherwise(pl.lit("Weekday"))
        .alias("week_period")
    )

    week_period_order = ["Weekday", "Weekend"]
    period_colors_btk = [
        ColorTheme.CHART_COLORS[1],
        ColorTheme.ORANGE_PRIMARY,
    ]

    # Agrégation
    minutes_by_period = (
        df.group_by("week_period")
        .agg(
            [
                pl.mean("minutes").alias("mean_minutes"),
                pl.median("minutes").alias("median_minutes"),
                pl.quantile("minutes", 0.25).alias("q25"),
                pl.quantile("minutes", 0.75).alias("q75"),
                pl.std("minutes").alias("std_minutes"),
                pl.len().alias("n_recipes"),
            ]
        )
        .join(
            pl.DataFrame(
                {
                    "week_period": week_period_order,
                    "order": range(len(week_period_order)),
                }
            ),
            on="week_period",
            how="left",
        )
        .sort("order")
        .drop("order")
    )

    minutes_by_period = minutes_by_period.with_columns(
        (pl.col("q75") - pl.col("q25")).alias("IQR")
    )

    # 📊 MÉTRIQUES BANNIÈRE
    wd_row = minutes_by_period.filter(pl.col("week_period") == "Weekday").row(
        0, named=True
    )
    we_row = minutes_by_period.filter(pl.col("week_period") == "Weekend").row(
        0, named=True
    )
    diff_abs = we_row["mean_minutes"] - wd_row["mean_minutes"]
    diff_pct = (diff_abs / wd_row["mean_minutes"]) * 100

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(t("weekday_average"), f"{wd_row['mean_minutes']:.1f} min")
    with col2:
        st.metric(t("weekend_average"), f"{we_row['mean_minutes']:.1f} min")
    with col3:
        st.metric(t("difference"), f"{diff_abs:+.1f} min", delta=f"{diff_pct:+.2f}%")
    with col4:
        st.metric("IQR Semaine", f"{wd_row['IQR']:.0f} min")

    # 🎨 VISUALISATION (2 panels)
    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=(
            t("duree_recettes_periode"),
            t("distribution_durees_boxplot"),
        ),
        specs=[[{"type": "bar"}, {"type": "box"}]],
    )

    # --- PANEL 1: Barres + Médiane + IQR ---
    fig.add_trace(
        go.Bar(
            x=minutes_by_period["week_period"],
            y=minutes_by_period["mean_minutes"],
            marker=dict(
                color=period_colors_btk,
                line=dict(color=ColorTheme.TEXT_SECONDARY, width=1),
            ),
            text=[f"{val:.1f} m" for val in minutes_by_period["mean_minutes"]],
            textposition="outside",
            textfont=dict(size=12, color=ColorTheme.TEXT_PRIMARY),
            name=t("label_average"),
            showlegend=True,
        ),
        row=1,
        col=1,
    )

    # Ligne médiane
    fig.add_trace(
        go.Scatter(
            x=minutes_by_period["week_period"],
            y=minutes_by_period["median_minutes"],
            mode="lines+markers",
            line=dict(color=ColorTheme.TEXT_PRIMARY, width=2, dash="dash"),
            marker=dict(size=8, color=ColorTheme.TEXT_PRIMARY, symbol="circle"),
            name=t("label_median"),
        ),
        row=1,
        col=1,
    )

    # IQR (lignes verticales avec Scatter)
    for row_data in minutes_by_period.iter_rows(named=True):
        period = row_data["week_period"]
        q25 = row_data["q25"]
        q75 = row_data["q75"]

        fig.add_trace(
            go.Scatter(
                x=[period, period],
                y=[q25, q75],
                mode="lines",
                line=dict(color=ColorTheme.TEXT_PRIMARY, width=3),
                showlegend=False,
                hoverinfo="skip",
            ),
            row=1,
            col=1,
        )

        # Markers Q1/Q3
        fig.add_trace(
            go.Scatter(
                x=[period],
                y=[q25],
                mode="markers",
                marker=dict(size=6, color=ColorTheme.TEXT_PRIMARY, symbol="circle"),
                showlegend=False,
                hovertemplate=f"Q1: {q25:.1f}",
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=[period],
                y=[q75],
                mode="markers",
                marker=dict(size=6, color=ColorTheme.TEXT_PRIMARY, symbol="circle"),
                showlegend=False,
                hovertemplate=f"Q3: {q75:.1f}",
            ),
            row=1,
            col=1,
        )

    # --- PANEL 2: Boxplot par période ---
    for i, period in enumerate(week_period_order):
        period_data = df.filter(pl.col("week_period") == period)["minutes"]

        fig.add_trace(
            go.Box(
                y=period_data,
                name=period,
                marker=dict(color=period_colors_btk[i]),
                boxmean=False,
                showlegend=False,
                line=dict(width=2),
            ),
            row=1,
            col=2,
        )

    # Axes
    fig.update_yaxes(title_text=t("axis_minutes"), row=1, col=1)
    fig.update_yaxes(title_text=t("axis_minutes"), row=1, col=2)
    fig.update_xaxes(title_text=t("axis_period"), row=1, col=1)
    fig.update_xaxes(title_text=t("axis_period"), row=1, col=2)

    # Appliquer thème
    chart_theme.apply_subplot_theme(fig, num_rows=1, num_cols=2)
    fig.update_layout(height=500)

    st.plotly_chart(fig, use_container_width=True)

    # 📝 INTERPRÉTATION
    st.info(t('duration_interpretation', category='weekend'))


def analyse_weekend_complexite() -> None:
    """
    📊 ANALYSE 3: Complexité (Weekday vs Weekend)

    Insight: Complexité quasi identique entre semaine et week-end.
    Scores, nombre d'étapes et d'ingrédients constants.
    """
    df = load_recipes_clean()

    # Ajout colonne week_period
    df = df.with_columns(
        pl.when(pl.col("is_weekend") == 1)
        .then(pl.lit("Weekend"))
        .otherwise(pl.lit("Weekday"))
        .alias("week_period")
    )

    week_period_order = ["Weekday", "Weekend"]
    period_colors_btk = [
        ColorTheme.CHART_COLORS[1],
        ColorTheme.ORANGE_PRIMARY,
    ]

    # Agrégation par période
    complexity_by_period = (
        df.group_by("week_period")
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
                pl.len().alias("n_recipes"),
            ]
        )
        .join(
            pl.DataFrame(
                {
                    "week_period": week_period_order,
                    "order": range(len(week_period_order)),
                }
            ),
            on="week_period",
            how="left",
        )
        .sort("order")
        .drop("order")
    )

    # 📊 MÉTRIQUES BANNIÈRE
    wd_row = complexity_by_period.filter(pl.col("week_period") == "Weekday").row(
        0, named=True
    )
    we_row = complexity_by_period.filter(pl.col("week_period") == "Weekend").row(
        0, named=True
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            t("complexity_weekday", category="weekend"),
            f"{wd_row['mean_complexity']:.2f}",
            delta=f"{wd_row['mean_steps']:.1f} steps",
        )
    with col2:
        st.metric(
            t("complexity_weekend", category="weekend"),
            f"{we_row['mean_complexity']:.2f}",
            delta=f"{we_row['mean_steps']:.1f} steps",
        )
    with col3:
        diff_pct = (
            (we_row["mean_complexity"] - wd_row["mean_complexity"])
            / wd_row["mean_complexity"]
        ) * 100
        st.metric(t("difference"), f"{diff_pct:+.2f}%")

    # 🎨 VISUALISATION (3 panels)
    fig = make_subplots(
        rows=1,
        cols=3,
        subplot_titles=(
            t("score_complexite"),
            t("nombre_etapes"),
            t("nombre_ingredients"),
        ),
        specs=[[{"type": "bar"}, {"type": "bar"}, {"type": "bar"}]],
    )

    # --- PANEL 1: Score complexité ---
    fig.add_trace(
        go.Bar(
            x=complexity_by_period["week_period"],
            y=complexity_by_period["mean_complexity"],
            marker=dict(
                color=period_colors_btk,
                line=dict(color=ColorTheme.TEXT_SECONDARY, width=1),
            ),
            text=[f"{val:.2f}" for val in complexity_by_period["mean_complexity"]],
            textposition="outside",
            textfont=dict(size=12, color=ColorTheme.TEXT_PRIMARY),
            name=t("label_average"),
            showlegend=False,
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=complexity_by_period["week_period"],
            y=complexity_by_period["median_complexity"],
            mode="lines+markers",
            line=dict(color=ColorTheme.TEXT_PRIMARY, width=2, dash="dash"),
            marker=dict(size=8, color=ColorTheme.TEXT_PRIMARY, symbol="square"),
            name=t("label_median"),
        ),
        row=1,
        col=1,
    )

    # --- PANEL 2: Nombre d'étapes ---
    fig.add_trace(
        go.Bar(
            x=complexity_by_period["week_period"],
            y=complexity_by_period["mean_steps"],
            marker=dict(
                color=period_colors_btk,
                line=dict(color=ColorTheme.TEXT_SECONDARY, width=1),
            ),
            text=[f"{val:.1f}" for val in complexity_by_period["mean_steps"]],
            textposition="outside",
            textfont=dict(size=12, color=ColorTheme.TEXT_PRIMARY),
            name=t("label_average"),
            showlegend=False,
        ),
        row=1,
        col=2,
    )

    fig.add_trace(
        go.Scatter(
            x=complexity_by_period["week_period"],
            y=complexity_by_period["median_steps"],
            mode="lines+markers",
            line=dict(color=ColorTheme.TEXT_PRIMARY, width=2, dash="dash"),
            marker=dict(size=8, color=ColorTheme.TEXT_PRIMARY, symbol="square"),
            name=t("label_median"),
        ),
        row=1,
        col=2,
    )

    # --- PANEL 3: Nombre d'ingrédients ---
    fig.add_trace(
        go.Bar(
            x=complexity_by_period["week_period"],
            y=complexity_by_period["mean_ingredients"],
            marker=dict(
                color=period_colors_btk,
                line=dict(color=ColorTheme.TEXT_SECONDARY, width=1),
            ),
            text=[f"{val:.1f}" for val in complexity_by_period["mean_ingredients"]],
            textposition="outside",
            textfont=dict(size=12, color=ColorTheme.TEXT_PRIMARY),
            name=t("label_average"),
            showlegend=False,
        ),
        row=1,
        col=3,
    )

    fig.add_trace(
        go.Scatter(
            x=complexity_by_period["week_period"],
            y=complexity_by_period["median_ingredients"],
            mode="lines+markers",
            line=dict(color=ColorTheme.TEXT_PRIMARY, width=2, dash="dash"),
            marker=dict(size=8, color=ColorTheme.TEXT_PRIMARY, symbol="square"),
            name=t("label_median"),
        ),
        row=1,
        col=3,
    )

    # Axes
    fig.update_yaxes(title_text="Complexity Score", row=1, col=1)
    fig.update_yaxes(title_text=t("nombre_etapes"), row=1, col=2)
    fig.update_yaxes(title_text=t("nombre_ingredients"), row=1, col=3)

    fig.update_xaxes(title_text=t("axis_period"), row=1, col=1)
    fig.update_xaxes(title_text=t("axis_period"), row=1, col=2)
    fig.update_xaxes(title_text=t("axis_period"), row=1, col=3)

    # Appliquer thème
    chart_theme.apply_subplot_theme(fig, num_rows=1, num_cols=3)
    fig.update_layout(height=500)

    st.plotly_chart(fig, use_container_width=True)

    # 📝 INTERPRÉTATION
    st.info(t('complexity_interpretation', category='weekend'))


def analyse_weekend_nutrition() -> None:
    """
    📊 ANALYSE 4: Nutrition (Weekday vs Weekend)

    Insight: Profils nutritionnels globalement similaires.
    Une seule différence significative: protéines (-3% le week-end).
    """
    df = load_recipes_clean()

    # Ajout colonne week_period
    df = df.with_columns(
        pl.when(pl.col("is_weekend") == 1)
        .then(pl.lit("Weekend"))
        .otherwise(pl.lit("Weekday"))
        .alias("week_period")
    )

    week_period_order = ["Weekday", "Weekend"]

    # Agrégation nutritionnelle
    nutrition_by_period = (
        df.group_by("week_period")
        .agg(
            [
                pl.mean("calories").alias("mean_calories"),
                pl.mean("protein_pct").alias("mean_protein"),
                pl.mean("total_fat_pct").alias("mean_fat"),
                pl.mean("sat_fat_pct").alias("mean_sat_fat"),
                pl.mean("sugar_pct").alias("mean_sugar"),
                pl.mean("sodium_pct").alias("mean_sodium"),
            ]
        )
        .join(
            pl.DataFrame(
                {
                    "week_period": week_period_order,
                    "order": range(len(week_period_order)),
                }
            ),
            on="week_period",
            how="left",
        )
        .sort("order")
        .drop("order")
    )

    # Tests statistiques
    nutrients_list = [
        ("Calories", "calories", "mean_calories", 0),
        (t("proteines_pct"), "protein_pct", "mean_protein", 1),
        ( t("lipides_pct"), "total_fat_pct", "mean_fat", 1),
        ( t("graisses_sat_pct"), "sat_fat_pct", "mean_sat_fat", 1),
        ("Sucres (%)", "sugar_pct", "mean_sugar", 1),
        ("Sodium (%)", "sodium_pct", "mean_sodium", 1),
    ]

    results = []

    for nutrient_name, col_polars, col_agg, decimals in nutrients_list:
        weekday_vals = df.filter(pl.col("week_period") == "Weekday")[
            col_polars
        ].to_numpy()
        weekend_vals = df.filter(pl.col("week_period") == "Weekend")[
            col_polars
        ].to_numpy()

        t_stat, p_value = stats.ttest_ind(weekday_vals, weekend_vals, equal_var=True)

        wd_val = nutrition_by_period.filter(pl.col("week_period") == "Weekday")[
            col_agg
        ][0]
        we_val = nutrition_by_period.filter(pl.col("week_period") == "Weekend")[
            col_agg
        ][0]
        diff_pct = ((we_val - wd_val) / wd_val) * 100

        results.append(
            {
                "nutrient": nutrient_name,
                "weekday": wd_val,
                "weekend": we_val,
                "diff_pct": diff_pct,
                "p_value": p_value,
                "significant": bool(p_value < 0.05),
                "decimals": decimals,
            }
        )

    results_df = pl.DataFrame(results)

    # 📊 MÉTRIQUES BANNIÈRE
    signif_count = results_df.filter(pl.col("significant"))["nutrient"].len()
    max_diff = results_df.sort(pl.col("diff_pct").abs(), descending=True).row(
        0, named=True
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(t("nutrients_analyzed", category="common"), "6")
    with col2:
        st.metric(t("significant_differences", category="common"), f"{signif_count}")
    with col3:
        st.metric(
            t("max_gap", category="weekend").format(nutrient=max_diff['nutrient']),
            f"{max_diff['diff_pct']:+.1f}%",
            delta="p<0.05" if max_diff["significant"] else "NS",
        )

    # 🎨 VISUALISATION: Bar chart horizontal
    fig = go.Figure()

    # Couleurs selon direction et significativité
    colors = [
        (
            ColorTheme.CHART_COLORS[2]
            if (row["diff_pct"] < 0 and row["significant"])
            else (
                ColorTheme.ORANGE_PRIMARY
                if (row["diff_pct"] > 0 and row["significant"])
                else (
                    ColorTheme.CHART_COLORS[1]
                    if row["diff_pct"] < 0
                    else ColorTheme.ORANGE_LIGHT
                )
            )
        )
        for row in results_df.iter_rows(named=True)
    ]

    fig.add_trace(
        go.Bar(
            y=results_df["nutrient"],
            x=results_df["diff_pct"],
            orientation="h",
            marker=dict(
                color=colors,
                line=dict(color=ColorTheme.TEXT_SECONDARY, width=1),
            ),
            text=[
                f"{row['diff_pct']:+.1f}%" + (" *" if row["significant"] else "")
                for row in results_df.iter_rows(named=True)
            ],
            textposition="outside",
            textfont=dict(size=12, color=ColorTheme.TEXT_PRIMARY),
            showlegend=False,
            hovertemplate=("<b>%{y}</b><br>" "Écart: %{x:+.1f}%<br>" "<extra></extra>"),
        )
    )

    # Ligne zéro
    fig.add_vline(x=0, line=dict(color=ColorTheme.TEXT_PRIMARY, width=2))

    # Mise en page
    fig.update_xaxes(
        title_text=t("legend_weekend_diff", category="trends"),
        title_font=dict(size=13, color=ColorTheme.TEXT_PRIMARY),
    )

    fig.update_yaxes(title_text="", autorange="reversed")

    chart_theme.apply_chart_theme(fig)
    fig.update_layout(
        title={
            "text": "Profil nutritionnel: Écarts Weekend vs Weekday<br><sub>(* = effet significatif, p < 0.05)</sub>",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 16, "color": ColorTheme.TEXT_PRIMARY},
        },
        height=500,
    )

    st.plotly_chart(fig, use_container_width=True)

    # 📝 INTERPRÉTATION
    st.info(t('nutrition_interpretation', category='weekend'))


def analyse_weekend_ingredients() -> None:
    """
    📊 ANALYSE 5: Ingrédients les plus variables (Weekday vs Weekend)

    Insight: Écarts faibles (<0.4pp) sur ingrédients.
    Week-end: +cinnamon, +canola oil. Semaine: +mozzarella, +chicken breasts.
    """
    df = load_recipes_clean()

    # Ajout colonne week_period
    df = df.with_columns(
        pl.when(pl.col("is_weekend") == 1)
        .then(pl.lit("Weekend"))
        .otherwise(pl.lit("Weekday"))
        .alias("week_period")
    )

    week_period_order = ["Weekday", "Weekend"]

    # Extraction des ingrédients par période
    ingredients_by_period = {}
    n_recipes_by_period = {}

    for period in week_period_order:
        period_df = df.filter(pl.col("week_period") == period)
        n_recipes_by_period[period] = period_df.height
        ingredient_counts = (
            period_df.select(pl.col("ingredients").explode())
            .group_by("ingredients")
            .agg(pl.count().alias("count"))
        )
        ingredients_by_period[period] = dict(
            zip(
                ingredient_counts["ingredients"].to_list(),
                ingredient_counts["count"].to_list(),
            )
        )

    all_ingredients = set().union(
        *[set(ing.keys()) for ing in ingredients_by_period.values()]
    )

    # Tests statistiques Chi-2
    ingredients_results = []
    for ing in all_ingredients:
        weekday_count = ingredients_by_period["Weekday"].get(ing, 0)
        weekend_count = ingredients_by_period["Weekend"].get(ing, 0)
        weekday_freq = (weekday_count / n_recipes_by_period["Weekday"]) * 100
        weekend_freq = (weekend_count / n_recipes_by_period["Weekend"]) * 100

        contingency = np.array(
            [
                [weekday_count, n_recipes_by_period["Weekday"] - weekday_count],
                [weekend_count, n_recipes_by_period["Weekend"] - weekend_count],
            ]
        )

        try:
            chi2_stat, p_val, _, _ = chi2_contingency(contingency)
        except Exception:
            chi2_stat, p_val = 0, 1.0  # noqa: F841

        ingredients_results.append(
            {
                "ingredient": ing,
                "weekday_freq": weekday_freq,
                "weekend_freq": weekend_freq,
                "mean_freq": (weekday_freq + weekend_freq) / 2,
                "diff_abs": weekend_freq - weekday_freq,
                "p_value": p_val,
            }
        )

    ingredients_df = pl.DataFrame(ingredients_results)

    # Filtrage strict
    FREQ_THRESHOLD = 1
    ABS_DIFF_THRESHOLD = 0.2

    ingredients_filtered = ingredients_df.filter(
        (pl.col("mean_freq") >= FREQ_THRESHOLD)
        & (pl.col("diff_abs").abs() >= ABS_DIFF_THRESHOLD)
        & (pl.col("p_value") < 0.05)
    )

    # 📊 MÉTRIQUES BANNIÈRE
    total_ingredients = len(all_ingredients)
    filtered_ingredients = len(ingredients_filtered)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(t("total_ingredients", category="common"), f"{total_ingredients:,}")
    with col2:
        st.metric(t("variable_ingredients", category="common"), f"{filtered_ingredients}")
    with col3:
        pct_filtered = (filtered_ingredients / total_ingredients) * 100
        st.metric("% variables", f"{pct_filtered:.1f}%")

    # 🎨 VISUALISATION (Top 20)
    if len(ingredients_filtered) > 0:
        top_ingredients = ingredients_filtered.sort("diff_abs", descending=False).tail(
            20
        )

        # Couleurs
        colors = [
            (ColorTheme.ORANGE_PRIMARY if x < 0 else ColorTheme.CHART_COLORS[2])
            for x in top_ingredients["diff_abs"]
        ]

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                y=top_ingredients["ingredient"],
                x=top_ingredients["diff_abs"],
                orientation="h",
                marker=dict(
                    color=colors,
                    line=dict(color=ColorTheme.TEXT_SECONDARY, width=1),
                ),
                text=[f"{val:+.2f}" for val in top_ingredients["diff_abs"]],
                textposition="outside",
                textfont=dict(size=11, color=ColorTheme.TEXT_PRIMARY),
                showlegend=False,
                hovertemplate=(
                    "<b>%{y}</b><br>" "Écart: %{x:+.2f}pp<br>" "<extra></extra>"
                ),
            )
        )

        # Ligne zéro
        fig.add_vline(x=0, line=dict(color=ColorTheme.TEXT_PRIMARY, width=1.5))

        # Axes
        fig.update_xaxes(
            title_text="Δ Weekend - Weekday (pp)",
            title_font=dict(size=13, color=ColorTheme.TEXT_PRIMARY),
        )
        fig.update_yaxes(autorange="reversed")

        chart_theme.apply_chart_theme(fig)
        fig.update_layout(
            title={
                "text": f"Top {len(top_ingredients)} ingrédients: Écarts Weekend vs Weekday (+ si week-end)",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 16, "color": ColorTheme.TEXT_PRIMARY},
            },
            height=max(500, len(top_ingredients) * 25),
        )

        st.plotly_chart(fig, use_container_width=True)

        # 📝 INTERPRÉTATION
        st.info(t('ingredients_interpretation', category='weekend'))
    else:
        st.warning(
            "⚠️ Aucun ingrédient ne satisfait les critères de filtrage (freq ≥1%, |diff| ≥0.2pp, p<0.05)"
        )


def analyse_weekend_tags() -> None:
    """
    📊 ANALYSE 6: Tags les plus variables (Weekday vs Weekend)

    Insight: Écarts faibles (<0.5pp) sur tags.
    Week-end: +vegetarian, +christmas, +breakfast. Semaine: +one-dish-meal, +beginner-cook.
    """
    df = load_recipes_clean()

    # Ajout colonne week_period
    df = df.with_columns(
        pl.when(pl.col("is_weekend") == 1)
        .then(pl.lit("Weekend"))
        .otherwise(pl.lit("Weekday"))
        .alias("week_period")
    )

    week_period_order = ["Weekday", "Weekend"]

    # Extraction des tags par période
    tags_by_period = {}
    n_recipes_by_period_tags = {}

    for period in week_period_order:
        period_df = df.filter(pl.col("week_period") == period)
        n_recipes_by_period_tags[period] = period_df.height
        tag_counts = (
            period_df.select(pl.col("tags").explode())
            .group_by("tags")
            .agg(pl.count().alias("count"))
        )
        tags_by_period[period] = dict(
            zip(tag_counts["tags"].to_list(), tag_counts["count"].to_list())
        )

    all_tags = set().union(*[set(tag.keys()) for tag in tags_by_period.values()])

    # Tests statistiques Chi-2
    tags_results = []
    for tag in all_tags:
        weekday_count = tags_by_period["Weekday"].get(tag, 0)
        weekend_count = tags_by_period["Weekend"].get(tag, 0)
        weekday_freq = (weekday_count / n_recipes_by_period_tags["Weekday"]) * 100
        weekend_freq = (weekend_count / n_recipes_by_period_tags["Weekend"]) * 100

        observed = [
            [weekday_count, n_recipes_by_period_tags["Weekday"] - weekday_count],
            [weekend_count, n_recipes_by_period_tags["Weekend"] - weekend_count],
        ]
        try:
            chi2, p_value, _, _ = chi2_contingency(observed)
        except Exception:
            chi2, p_value = np.nan, np.nan  # noqa: F841

        tags_results.append(
            {
                "tag": tag,
                "weekday_freq": weekday_freq,
                "weekend_freq": weekend_freq,
                "mean_freq": (weekday_freq + weekend_freq) / 2,
                "diff_abs": weekend_freq - weekday_freq,
                "p_value": p_value,
            }
        )

    tags_df = pl.DataFrame(tags_results)

    # Filtrage strict
    FREQ_THRESHOLD = 1
    ABS_DIFF_THRESHOLD = 0.2

    tags_filtered = tags_df.filter(
        (pl.col("mean_freq") >= FREQ_THRESHOLD)
        & (pl.col("diff_abs").abs() >= ABS_DIFF_THRESHOLD)
        & (pl.col("p_value") < 0.05)
    )

    # 📊 MÉTRIQUES BANNIÈRE
    total_tags = len(all_tags)
    filtered_tags = len(tags_filtered)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Tags totaux", f"{total_tags:,}")
    with col2:
        st.metric("Tags variables", f"{filtered_tags}")
    with col3:
        pct_filtered = (filtered_tags / total_tags) * 100
        st.metric("% variables", f"{pct_filtered:.1f}%")

    # 🎨 VISUALISATION (Top 20)
    if len(tags_filtered) > 0:
        top_tags = tags_filtered.sort("diff_abs", descending=False).tail(20)

        # Couleurs
        colors = [
            (ColorTheme.ORANGE_PRIMARY if x < 0 else ColorTheme.CHART_COLORS[2])
            for x in top_tags["diff_abs"]
        ]

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                y=top_tags["tag"],
                x=top_tags["diff_abs"],
                orientation="h",
                marker=dict(
                    color=colors,
                    line=dict(color=ColorTheme.TEXT_SECONDARY, width=1),
                ),
                text=[f"{val:+.2f}" for val in top_tags["diff_abs"]],
                textposition="outside",
                textfont=dict(size=11, color=ColorTheme.TEXT_PRIMARY),
                showlegend=False,
                hovertemplate=(
                    "<b>%{y}</b><br>" "Écart: %{x:+.2f}pp<br>" "<extra></extra>"
                ),
            )
        )

        # Ligne zéro
        fig.add_vline(x=0, line=dict(color=ColorTheme.TEXT_PRIMARY, width=1.5))

        # Axes
        fig.update_xaxes(
            title_text="Δ Weekend - Weekday (pp)",
            title_font=dict(size=13, color=ColorTheme.TEXT_PRIMARY),
        )
        fig.update_yaxes(autorange="reversed")

        chart_theme.apply_chart_theme(fig)
        fig.update_layout(
            title={
                "text": f"Top {len(top_tags)} tags: Écarts Weekend vs Weekday",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 16, "color": ColorTheme.TEXT_PRIMARY},
            },
            height=max(500, len(top_tags) * 25),
        )

        st.plotly_chart(fig, use_container_width=True)

        # 📝 INTERPRÉTATION
        st.info(t('tags_interpretation', category='weekend'))
    else:
        st.warning(
            "⚠️ Aucun tag ne satisfait les critères de filtrage (freq ≥1%, |diff| ≥0.2pp, p<0.05)"
        )


def render_weekend_analysis() -> None:
    """
    Point d'entrée principal pour les analyses d'effet week-end.

    Format: Page continue affichant toutes les analyses d'un coup (comme Tendances).
    """
    st.markdown(
        f'<h1 style="margin-top: 0; padding-top: 0;">📆 {t("main_title", category="weekend")}</h1>',
        unsafe_allow_html=True,
    )

    st.markdown(t("main_description", category="weekend"))

    # Affichage de toutes les analyses en continu (comme page Tendances)

    st.subheader(f"📊 {t('volume_title', category='weekend')}")
    analyse_weekend_volume()
    st.markdown("---")

    st.subheader(f"⏱️ {t('duration_title', category='weekend')}")
    analyse_weekend_duree()
    st.markdown("---")

    st.subheader(f"🔧 {t('complexity_title', category='weekend')}")
    analyse_weekend_complexite()
    st.markdown("---")

    st.subheader(f"🥗 {t('nutrition_title', category='weekend')}")
    analyse_weekend_nutrition()
    st.markdown("---")

    st.subheader(f"🥘 {t('ingredients_title', category='weekend')}")
    analyse_weekend_ingredients()
    st.markdown("---")

    st.subheader(f"🏷️ {t('tags_title', category='weekend')}")
    analyse_weekend_tags()
