"""Module d'analyse des ratings/notes temporelles.

Ce module contient les analyses de l'évolution des ratings dans le temps,
incluant les analyses de tendances, saisonnalité et effet weekend.
Converti depuis rating_analysis_integration.py avec thème Back to the Kitchen.
"""

import streamlit as st
import pandas as pd
import polars as pl
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import kendalltau, linregress, f_oneway, kruskal
import statsmodels.api as sm

# Import du thème graphique
from utils import chart_theme
from utils import colors

# Import des utilitaires de chargement avec cache
from data.cached_loaders import get_ratings_longterm as load_ratings_for_longterm_analysis

# Import direct sans cache (utilisé rarement)
from mangetamain_data_utils.data_utils_ratings import load_clean_interactions


def weighted_spearman(x, y, w):
    """Calcule le coefficient de corrélation de Spearman pondéré.

    Args:
        x: Variable X
        y: Variable Y
        w: Poids pour chaque observation

    Returns:
        float: Coefficient de Spearman pondéré
    """
    # Rang pondéré
    rank_x = pd.Series(x).rank(method="average").values
    rank_y = pd.Series(y).rank(method="average").values

    # Corrélation pondérée entre les rangs
    cov_matrix = np.cov(rank_x, rank_y, aweights=w)
    cov_xy = cov_matrix[0, 1]
    var_x = np.cov(rank_x, aweights=w)
    var_y = np.cov(rank_y, aweights=w)

    # Gestion du cas où np.cov retourne un scalaire
    if np.ndim(var_x) == 0:
        std_x = np.sqrt(var_x)
    else:
        std_x = np.sqrt(var_x[0, 0])

    if np.ndim(var_y) == 0:
        std_y = np.sqrt(var_y)
    else:
        std_y = np.sqrt(var_y[0, 0])

    weighted_corr = cov_xy / (std_x * std_y)
    return weighted_corr


def analyse_ratings_validation_ponderee():
    """Analyse 1: Validation méthodologique - Tests pondérés vs non-pondérés."""
    st.markdown(
        """
        Comparaison des méthodes **pondérées** vs **non-pondérées** pour analyser
        l'évolution des ratings dans le temps. Cette analyse démontre l'importance
        de la pondération par le volume d'interactions.
        """
    )

    # Chargement des données
    with st.spinner("Chargement des statistiques mensuelles..."):
        monthly_stats, metadata = load_ratings_for_longterm_analysis(
            min_interactions=100, return_metadata=True, verbose=False
        )

    if monthly_stats.empty:
        st.error("❌ Aucune donnée disponible")
        return

    # Préparation du DataFrame
    monthly_df = monthly_stats.copy()
    monthly_df["date"] = pd.to_datetime(monthly_df["date"])
    monthly_df = monthly_df.sort_values("date")
    monthly_df["mean_rating"] = pd.to_numeric(
        monthly_df["mean_rating"], errors="coerce"
    )
    monthly_df["std_rating"] = pd.to_numeric(
        monthly_df.get("std_rating", 0), errors="coerce"
    ).fillna(0)
    monthly_df["n_interactions"] = pd.to_numeric(
        monthly_df["n_interactions"], errors="coerce"
    ).fillna(0)
    monthly_df = monthly_df.dropna(subset=["mean_rating"])

    # Variables pour tests statistiques
    monthly_sorted = monthly_df.sort_values("date")
    time_index = range(len(monthly_sorted))
    ratings = monthly_sorted["mean_rating"].values
    weights = np.sqrt(monthly_df["n_interactions"].values)
    weights_normalized = weights / weights.sum()

    # Analyse de l'hétérogénéité
    cv_volumes = np.std(monthly_df["n_interactions"]) / np.mean(
        monthly_df["n_interactions"]
    )
    # noqa: F841
    # Création du graphique avec 4 subplots
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "Distribution des volumes mensuels",
            "Évolution des poids dans le temps",
            "Ratings pondérés par volume",
            "Variance des ratings",
        ),
        specs=[
            [{"type": "histogram"}, {"type": "scatter"}],
            [{"type": "scatter"}, {"type": "bar"}],
        ],
    )

    # (1) Distribution des volumes (histogram)
    fig.add_trace(
        go.Histogram(
            x=monthly_df["n_interactions"],
            nbinsx=20,
            marker=dict(
                color=colors.CHART_COLORS[0],
                opacity=0.7,
                line=dict(width=0),  # Pas de contour
            ),
            showlegend=False,
        ),
        row=1,
        col=1,
    )

    # (2) Poids calculés dans le temps
    fig.add_trace(
        go.Scatter(
            x=monthly_df["date"],
            y=weights_normalized,
            mode="lines+markers",
            line=dict(color=colors.CHART_COLORS[2], width=2),
            marker=dict(size=4),
            name="Poids normalisés",
            showlegend=True,
        ),
        row=1,
        col=2,
    )

    # (3) Ratings avec taille proportionnelle au poids
    sizes = weights_normalized * 1000

    fig.add_trace(
        go.Scatter(
            x=monthly_df["date"],
            y=monthly_df["mean_rating"],
            mode="markers",
            marker=dict(
                size=sizes * 2,  # Points beaucoup plus gros
                color=monthly_df["n_interactions"],
                colorscale="YlOrRd",  # Colorscale Plotly: Jaune → Orange → Rouge
                opacity=0.7,
                line=dict(color=colors.TEXT_PRIMARY, width=0.5),
                colorbar=dict(
                    title=dict(
                        text="Volume", font=dict(color=colors.TEXT_PRIMARY, size=12)
                    ),
                    tickfont=dict(color=colors.TEXT_PRIMARY, size=10),
                    x=0.46,  # Repositionné entre les 2 colonnes
                    len=0.35,
                    y=0.23,
                    yanchor="middle",
                ),
            ),
            showlegend=False,
        ),
        row=2,
        col=1,
    )

    # (4) Comparaison variance pondérée vs non-pondérée
    var_unweighted = np.var(monthly_df["mean_rating"])
    var_weighted = np.average(
        (
            monthly_df["mean_rating"]
            - np.average(monthly_df["mean_rating"], weights=weights)
        )
        ** 2,
        weights=weights,
    )

    fig.add_trace(
        go.Bar(
            x=["Non pondérée", "Pondérée"],
            y=[var_unweighted, var_weighted],
            marker=dict(
                color=[colors.CHART_COLORS[2], colors.CHART_COLORS[0]],
                opacity=0.8,
                line=dict(width=0),  # Pas de contour
            ),
            text=[f"{var_unweighted:.4f}", f"{var_weighted:.4f}"],
            textposition="outside",
            textfont=dict(size=12, color=colors.TEXT_PRIMARY),
            showlegend=False,
        ),
        row=2,
        col=2,
    )

    # Axes
    fig.update_xaxes(title_text="Nombre d'interactions", row=1, col=1)
    fig.update_yaxes(title_text="Fréquence (log)", type="log", row=1, col=1)

    fig.update_xaxes(title_text="Date", row=1, col=2)
    fig.update_yaxes(title_text="Poids normalisé", row=1, col=2)

    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Rating moyen", row=2, col=1)

    fig.update_yaxes(title_text="Variance", row=2, col=2)

    # Mise en forme
    fig.update_layout(
        height=900,
        showlegend=True,
        title_text="Impact de la pondération par volume sur l'analyse",
        bargap=0,  # Supprime l'espace entre les barres de l'histogramme
    )

    # Application du thème "Back to the Kitchen"
    chart_theme.apply_subplot_theme(fig, num_rows=2, num_cols=2)

    st.plotly_chart(fig, use_container_width=True)

    # Tests statistiques
    tau, p_value_kendall = kendalltau(time_index, ratings)
    slope, intercept, r_value, p_value_reg, std_err = linregress(time_index, ratings)

    # Tests pondérés
    x = np.array(time_index)
    y = ratings
    w = weights

    # Régression pondérée (WLS)
    X_const = sm.add_constant(x)
    wls_model = sm.WLS(y, X_const, weights=w)
    wls_result = wls_model.fit()
    y_pred_weighted = wls_result.predict(X_const)
    y_mean_weighted = np.average(y, weights=w)
    r2_weighted = 1 - np.average((y - y_pred_weighted) ** 2, weights=w) / np.average(
        (y - y_mean_weighted) ** 2, weights=w
    )

    bias_slope = (
        abs(wls_result.params[1] - slope) / abs(slope) * 100 if slope != 0 else 0
    )

    # Métriques
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("CV Volumes", f"{cv_volumes:.2f}")
    with col2:
        st.metric("Biais pente", f"{bias_slope:.1f}%")
    with col3:  # noqa: F841
        st.metric("R² pondéré", f"{r2_weighted:.4f}")
    with col4:
        st.metric("P-value WLS", f"{wls_result.pvalues[1]:.4f}")

    # Interprétation
    st.info(
        "🔬 **Interprétation**: L'analyse méthodologique révèle une **hétérogénéité extrême des volumes d'interactions** mensuels "
        f"(Coefficient de variation = **{cv_volumes:.2f}**), ce qui rend les tests statistiques standards **non fiables**. "
        f"Les tests non-pondérés s'avèrent **fortement biaisés** (biais de pente de **+{bias_slope:.1f}%**), car ils donnent une importance "
        "disproportionnée aux périodes de **très forte activité** (comme 2008-2009), écrasant l'influence des autres périodes. "
        "L'utilisation de **méthodes pondérées** (comme la régression WLS et le Spearman pondéré) est donc **indispensable** pour corriger "
        "ce biais et obtenir une **interprétation juste et robuste** des tendances réelles du comportement utilisateur."
    )


def analyse_ratings_tendance_temporelle():
    """Analyse 2: Tendance temporelle des ratings (Méthodes pondérées)."""
    st.markdown(
        """
        Analyse de l'évolution des ratings dans le temps avec **régression WLS pondérée**.
        Examine la stabilité, le volume d'interactions et la corrélation volume-qualité.
        """
    )

    # Chargement des données
    with st.spinner("Chargement des statistiques mensuelles..."):
        monthly_stats, _ = load_ratings_for_longterm_analysis(
            min_interactions=100, return_metadata=True
        )

    if monthly_stats.empty:
        st.error("❌ Aucune donnée disponible")
        return

    # Préparation du DataFrame
    monthly_df = monthly_stats.copy()
    monthly_df["date"] = pd.to_datetime(monthly_df["date"])
    monthly_df = monthly_df.sort_values("date")
    monthly_df = monthly_df.dropna(subset=["mean_rating"])

    # Variables pour tests
    ratings = monthly_df["mean_rating"].values
    volumes = monthly_df["n_interactions"].values
    weights = np.sqrt(volumes)
    weights_normalized = weights / weights.sum()

    # Calcul tendance pondérée
    X_trend = np.arange(len(monthly_df))
    X_const_trend = sm.add_constant(X_trend)  # noqa: F841
    wls_trend = sm.WLS(ratings, X_const_trend, weights=weights)
    wls_trend_result = wls_trend.fit()
    trend_line_weighted = wls_trend_result.predict(X_const_trend)

    # R² pondéré
    y_mean_weighted = np.average(ratings, weights=weights)
    r2_weighted = 1 - np.average(
        (ratings - trend_line_weighted) ** 2, weights=weights
    ) / np.average((ratings - y_mean_weighted) ** 2, weights=weights)

    # Écart-type pondéré
    weighted_std = np.sqrt(
        np.average(
            (ratings - np.average(ratings, weights=weights)) ** 2, weights=weights
        )
    )

    # Régression volume vs qualité
    X_vol_const = sm.add_constant(volumes)
    wls_vol = sm.WLS(ratings, X_vol_const, weights=weights)
    wls_vol_result = wls_vol.fit()
    vol_pred = wls_vol_result.predict(X_vol_const)

    # Création du graphique avec 4 subplots
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "Évolution des ratings - Tendance pondérée",
            "Volume d'interactions",
            "Stabilité des ratings",
            "Corrélation volume-qualité",
        ),
    )

    # (1) Tendance des ratings
    fig.add_trace(
        go.Scatter(
            x=monthly_df["date"],
            y=ratings,
            mode="lines+markers",
            line=dict(color=colors.CHART_COLORS[3], width=2),
            marker=dict(size=4),
            name="Rating moyen",
            showlegend=True,
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=monthly_df["date"],
            y=trend_line_weighted,
            mode="lines",
            line=dict(color=colors.CHART_COLORS[2], width=2, dash="dash"),
            name=f"Tendance ({wls_trend_result.params[1]:.4f}/mois)",
            showlegend=True,
        ),
        row=1,
        col=1,
    )

    # (2) Volume d'interactions
    sizes = weights_normalized * 500
    fig.add_trace(
        go.Scatter(
            x=monthly_df["date"],
            y=volumes,
            mode="markers",
            marker=dict(
                size=sizes * 2,  # Points beaucoup plus gros
                color=colors.CHART_COLORS[0],
                opacity=0.7,
                line=dict(width=0),  # Pas de contour
            ),
            showlegend=False,
        ),
        row=1,
        col=2,
    )

    # (3) Stabilité (écart-type)
    fig.add_trace(
        go.Scatter(
            x=monthly_df["date"],
            y=monthly_df["std_rating"],
            mode="lines+markers",
            line=dict(color=colors.CHART_COLORS[1], width=2),
            marker=dict(size=4),
            name="Écart-type brut",
            showlegend=True,
        ),
        row=2,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=[monthly_df["date"].min(), monthly_df["date"].max()],
            y=[weighted_std, weighted_std],
            mode="lines",
            line=dict(color=colors.CHART_COLORS[2], width=2, dash="dash"),
            name=f"Écart-type pondéré ({weighted_std:.3f})",
            showlegend=True,
        ),
        row=2,
        col=1,
    )

    # (4) Relation volume vs qualité
    sizes_scatter = weights_normalized * 300
    fig.add_trace(
        go.Scatter(
            x=volumes,
            y=ratings,
            mode="markers",
            marker=dict(
                size=sizes_scatter * 2,  # Points plus gros
                color=weights_normalized,
                colorscale="YlOrRd",  # Colorscale charte: Jaune → Orange → Rouge
                opacity=0.7,
                line=dict(width=0),  # Pas de contour
                colorbar=dict(title="Poids", x=1.0, len=0.4, y=0.25),
            ),
            showlegend=False,
        ),
        row=2,
        col=2,
    )

    # Ligne de régression
    fig.add_trace(
        go.Scatter(
            x=volumes,
            y=vol_pred,
            mode="lines",
            line=dict(color=colors.CHART_COLORS[2], width=2, dash="dash"),
            name="Régression pondérée",
            showlegend=True,
        ),
        row=2,
        col=2,
    )

    # Axes
    fig.update_yaxes(title_text="Rating moyen", row=1, col=1)
    fig.update_yaxes(title_text="Nombre d'interactions", row=1, col=2)
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Écart-type", row=2, col=1)
    fig.update_xaxes(title_text="Nombre d'interactions", row=2, col=2)
    fig.update_yaxes(title_text="Rating moyen", row=2, col=2)

    # Mise en forme
    fig.update_layout(
        height=900,
        showlegend=True,
        title_text=f"Analyse Temporelle - Pente: {wls_trend_result.params[1]:+.4f}/mois",
    )

    # Application du thème
    chart_theme.apply_subplot_theme(fig, num_rows=2, num_cols=2)

    st.plotly_chart(fig, use_container_width=True)

    # Corrélation pondérée
    vol_qual_weighted = weighted_spearman(volumes, ratings, weights)

    # Métriques
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Pente pondérée", f"{wls_trend_result.params[1]:.6f} pts/mois")
    with col2:
        st.metric("R² pondéré", f"{r2_weighted:.4f}")
    with col3:
        st.metric("P-value", f"{wls_trend_result.pvalues[1]:.4f}")
    with col4:
        st.metric("Corr. volume-qualité", f"{vol_qual_weighted:.3f}")

    # Interprétation
    st.info(
        "📈 **Interprétation**: L'analyse temporelle pondérée révèle une **stabilité remarquable des notes moyennes** sur le long terme, "
        "contredisant l'intuition d'une éventuelle dégradation ou amélioration. "
        f"La tendance observée est **statistiquement non significative** (pente annuelle = **{wls_trend_result.params[1] * 12:.4f} points/an**, "
        f"p-value = **{wls_trend_result.pvalues[1]:.2f}**). Le R² pondéré de **{r2_weighted:.3f}** confirme que le temps n'explique quasiment "
        "**aucune variance** dans les notes. On observe également une **faible corrélation négative** entre le **volume** d'interactions et "
        f"la **qualité** perçue (ρ = **{vol_qual_weighted:.3f}**), suggérant que les mois de **plus forte activité** sont associés à des "
        "**notes moyennes très légèrement plus basses**. Cette stabilité globale confirme que le **comportement de notation des utilisateurs** "
        "est **extrêmement constant** depuis 2005."
    )


def analyse_ratings_distribution():
    """Analyse 3: Évolution détaillée et corrélations (bandes de confiance)."""
    st.markdown(
        """
        Analyse détaillée de l'évolution des ratings avec **bandes de confiance**.
        Vue d'ensemble et vue zoomée de la stabilité temporelle.
        """
    )

    # Chargement des données
    with st.spinner("Chargement des statistiques mensuelles..."):
        monthly_stats, _ = load_ratings_for_longterm_analysis(
            min_interactions=100, return_metadata=True
        )

    if monthly_stats.empty:
        st.error("❌ Aucune donnée disponible")
        return

    # Préparation du DataFrame
    monthly_df = monthly_stats.copy()
    monthly_df["date"] = pd.to_datetime(monthly_df["date"])
    monthly_df = monthly_df.sort_values("date")
    monthly_df = monthly_df.dropna(subset=["mean_rating"])

    # Variables pour tests
    ratings = monthly_df["mean_rating"].values
    volumes = monthly_df["n_interactions"].values
    weights = np.sqrt(volumes)
    weights_normalized = weights / weights.sum()

    # --- CALCUL TENDANCE ET IC ---
    mean_rating_weighted = np.average(ratings, weights=weights)
    std_rating_weighted = np.sqrt(
        np.average((ratings - mean_rating_weighted) ** 2, weights=weights)
    )

    # IC 95%
    upper_bound_weighted = mean_rating_weighted + 1.96 * std_rating_weighted / np.sqrt(
        np.sum(weights)
    )
    lower_bound_weighted = mean_rating_weighted - 1.96 * std_rating_weighted / np.sqrt(
        np.sum(weights)
    )

    # Tendance (WLS)
    X_trend = np.arange(len(monthly_df))
    X_const_trend = sm.add_constant(X_trend)
    wls_trend = sm.WLS(ratings, X_const_trend, weights=weights)
    wls_trend_result = wls_trend.fit()
    trend_weighted_detailed = wls_trend_result.predict(X_const_trend)

    # Corrélation volume-qualité
    X_vol_detailed = sm.add_constant(volumes)
    wls_vol_detailed = sm.WLS(ratings, X_vol_detailed, weights=weights)
    wls_vol_detailed_result = wls_vol_detailed.fit()
    vol_pred_detailed = wls_vol_detailed_result.predict(X_vol_detailed)
    vol_qual_weighted = weighted_spearman(volumes, ratings, weights)

    # Création du graphique avec 3 subplots
    fig = make_subplots(
        rows=3,
        cols=1,
        subplot_titles=(
            "Évolution temporelle - Vue d'ensemble",
            "Évolution temporelle - Vue zoomée",
            "Corrélation volume-qualité",
        ),
        vertical_spacing=0.08,
    )

    # (1) Vue d'ensemble
    fig.add_trace(
        go.Scatter(
            x=monthly_df["date"],
            y=ratings,
            mode="lines+markers",
            line=dict(color=colors.CHART_COLORS[3], width=2),
            marker=dict(size=4),
            name="Rating moyen mensuel",
            showlegend=True,
        ),
        row=1,
        col=1,
    )

    # Bandes de confiance
    fig.add_trace(
        go.Scatter(
            x=monthly_df["date"].tolist() + monthly_df["date"].tolist()[::-1],
            y=[upper_bound_weighted] * len(monthly_df)
            + [lower_bound_weighted] * len(monthly_df),
            fill="toself",
            fillcolor=colors.get_rgba(colors.ORANGE_SECONDARY, 0.2),
            line=dict(color="rgba(255,255,255,0)"),
            name=f"IC 95% (±{1.96 * std_rating_weighted / np.sqrt(np.sum(weights)):.3f})",
            showlegend=True,
        ),
        row=1,
        col=1,
    )

    # Tendance
    fig.add_trace(
        go.Scatter(
            x=monthly_df["date"],
            y=trend_weighted_detailed,
            mode="lines",
            line=dict(color=colors.CHART_COLORS[2], width=2, dash="dash"),
            name=f"Tendance ({wls_trend_result.params[1]*12:.4f}/an)",
            showlegend=True,
        ),
        row=1,
        col=1,
    )

    # Moyenne
    fig.add_trace(
        go.Scatter(
            x=[monthly_df["date"].min(), monthly_df["date"].max()],
            y=[mean_rating_weighted, mean_rating_weighted],
            mode="lines",
            line=dict(color=colors.CHART_COLORS[0], width=2),
            name=f"Moyenne ({mean_rating_weighted:.3f})",
            showlegend=True,
        ),
        row=1,
        col=1,
    )

    # (2) Vue zoomée
    fig.add_trace(
        go.Scatter(
            x=monthly_df["date"],
            y=ratings,
            mode="lines+markers",
            line=dict(color=colors.CHART_COLORS[3], width=2),
            marker=dict(size=6),
            name="Rating moyen mensuel",
            showlegend=False,
        ),
        row=2,
        col=1,
    )

    # Bandes de confiance zoomées
    fig.add_trace(
        go.Scatter(
            x=monthly_df["date"].tolist() + monthly_df["date"].tolist()[::-1],
            y=[upper_bound_weighted] * len(monthly_df)
            + [lower_bound_weighted] * len(monthly_df),
            fill="toself",
            fillcolor=colors.get_rgba(colors.ORANGE_SECONDARY, 0.3),
            line=dict(color="rgba(255,255,255,0)"),
            name=f"IC 95% (±{1.96 * std_rating_weighted / np.sqrt(np.sum(weights)):.4f})",
            showlegend=False,
        ),
        row=2,
        col=1,
    )

    # Tendance zoomée
    fig.add_trace(
        go.Scatter(
            x=monthly_df["date"],
            y=trend_weighted_detailed,
            mode="lines",
            line=dict(color=colors.CHART_COLORS[2], width=3, dash="dash"),
            name=f"Tendance ({wls_trend_result.params[1]*12:.4f}/an)",
            showlegend=False,
        ),
        row=2,
        col=1,
    )

    # Moyenne zoomée
    fig.add_trace(
        go.Scatter(
            x=[monthly_df["date"].min(), monthly_df["date"].max()],
            y=[mean_rating_weighted, mean_rating_weighted],
            mode="lines",
            line=dict(color=colors.CHART_COLORS[0], width=2),
            name=f"Moyenne ({mean_rating_weighted:.3f})",
            showlegend=False,
        ),
        row=2,
        col=1,
    )

    # (3) Corrélation volume-qualité
    sizes_detailed = weights_normalized * 800
    fig.add_trace(
        go.Scatter(
            x=volumes,
            y=ratings,
            mode="markers",
            marker=dict(
                size=sizes_detailed * 2,  # Points plus gros
                color=monthly_df["n_interactions"],
                colorscale="YlOrRd",  # Colorscale charte: Jaune → Orange → Rouge
                opacity=0.7,
                line=dict(width=0),  # Pas de contour
                colorbar=dict(title="Volume", x=1.0, len=0.25, y=0.12),
            ),
            showlegend=False,
        ),
        row=3,
        col=1,
    )

    # Ligne de régression
    fig.add_trace(
        go.Scatter(
            x=volumes,
            y=vol_pred_detailed,
            mode="lines",
            line=dict(color=colors.CHART_COLORS[2], width=3, dash="dash"),
            name=f"Régression pondérée (ρ={vol_qual_weighted:.3f})",
            showlegend=True,
        ),
        row=3,
        col=1,
    )

    # Axes
    fig.update_yaxes(title_text="Rating moyen", row=1, col=1)
    fig.update_yaxes(
        title_text="Rating moyen", row=2, col=1, range=[4.65, 4.72]
    )  # Zoom
    fig.update_xaxes(title_text="Nombre d'interactions mensuelles", row=3, col=1)
    fig.update_yaxes(title_text="Rating moyen", row=3, col=1)

    # Mise en forme
    fig.update_layout(
        height=1200,
        showlegend=True,
        title_text="Analyse détaillée avec bandes de confiance",
    )

    # Application du thème
    chart_theme.apply_subplot_theme(fig, num_rows=3, num_cols=1)

    st.plotly_chart(fig, use_container_width=True)

    # Métriques
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Moyenne pondérée", f"{mean_rating_weighted:.3f}")
    with col2:
        st.metric(
            "IC 95%", f"±{1.96 * std_rating_weighted / np.sqrt(np.sum(weights)):.4f}"
        )
    with col3:
        st.metric("Corr. volume-qualité", f"{vol_qual_weighted:.3f}")

    # Interprétation
    st.info(
        "📊 **Interprétation**: L'analyse détaillée confirme la **très forte stabilité** des ratings, avec une **moyenne pondérée** se situant à "
        f"**{mean_rating_weighted:.3f}**. Les **bandes de confiance à 95%** calculées sur la moyenne pondérée sont **extrêmement resserrées** "
        f"(IC 95% = **±{1.96 * std_rating_weighted / np.sqrt(np.sum(weights)):.4f}**), ce qui démontre une **variance globale très faible** et une "
        "**grande prévisibilité** du comportement de notation. Visuellement, bien que les notes mensuelles individuelles fluctuent légèrement, "
        "elles restent **constamment groupées** autour de cette moyenne stable, renforçant la conclusion d'une **absence totale de tendance significative** "
        "à long terme."
    )


def analyse_ratings_seasonality_1():
    """Analyse 4: Statistiques descriptives des données saisonnières."""
    st.markdown(
        """
        Analyse de la distribution des interactions et ratings par saison.
        Examine l'équilibre des données et la validité de l'analyse saisonnière.
        """
    )

    # Chargement des données
    with st.spinner("Chargement des interactions..."):
        df_clean = load_clean_interactions()

    if df_clean.shape[0] == 0:
        st.error("❌ Aucune donnée disponible")
        return

    df_pandas = df_clean.to_pandas()

    # Calcul des statistiques par saison
    seasonal_stats = (
        df_pandas.groupby("season")
        .agg(
            {
                "rating": ["mean", "std", "count"],
                "user_id": "nunique",
                "recipe_id": "nunique",
            }
        )
        .round(4)
    )

    seasonal_stats.columns = [
        "mean_rating",
        "std_rating",
        "count_ratings",
        "unique_users",
        "unique_recipes",
    ]
    seasonal_stats = seasonal_stats.reset_index()

    # Ordre logique des saisons
    season_order = ["Spring", "Summer", "Autumn", "Winter"]
    seasonal_stats["season_cat"] = pd.Categorical(
        seasonal_stats["season"], categories=season_order, ordered=True
    )
    seasonal_stats = seasonal_stats.sort_values("season_cat")

    # Informations sur les volumes
    volumes = seasonal_stats["count_ratings"].values
    cv_volumes = np.std(volumes) / np.mean(volumes)
    ratio_max_min = volumes.max() / volumes.min()
    volume_total = volumes.sum()

    # Graphique avec 2 subplots
    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=(
            "Distribution des interactions par saison",
            "Statistiques de rating par saison",
        ),
        specs=[[{"type": "bar"}, {"type": "bar"}]],
    )

    # (1) Volume d'interactions
    # Couleurs saisonnières "Back to the Kitchen" (même palette que analyse_seasonality.py)
    season_colors_btk = {
        "Winter": colors.CHART_COLORS[1],  # Jaune doré (#FFD700)
        "Spring": colors.CHART_COLORS[2],  # Rouge/Orange profond (#E24E1B)
        "Summer": colors.ORANGE_PRIMARY,  # Orange vif (#FF8C00)
        "Autumn": colors.ORANGE_SECONDARY,  # Rouge/Orange profond (#E24E1B)
    }
    colors_season = [season_colors_btk[s] for s in seasonal_stats["season"]]
    fig.add_trace(
        go.Bar(
            x=seasonal_stats["season"],
            y=seasonal_stats["count_ratings"] / 1000,
            marker=dict(color=colors_season, opacity=0.8, line=dict(width=0)),
            text=[f"{int(v/1000)}K" for v in seasonal_stats["count_ratings"]],
            textposition="outside",
            textfont=dict(size=10, color=colors.TEXT_PRIMARY),
            showlegend=False,
        ),
        row=1,
        col=1,
    )

    # (2) Rating moyen
    fig.add_trace(
        go.Bar(
            x=seasonal_stats["season"],
            y=seasonal_stats["mean_rating"],
            marker=dict(color=colors_season, opacity=0.8, line=dict(width=0)),
            text=[f"{v:.4f}" for v in seasonal_stats["mean_rating"]],
            textposition="outside",
            textfont=dict(size=10, color=colors.TEXT_PRIMARY),
            showlegend=False,
        ),
        row=1,
        col=2,
    )

    # Axes
    fig.update_yaxes(title_text="Nombre (milliers)", row=1, col=1)
    fig.update_yaxes(title_text="Rating moyen", row=1, col=2)

    # Mise en forme
    fig.update_layout(
        height=500,
        showlegend=False,
        title_text=f"Répartition saisonnière (CV={cv_volumes:.3f}, Ratio={ratio_max_min:.2f}:1)",
    )

    # Application du thème
    chart_theme.apply_subplot_theme(fig, num_rows=1, num_cols=2)

    st.plotly_chart(fig, use_container_width=True)

    # Affichage du tableau
    with st.expander("Voir les statistiques détaillées"):
        st.dataframe(
            seasonal_stats[
                [
                    "season",
                    "mean_rating",
                    "std_rating",
                    "count_ratings",
                    "unique_users",
                    "unique_recipes",
                ]
            ]
        )

    # Métriques
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("CV Volumes", f"{cv_volumes:.3f}")
    with col2:
        st.metric("Ratio max/min", f"{ratio_max_min:.2f}:1")
    with col3:
        st.metric("Volume total", f"{volume_total:,}")
    with col4:
        st.metric("Saisons", f"{len(seasonal_stats)}")

    # Interprétation
    st.info(
        "🍂 **Interprétation**: Les statistiques descriptives confirment la **validité de l'analyse saisonnière**. "
        "Le volume d'interactions est **remarquablement bien équilibré** entre les quatre saisons, chacune représentant environ **25%** du total. "
        f"Le **Coefficient de Variation ({cv_volumes:.3f})** et le **ratio max/min ({ratio_max_min:.2f}:1)** des volumes sont **extrêmement faibles**, "
        "indiquant qu'aucune saison ne pèse indûment sur l'analyse. Les comparaisons entre saisons seront donc **fiables et robustes**."
    )


def analyse_ratings_seasonality_2():
    """Analyse 5: Variations saisonnières des ratings (Stats et Visualisations)."""
    st.markdown(
        """
        Analyse détaillée des variations saisonnières des ratings avec dashboard complet.
        Examine moyennes, pourcentages de ratings parfaits/négatifs, et stabilité par saison.
        """
    )

    # Chargement des données
    with st.spinner("Chargement des interactions..."):
        df_clean = load_clean_interactions()

    if df_clean.shape[0] == 0:
        st.error("❌ Aucune donnée disponible")
        return

    # --- PRÉPARATION ET STATS ---
    seasonal_ratings = (
        df_clean.group_by("season")
        .agg(
            [
                pl.col("rating").mean().alias("mean_rating"),
                pl.col("rating").median().alias("median_rating"),
                pl.col("rating").std().alias("std_rating"),
                pl.len().alias("n_interactions"),
                pl.col("rating").quantile(0.25).alias("q25"),
                pl.col("rating").quantile(0.75).alias("q75"),
            ]
        )
        .to_pandas()
    )

    # Ordre logique des saisons
    season_order = ["Spring", "Summer", "Autumn", "Winter"]
    seasonal_ratings = (
        seasonal_ratings.set_index("season").loc[season_order].reset_index()
    )

    # Tests statistiques
    season_groups = [
        df_clean.filter(pl.col("season") == season)["rating"].to_pandas().tolist()
        for season in season_order
    ]
    f_stat, p_anova = f_oneway(*season_groups)
    h_stat, p_kruskal = kruskal(*season_groups)

    # Calcul % 5★ et % négatifs
    seasonal_perfect = (
        df_clean.group_by("season")
        .agg([(pl.col("rating") == 5).sum().alias("count_5"), pl.len().alias("total")])
        .with_columns((pl.col("count_5") / pl.col("total") * 100).alias("pct_5_stars"))
        .to_pandas()
        .set_index("season")
        .loc[season_order]
        .reset_index()
    )

    seasonal_negative = (
        df_clean.group_by("season")
        .agg(
            [
                (pl.col("rating") <= 2).sum().alias("count_negative"),
                pl.len().alias("total"),
            ]
        )
        .with_columns(
            (pl.col("count_negative") / pl.col("total") * 100).alias("pct_negative")
        )
        .to_pandas()
        .set_index("season")
        .loc[season_order]
        .reset_index()
    )

    # --- VISUALISATION : Dashboard Saisonnier (6 panels) ---
    fig = make_subplots(
        rows=2,
        cols=3,
        subplot_titles=(
            "Variations saisonnières (Radar)",
            "Rating moyen par saison",
            "% Ratings parfaits (5★)",
            "% Ratings négatifs (1-2★)",
            "Écart-type des ratings",
            "Volume d'interactions",
        ),
        specs=[
            [{"type": "scatterpolar"}, {"type": "bar"}, {"type": "bar"}],
            [{"type": "bar"}, {"type": "bar"}, {"type": "bar"}],
        ],
        horizontal_spacing=0.12,
        vertical_spacing=0.15,
    )

    # Couleurs saisonnières "Back to the Kitchen" (même palette que analyse_seasonality.py)
    season_colors_btk = {
        "Winter": colors.CHART_COLORS[1],  # Jaune doré (#FFD700)
        "Spring": colors.CHART_COLORS[2],  # Rouge/Orange profond (#E24E1B)
        "Summer": colors.ORANGE_PRIMARY,  # Orange vif (#FF8C00)
        "Autumn": colors.ORANGE_SECONDARY,  # Rouge/Orange profond (#E24E1B)
    }
    colors_season = [season_colors_btk[s] for s in seasonal_ratings["season"]]

    # 1. Radar chart
    theta = list(seasonal_ratings["season"]) + [seasonal_ratings["season"].iloc[0]]
    values = list(seasonal_ratings["mean_rating"]) + [
        seasonal_ratings["mean_rating"].iloc[0]
    ]

    fig.add_trace(
        go.Scatterpolar(
            r=values,
            theta=theta,
            mode="lines+markers",
            fill="toself",
            line=dict(color=colors.CHART_COLORS[2], width=3),
            marker=dict(size=8),
            fillcolor=colors.get_rgba(colors.ORANGE_SECONDARY, 0.25),
            showlegend=False,
        ),
        row=1,
        col=1,
    )

    fig.update_polars(radialaxis=dict(range=[4.5, 4.8]), row=1, col=1)

    # 2. Moyenne par saison
    fig.add_trace(
        go.Bar(
            x=seasonal_ratings["season"],
            y=seasonal_ratings["mean_rating"],
            marker=dict(color=colors_season, opacity=0.8, line=dict(width=0)),
            text=[f"{v:.4f}" for v in seasonal_ratings["mean_rating"]],
            textposition="outside",
            textfont=dict(size=9, color=colors.TEXT_PRIMARY),
            showlegend=False,
        ),
        row=1,
        col=2,
    )
    fig.update_yaxes(title_text="Rating moyen", range=[4.60, 4.70], row=1, col=2)

    # 3. % Ratings parfaits (5★)
    fig.add_trace(
        go.Bar(
            x=seasonal_perfect["season"],
            y=seasonal_perfect["pct_5_stars"],
            marker=dict(color=colors_season, opacity=0.8, line=dict(width=0)),
            text=[f"{v:.2f}%" for v in seasonal_perfect["pct_5_stars"]],
            textposition="outside",
            textfont=dict(size=9, color=colors.TEXT_PRIMARY),
            showlegend=False,
        ),
        row=1,
        col=3,
    )
    fig.update_yaxes(title_text="% de ratings = 5", range=[74, 78], row=1, col=3)

    # 4. % Ratings négatifs (1-2★)
    fig.add_trace(
        go.Bar(
            x=seasonal_negative["season"],
            y=seasonal_negative["pct_negative"],
            marker=dict(color=colors_season, opacity=0.8, line=dict(width=0)),
            text=[f"{v:.2f}%" for v in seasonal_negative["pct_negative"]],
            textposition="outside",
            textfont=dict(size=9, color=colors.TEXT_PRIMARY),
            showlegend=False,
        ),
        row=2,
        col=1,
    )
    fig.update_yaxes(title_text="% de ratings ≤ 2", range=[0, 4], row=2, col=1)

    # 5. Écart-type
    fig.add_trace(
        go.Bar(
            x=seasonal_ratings["season"],
            y=seasonal_ratings["std_rating"],
            marker=dict(color=colors_season, opacity=0.8, line=dict(width=0)),
            text=[f"{v:.3f}" for v in seasonal_ratings["std_rating"]],
            textposition="outside",
            textfont=dict(size=9, color=colors.TEXT_PRIMARY),
            showlegend=False,
        ),
        row=2,
        col=2,
    )
    fig.update_yaxes(title_text="Écart-type", range=[0.0, 0.70], row=2, col=2)

    # 6. Volume d'interactions
    fig.add_trace(
        go.Bar(
            x=seasonal_ratings["season"],
            y=seasonal_ratings["n_interactions"] / 1000,
            marker=dict(color=colors_season, opacity=0.8, line=dict(width=0)),
            text=[f"{int(v/1000)}K" for v in seasonal_ratings["n_interactions"]],
            textposition="outside",
            textfont=dict(size=9, color=colors.TEXT_PRIMARY),
            showlegend=False,
        ),
        row=2,
        col=3,
    )
    fig.update_yaxes(title_text="Nombre (milliers)", row=2, col=3)

    # Mise en forme
    fig.update_layout(
        height=900,
        showlegend=False,
        title_text=f"Analyse des variations saisonnières (ANOVA p={p_anova:.4f}, Kruskal p={p_kruskal:.4f})",
    )

    # Application du thème
    chart_theme.apply_subplot_theme(fig, num_rows=2, num_cols=3)

    st.plotly_chart(fig, use_container_width=True)

    # Métriques
    col1, col2, col3, col4 = st.columns(4)
    best_season = seasonal_ratings.loc[seasonal_ratings["mean_rating"].idxmax()]
    worst_season = seasonal_ratings.loc[seasonal_ratings["mean_rating"].idxmin()]

    with col1:
        st.metric("ANOVA F-stat", f"{f_stat:.3f}")
    with col2:
        st.metric("P-value", f"{p_anova:.4f}")
    with col3:
        st.metric(
            "Meilleure saison",
            f"{best_season['season']} ({best_season['mean_rating']:.4f})",
        )
    with col4:
        st.metric(
            "Écart max",
            f"{best_season['mean_rating'] - worst_season['mean_rating']:.4f}",
        )

    # Interprétation
    st.info(
        f"🌸 **Interprétation**: Les tests statistiques (ANOVA F={f_stat:.3f} et Kruskal-Wallis H={h_stat:.3f}) révèlent des "
        "**différences statistiquement significatives** entre les saisons (p < 0.0001), **confirmant l'existence d'une variation saisonnière**. "
        f"Cependant, l'**ampleur de cette différence est infime** : l'écart entre la meilleure saison (**{best_season['season']}**, {best_season['mean_rating']:.3f}) "
        f"et la moins bonne (**{worst_season['season']}**, {worst_season['mean_rating']:.3f}) n'est que de **{best_season['mean_rating'] - worst_season['mean_rating']:.3f} points** "
        "sur une échelle de 5. L'analyse visuelle confirme la **stabilité globale**, mais révèle un **schéma saisonnier cohérent**. "
        "Malgré une **significativité statistique irréfutable**, l'**impact pratique de cette saisonnalité est nul**."
    )


def render_ratings_analysis():
    """Point d'entrée principal pour les analyses de ratings."""
    st.markdown(
        '<h1 style="margin-top: 0; padding-top: 0;">⭐ Analyses des Ratings (1999-2018)</h1>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
    Cette section présente les analyses de **l'évolution des ratings/notes** sur Food.com (1999-2018).

    Les analyses examinent la **stabilité temporelle**, les **tendances**, et les **variations saisonnières**
    des notes moyennes attribuées aux recettes par les utilisateurs.
    """
    )

    # Affichage de toutes les analyses en continu (comme page Saisonnalité)

    st.subheader("🔬 Validation méthodologique")
    analyse_ratings_validation_ponderee()
    st.markdown("---")

    st.subheader("📈 Tendance temporelle")
    analyse_ratings_tendance_temporelle()
    st.markdown("---")

    st.subheader("📊 Distribution et stabilité")
    analyse_ratings_distribution()
    st.markdown("---")

    st.subheader("🍂 Statistiques saisonnières")
    analyse_ratings_seasonality_1()
    st.markdown("---")

    st.subheader("🌸 Variations saisonnières")
    analyse_ratings_seasonality_2()
    st.markdown("---")
