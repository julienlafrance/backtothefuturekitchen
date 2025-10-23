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
    """
    Analyse interactive du volume de recettes par année.
    Version preprod avec filtres et statistiques.
    """

    # Chargement des données
    df = load_and_prepare_data()

    # ========================================
    # WIDGETS INTERACTIFS
    # ========================================

    col1, col2, col3 = st.columns(3)

    with col1:
        # Filtre années
        all_years = sorted(df["year"].unique().to_list())
        year_range = st.slider(
            "📅 Plage d'années",
            min_value=int(all_years[0]),
            max_value=int(all_years[-1]),
            value=(int(all_years[0]), int(all_years[-1])),
        )

    with col2:
        # Choix couleur barres
        bar_color = st.selectbox(
            "🎨 Couleur", ["steelblue", "coral", "lightgreen", "mediumpurple"], index=0
        )

    with col3:
        # Afficher valeurs
        show_values = st.checkbox("🔢 Afficher valeurs", value=True)

    # ========================================
    # FILTRAGE DES DONNÉES
    # ========================================

    df_filtered = df.filter(
        (pl.col("year") >= year_range[0]) & (pl.col("year") <= year_range[1])
    )

    recipes_per_year = (
        df_filtered.group_by("year")
        .agg(pl.len().alias("n_recipes"))
        .sort("year")
        .to_pandas()
    )

    data = recipes_per_year["n_recipes"].values

    # Stats en bannière
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("📊 Années", len(recipes_per_year))
    with col_b:
        st.metric("🍳 Total recettes", f"{data.sum():,}")
    with col_c:
        st.metric("📈 Moyenne/an", f"{data.mean():.0f}")

    # ========================================
    # GRAPHIQUE
    # ========================================

    # Calcul Q-Q plot
    (osm, osr), (slope, intercept, r) = stats.probplot(data, dist="norm")

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Nombre de recettes par année", "Q-Q Plot (Test de normalité)"),
        horizontal_spacing=0.12,
    )

    # SUBPLOT 1 : Bar chart
    fig.add_trace(
        go.Bar(
            x=recipes_per_year["year"].astype(str),
            y=recipes_per_year["n_recipes"],
            marker=dict(color=bar_color, opacity=0.8),
            text=[f"{val:,}" if show_values else "" for val in recipes_per_year["n_recipes"]],
            textposition="outside",
            textfont=dict(size=9, color="black"),
            showlegend=False,
            hovertemplate="<b>Année %{x}</b><br>Recettes: %{y:,}<extra></extra>",
        ),
        row=1,
        col=1,
    )

    # SUBPLOT 2 : Q-Q plot
    fig.add_trace(
        go.Scatter(
            x=osm,
            y=osr,
            mode="markers",
            marker=dict(color="#5470c6", size=8, opacity=0.8),
            name="Observations",
            hovertemplate="Théorique: %{x:.2f}<br>Observé: %{y:,.0f}<extra></extra>",
        ),
        row=1,
        col=2,
    )

    fig.add_trace(
        go.Scatter(
            x=[osm.min(), osm.max()],
            y=[slope * osm.min() + intercept, slope * osm.max() + intercept],
            mode="lines",
            line=dict(color="red", width=2, dash="dash"),
            name="Ligne théorique",
            hoverinfo="skip",
        ),
        row=1,
        col=2,
    )

    # Mise en forme axes
    fig.update_xaxes(
        title_text="Année",
        title_font=dict(size=12, color="black"),
        tickfont=dict(size=10, color="black"),
        showgrid=False,
        row=1,
        col=1,
    )
    fig.update_yaxes(
        title_text="Nombre de recettes",
        title_font=dict(size=12, color="black"),
        tickfont=dict(size=10, color="black"),
        showgrid=True,
        gridcolor="rgba(200,200,200,0.4)",
        row=1,
        col=1,
    )
    fig.update_xaxes(
        title_text="Quantiles théoriques (loi normale)",
        title_font=dict(size=12, color="black"),
        tickfont=dict(size=10, color="black"),
        showgrid=True,
        gridcolor="rgba(200,200,200,0.4)",
        row=1,
        col=2,
    )
    fig.update_yaxes(
        title_text="Quantiles observés",
        title_font=dict(size=12, color="black"),
        tickfont=dict(size=10, color="black"),
        showgrid=True,
        gridcolor="rgba(200,200,200,0.4)",
        row=1,
        col=2,
    )

    # Layout global
    fig.update_layout(
        height=600,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(size=11, color="black", family="Arial, sans-serif"),
        showlegend=False,
    )

    # Titres des subplots
    for annotation in fig["layout"]["annotations"]:
        annotation["font"] = dict(
            size=13, color="black", family="Arial, sans-serif", weight="bold"
        )

    # Affichage
    st.plotly_chart(fig, use_container_width=True)

    # ========================================
    # STATISTIQUES DÉTAILLÉES (EXPANDER)
    # ========================================

    with st.expander("📊 Statistiques détaillées"):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Min", f"{data.min():,}")
            st.metric("Q1", f"{np.percentile(data, 25):,.0f}")

        with col2:
            st.metric("Médiane", f"{np.median(data):,.0f}")
            st.metric("Moyenne", f"{data.mean():,.0f}")

        with col3:
            st.metric("Q3", f"{np.percentile(data, 75):,.0f}")
            st.metric("Max", f"{data.max():,}")

        with col4:
            st.metric("Écart-type", f"{data.std():.0f}")
            st.metric("Coef. variation", f"{(data.std()/data.mean()*100):.1f}%")

        st.divider()
        st.write(f"**R² (test normalité):** {r**2:.4f}")

        if r**2 > 0.95:
            st.success("✅ Distribution proche de la normale")
        elif r**2 > 0.90:
            st.warning("⚠️ Distribution légèrement éloignée de la normale")
        else:
            st.error("❌ Distribution non normale")


# ============================================================================
# ANALYSE 2: DURÉE DE PRÉPARATION
# ============================================================================

def analyse_trendline_duree():
    """
    Analyse WLS de l'évolution de la durée - Version style professionnel.
    MÊME ANALYSE que l'original matplotlib, juste un meilleur rendu visuel.
    Conserve la logique: 2 courbes (moyenne/médiane), 2 régressions WLS, zone IQR, bulles.
    """

    # Chargement des données
    df = load_and_prepare_data()

    # ========================================
    # WIDGETS INTERACTIFS
    # ========================================

    col1, col2 = st.columns(2)

    with col1:
        # Filtre années
        all_years = sorted(df["year"].unique().to_list())
        year_range = st.slider(
            "📅 Plage d'années",
            min_value=int(all_years[0]),
            max_value=int(all_years[-1]),
            value=(int(all_years[0]), int(all_years[-1])),
            key="slider_duree_years_v2"
        )

    with col2:
        # Option bulles
        show_bubbles = st.checkbox("⭕ Afficher les bulles proportionnelles", value=True)

    # ========================================
    # AGRÉGATION DURÉE PAR ANNÉE (IDENTIQUE À L'ORIGINAL)
    # ========================================

    df_filtered = df.filter(
        (pl.col("year") >= year_range[0]) &
        (pl.col("year") <= year_range[1])
    )

    minutes_by_year = (
        df_filtered.group_by("year")
        .agg([
            pl.mean("minutes").alias("mean_minutes"),
            pl.median("minutes").alias("median_minutes"),
            pl.quantile("minutes", 0.25).alias("q25"),
            pl.quantile("minutes", 0.75).alias("q75"),
            pl.len().alias("n_recipes")
        ])
        .sort("year")
        .to_pandas()
    )

    # ========================================
    # CALCUL DES RÉGRESSIONS WLS (IDENTIQUE À L'ORIGINAL)
    # ========================================

    X = minutes_by_year["year"].values
    w = minutes_by_year["n_recipes"].values

    metrics_config = {
        "mean_minutes": {
            "color": "steelblue",
            "label": "Moyenne",
            "ylabel": "minutes/an"
        },
        "median_minutes": {
            "color": "coral",
            "label": "Médiane",
            "ylabel": "minutes/an"
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
            "y_pred": y_pred,
            "slope": wls_result.params[1],
            "intercept": wls_result.params[0],
            "r2": r2_w,
            "p_value": wls_result.pvalues[1]
        }

    # Taille des bulles (identique à l'original)
    sizes = minutes_by_year["n_recipes"] / minutes_by_year["n_recipes"].max() * 35

    # ========================================
    # MÉTRIQUES EN BANNIÈRE
    # ========================================

    col_a, col_b, col_c, col_d = st.columns(4)

    with col_a:
        st.metric(
            "⏱️ Moyenne actuelle",
            f"{minutes_by_year['mean_minutes'].iloc[-1]:.1f} min"
        )

    with col_b:
        st.metric(
            "📊 Médiane actuelle",
            f"{minutes_by_year['median_minutes'].iloc[-1]:.1f} min"
        )

    with col_c:
        trend_mean = regressions["mean_minutes"]["slope"]
        st.metric(
            "📉 Pente Moyenne",
            f"{trend_mean:+.4f} min/an"
        )

    with col_d:
        trend_median = regressions["median_minutes"]["slope"]
        st.metric(
            "📉 Pente Médiane",
            f"{trend_median:+.4f} min/an"
        )

    st.markdown("---")

    # ========================================
    # GRAPHIQUE AVEC STYLE PROFESSIONNEL
    # ========================================

    fig = go.Figure()

    # 1. ZONE IQR (Q25-Q75) - EN FOND
    fig.add_trace(go.Scatter(
        x=minutes_by_year["year"],
        y=minutes_by_year["q75"],
        fill=None,
        mode="lines",
        line=dict(width=0),
        showlegend=False,
        hoverinfo="skip"
    ))

    fig.add_trace(go.Scatter(
        x=minutes_by_year["year"],
        y=minutes_by_year["q25"],
        fill="tonexty",
        mode="lines",
        line=dict(width=0),
        fillcolor="rgba(70, 130, 180, 0.15)",
        name="IQR (Q25-Q75)",
        hovertemplate="<b>Année %{x}</b><br>IQR: Q25-Q75<extra></extra>"
    ))

    # 2. MOYENNE - Courbe observée
    fig.add_trace(go.Scatter(
        x=minutes_by_year["year"],
        y=minutes_by_year["mean_minutes"],
        mode="lines",
        name="Moyenne (observée)",
        line=dict(color="steelblue", width=2),
        opacity=0.7,
        hovertemplate="<b>Année %{x}</b><br>Moyenne: %{y:.1f} min<br>Recettes: %{customdata:,}<extra></extra>",
        customdata=minutes_by_year["n_recipes"]
    ))

    # 3. MOYENNE - Bulles proportionnelles
    if show_bubbles:
        fig.add_trace(go.Scatter(
            x=minutes_by_year["year"],
            y=minutes_by_year["mean_minutes"],
            mode="markers",
            name="Volume (moyenne)",
            marker=dict(
                color="steelblue",
                size=sizes,
                opacity=0.6,
                line=dict(color="black", width=0.5)
            ),
            hovertemplate="<b>Année %{x}</b><br>Moyenne: %{y:.1f} min<br>Recettes: %{customdata:,}<extra></extra>",
            customdata=minutes_by_year["n_recipes"],
            showlegend=False
        ))

    # 4. MOYENNE - Régression WLS
    fig.add_trace(go.Scatter(
        x=minutes_by_year["year"],
        y=regressions["mean_minutes"]["y_pred"],
        mode="lines",
        name=f"Régression Moyenne (R²={regressions['mean_minutes']['r2']:.3f})",
        line=dict(color="darkblue", width=2.5, dash="dash"),
        opacity=0.8,
        hovertemplate="<b>Année %{x}</b><br>Régression: %{y:.1f} min<extra></extra>"
    ))

    # 5. MÉDIANE - Courbe observée
    fig.add_trace(go.Scatter(
        x=minutes_by_year["year"],
        y=minutes_by_year["median_minutes"],
        mode="lines",
        name="Médiane (observée)",
        line=dict(color="coral", width=2),
        opacity=0.7,
        hovertemplate="<b>Année %{x}</b><br>Médiane: %{y:.1f} min<br>Recettes: %{customdata:,}<extra></extra>",
        customdata=minutes_by_year["n_recipes"]
    ))

    # 6. MÉDIANE - Bulles proportionnelles
    if show_bubbles:
        fig.add_trace(go.Scatter(
            x=minutes_by_year["year"],
            y=minutes_by_year["median_minutes"],
            mode="markers",
            name="Volume (médiane)",
            marker=dict(
                color="coral",
                size=sizes,
                opacity=0.6,
                line=dict(color="black", width=0.5)
            ),
            hovertemplate="<b>Année %{x}</b><br>Médiane: %{y:.1f} min<br>Recettes: %{customdata:,}<extra></extra>",
            customdata=minutes_by_year["n_recipes"],
            showlegend=False
        ))

    # 7. MÉDIANE - Régression WLS
    fig.add_trace(go.Scatter(
        x=minutes_by_year["year"],
        y=regressions["median_minutes"]["y_pred"],
        mode="lines",
        name=f"Régression Médiane (R²={regressions['median_minutes']['r2']:.3f})",
        line=dict(color="darkred", width=2.5, dash="dash"),
        opacity=0.8,
        hovertemplate="<b>Année %{x}</b><br>Régression: %{y:.1f} min<extra></extra>"
    ))

    # ========================================
    # MISE EN FORME PROFESSIONNELLE
    # ========================================

    title_text = (
        f"Évolution de la durée (minutes)<br>"
        f"<sub>Moyenne: {regressions['mean_minutes']['slope']:+.4f} min/an | "
        f"Médiane: {regressions['median_minutes']['slope']:+.4f} min/an</sub>"
    )

    fig.update_layout(
        title=dict(
            text=title_text,
            font=dict(size=14, color="black", family="Arial, sans-serif"),
            x=0.5,
            xanchor="center"
        ),
        xaxis=dict(
            title="Année",
            title_font=dict(size=12, color="black"),
            tickfont=dict(size=10, color="black"),
            showgrid=True,
            gridcolor="rgba(200,200,200,0.3)",
            gridwidth=1,
            zeroline=False
        ),
        yaxis=dict(
            title="Minutes",
            title_font=dict(size=12, color="black"),
            tickfont=dict(size=10, color="black"),
            showgrid=True,
            gridcolor="rgba(200,200,200,0.3)",
            gridwidth=1,
            zeroline=False
        ),
        height=650,
        plot_bgcolor="rgba(245, 245, 245, 0.8)",
        paper_bgcolor="white",
        font=dict(size=11, color="black", family="Arial, sans-serif"),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.98,
            xanchor="right",
            x=0.98,
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="rgba(0,0,0,0.2)",
            borderwidth=1,
            font=dict(size=9)
        ),
        hovermode="closest"
    )

    # Affichage
    st.plotly_chart(fig, use_container_width=True)

    # ========================================
    # INTERPRÉTATION (IDENTIQUE À L'ORIGINAL)
    # ========================================

    st.markdown("### 📊 Interprétation")

    st.write(f"""
    L'analyse de la durée moyenne de préparation montre une **tendance globale à la baisse**
    depuis la création du site. En moyenne, le temps de préparation diminue d'environ
    **{regressions['mean_minutes']['slope']:.2f} min/an**, tandis que la médiane recule de
    **{regressions['median_minutes']['slope']:.2f} min/an**, ce qui traduit une légère
    **simplification des recettes** au fil du temps.
    """)

    # ========================================
    # STATISTIQUES DÉTAILLÉES
    # ========================================

    with st.expander("📊 Statistiques détaillées des régressions"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📈 Moyenne")
            st.write(f"**Pente:** {regressions['mean_minutes']['slope']:.6f} min/an")
            st.write(f"**Intercept:** {regressions['mean_minutes']['intercept']:.2f}")
            st.write(f"**R² pondéré:** {regressions['mean_minutes']['r2']:.4f}")
            st.write(f"**p-value:** {regressions['mean_minutes']['p_value']:.4e}")

        with col2:
            st.markdown("### 📊 Médiane")
            st.write(f"**Pente:** {regressions['median_minutes']['slope']:.6f} min/an")
            st.write(f"**Intercept:** {regressions['median_minutes']['intercept']:.2f}")
            st.write(f"**R² pondéré:** {regressions['median_minutes']['r2']:.4f}")
            st.write(f"**p-value:** {regressions['median_minutes']['p_value']:.4e}")

    # ========================================
    # TABLEAU DES DONNÉES
    # ========================================

    with st.expander("📋 Tableau des données"):
        display_df = minutes_by_year.copy()
        display_df["year"] = display_df["year"].astype(int)
        display_df["mean_pred"] = regressions["mean_minutes"]["y_pred"]
        display_df["median_pred"] = regressions["median_minutes"]["y_pred"]

        st.dataframe(
            display_df[[
                "year", "mean_minutes", "mean_pred", "median_minutes", "median_pred",
                "q25", "q75", "n_recipes"
            ]].style.format({
                "mean_minutes": "{:.2f}",
                "mean_pred": "{:.2f}",
                "median_minutes": "{:.2f}",
                "median_pred": "{:.2f}",
                "q25": "{:.2f}",
                "q75": "{:.2f}",
                "n_recipes": "{:,}"
            }),
            use_container_width=True
        )


def analyse_trendline_duree_old_intervals():
    """
    Analyse professionnelle de l'évolution de la durée de préparation.
    Avec intervalles de confiance (95%) et intervalles de prédiction.
    """

    # Chargement des données
    df = load_and_prepare_data()

    # ========================================
    # WIDGETS INTERACTIFS
    # ========================================

    col1, col2, col3 = st.columns(3)

    with col1:
        # Filtre années
        all_years = sorted(df["year"].unique().to_list())
        year_range = st.slider(
            "📅 Plage d'années",
            min_value=int(all_years[0]),
            max_value=int(all_years[-1]),
            value=(int(all_years[0]), int(all_years[-1])),
            key="slider_duree_years"
        )

    with col2:
        # Choix métrique
        metric_choice = st.selectbox(
            "📊 Métrique à analyser",
            options=['Moyenne', 'Médiane'],
            index=0,
            key="select_duree_metric"
        )

    with col3:
        # Niveau de confiance
        confidence_level = st.slider(
            "🎯 Niveau de confiance (%)",
            min_value=90,
            max_value=99,
            value=95,
            step=1,
            key="slider_confidence"
        )

    # ========================================
    # FILTRAGE DES DONNÉES
    # ========================================

    df_filtered = df.filter(
        (pl.col("year") >= year_range[0]) & (pl.col("year") <= year_range[1])
    )

    # Agrégation par année
    if metric_choice == 'Moyenne':
        metric_col = "prep_time_mean"
        df_yearly = (
            df_filtered.group_by("year")
            .agg([
                pl.col("minutes").mean().alias("prep_time_mean"),
                pl.len().alias("n_recipes")
            ])
            .sort("year")
        )
    else:
        metric_col = "prep_time_median"
        df_yearly = (
            df_filtered.group_by("year")
            .agg([
                pl.col("minutes").median().alias("prep_time_median"),
                pl.len().alias("n_recipes")
            ])
            .sort("year")
        )

    # ========================================
    # RÉGRESSION WLS
    # ========================================

    X = df_yearly["year"].to_numpy()
    y = df_yearly[metric_col].to_numpy()
    w = df_yearly["n_recipes"].to_numpy()

    # Modèle WLS
    X_const = sm.add_constant(X)
    wls_model = sm.WLS(y, X_const, weights=w)
    wls_result = wls_model.fit()

    # Prédictions
    y_pred = wls_result.predict(X_const)

    # ========================================
    # INTERVALLES DE CONFIANCE (pour la moyenne)
    # ========================================

    alpha = 1 - confidence_level / 100
    predictions = wls_result.get_prediction(X_const)
    conf_int = predictions.conf_int(alpha=alpha)
    conf_lower = conf_int[:, 0]
    conf_upper = conf_int[:, 1]

    # ========================================
    # INTERVALLES DE PRÉDICTION (pour individus)
    # ========================================

    # Calcul manuel des intervalles de prédiction
    residuals = y - y_pred
    mse = np.average(residuals**2, weights=w)

    # Variance de prédiction
    X_mean = np.average(X, weights=w)
    sxx = np.sum(w * (X - X_mean)**2)

    pred_std = []
    for i, x_val in enumerate(X):
        # Effet de levier
        h_ii = w[i] * (1 + (x_val - X_mean)**2 / sxx)
        # Variance de prédiction = MSE * (1 + h_ii)
        pred_var = mse * (1 + h_ii)
        pred_std.append(np.sqrt(pred_var))

    pred_std = np.array(pred_std)

    # Valeur critique t de Student
    t_val = stats.t.ppf(1 - alpha/2, df=len(X)-2)

    # Bornes des intervalles de prédiction
    pred_lower = y_pred - t_val * pred_std
    pred_upper = y_pred + t_val * pred_std

    # ========================================
    # GRAPHIQUE
    # ========================================

    fig = go.Figure()

    # 1. Intervalle de prédiction (FOND orange clair)
    fig.add_trace(go.Scatter(
        x=X,
        y=pred_lower,
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))

    fig.add_trace(go.Scatter(
        x=X,
        y=pred_upper,
        mode='lines',
        fill='tonexty',
        fillcolor='rgba(255, 165, 0, 0.1)',
        line=dict(width=0),
        name=f'Intervalle de prédiction {confidence_level}% (individuel)',
        hoverinfo='skip'
    ))

    # 2. Lignes pointillées orange (bornes prédiction)
    fig.add_trace(go.Scatter(
        x=X,
        y=pred_lower,
        mode='lines',
        line=dict(color='orange', width=2, dash='dot'),
        name='Borne inf. prédiction',
        hovertemplate='<b>%{x}</b><br>Borne inf: %{y:.1f} min<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=X,
        y=pred_upper,
        mode='lines',
        line=dict(color='orange', width=2, dash='dot'),
        name='Borne sup. prédiction',
        hovertemplate='<b>%{x}</b><br>Borne sup: %{y:.1f} min<extra></extra>'
    ))

    # 3. Intervalle de confiance (FOND vert clair)
    fig.add_trace(go.Scatter(
        x=X,
        y=conf_lower,
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))

    fig.add_trace(go.Scatter(
        x=X,
        y=conf_upper,
        mode='lines',
        fill='tonexty',
        fillcolor='rgba(0, 128, 0, 0.15)',
        line=dict(width=0),
        name=f'Intervalle de confiance {confidence_level}% (moyenne)',
        hoverinfo='skip'
    ))

    # 4. Lignes tiretées vertes (bornes confiance)
    fig.add_trace(go.Scatter(
        x=X,
        y=conf_lower,
        mode='lines',
        line=dict(color='green', width=2, dash='dash'),
        name='Borne inf. confiance',
        hovertemplate='<b>%{x}</b><br>Borne inf: %{y:.1f} min<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=X,
        y=conf_upper,
        mode='lines',
        line=dict(color='green', width=2, dash='dash'),
        name='Borne sup. confiance',
        hovertemplate='<b>%{x}</b><br>Borne sup: %{y:.1f} min<extra></extra>'
    ))

    # 5. Droite de régression (ROUGE)
    fig.add_trace(go.Scatter(
        x=X,
        y=y_pred,
        mode='lines',
        line=dict(color='red', width=3),
        name='Régression WLS',
        hovertemplate='<b>%{x}</b><br>Prédiction: %{y:.1f} min<extra></extra>'
    ))

    # 6. Points observés (BLEU FONCÉ)
    fig.add_trace(go.Scatter(
        x=X,
        y=y,
        mode='markers',
        marker=dict(
            color='darkblue',
            size=10,
            line=dict(color='white', width=1)
        ),
        name='Données observées',
        hovertemplate='<b>%{x}</b><br>Valeur: %{y:.1f} min<extra></extra>'
    ))

    # Mise en forme
    fig.update_layout(
        title={
            'text': f"Évolution de la durée de préparation ({metric_choice.lower()})<br><sub>Avec intervalles de confiance et de prédiction à {confidence_level}%</sub>",
            'x': 0.5,
            'xanchor': 'center',
            'font': dict(size=16, color='black')
        },
        xaxis=dict(
            title='Année',
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)',
            title_font=dict(size=12, color='black'),
            tickfont=dict(size=10, color='black')
        ),
        yaxis=dict(
            title=f'Durée ({metric_choice.lower()}, minutes)',
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)',
            title_font=dict(size=12, color='black'),
            tickfont=dict(size=10, color='black')
        ),
        hovermode='x unified',
        plot_bgcolor='white',
        height=600,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="black",
            borderwidth=1
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    # ========================================
    # MÉTRIQUES
    # ========================================

    col_a, col_b, col_c, col_d = st.columns(4)

    with col_a:
        current_value = y[-1]
        st.metric(
            f"📊 {metric_choice} actuelle",
            f"{current_value:.1f} min"
        )

    with col_b:
        slope = wls_result.params[1]
        trend = "📈 Hausse" if slope > 0 else "📉 Baisse"
        st.metric(
            "Tendance",
            trend,
            f"{slope:.2f} min/an"
        )

    with col_c:
        r_squared = wls_result.rsquared
        st.metric(
            "R² pondéré",
            f"{r_squared:.3f}",
            "Qualité du modèle"
        )

    with col_d:
        p_value = wls_result.pvalues[1]
        significance = "✅ Significatif" if p_value < 0.05 else "⚠️ Non significatif"
        st.metric(
            "p-value",
            f"{p_value:.4f}",
            significance
        )

    # ========================================
    # EXPLICATIONS
    # ========================================

    with st.expander("📖 Comprendre les intervalles"):
        st.markdown("""
        **Intervalle de confiance (vert)** 🟢
        - Incertitude sur la **position moyenne** de la droite de régression
        - "Où se trouve la vraie moyenne de la population ?"
        - Plus étroit car basé sur une moyenne d'observations

        **Intervalle de prédiction (orange)** 🟠
        - Incertitude sur une **observation individuelle future**
        - "Où se situera la prochaine recette ?"
        - Plus large car inclut la variabilité individuelle des recettes

        **Pourquoi l'intervalle de prédiction est plus large ?**
        - Il inclut 2 sources d'incertitude :
          1. L'incertitude sur la moyenne (comme l'IC)
          2. La variabilité naturelle entre recettes individuelles
        """)

    with st.expander("📊 Statistiques détaillées de la régression"):
        st.markdown("**Équation du modèle WLS :**")
        intercept = wls_result.params[0]
        st.latex(rf"\text{{Durée}} = {intercept:.2f} + {slope:.2f} \times \text{{Année}}")

        st.markdown("**Coefficients :**")
        st.write(f"- Ordonnée à l'origine : {intercept:.2f} minutes")
        st.write(f"- Pente : {slope:.2f} minutes/an")
        st.write(f"- R² pondéré : {r_squared:.4f}")
        st.write(f"- p-value (pente) : {p_value:.4e}")

        st.markdown("**Résumé complet du modèle :**")
        st.text(wls_result.summary())

    with st.expander("📋 Tableau des données avec prédictions"):
        df_table = pl.DataFrame({
            "Année": X,
            f"{metric_choice} observée": y,
            "Prédiction WLS": y_pred,
            "Résidu": residuals,
            f"IC inf ({confidence_level}%)": conf_lower,
            f"IC sup ({confidence_level}%)": conf_upper,
            f"IP inf ({confidence_level}%)": pred_lower,
            f"IP sup ({confidence_level}%)": pred_upper,
        })

        st.dataframe(
            df_table.to_pandas().style.format({
                f"{metric_choice} observée": "{:.1f}",
                "Prédiction WLS": "{:.1f}",
                "Résidu": "{:.2f}",
                f"IC inf ({confidence_level}%)": "{:.1f}",
                f"IC sup ({confidence_level}%)": "{:.1f}",
                f"IP inf ({confidence_level}%)": "{:.1f}",
                f"IP sup ({confidence_level}%)": "{:.1f}",
            }),
            use_container_width=True
        )


def analyse_trendline_duree_old():
    """
    Analyse interactive de l'évolution de la durée de préparation.
    Version preprod avec filtres, régressions WLS et statistiques.
    """

    # Chargement des données
    df = load_and_prepare_data()

    # ========================================
    # WIDGETS INTERACTIFS
    # ========================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Filtre années
        all_years = sorted(df["year"].unique().to_list())
        year_range = st.slider(
            "📅 Plage d'années",
            min_value=int(all_years[0]),
            max_value=int(all_years[-1]),
            value=(int(all_years[0]), int(all_years[-1])),
        )

    with col2:
        # Choix couleur moyenne
        color_mean = st.selectbox(
            "🎨 Couleur Moyenne", ["steelblue", "royalblue", "mediumblue", "dodgerblue"], index=0
        )

    with col3:
        # Choix couleur médiane
        color_median = st.selectbox(
            "🎨 Couleur Médiane", ["coral", "tomato", "salmon", "lightsalmon"], index=0
        )

    with col4:
        # Options d'affichage
        show_iqr = st.checkbox("📊 Afficher IQR", value=True)
        show_bubbles = st.checkbox("⭕ Bulles proportionnelles", value=True)

    # ========================================
    # FILTRAGE ET AGRÉGATION DES DONNÉES
    # ========================================

    df_filtered = df.filter(
        (pl.col("year") >= year_range[0]) & (pl.col("year") <= year_range[1])
    )

    minutes_by_year = (
        df_filtered.group_by("year")
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

    # ========================================
    # CALCUL DES RÉGRESSIONS WLS
    # ========================================

    X = minutes_by_year["year"].values
    w = minutes_by_year["n_recipes"].values

    regressions = {}
    for metric_col in ["mean_minutes", "median_minutes"]:
        y = minutes_by_year[metric_col].values
        X_const = sm.add_constant(X)
        wls_model = sm.WLS(y, X_const, weights=w)
        wls_result = wls_model.fit()
        y_pred = wls_result.predict(X_const)

        # R² pondéré
        r2_w = 1 - np.average((y - y_pred) ** 2, weights=w) / np.average(
            (y - np.average(y, weights=w)) ** 2, weights=w
        )

        regressions[metric_col] = {
            "y_pred": y_pred,
            "slope": wls_result.params[1],
            "intercept": wls_result.params[0],
            "r2": r2_w,
            "p_value": wls_result.pvalues[1],
        }

    # ========================================
    # MÉTRIQUES EN BANNIÈRE
    # ========================================

    col_a, col_b, col_c, col_d = st.columns(4)

    with col_a:
        st.metric("⏱️ Moyenne actuelle", f"{minutes_by_year['mean_minutes'].iloc[-1]:.1f} min")

    with col_b:
        st.metric("📊 Médiane actuelle", f"{minutes_by_year['median_minutes'].iloc[-1]:.1f} min")

    with col_c:
        trend_mean = regressions["mean_minutes"]["slope"]
        st.metric(
            "📉 Tendance Moyenne",
            f"{trend_mean:+.3f} min/an",
            delta=f"{trend_mean * len(minutes_by_year):.1f} min sur période",
            delta_color="inverse",
        )

    with col_d:
        trend_median = regressions["median_minutes"]["slope"]
        st.metric(
            "📉 Tendance Médiane",
            f"{trend_median:+.3f} min/an",
            delta=f"{trend_median * len(minutes_by_year):.1f} min sur période",
            delta_color="inverse",
        )

    # ========================================
    # GRAPHIQUE PRINCIPAL
    # ========================================

    fig = go.Figure()

    # Taille des bulles proportionnelle au nombre de recettes
    sizes = minutes_by_year["n_recipes"] / minutes_by_year["n_recipes"].max() * 40

    # Zone IQR (en arrière-plan)
    if show_iqr:
        fig.add_trace(
            go.Scatter(
                x=minutes_by_year["year"],
                y=minutes_by_year["q75"],
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
                y=minutes_by_year["q25"],
                fill="tonexty",
                mode="lines",
                line=dict(width=0),
                fillcolor="rgba(70, 130, 180, 0.15)",
                name="IQR (Q25-Q75)",
                hovertemplate="<b>Année %{x}</b><br>Q25-Q75: %{y:.1f} min<extra></extra>",
            )
        )

    # MOYENNE - Courbe observée
    fig.add_trace(
        go.Scatter(
            x=minutes_by_year["year"],
            y=minutes_by_year["mean_minutes"],
            mode="lines",
            name="Moyenne (observée)",
            line=dict(color=color_mean, width=2.5),
            hovertemplate="<b>Année %{x}</b><br>Moyenne: %{y:.1f} min<br>Recettes: %{customdata:,}<extra></extra>",
            customdata=minutes_by_year["n_recipes"],
        )
    )

    # MOYENNE - Bulles
    if show_bubbles:
        fig.add_trace(
            go.Scatter(
                x=minutes_by_year["year"],
                y=minutes_by_year["mean_minutes"],
                mode="markers",
                name="Moyenne (bulles)",
                marker=dict(
                    color=color_mean, size=sizes, opacity=0.6, line=dict(color="black", width=0.5)
                ),
                showlegend=False,
                hoverinfo="skip",
            )
        )

    # MOYENNE - Régression WLS
    fig.add_trace(
        go.Scatter(
            x=minutes_by_year["year"],
            y=regressions["mean_minutes"]["y_pred"],
            mode="lines",
            name=f"Régression Moyenne (R²={regressions['mean_minutes']['r2']:.3f})",
            line=dict(color="darkblue", width=2.5, dash="dash"),
            hovertemplate="<b>Année %{x}</b><br>Régression: %{y:.1f} min<extra></extra>",
        )
    )

    # MÉDIANE - Courbe observée
    fig.add_trace(
        go.Scatter(
            x=minutes_by_year["year"],
            y=minutes_by_year["median_minutes"],
            mode="lines",
            name="Médiane (observée)",
            line=dict(color=color_median, width=2),
            hovertemplate="<b>Année %{x}</b><br>Médiane: %{y:.1f} min<br>Recettes: %{customdata:,}<extra></extra>",
            customdata=minutes_by_year["n_recipes"],
        )
    )

    # MÉDIANE - Bulles
    if show_bubbles:
        fig.add_trace(
            go.Scatter(
                x=minutes_by_year["year"],
                y=minutes_by_year["median_minutes"],
                mode="markers",
                name="Médiane (bulles)",
                marker=dict(
                    color=color_median,
                    size=sizes,
                    opacity=0.6,
                    line=dict(color="black", width=0.5),
                ),
                showlegend=False,
                hoverinfo="skip",
            )
        )

    # MÉDIANE - Régression WLS
    fig.add_trace(
        go.Scatter(
            x=minutes_by_year["year"],
            y=regressions["median_minutes"]["y_pred"],
            mode="lines",
            name=f"Régression Médiane (R²={regressions['median_minutes']['r2']:.3f})",
            line=dict(color="darkred", width=2.5, dash="dash"),
            hovertemplate="<b>Année %{x}</b><br>Régression: %{y:.1f} min<extra></extra>",
        )
    )

    # ========================================
    # MISE EN FORME
    # ========================================

    title_html = (
        f"<b>Évolution de la durée de préparation (minutes)</b><br>"
        f"<span style='font-size:12px;'>Moyenne: {regressions['mean_minutes']['slope']:+.4f} min/an | "
        f"Médiane: {regressions['median_minutes']['slope']:+.4f} min/an</span>"
    )

    fig.update_layout(
        title=dict(
            text=title_html, font=dict(size=14, color="black", family="Arial, sans-serif")
        ),
        xaxis=dict(
            title="Année",
            title_font=dict(size=12, color="black"),
            tickfont=dict(size=10, color="black"),
            showgrid=True,
            gridcolor="rgba(200,200,200,0.3)",
        ),
        yaxis=dict(
            title="Minutes",
            title_font=dict(size=12, color="black"),
            tickfont=dict(size=10, color="black"),
            showgrid=True,
            gridcolor="rgba(200,200,200,0.3)",
        ),
        height=600,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(size=11, color="black", family="Arial, sans-serif"),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="black",
            borderwidth=1,
            font=dict(size=9),
        ),
        hovermode="x unified",
    )

    # Affichage
    st.plotly_chart(fig, use_container_width=True)

    # ========================================
    # STATISTIQUES DÉTAILLÉES
    # ========================================

    with st.expander("📊 Statistiques détaillées des régressions"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📈 Moyenne")
            st.write(f"**Pente:** {regressions['mean_minutes']['slope']:.6f} min/an")
            st.write(f"**Intercept:** {regressions['mean_minutes']['intercept']:.2f}")
            st.write(f"**R² pondéré:** {regressions['mean_minutes']['r2']:.4f}")
            st.write(f"**p-value:** {regressions['mean_minutes']['p_value']:.4e}")

            if regressions["mean_minutes"]["p_value"] < 0.001:
                st.success("✅ Tendance hautement significative (p < 0.001)")
            elif regressions["mean_minutes"]["p_value"] < 0.05:
                st.success("✅ Tendance significative (p < 0.05)")
            else:
                st.warning("⚠️ Tendance non significative")

            # Calcul du changement total
            total_change_mean = regressions["mean_minutes"]["slope"] * len(minutes_by_year)
            pct_change_mean = (
                total_change_mean / minutes_by_year["mean_minutes"].iloc[0]
            ) * 100
            st.info(f"📉 Changement total: {total_change_mean:+.1f} min ({pct_change_mean:+.1f}%)")

        with col2:
            st.markdown("### 📊 Médiane")
            st.write(f"**Pente:** {regressions['median_minutes']['slope']:.6f} min/an")
            st.write(f"**Intercept:** {regressions['median_minutes']['intercept']:.2f}")
            st.write(f"**R² pondéré:** {regressions['median_minutes']['r2']:.4f}")
            st.write(f"**p-value:** {regressions['median_minutes']['p_value']:.4e}")

            if regressions["median_minutes"]["p_value"] < 0.001:
                st.success("✅ Tendance hautement significative (p < 0.001)")
            elif regressions["median_minutes"]["p_value"] < 0.05:
                st.success("✅ Tendance significative (p < 0.05)")
            else:
                st.warning("⚠️ Tendance non significative")

            # Calcul du changement total
            total_change_median = regressions["median_minutes"]["slope"] * len(minutes_by_year)
            pct_change_median = (
                total_change_median / minutes_by_year["median_minutes"].iloc[0]
            ) * 100
            st.info(
                f"📉 Changement total: {total_change_median:+.1f} min ({pct_change_median:+.1f}%)"
            )

        st.divider()
        st.markdown("### 🔍 Interprétation")

        if regressions["mean_minutes"]["slope"] < 0:
            st.write(
                f"""
            L'analyse de la durée moyenne de préparation montre une **tendance globale à la baisse**
            depuis la création du site. En moyenne, le temps de préparation diminue d'environ
            **{regressions['mean_minutes']['slope']:.2f} min/an**, tandis que la médiane recule de
            **{regressions['median_minutes']['slope']:.2f} min/an**, ce qui traduit une légère
            **simplification des recettes** au fil du temps.
            """
            )
        else:
            st.write(
                f"""
            L'analyse de la durée moyenne de préparation montre une **tendance à la hausse**.
            En moyenne, le temps de préparation augmente d'environ
            **{regressions['mean_minutes']['slope']:+.2f} min/an**, tandis que la médiane progresse de
            **{regressions['median_minutes']['slope']:+.2f} min/an**, ce qui pourrait indiquer une
            **complexification des recettes** au fil du temps.
            """
            )

    # ========================================
    # TABLEAU DES DONNÉES
    # ========================================

    with st.expander("📋 Tableau des données"):
        display_df = minutes_by_year.copy()
        display_df["year"] = display_df["year"].astype(int)
        display_df["mean_minutes"] = display_df["mean_minutes"].round(2)
        display_df["median_minutes"] = display_df["median_minutes"].round(2)
        display_df["q25"] = display_df["q25"].round(2)
        display_df["q75"] = display_df["q75"].round(2)

        st.dataframe(
            display_df.style.format(
                {
                    "mean_minutes": "{:.2f}",
                    "median_minutes": "{:.2f}",
                    "q25": "{:.2f}",
                    "q75": "{:.2f}",
                    "n_recipes": "{:,}",
                }
            ),
            use_container_width=True,
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
