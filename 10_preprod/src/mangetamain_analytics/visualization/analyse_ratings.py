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
from scipy.stats import kendalltau, spearmanr
from scipy.stats import linregress
import statsmodels.api as sm

# Import du thème graphique
from utils import chart_theme

# Import des utilitaires de chargement des données ratings
try:
    from mangetamain_data_utils.data_utils_ratings import load_ratings_for_longterm_analysis
except ImportError:
    st.error("❌ Module mangetamain_data_utils non disponible")

    def load_ratings_for_longterm_analysis(*args, **kwargs):
        """Fonction fallback si import échoue."""
        return pd.DataFrame(), {}


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
    rank_x = pd.Series(x).rank(method='average')
    rank_y = pd.Series(y).rank(method='average')

    # Corrélation pondérée entre les rangs
    weighted_corr = np.cov(rank_x, rank_y, aweights=w)[0, 1] / (
        np.sqrt(np.cov(rank_x, aweights=w)[0, 0]) * np.sqrt(np.cov(rank_y, aweights=w)[0, 0])
    )
    return weighted_corr


def analyse_ratings_validation_ponderee():
    """Analyse 1: Validation méthodologique - Tests pondérés vs non-pondérés."""
    st.markdown("### 🔬 Validation méthodologique")
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
            min_interactions=100,
            return_metadata=True,
            verbose=False
        )

    if monthly_stats.empty:
        st.error("❌ Aucune donnée disponible")
        return

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
    cv_volumes = np.std(monthly_df['n_interactions']) / np.mean(monthly_df['n_interactions'])

    # Création du graphique avec 4 subplots
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "Distribution des volumes mensuels",
            "Évolution des poids dans le temps",
            "Ratings pondérés par volume",
            "Variance des ratings"
        ),
        specs=[
            [{"type": "histogram"}, {"type": "scatter"}],
            [{"type": "scatter"}, {"type": "bar"}]
        ]
    )

    # (1) Distribution des volumes (histogram)
    fig.add_trace(
        go.Histogram(
            x=monthly_df['n_interactions'],
            nbinsx=20,
            marker=dict(
                color=chart_theme.colors.CHART_COLORS[0],
                opacity=0.7,
                line=dict(color=chart_theme.colors.TEXT_PRIMARY, width=1)
            ),
            showlegend=False
        ),
        row=1,
        col=1
    )

    # (2) Poids calculés dans le temps
    fig.add_trace(
        go.Scatter(
            x=monthly_df['date'],
            y=weights_normalized,
            mode='lines+markers',
            line=dict(color=chart_theme.colors.CHART_COLORS[2], width=2),
            marker=dict(size=4),
            name='Poids normalisés',
            showlegend=True
        ),
        row=1,
        col=2
    )

    # (3) Ratings avec taille proportionnelle au poids
    sizes = weights_normalized * 1000
    fig.add_trace(
        go.Scatter(
            x=monthly_df['date'],
            y=monthly_df['mean_rating'],
            mode='markers',
            marker=dict(
                size=sizes / 50,  # Ajustement taille
                color=monthly_df['n_interactions'],
                colorscale='Viridis',
                opacity=0.7,
                line=dict(color=chart_theme.colors.TEXT_PRIMARY, width=0.5),
                colorbar=dict(
                    title="Volume",
                    x=0.46,
                    len=0.4,
                    y=0.25
                )
            ),
            showlegend=False
        ),
        row=2,
        col=1
    )

    # (4) Comparaison variance pondérée vs non-pondérée
    var_unweighted = np.var(monthly_df['mean_rating'])
    var_weighted = np.average(
        (monthly_df['mean_rating'] - np.average(monthly_df['mean_rating'], weights=weights))**2,
        weights=weights
    )

    fig.add_trace(
        go.Bar(
            x=['Non pondérée', 'Pondérée'],
            y=[var_unweighted, var_weighted],
            marker=dict(
                color=[chart_theme.colors.CHART_COLORS[2], chart_theme.colors.CHART_COLORS[0]],
                opacity=0.8,
                line=dict(color=chart_theme.colors.TEXT_PRIMARY, width=1)
            ),
            text=[f'{var_unweighted:.4f}', f'{var_weighted:.4f}'],
            textposition='outside',
            textfont=dict(size=12, color=chart_theme.colors.TEXT_PRIMARY),
            showlegend=False
        ),
        row=2,
        col=2
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
        title_text="Impact de la pondération par volume sur l'analyse"
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

    spearman_weighted = weighted_spearman(x, y, w)

    # Régression pondérée (WLS)
    X_const = sm.add_constant(x)
    wls_model = sm.WLS(y, X_const, weights=w)
    wls_result = wls_model.fit()
    y_pred_weighted = wls_result.predict(X_const)
    y_mean_weighted = np.average(y, weights=w)
    r2_weighted = 1 - np.average((y - y_pred_weighted)**2, weights=w) / np.average((y - y_mean_weighted)**2, weights=w)

    bias_slope = abs(wls_result.params[1] - slope) / abs(slope) * 100 if slope != 0 else 0
    bias_corr = abs(spearman_weighted - tau) / abs(tau) * 100 if tau != 0 else 0

    # Métriques
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("CV Volumes", f"{cv_volumes:.2f}")
    with col2:
        st.metric("Biais pente", f"{bias_slope:.1f}%")
    with col3:
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


def render_ratings_analysis():
    """Point d'entrée principal pour les analyses de ratings."""
    st.title("📊 Analyses des Ratings")

    # Sélecteur d'analyse
    analyse_options = {
        "1. Validation méthodologique (pondération)": analyse_ratings_validation_ponderee,
        # "2. Tendance temporelle": analyse_ratings_tendance,
        # "3. Distribution et stabilité": analyse_ratings_distribution,
        # "4. Saisonnalité ratings": analyse_ratings_seasonality_1,
        # "5. Weekend effect ratings": analyse_ratings_weekend_1,
    }

    selected_analyse = st.selectbox(
        "Choisir une analyse:",
        list(analyse_options.keys()),
        key="ratings_selector"
    )

    # Afficher l'analyse sélectionnée
    if selected_analyse:
        analyse_options[selected_analyse]()
