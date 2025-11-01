"""
Module de traductions pour l'application Streamlit Mangetamain Analytics.

Ce module contient toutes les chaînes de caractères traduites en anglais et français
pour rendre l'application bilingue.

Structure:
- common: Chaînes communes à toute l'application
- sidebar: Navigation et menu latéral
- pages: Noms des pages/analyses
- trends: Analyse des tendances temporelles (1999-2018)
- seasonality: Analyses saisonnières
- weekend: Analyses effet jour/week-end
- ratings: Analyses des notes et évaluations
- seasons: Valeurs des saisons (données)
- days: Valeurs des jours de la semaine (données)

Usage:
    from i18n.translations import TRANSLATIONS

    # Obtenir une traduction
    text = TRANSLATIONS["common"]["app_title"]["fr"]  # ou ["en"]
"""

TRANSLATIONS = {
    # ===== COMMON (chaînes communes) =====
    "common": {
        "app_title": {"en": "Mangetamain Analytics", "fr": "Mangetamain Analytics"},
        "back_to_kitchen": {"en": "Back to the Kitchen", "fr": "Back to the Kitchen"},
        "refresh_button": {"en": "Refresh", "fr": "Rafraîchir"},
        "refresh_toast": {
            "en": "Cache cleared - Reloading data...",
            "fr": "Cache vidé - Rechargement des données...",
        },
        "s3_ready": {"en": "S3 Ready", "fr": "S3 Ready"},
        "s3_error": {"en": "S3 Error", "fr": "S3 Error"},
        "last_update": {"en": "Last update", "fr": "Dernière màj"},
        "version": {"en": "Version", "fr": "Version"},
        "documentation": {"en": "Documentation", "fr": "Documentation"},
        "analyses_section": {"en": "ANALYSES", "fr": "ANALYSES"},
        "choose_analysis": {"en": "CHOOSE AN ANALYSIS:", "fr": "CHOISIR UNE ANALYSE:"},
        "coming_soon": {
            "en": "This analysis will be available soon.",
            "fr": "Cette analyse sera disponible prochainement.",
        },
        # Widget & Chart Labels
        "year_range": {"en": "📅 Year range", "fr": "📅 Plage d'années"},
        "show_values": {"en": "🔢 Show values", "fr": "🔢 Afficher valeurs"},
        "show_proportional_bubbles": {
            "en": "⭕ Show proportional bubbles",
            "fr": "⭕ Afficher les bulles proportionnelles",
        },
        "dispersion_interval": {
            "en": "📊 Dispersion interval",
            "fr": "📊 Intervalle de dispersion",
        },
        "detailed_statistics": {
            "en": "📊 Detailed statistics",
            "fr": "📊 Statistiques détaillées",
        },
        "detailed_regression_stats": {
            "en": "📊 Detailed regression statistics",
            "fr": "📊 Statistiques détaillées des régressions",
        },
        "detailed_regression_stat": {
            "en": "📊 Detailed regression statistics",
            "fr": "📊 Statistiques détaillées de la régression",
        },
        "years": {"en": "📊 Years", "fr": "📊 Années"},
        "metric_to_analyze": {
            "en": "📊 Metric to analyze",
            "fr": "📊 Métrique à analyser",
        },
        "average_per_year": {"en": "📈 Average/year", "fr": "📈 Moyenne/an"},
        "label_median": {"en": "Median", "fr": "Médiane"},
        "label_average": {"en": "Average", "fr": "Moyenne"},
        "std_dev": {"en": "Std dev", "fr": "Écart-type"},
        "current_average": {"en": "⏱️ Current average", "fr": "⏱️ Moyenne actuelle"},
        "current_median": {"en": "📊 Current median", "fr": "📊 Médiane actuelle"},
        "average_slope": {"en": "📉 Average slope", "fr": "📉 Pente Moyenne"},
        "median_slope": {"en": "📉 Median slope", "fr": "📉 Pente Médiane"},
        "current_dispersion": {
            "en": "📏 Current dispersion",
            "fr": "📏 Dispersion actuelle",
        },
        "average_per_season": {
            "en": "📈 Average per season",
            "fr": "📈 Moyenne par saison",
        },
        "global_average": {"en": "📊 Global average", "fr": "📊 Moyenne globale"},
        "weekday_average": {"en": "Weekday (average)", "fr": "Semaine (moyenne)"},
        "weekend_average": {"en": "Weekend (average)", "fr": "Week-end (moyenne)"},
        "average_observed": {"en": "Average (observed)", "fr": "Moyenne (observée)"},
        "median_observed": {"en": "Median (observed)", "fr": "Médiane (observée)"},
        "volume_average": {"en": "Volume (average)", "fr": "Volume (moyenne)"},
        "volume_median": {"en": "Volume (median)", "fr": "Volume (médiane)"},
        "observed_trend": {"en": "Observed trend", "fr": "Tendance observée"},
        "observed_data": {"en": "Observed data", "fr": "Données observées"},
        "average_bubbles": {"en": "Average (bubbles)", "fr": "Moyenne (bulles)"},
        "median_bubbles": {"en": "Median (bubbles)", "fr": "Médiane (bulles)"},
        "theoretical_line": {"en": "Theoretical line", "fr": "Ligne théorique"},
        "wls_regression": {"en": "WLS regression", "fr": "Régression WLS"},
        "view_raw_values": {
            "en": "View raw values (non-normalized)",
            "fr": "Voir les valeurs brutes (non normalisées)",
        },
        "avg_duration_season_iqr": {
            "en": "Average duration per season (with IQR)",
            "fr": "Durée moyenne par saison (avec IQR)",
        },
        "deviation_from_average": {
            "en": "Deviation from global average (%)",
            "fr": "Écart à la moyenne globale (%)",
        },
        "interpretation_title": {
            "en": "### 📊 Interpretation",
            "fr": "### 📊 Interprétation",
        },
        "weighted_r2": {"en": "Weighted R²", "fr": "R² pondéré"},
        # Axes labels
        "axis_period": {"en": "Period", "fr": "Période"},
        "axis_minutes": {"en": "Minutes", "fr": "Minutes"},
        "axis_season": {"en": "Season", "fr": "Saison"},
        "axis_year": {"en": "Year", "fr": "Année"},
        "axis_frequency": {"en": "Frequency", "fr": "Fréquence"},
        "axis_ingredient": {"en": "Ingredient", "fr": "Ingrédient"},
        # Metrics headers
        "semaine_moyenne": {"en": "WEEKDAY (AVERAGE)", "fr": "SEMAINE (MOYENNE)"},
        "difference": {"en": "DIFFERENCE", "fr": "DIFFÉRENCE"},
        "iqr_semaine": {"en": "WEEKDAY IQR", "fr": "IQR SEMAINE"},
        # Chart titles
        "duree_recettes_periode": {
            "en": "Recipe duration by period",
            "fr": "Durée des recettes par période",
        },
        "distribution_durees_boxplot": {
            "en": "Duration distribution (boxplot)",
            "fr": "Distribution des durées (boxplot)",
        },
        "nombre_recettes_saison": {
            "en": "Number of recipes per season",
            "fr": "Nombre de recettes par saison",
        },
        "repartition_saisonniere": {
            "en": "Seasonal distribution (%)",
            "fr": "Répartition saisonnière (%)",
        },
        "score_complexite": {"en": "Complexity score", "fr": "Score de complexité"},
        "nombre_etapes": {"en": "Number of steps", "fr": "Nombre d'étapes"},
        "nombre_ingredients": {
            "en": "Number of ingredients",
            "fr": "Nombre d'ingrédients",
        },
        "profil_nutritionnel_normalise": {
            "en": "Nutritional profile by season (normalized values)",
            "fr": "Profil nutritionnel par saison (valeurs normalisées)",
        },
        "top20_ingredients_variabilite": {
            "en": "Top 20 ingredients - Seasonal variability",
            "fr": "Top 20 ingrédients - Variabilité saisonnière",
        },
        # Other metrics
        "ecart_max_min": {"en": "📏 Max-min range", "fr": "📏 Écart max-min"},
        "ecart_calorique": {"en": "📊 Caloric range", "fr": "📊 Écart calorique"},
        "ingredients_analyses": {
            "en": "🔍 Ingredients analyzed",
            "fr": "🔍 Ingrédients analysés",
        },
        "variables_filtres": {
            "en": "📊 Variables (filtered)",
            "fr": "📊 Variables (filtrés)",
        },
        "top_affiches": {"en": "🏆 Top displayed", "fr": "🏆 Top affichés"},
        "tags_analyses": {"en": "🏷️ Tags analyzed", "fr": "🏷️ Tags analysés"},
        # Nutrients
        "proteines_pct": {"en": "Protein (%)", "fr": "Protéines (%)"},
        "lipides_pct": {"en": "Lipids (%)", "fr": "Lipides (%)"},
        "graisses_sat_pct": {"en": "Sat. fat (%)", "fr": "Graisses sat. (%)"},
        # Metrics
        "nutrients_analyzed": {"en": "Nutrients analyzed", "fr": "Nutriments analysés"},
        "significant_differences": {
            "en": "Significant differences",
            "fr": "Différences significatives",
        },
        "total_ingredients": {"en": "Total ingredients", "fr": "Total ingrédients"},
        "variable_ingredients": {
            "en": "Variable ingredients",
            "fr": "Ingrédients variables",
        },
        # Hovertemplate
        "hover_moyenne": {"en": "Average", "fr": "Moyenne"},
        "hover_mediane": {"en": "Median", "fr": "Médiane"},
        "hover_recettes": {"en": "Recipes", "fr": "Recettes"},
        "hover_complexite": {"en": "Complexity", "fr": "Complexité"},
        "hover_etapes": {"en": "Steps", "fr": "Étapes"},
        "hover_ingredients": {"en": "Ingredients", "fr": "Ingrédients"},
        "hover_frequence": {"en": "Frequency", "fr": "Fréquence"},
        "hover_saison": {"en": "Season", "fr": "Saison"},
        # Z-score
        "zscore_ecart_moyenne": {
            "en": "Z-score<br>(deviation from mean)",
            "fr": "Z-score<br>(écart à la moyenne)",
        },
        # Season labels
        "plus_etapes": {"en": "(+ steps)", "fr": "(+ étapes)"},
        "plus_ingredients": {"en": "(+ ingredients)", "fr": "(+ ingrédients)"},
        "plus_leger": {"en": "(lighter)", "fr": "(+ léger)"},
        "utilisation_saisonniere": {
            "en": "Seasonal<br>usage (%)",
            "fr": "Utilisation<br>saisonnière (%)",
        },
        # Axis titles
        "nb_etapes": {"en": "Num. steps", "fr": "Nb étapes"},
        "nb_ingredients": {"en": "Num. ingredients", "fr": "Nb ingrédients"},
    },
    # ===== SIDEBAR (navigation, menu) =====
    "sidebar": {
        "navigation": {"en": "Navigation", "fr": "Navigation"},
    },
    # ===== PAGES (noms des analyses) =====
    "pages": {
        "trends": {"en": "Trends 1999-2018", "fr": "Tendances 1999-2018"},
        "seasonality": {"en": "Seasonal Analyses", "fr": "Analyses Saisonnières"},
        "weekend": {"en": "Day/Weekend Effect", "fr": "Effet Jour/Week-end"},
        "ratings": {"en": "Ratings Analyses", "fr": "Analyses Ratings"},
    },
    # ===== TRENDS (analyse_trendlines_v2.py) =====
    "trends": {
        "main_title": {
            "en": "Long-term Trend Analyses (1999-2018)",
            "fr": "Analyses des tendances temporelles (1999-2018)",
        },
        "main_description": {
            "en": """This section presents **long-term trend analyses** of Food.com recipes
from 1999 to 2018, using **WLS (Weighted Least Squares) regressions**
to identify significant trends.""",
            "fr": """Cette section présente les **analyses de tendances à long terme** des recettes Food.com
sur la période 1999-2018, en utilisant des **régressions WLS (Weighted Least Squares)**
pour identifier les évolutions significatives.""",
        },
        "metric_period": {"en": "Period", "fr": "Période"},
        "metric_period_value": {"en": "20 years", "fr": "20 années"},
        "metric_recipes": {"en": "Recipes", "fr": "Recettes"},
        "metric_recipes_value": {"en": "Total analyzed", "fr": "Total analysées"},
        "metric_analyses": {"en": "Analyses", "fr": "Analyses"},
        "metric_analyses_value": {
            "en": "Dimensions studied",
            "fr": "Dimensions étudiées",
        },
        "metric_method": {"en": "Method", "fr": "Méthode"},
        "metric_method_value": {
            "en": "Weighted Least Squares",
            "fr": "Weighted Least Squares",
        },
        # Volume
        "volume_title": {"en": "Recipe Volume", "fr": "Volume de recettes"},
        "volume_year_range": {"en": "Year range", "fr": "Plage d'années"},
        "volume_show_values": {"en": "Show values", "fr": "Afficher valeurs"},
        "volume_metric_years": {"en": "Years", "fr": "Années"},
        "volume_metric_total": {"en": "Total recipes", "fr": "Total recettes"},
        "volume_metric_average": {"en": "Average/year", "fr": "Moyenne/an"},
        "volume_chart_title": {
            "en": "Number of recipes per year",
            "fr": "Nombre de recettes par année",
        },
        "volume_chart_qq_title": {
            "en": "Q-Q Plot (Normality test)",
            "fr": "Q-Q Plot (Test de normalité)",
        },
        "volume_axis_year": {"en": "Year", "fr": "Année"},
        "volume_axis_recipes": {"en": "Number of recipes", "fr": "Nombre de recettes"},
        "volume_axis_theoretical": {
            "en": "Theoretical quantiles (normal distribution)",
            "fr": "Quantiles théoriques (loi normale)",
        },
        "volume_axis_observed": {
            "en": "Observed quantiles",
            "fr": "Quantiles observés",
        },
        "volume_stats_title": {
            "en": "Detailed statistics",
            "fr": "Statistiques détaillées",
        },
        "volume_stats_min": {"en": "Min", "fr": "Min"},
        "volume_stats_q1": {"en": "Q1", "fr": "Q1"},
        "volume_stats_median": {"en": "Median", "fr": "Médiane"},
        "volume_stats_mean": {"en": "Mean", "fr": "Moyenne"},
        "volume_stats_q3": {"en": "Q3", "fr": "Q3"},
        "volume_stats_max": {"en": "Max", "fr": "Max"},
        "volume_stats_std": {"en": "Std dev", "fr": "Écart-type"},
        "volume_stats_cv": {"en": "Coef. of variation", "fr": "Coef. variation"},
        "volume_stats_r2": {"en": "R² (normality test):", "fr": "R² (test normalité):"},
        "volume_stats_normal": {
            "en": "Distribution close to normal",
            "fr": "Distribution proche de la normale",
        },
        "volume_stats_slightly_normal": {
            "en": "Distribution slightly deviating from normal",
            "fr": "Distribution légèrement éloignée de la normale",
        },
        "volume_stats_not_normal": {
            "en": "Non-normal distribution",
            "fr": "Distribution non normale",
        },
        "volume_interpretation": {
            "en": """💡 **Statistical interpretation**
We observe a **sharp increase in the number of posted recipes until 2007**,
the year of **peak activity**, followed by a **marked decline** in subsequent years.
The **normality tests** and **Q-Q plots** show that the distribution of
**recipes per year** is **not perfectly normal**, with **visible deviations**
from the **theoretical normal distribution**.""",
            "fr": """💡 **Interprétation statistique**
Nous observons une **forte augmentation du nombre de recettes postées jusqu'en 2007**,
année du **pic d'activité**, suivie d'une **chute marquée** les années suivantes.
Les **tests de normalité** et les **Q-Q plots** montrent que la distribution du
**nombre de recettes par an** **n'est pas parfaitement normale**, avec des **écarts visibles**
par rapport à la **loi normale théorique**.""",
        },
        # Durée
        "duration_title": {"en": "Preparation Time", "fr": "Durée de préparation"},
        "duration_show_bubbles": {
            "en": "Show proportional bubbles",
            "fr": "Afficher les bulles proportionnelles",
        },
        "duration_dispersion_interval": {
            "en": "Dispersion interval",
            "fr": "Intervalle de dispersion",
        },
        "duration_interval_iqr": {
            "en": "Q25-Q75 (Classic IQR)",
            "fr": "Q25-Q75 (IQR classique)",
        },
        "duration_interval_large": {"en": "Q10-Q90 (Wide)", "fr": "Q10-Q90 (Large)"},
        "duration_interval_very_large": {
            "en": "Q5-Q95 (Very wide)",
            "fr": "Q5-Q95 (Très large)",
        },
        "duration_interval_narrow": {
            "en": "Q33-Q66 (Narrow)",
            "fr": "Q33-Q66 (Étroit)",
        },
        "duration_metric_current_mean": {
            "en": "Current average",
            "fr": "Moyenne actuelle",
        },
        "duration_metric_current_median": {
            "en": "Current median",
            "fr": "Médiane actuelle",
        },
        "duration_metric_slope_mean": {"en": "Mean slope", "fr": "Pente Moyenne"},
        "duration_metric_slope_median": {"en": "Median slope", "fr": "Pente Médiane"},
        "duration_metric_current_dispersion": {
            "en": "Current dispersion",
            "fr": "Dispersion actuelle",
        },
        "duration_interpretation": {
            "en": """💡 **Statistical interpretation**

**The analysis of average preparation time** shows a **global downward trend**
since the site's creation.

On average, **preparation time decreases by approximately −0.46 min per year**, while the **median declines by −0.26 min per year**,
indicating a **slight simplification of recipes** over time.""",
            "fr": """💡 **Interprétation statistique**

**L'analyse de la durée moyenne de préparation** montre une **tendance globale à la baisse**
depuis la création du site.

En moyenne, le **temps de préparation diminue d'environ −0.46 min par an**, tandis que la **médiane recule de −0.26 min par an**,
ce qui traduit une **légère simplification des recettes** au fil du temps.""",
        },
        # Complexité
        "complexity_title": {
            "en": "Recipe Complexity",
            "fr": "Complexité des recettes",
        },
        "complexity_interpretation": {
            "en": """💡 **Statistical interpretation**
The **weighted linear regression** reveals a **significant upward trend**
in the **average complexity score** (slope = **+0.0008**,
R² = **0.76**, p = **4.70e-08**).
This evolution indicates a **progressive increase in recipe complexity** over time,
suggesting **increasingly elaborate preparations**. The trend is **consistent** with the increase
in **number of steps** and **number of ingredients**, confirming a **global complexification** of published recipes.""",
            "fr": """💡 **Interprétation statistique**
La **régression linéaire pondérée** met en évidence une **tendance significative à la hausse**
du **score moyen de complexité** (pente = **+0.0008**,
R² = **0.76**, p = **4.70e-08**).
Cette évolution indique une **augmentation progressive de la complexité des recettes** au fil du temps,
suggérant des **préparations de plus en plus élaborées**. La tendance est **cohérente** avec l'augmentation
du **nombre d'étapes** et du **nombre d'ingrédients**, confirmant une **complexification globale** des recettes publiées.""",
        },
        # Nutrition
        "nutrition_title": {
            "en": "Nutritional Values",
            "fr": "Valeurs nutritionnelles",
        },
        "nutrition_interpretation": {
            "en": """💡 **Statistical interpretation**
The **weighted linear regressions** show a **significant downward trend**
in **average nutritional values** over time. **Calories**, **carbs**, **fats**, and **proteins**
all show **negative slopes**, with **weighted R² between 0.39 and 0.56**, indicating a
**good portion of explained variance** and a **measurable decrease** in average nutritional intakes per recipe.
This evolution reflects a **progressive shift towards lighter recipes**, less rich in **calories**
and **macronutrients**, likely reflecting an **adaptation to modern dietary trends**
(seeking more balanced and less energy-dense dishes).""",
            "fr": """💡 **Interprétation statistique**
Les **régressions linéaires pondérées** montrent une **tendance significative à la baisse**
des valeurs **nutritionnelles moyennes** au fil du temps. Les **calories**, **glucides**, **lipides** et **protéines**
présentent toutes des **pentes négatives**, avec des **R² pondérés entre 0.39 et 0.56**, indiquant une
**bonne part de variance expliquée** et une **diminution mesurable** des apports nutritionnels moyens par recette.
Cette évolution traduit une **orientation progressive vers des recettes plus légères**, moins riches en **calories**
et en **macronutriments**, reflétant probablement une **adaptation aux tendances alimentaires modernes**
(recherche de plats plus équilibrés et moins énergétiques).""",
        },
        # Ingrédients
        "ingredients_title": {"en": "Ingredients", "fr": "Ingrédients"},
        "ingredients_info": {
            "en": "Analysis of the 10 most popular ingredients",
            "fr": "Analyse des 10 ingrédients les plus populaires",
        },
        "ingredients_interpretation": {
            "en": """💡 **Statistical interpretation**
The analysis reveals a **profound transformation** in ingredient usage over time.
**Rising trends**: Ingredients like *kosher salt*, *garlic cloves*, *olive oil*, and *unsalted butter*
show strong growth, perhaps reflecting a shift towards more communal or Mediterranean cuisine.
**Declining trends**: Traditional ingredients like *sugar*, *butter*, *eggs*, and *vanilla* are in sharp decline,
suggesting a decrease in classic baking recipes and a search for less sweet recipes.
**Diversity decline**: The number of unique ingredients drops drastically, from the maximum at the beginning of the period
to a minimum at the end. This significant drop is explained by the decrease in recipe volume posted
after 2007, leading to a concentration on more common ingredients and a loss of culinary innovation.""",
            "fr": """💡 **Interprétation statistique**
L'analyse révèle une **transformation profonde** de l'usage des ingrédients au fil du temps.
**Tendances montantes**: Des ingrédients comme *kosher salt*, *garlic cloves*, *olive oil* et *unsalted butter*
connaissent une forte progression, reflétant peut-être un virage vers une cuisine plus communautaire ou méditerranéenne.
**Tendances descendantes**: Les ingrédients traditionnels comme *sugar*, *butter*, *eggs* et *vanilla* sont en net recul,
suggérant une diminution des recettes de pâtisserie classique et une recherche de recettes moins sucrées.
**Chute de la diversité**: Le nombre d'ingrédients uniques chute drastiquement, passant du maximum en début de période
à un minimum en fin de période. Cette baisse significative s'explique par la diminution du volume de recettes postées
après 2007, entraînant une concentration sur des ingrédients plus courants et une perte d'innovation culinaire.""",
        },
        # Tags
        "tags_title": {"en": "Tags/Categories", "fr": "Tags/Catégories"},
        "tags_info": {
            "en": "Analysis of the 10 most frequent tags",
            "fr": "Analyse des 10 tags les plus fréquents",
        },
        "tags_interpretation": {
            "en": """💡 **Statistical interpretation**
Tag analysis reveals the **thematic evolution** of recipes over time.
Like ingredients, we observe a **diversity decline** of tags, from a maximum at the beginning
of the period to a minimum at the end, reflecting the decrease in recipe volume posted after 2007.
The **rising and falling trends** of tags allow identifying **culinary themes**
that gain or lose popularity, offering insight into **food preferences** and **culinary trends**
that characterize each period.""",
            "fr": """💡 **Interprétation statistique**
L'analyse des tags révèle les **évolutions thématiques** des recettes au fil du temps.
Comme pour les ingrédients, on observe une **chute de la diversité** des tags, passant d'un maximum en début
de période à un minimum en fin de période, reflétant la diminution du volume de recettes postées après 2007.
Les **tendances montantes et descendantes** des tags permettent d'identifier les **thématiques culinaires**
qui gagnent ou perdent en popularité, offrant un aperçu des **préférences alimentaires** et des **modes culinaires**
qui caractérisent chaque période.""",
        },
        # Complexity regression interpretation
        "complexity_regression_interpretation": {
            "fr": """La **régression linéaire pondérée** met en évidence une **tendance significative à la hausse**
du **score moyen de complexité** (pente = **{slope:+.4f}**, R² = **{r2:.2f}**, p = **{pvalue:.2e}**).""",
            "en": """The **weighted linear regression** reveals a **significant upward trend**
in the **average complexity score** (slope = **{slope:+.4f}**, R² = **{r2:.2f}**, p = **{pvalue:.2e}**).""",
        },
        # Graph titles - Ingredients
        "ingredients_most_frequent": {
            "en": "Top {n} most frequent ingredients",
            "fr": "Top {n} ingrédients les plus fréquents",
        },
        "ingredients_diversity_evolution": {
            "en": "Ingredient diversity evolution",
            "fr": "Évolution de la diversité des ingrédients",
        },
        "ingredients_top_increases_short": {
            "en": "Top {n} increases ({min_year}→{max_year})",
            "fr": "Top {n} hausses ({min_year}→{max_year})",
        },
        "ingredients_top_decreases_short": {
            "en": "Top {n} decreases ({min_year}→{max_year})",
            "fr": "Top {n} baisses ({min_year}→{max_year})",
        },
        "ingredients_top_increases": {
            "en": "Evolution: Top {n} increases",
            "fr": "Évolution : Top {n} hausses",
        },
        "ingredients_top_decreases": {
            "en": "Evolution: Top {n} decreases",
            "fr": "Évolution : Top {n} baisses",
        },
        "ingredients_top_increases_period": {
            "en": "Top 10 increases (1999 - 2018)",
            "fr": "Top 10 hausses (1999 - 2018)",
        },
        "ingredients_top_decreases_period": {
            "en": "Top 10 decreases (1999 - 2018)",
            "fr": "Top 10 baisses (1999 - 2018)",
        },
        # Graph titles - Tags
        "tags_most_frequent": {
            "en": "Top {n} most frequent tags",
            "fr": "Top {n} tags les plus fréquents",
        },
        "tags_diversity_evolution": {
            "en": "Tag diversity evolution",
            "fr": "Évolution de la diversité des tags",
        },
        "tags_top_increases_short": {
            "en": "Top {n} increases ({min_year}→{max_year})",
            "fr": "Top {n} hausses ({min_year}→{max_year})",
        },
        "tags_top_decreases_short": {
            "en": "Top {n} decreases ({min_year}→{max_year})",
            "fr": "Top {n} baisses ({min_year}→{max_year})",
        },
        "tags_top_increases": {
            "en": "Evolution: Top {n} increases",
            "fr": "Évolution : Top {n} hausses",
        },
        "tags_top_decreases": {
            "en": "Evolution: Top {n} decreases",
            "fr": "Évolution : Top {n} baisses",
        },
        # Axis labels
        "axis_total_occurrences": {
            "en": "Total occurrences",
            "fr": "Occurrences totales",
        },
        "axis_unique_ingredients": {
            "en": "Unique ingredients count",
            "fr": "Nombre d'ingrédients uniques",
        },
        "axis_unique_tags": {
            "en": "Unique tags count",
            "fr": "Nombre de tags uniques",
        },
        "axis_ingredients_count": {
            "en": "Ingredients count",
            "fr": "Nombre d'ingrédients",
        },
        "axis_frequency": {
            "en": "Frequency",
            "fr": "Fréquence",
        },
        "axis_occurrences": {
            "en": "Occurrences",
            "fr": "Occurrences",
        },
        "duration_evolution_title": {
            "en": "Duration Evolution (minutes)",
            "fr": "Évolution de la durée (minutes)",
        },
        "info_blue_zone": {
            "fr": """💡 **Zone bleue ({quantile})** : Représente la dispersion des durées de recettes.

- **Zone large** → Grande variété de durées (recettes courtes ET longues)
- **Zone étroite** → Durées homogènes (recettes similaires)
- **Changement de largeur** → Évolution de la diversité des recettes au fil du temps

📊 Dispersion actuelle : **{dispersion:.1f} minutes** d'écart entre Q{q_low} et Q{q_high}""",
            "en": """💡 **Blue zone ({quantile})**: Represents the dispersion of recipe durations.

- **Wide zone** → High variety of durations (short AND long recipes)
- **Narrow zone** → Homogeneous durations (similar recipes)
- **Width change** → Evolution of recipe diversity over time

📊 Current dispersion: **{dispersion:.1f} minutes** between Q{q_low} and Q{q_high}""",
        },
    },
    # ===== SEASONALITY (analyse_seasonality.py) =====
    "seasonality": {
        "main_title": {
            "en": "Seasonal Analyses (1999-2018)",
            "fr": "Analyses Saisonnières (1999-2018)",
        },
        "main_description": {
            "en": """This section presents **seasonality analyses** of recipes published on Food.com (1999-2018).

The analyses compare recipe characteristics across **4 seasons**:
- **Winter**: December, January, February
- **Spring**: March, April, May
- **Summer**: June, July, August
- **Autumn**: September, October, November""",
            "fr": """Cette section présente les analyses de **saisonnalité** des recettes publiées sur Food.com (1999-2018).

Les analyses comparent les caractéristiques des recettes selon les **4 saisons** :
- **Winter** (Hiver) : Décembre, Janvier, Février
- **Spring** (Printemps) : Mars, Avril, Mai
- **Summer** (Été) : Juin, Juillet, Août
- **Autumn** (Automne) : Septembre, Octobre, Novembre""",
        },
        # Volume
        "volume_title": {
            "en": "Recipe volume by season",
            "fr": "Volume de recettes par saison",
        },
        "volume_metric_total": {"en": "Total recipes", "fr": "Total recettes"},
        "volume_metric_average": {
            "en": "Average per season",
            "fr": "Moyenne par saison",
        },
        "volume_interpretation": {
            "en": """💡 **Statistical interpretation**
The **Chi-squared test** shows that the **seasonal distribution** of recipe numbers **is not uniform**,
with **significant differences** between seasons.

**Spring**, well above average (+8.7%),
indicates a **marked seasonality** in production, while other seasons remain **relatively stable**.""",
            "fr": """💡 **Interprétation statistique**
Le **test du χ²** montre que la **répartition saisonnière** du nombre de recettes **n'est pas uniforme**,
avec des **écarts significatifs** entre les saisons.

Le **Printemps**, nettement au-dessus de la moyenne (+8.7%),
indique une **saisonnalité marquée** dans la production, tandis que les autres saisons restent **relativement stables**.""",
        },
        # Durée
        "duration_title": {
            "en": "Preparation time by season",
            "fr": "Durée de préparation par saison",
        },
        "duration_interpretation": {
            "en": """💡 **Statistical interpretation**
The **Kruskal-Wallis test** confirms **significant differences** in duration between seasons (p < 0.001).

Recipes posted in **Autumn** are the longest (43-44 minutes on average),
while those posted in **Summer** are the shortest (41-42 minutes).

**Autumn/Winter:** More elaborate recipes (stews, soups)
**Summer/Spring:** Faster recipes (salads, grills, fresh dishes)""",
            "fr": """💡 **Interprétation statistique**
Le **test de Kruskal-Wallis** confirme des **différences significatives** de durée entre les saisons (p < 0.001).

Les recettes postées en **Automne** sont les plus longues (43-44 minutes en moyenne),
tandis que celles postées en **Été** sont les plus courtes (41-42 minutes).

**Automne/Hiver:** Recettes plus élaborées (plats mijotés, soupes)
**Été/Printemps:** Recettes plus rapides (salades, grillades, plats frais)""",
        },
        # Complexité
        "complexity_title": {
            "en": "Complexity (steps/ingredients) by season",
            "fr": "Complexité (étapes/ingrédients) par saison",
        },
        "complexity_interpretation": {
            "en": """💡 **Statistical interpretation**
The **Kruskal-Wallis tests** reveal **significant differences** in complexity between seasons (p < 0.001).

Recipes posted in **Winter/Autumn** are the most elaborate, while those posted in **summer**
favor simplified preparations.

This **marked seasonality** reflects culinary habits:
- **Winter/Autumn:** Stews, soups, ragouts (more steps, more ingredients)
- **Summer/Spring:** Quick and fresh recipes (salads, grills, simple dishes)""",
            "fr": """💡 **Interprétation statistique**
Les **tests de Kruskal-Wallis** révèlent des **différences significatives** de complexité entre les saisons (p < 0.001).

Les recettes postées en **Hiver/Automne** sont les plus élaborées, tandis que celles postées en **été**
privilégient des préparations simplifiées.

Cette **saisonnalité marquée** reflète les habitudes culinaires :
- **Hiver/Automne:** Plats mijotés, soupes, ragoûts (plus d'étapes, plus d'ingrédients)
- **Été/Printemps:** Recettes rapides et fraîches (salades, grillades, plats simples)""",
        },
        # Nutrition
        "nutrition_title": {
            "en": "Nutritional profile by season",
            "fr": "Profil nutritionnel par saison",
        },
        "nutrition_interpretation": {
            "en": """💡 **Statistical interpretation**
The **Kruskal-Wallis tests** reveal **significant nutritional differences** between seasons (p < 0.05).

Recipes posted in **Autumn** are the most **caloric** (492 kcal on average)
and rich in **fats**, **sugars**, and **saturated fats**.

Conversely, those posted in **Summer** favor **lighter** preparations
with 446 kcal on average.

**Seasonal pattern:**
- **Autumn/Winter:** Comforting, rich recipes (creamy soups, stews, pastries)
- **Spring/Summer:** Fresh, light recipes (salads, grills, fruits)""",
            "fr": """💡 **Interprétation statistique**
Les **tests de Kruskal-Wallis** révèlent des **différences nutritionnelles significatives** entre les saisons (p < 0.05).

Les recettes postées en **Automne** sont les plus **caloriques** (492 kcal en moyenne)
et riches en **lipides**, **sucres** et **graisses saturées**.

À l'inverse, celles postées en **Été** privilégient des préparations plus **légères**
avec 446 kcal en moyenne.

**Pattern saisonnier:**
- **Automne/Hiver:** Recettes réconfortantes, riches (soupes crémeuses, ragoûts, pâtisseries)
- **Printemps/Été:** Recettes fraîches, légères (salades, grillades, fruits)""",
        },
        # Ingrédients
        "ingredients_title": {
            "en": "Common ingredients by season",
            "fr": "Ingrédients fréquents par saison",
        },
        "ingredients_interpretation": {
            "en": """💡 **Statistical interpretation**
The **Chi-squared tests** reveal **significant seasonal variability (p < 0.05)** among the most
variable ingredients (**top 20**), confirming that **posted recipes clearly vary by season**.

These differences reflect **marked culinary habits** and adaptation to **available products**
throughout the year.

**Seasonal patterns:**
- **Summer:** Freshness and lightness (fresh vegetables, aromatic herbs, fruits)
- **Autumn:** Rich and comforting preparations (baking soda, carrots, pastry)
- **Winter:** Stews and soups
- **Spring:** Renewal and spring vegetables""",
            "fr": """💡 **Interprétation statistique**
Les **tests du Chi-2** révèlent une **variabilité saisonnière significative (p < 0.05)** parmi les ingrédients
les plus variables (**top 20**), confirmant que les **recettes postées varient clairement selon les saisons**.

Ces différences traduisent des **habitudes culinaires marquées** et une adaptation aux **produits disponibles**
au fil de l'année.

**Patterns saisonniers:**
- **Été:** Fraîcheur et légèreté (légumes frais, herbes aromatiques, fruits)
- **Automne:** Préparations riches et réconfortantes (baking soda, carottes, pâtisserie)
- **Hiver:** Plats mijotés et soupes
- **Printemps:** Renouveau et légumes printaniers""",
        },
        # Tags
        "tags_title": {
            "en": "Popular tags by season",
            "fr": "Tags populaires par saison",
        },
        "tags_interpretation": {
            "en": """💡 **Statistical interpretation**
Analyses of seasonal variability in culinary tags show **clear segmentation by season**,
confirming **trends consistent with periods of the year**.

**Identified seasonal patterns:**

- **Summer:** Summer conviviality tags (summer, barbecue, grilling)
- **Autumn/Winter:** Event tags (thanksgiving, christmas) and comfort (winter, gifts, new-years)
- **Spring:** Renewal tags (spring, berries) reflecting fresh and light cuisine
- **Winter:** Holiday themes and rich traditional cuisine

These differences confirm that **posted recipes clearly vary by season**, consistent
with calendar events and seasonal culinary habits.""",
            "fr": """💡 **Interprétation statistique**
Les analyses de variabilité saisonnière des tags culinaires montrent une **segmentation claire selon les saisons**,
confirmant des **tendances cohérentes avec les périodes de l'année**.

**Patterns saisonniers identifiés:**

- **Été:** Tags de convivialité estivale (summer, barbecue, grilling)
- **Automne/Hiver:** Tags d'événements (thanksgiving, christmas) et réconfort (winter, gifts, new-years)
- **Printemps:** Tags de renouveau (spring, berries) reflétant une cuisine fraîche et légère
- **Hiver:** Thèmes de fêtes et cuisine traditionnelle riche

Ces différences confirment que les **recettes postées varient clairement selon les saisons**, en cohérence
avec les événements calendaires et les habitudes culinaires saisonnières.""",
        },
        # Metric labels
        "season_most_steps": {
            "en": "{season} (+ complex)",
            "fr": "{season} (+ complexe)",
        },
        "steps_count": {
            "en": "{count} steps",
            "fr": "{count} étapes",
        },
        "season_most_ingredients": {
            "en": "{season} (+ varied)",
            "fr": "{season} (+ varié)",
        },
        "season_lightest": {
            "en": "{season} (+ light)",
            "fr": "{season} (+ léger)",
        },
        "calories_count": {
            "en": "{calories} kcal",
            "fr": "{calories} kcal",
        },
        "tags_seasonal_variability": {
            "en": "Seasonal variability of culinary tags",
            "fr": "Variabilité saisonnière des tags culinaires",
        },
    },
    # ===== WEEKEND (analyse_weekend.py) =====
    "weekend": {
        "main_title": {
            "en": "Day/Weekend Effect Analyses (1999-2018)",
            "fr": "Analyses Effet Jour/Week-end (1999-2018)",
        },
        "main_description": {
            "en": """This section presents analyses of the **weekend effect** on recipes published on Food.com (1999-2018).

The analyses compare recipe characteristics **Weekday** (Monday-Friday) vs. **Weekend** (Saturday-Sunday).""",
            "fr": """Cette section présente les analyses de l'**effet week-end** sur les recettes publiées sur Food.com (1999-2018).

Les analyses comparent les caractéristiques des recettes **Weekday** (Lundi-Vendredi) vs. **Weekend** (Samedi-Dimanche).""",
        },
        # Volume
        "volume_title": {
            "en": "Recipe volume (Weekday vs Weekend)",
            "fr": "Volume de recettes (Weekday vs Weekend)",
        },
        "volume_interpretation": {
            "en": """💡 **Statistical interpretation**
The **weighted Chi-squared test** reveals a **statistically very significant difference**
(p < 0.001) between Weekday and Weekend volumes. **Recipes are massively published during the week**:
on average **recipes are published +51% more on weekdays than weekends**.

**Monday is the most active day** (+45% above average), followed by **Tuesday** (+29%) and **Wednesday** (+13%).
Conversely, **Saturday is the least active day** (-49%), followed by **Sunday** (-36%).
Users mainly publish **at the beginning of the week**.""",
            "fr": """💡 **Interprétation statistique**
Le **test Chi-2 pondéré** révèle une **différence statistiquement très significative**
(p < 0.001) entre les volumes Weekday et Weekend. **Les recettes sont massivement publiées en semaine** :
en moyenne **les recettes sont publiées +51% plus en semaine que le week-end**.

Le **lundi est le jour le plus actif** (+45% au-dessus de la moyenne), suivi du **mardi** (+29%) et du **mercredi** (+13%).
À l'inverse, le **samedi est le jour le moins actif** (-49%), suivi du **dimanche** (-36%).
Les utilisateurs publient principalement **en début de semaine**.""",
        },
        # Durée
        "duration_title": {
            "en": "Preparation time",
            "fr": "Durée de préparation",
        },
        "duration_interpretation": {
            "en": """💡 **Statistical interpretation**
The **Student's t-test** reveals **no significant difference**
between Weekday and Weekend durations. **Means are nearly identical**
(42.5 vs 42.4 min, difference +0.02%).
Recipe duration remains **constant regardless of period**, with no observable weekend effect.""",
            "fr": """💡 **Interprétation statistique**
Le **test t de Student** ne révèle **aucune différence significative**
entre les durées Weekday et Weekend. Les **moyennes sont quasi identiques**
(42.5 vs 42.4 min, différence +0.02%).
La durée des recettes publiées reste **constante indépendamment de la période**, sans effet week-end observable.""",
        },
        # Complexité
        "complexity_title": {
            "en": "Complexity (score, steps, ingredients)",
            "fr": "Complexité (score, étapes, ingrédients)",
        },
        "complexity_interpretation": {
            "en": """💡 **Statistical interpretation**
The **Student's t-test** reveals **no significant difference**
in complexity between Weekday and Weekend. **Complexity scores are nearly identical**,
as well as **number of steps** and **ingredients**.
Recipe complexity remains **constant regardless of period**, with no observable weekend effect.""",
            "fr": """💡 **Interprétation statistique**
Le **test t de Student** ne révèle **aucune différence significative**
de complexité entre Weekday et Weekend. Les **scores de complexité sont quasi identiques**,
ainsi que le **nombre d'étapes** et d'**ingrédients**.
La complexité des recettes publiées reste **constante indépendamment de la période**, sans effet week-end observable.""",
        },
        # Nutrition
        "nutrition_title": {"en": "Nutritional profile", "fr": "Profil nutritionnel"},
        "nutrition_interpretation": {
            "en": """💡 **Statistical interpretation**
**Student's t-tests** reveal **globally similar nutritional profiles**
between Weekday and Weekend.
Only one significant difference emerges: **proteins** (p < 0.01), with slightly more protein-rich recipes published during the week (about -3% on weekends).""",
            "fr": """💡 **Interprétation statistique**
Les **tests t de Student** révèlent des **profils nutritionnels globalement similaires**
entre Weekday et Weekend.
Une seule différence significative émerge: les **protéines** (p < 0.01), avec des recettes publiées légèrement plus protéinées en semaine (environ -3% le week-end).""",
        },
        # Ingrédients
        "ingredients_title": {
            "en": "Most variable ingredients",
            "fr": "Ingrédients les plus variables",
        },
        "ingredients_interpretation": {
            "en": """💡 **Statistical interpretation**
Out of all ingredients analyzed, a **strict filtering** was applied
to keep only ingredients with frequency ≥ 1%, absolute difference ≥ 0.2pp, and statistical significance (p < 0.05).

**Chi-squared tests** identify few ingredients with significant variations depending on posting time
(weekday vs weekend). **Weekend**: slight increase for `ground cinnamon`, `canola oil`.
**Weekday**: slight increase for `mozzarella cheese`, `boneless skinless chicken breasts`, `honey`.

**Gaps remain small (<0.4pp) and interpretation is debatable.**""",
            "fr": """💡 **Interprétation statistique**
Sur tous les ingrédients analysés, un **filtrage strict** a été appliqué
pour ne conserver que les ingrédients avec fréquence ≥ 1%, différence absolue ≥ 0.2pp, et significativité statistique (p < 0.05).

Les tests **Chi-2** identifient peu d'ingrédients avec variations significatives selon le moment posté
(weekday vs weekend). **Week-end**: légère hausse pour `ground cinnamon`, `canola oil`.
**Semaine**: légère hausse pour `mozzarella cheese`, `boneless skinless chicken breasts`, `honey`.

**Les écarts restent faibles (<0.4pp) et l'interprétation est sujette à débat.**""",
        },
        # Tags
        "tags_title": {"en": "Most variable tags", "fr": "Tags les plus variables"},
        "tags_interpretation": {
            "en": """💡 **Statistical interpretation**
Out of all tags analyzed, a **strict filtering** was applied
to keep only tags with frequency ≥ 1%, absolute difference ≥ 0.2pp, and statistical significance (p < 0.05).

**Chi-squared tests** reveal significant differences on few tags.
**Weekend (+)**: `vegetarian`, `christmas`, `from-scratch`, `breakfast`, `eggs`.
**Weekday (−)**: `one-dish-meal`, `beginner-cook`, `mexican`.

**Gaps remain small (<0.5pp) and interpretation is debatable.**""",
            "fr": """💡 **Interprétation statistique**
Sur tous les tags analysés, un **filtrage strict** a été appliqué
pour ne conserver que les tags avec fréquence ≥ 1%, différence absolue ≥ 0.2pp, et significativité statistique (p < 0.05).

Les **tests Chi-2** révèlent des différences significatives sur peu de tags.
**Week-end (+)**: `vegetarian`, `christmas`, `from-scratch`, `breakfast`, `eggs`.
**Semaine (−)**: `one-dish-meal`, `beginner-cook`, `mexican`.

**Les écarts restent faibles (<0.5pp) et l'interprétation est sujette à débat.**""",
        },
        # Stats labels for regression details
        "stat_slope": {
            "en": "**Slope:** {value} min/year",
            "fr": "**Pente:** {value} min/an",
        },
        "stat_r2_weighted": {
            "en": "**Weighted R²:** {value}",
            "fr": "**R² pondéré:** {value}",
        },
        "stat_intercept": {
            "en": "- Intercept: {value} minutes",
            "fr": "- Ordonnée à l'origine : {value} minutes",
        },
        "stat_p_value_slope": {
            "en": "- p-value (slope): {value}",
            "fr": "- p-value (pente) : {value}",
        },
        # Main duration analysis summaries
        "duration_analysis_downward": {
            "en": "The analysis of average preparation time shows a **global downward trend** since the site's creation. On average, preparation time decreases by approximately **{slope_mean} min/year**, while the median decreases by **{slope_median} min/year**, reflecting a slight **recipe simplification** over time.",
            "fr": "L'analyse de la durée moyenne de préparation montre une **tendance globale à la baisse** depuis la création du site. En moyenne, le temps de préparation diminue d'environ **{slope_mean} min/an**, tandis que la médiane recule de **{slope_median} min/an**, ce qui traduit une légère **simplification des recettes** au fil du temps.",
        },
        "duration_analysis_upward": {
            "en": "The analysis of average preparation time shows an **upward trend**. On average, preparation time increases by approximately **{slope_mean} min/year**, while the median increases by **{slope_median} min/year**, which could indicate a **complexification of recipes** over time.",
            "fr": "L'analyse de la durée moyenne de préparation montre une **tendance à la hausse**. En moyenne, le temps de préparation augmente d'environ **{slope_mean} min/an**, tandis que la médiane progresse de **{slope_median} min/an**, ce qui pourrait indiquer une **complexification des recettes** au fil du temps.",
        },
        # Plotly graph legends
        "legend_regression_mean": {
            "fr": "Régression Moyenne (R²={r2:.4f})",
            "en": "Mean Regression (R²={r2:.4f})",
        },
        "legend_regression_median": {
            "fr": "Régression Médiane (R²={r2:.4f})",
            "en": "Median Regression (R²={r2:.4f})",
        },
        "legend_regression_wls": {
            "fr": "Régression WLS (R²={r2:.4f})",
            "en": "WLS Regression (R²={r2:.4f})",
        },
        "legend_prediction_interval": {
            "fr": "Intervalle de prédiction {level}% (individuel)",
            "en": "Prediction interval {level}% (individual)",
        },
        "legend_confidence_interval": {
            "fr": "Intervalle de confiance {level}% (moyenne)",
            "en": "Confidence interval {level}% (mean)",
        },
        "legend_lower_bound_prediction": {
            "fr": "Borne inf. prédiction",
            "en": "Lower prediction bound",
        },
        "legend_upper_bound_prediction": {
            "fr": "Borne sup. prédiction",
            "en": "Upper prediction bound",
        },
        "legend_raw_std": {
            "fr": "Écart-type brut",
            "en": "Raw std dev",
        },
        "legend_weighted_std": {
            "fr": "Écart-type pondéré ({value:.3f})",
            "en": "Weighted std dev ({value:.3f})",
        },
        "legend_weighted_regression": {
            "fr": "Régression pondérée",
            "en": "Weighted regression",
        },
        "legend_weighted_mean": {
            "fr": "Moyenne ({value:.3f})",
            "en": "Mean ({value:.3f})",
        },
        "legend_trend_per_month": {
            "fr": "Tendance ({value:.4f}/mois)",
            "en": "Trend ({value:.4f}/month)",
        },
        "legend_trend_per_year": {
            "fr": "Tendance ({value:.4f}/an)",
            "en": "Trend ({value:.4f}/year)",
        },
        "legend_weighted_corr": {
            "fr": "Régression pondérée (ρ={value:.3f})",
            "en": "Weighted regression (ρ={value:.3f})",
        },
        "legend_log_frequency": {
            "fr": "Fréquence (log)",
            "en": "Frequency (log)",
        },
        "legend_weighted_volume": {
            "fr": "Volume pondéré",
            "en": "Weighted volume",
        },
        "legend_deviation_pct": {
            "fr": "Écart (%)",
            "en": "Deviation (%)",
        },
        "legend_weekend_diff": {
            "fr": "Différence Weekend vs Weekday (%)",
            "en": "Weekend vs Weekday Difference (%)",
        },
        # Plotly hovertemplates
        "hover_mean_minutes": {
            "fr": "<b>%{x}</b><br>Moyenne: %{y:.1f} min<extra></extra>",
            "en": "<b>%{x}</b><br>Mean: %{y:.1f} min<extra></extra>",
        },
        "hover_median_minutes": {
            "fr": "<b>%{x}</b><br>Médiane: %{y:.1f} min<extra></extra>",
            "en": "<b>%{x}</b><br>Median: %{y:.1f} min<extra></extra>",
        },
        "hover_complexity": {
            "fr": "<b>%{x}</b><br>Complexité: %{y:.2f}<extra></extra>",
            "en": "<b>%{x}</b><br>Complexity: %{y:.2f}<extra></extra>",
        },
        "hover_ingredients": {
            "fr": "<b>%{x}</b><br>Ingrédients: %{y:.1f}<extra></extra>",
            "en": "<b>%{x}</b><br>Ingredients: %{y:.1f}<extra></extra>",
        },
        "hover_season_freq": {
            "fr": "<b>%{y}</b><br>Saison: %{x}<br>Fréquence: %{z:.1f}%<extra></extra>",
            "en": "<b>%{y}</b><br>Season: %{x}<br>Frequency: %{z:.1f}%<extra></extra>",
        },
        "hover_year_regression": {
            "fr": "<b>Année %{x}</b><br>Régression: %{y:.1f} min<extra></extra>",
            "en": "<b>Year %{x}</b><br>Regression: %{y:.1f} min<extra></extra>",
        },
        # Info blocks and stat labels
        "info_blue_zone": {
            "fr": """💡 **Zone bleue ({quantile})** : Représente la dispersion des durées de recettes.

- **Zone large** → Grande variété de durées (recettes courtes ET longues)
- **Zone étroite** → Durées homogènes (recettes similaires)
- **Changement de largeur** → Évolution de la diversité des recettes au fil du temps

📊 Dispersion actuelle : **{dispersion:.1f} minutes** d'écart entre Q{q_low} et Q{q_high}""",
            "en": """💡 **Blue zone ({quantile})**: Represents the dispersion of recipe durations.

- **Wide zone** → High variety of durations (short AND long recipes)
- **Narrow zone** → Homogeneous durations (similar recipes)
- **Width change** → Evolution of recipe diversity over time

📊 Current dispersion: **{dispersion:.1f} minutes** between Q{q_low} and Q{q_high}""",
        },
        "trends_main_interpretation_down": {
            "fr": """L'analyse de la durée moyenne de préparation montre une **tendance globale à la baisse**
depuis la création du site. En moyenne, le temps de préparation diminue d'environ
**{slope_mean:.2f} min/an**, tandis que la médiane recule de
**{slope_median:.2f} min/an**, ce qui traduit une légère
**simplification des recettes** au fil du temps.""",
            "en": """The analysis of average preparation time shows a **global downward trend**
since the site's creation. On average, preparation time decreases by approximately
**{slope_mean:.2f} min/year**, while the median decreases by
**{slope_median:.2f} min/year**, reflecting a slight
**recipe simplification** over time.""",
        },
        "trends_main_interpretation_up": {
            "fr": """L'analyse de la durée moyenne de préparation montre une **tendance à la hausse**.
En moyenne, le temps de préparation augmente d'environ **{slope_mean:.2f} min/an**,
tandis que la médiane progresse de **{slope_median:.2f} min/an**, ce qui pourrait
indiquer une **complexification des recettes** au fil du temps.""",
            "en": """The analysis of average preparation time shows an **upward trend**.
On average, preparation time increases by approximately **{slope_mean:.2f} min/year**,
while the median increases by **{slope_median:.2f} min/year**, which could
indicate a **recipe complexification** over time.""",
        },
        "stats_section_mean": {
            "fr": "### 📈 Moyenne",
            "en": "### 📈 Mean",
        },
        "stats_section_median": {
            "fr": "### 📊 Médiane",
            "en": "### 📊 Median",
        },
        "stats_label_slope": {
            "fr": "**Pente:** {value:.6f} min/an",
            "en": "**Slope:** {value:.6f} min/year",
        },
        "stats_label_intercept": {
            "fr": "**Intercept:** {value:.2f}",
            "en": "**Intercept:** {value:.2f}",
        },
        "stats_label_r2_weighted": {
            "fr": "**R² pondéré:** {value:.4f}",
            "en": "**Weighted R²:** {value:.4f}",
        },
        "stats_label_pvalue": {
            "fr": "**p-value:** {value:.4e}",
            "en": "**p-value:** {value:.4e}",
        },
        "stats_label_r2_normality": {
            "fr": "**R² (test normalité):** {value:.4f}",
            "en": "**R² (normality test):** {value:.4f}",
        },
        "regression_detail_intercept": {
            "fr": "- Ordonnée à l'origine : {value:.2f} minutes",
            "en": "- Intercept: {value:.2f} minutes",
        },
        "regression_detail_slope": {
            "fr": "- Pente : {value:.6f} minutes/an",
            "en": "- Slope: {value:.6f} minutes/year",
        },
        "regression_detail_r2": {
            "fr": "- R² pondéré : {value:.4f}",
            "en": "- Weighted R²: {value:.4f}",
        },
        "regression_detail_pvalue": {
            "fr": "- p-value (pente) : {value:.4e}",
            "en": "- p-value (slope): {value:.4e}",
        },
        "ratings_methodology_desc": {
            "fr": """Comparaison des méthodes **pondérées** vs **non-pondérées** pour analyser
l'évolution des ratings dans le temps. Cette analyse démontre l'importance
de la pondération par le volume d'interactions.""",
            "en": """Comparison of **weighted** vs **unweighted** methods for analyzing
rating evolution over time. This analysis demonstrates the importance
of weighting by interaction volume.""",
        },
        "ratings_info_methodology": {
            "fr": """💡 **Interprétation statistique**

L'analyse méthodologique révèle une **divergence significative** entre les approches pondérées et non-pondérées.
La méthode **pondérée** (tenant compte du volume d'interactions) montre une **tendance stable** voire légèrement
positive, tandis que la méthode **non-pondérée** suggère une baisse artificielle due au biais d'échantillonnage.

**Conclusion** : La pondération par volume corrige le biais des recettes peu populaires et révèle la vraie tendance.""",
            "en": """💡 **Statistical interpretation**

The methodological analysis reveals a **significant divergence** between weighted and unweighted approaches.
The **weighted** method (accounting for interaction volume) shows a **stable trend** or slightly
positive, while the **unweighted** method suggests an artificial decline due to sampling bias.

**Conclusion**: Volume weighting corrects the bias from unpopular recipes and reveals the true trend.""",
        },
        "ratings_info_temporal": {
            "fr": """💡 **Interprétation statistique**

L'analyse temporelle pondérée révèle une **tendance stable** des ratings au fil du temps, avec une légère
amélioration de **+{trend_year:.4f} points/an**. La variance stable ({std_weighted:.3f}) confirme une
**qualité constante** des recettes publiées depuis 1999.

**Conclusion** : Les ratings Food.com restent remarquablement stables, signe d'une qualité maintenue.""",
            "en": """💡 **Statistical interpretation**

The weighted temporal analysis reveals a **stable trend** in ratings over time, with a slight
improvement of **+{trend_year:.4f} points/year**. The stable variance ({std_weighted:.3f}) confirms
**consistent quality** of recipes published since 1999.

**Conclusion**: Food.com ratings remain remarkably stable, indicating maintained quality.""",
        },
        "ratings_detailed_desc": {
            "fr": """Analyse détaillée de l'évolution des ratings avec **bandes de confiance** à 95%
et **régression pondérée** par volume d'interactions.""",
            "en": """Detailed analysis of rating evolution with 95% **confidence bands**
and **volume-weighted regression**.""",
        },
        "ratings_info_detailed": {
            "fr": """💡 **Interprétation statistique**

L'analyse détaillée confirme la **tendance stable** avec une légère hausse de **+{trend_year:.4f}/an**.
La corrélation volume-qualité pondérée (ρ={corr:.3f}) indique {interpretation}.

**Conclusion** : {conclusion}""",
            "en": """💡 **Statistical interpretation**

The detailed analysis confirms the **stable trend** with a slight increase of **+{trend_year:.4f}/year**.
The weighted volume-quality correlation (ρ={corr:.3f}) indicates {interpretation}.

**Conclusion**: {conclusion}""",
        },
        # Metric labels
        "complexity_weekday": {
            "en": "Weekday (Mon-Fri)",
            "fr": "Weekday (Lun-Ven)",
        },
        "complexity_weekend": {
            "en": "Weekend (Sat-Sun)",
            "fr": "Weekend (Sam-Dim)",
        },
        "max_gap": {
            "en": "Max gap ({nutrient})",
            "fr": "Écart max ({nutrient})",
        },
    },
    # ===== RATINGS (analyse_ratings.py) =====
    "ratings": {
        "main_title": {
            "en": "Rating and Evaluation Analyses",
            "fr": "Analyses des Notes et Évaluations",
        },
        "main_description": {
            "en": """This section presents **rating analyses** of Food.com recipes.

The analyses explore rating distributions, temporal trends, and relationships
between ratings and recipe characteristics.""",
            "fr": """Cette section présente les **analyses des notes** des recettes Food.com.

Les analyses explorent les distributions de notes, les tendances temporelles, et les relations
entre les notes et les caractéristiques des recettes.""",
        },
        # Titres de sections
        "validation_methodologique": {
            "en": "Methodological Validation",
            "fr": "Validation méthodologique",
        },
        "tendance_temporelle": {"en": "Temporal Trend", "fr": "Tendance temporelle"},
        "distribution_stabilite": {
            "en": "Distribution and Stability",
            "fr": "Distribution et stabilité",
        },
        "statistiques_saisonnieres": {
            "en": "Seasonal Statistics",
            "fr": "Statistiques saisonnières",
        },
        "variations_saisonnieres": {
            "en": "Seasonal Variations",
            "fr": "Variations saisonnières",
        },
        # Descriptions
        "ratings_methodology_desc": {
            "en": "Comparison of **weighted** vs **unweighted** methods for analyzing rating evolution over time. This analysis demonstrates the importance of weighting by interaction volume.",
            "fr": "Comparaison des méthodes **pondérées** vs **non-pondérées** pour analyser l'évolution des ratings dans le temps. Cette analyse démontre l'importance de la pondération par le volume d'interactions.",
        },
        "comparaison_methodes": {
            "en": "Comparison of weighted vs non-weighted methods to analyze rating evolution over time. This analysis demonstrates the importance of weighting by interaction volume.",
            "fr": "Comparaison des méthodes pondérées vs non-pondérées pour analyser l'évolution des ratings dans le temps. Cette analyse démontre l'importance de la pondération par le volume d'interactions.",
        },
        "analyse_evolution_wls": {
            "en": "Analysis of rating evolution over time with weighted WLS regression. Examines stability, interaction volume, and volume-quality correlation.",
            "fr": "Analyse de l'évolution des ratings dans le temps avec régression WLS pondérée. Examine la stabilité, le volume d'interactions et la corrélation volume-qualité.",
        },
        "analyse_distribution": {
            "en": "Analysis of interaction and rating distribution by season. Examines data balance and seasonal analysis validity.",
            "fr": "Analyse de la distribution des interactions et ratings par saison. Examine l'équilibre des données et la validité de l'analyse saisonnière.",
        },
        "analyse_variations_dashboard": {
            "en": "Detailed analysis of seasonal rating variations with complete dashboard. Examines averages, perfect/negative rating percentages, and stability by season.",
            "fr": "Analyse détaillée des variations saisonnières des ratings avec dashboard complet. Examine moyennes, pourcentages de ratings parfaits/négatifs, et stabilité par saison.",
        },
        "ratings_distribution_desc": {
            "en": "Analysis of interaction and rating distribution by season. Examines data balance and seasonal analysis validity.",
            "fr": "Analyse de la distribution des interactions et ratings par saison. Examine l'équilibre des données et la validité de l'analyse saisonnière.",
        },
        "ratings_seasonal_dashboard_desc": {
            "en": "Detailed analysis of seasonal rating variations with complete dashboard. Examines averages, perfect/negative rating percentages, and stability by season.",
            "fr": "Analyse détaillée des variations saisonnières des ratings avec dashboard complet. Examine moyennes, pourcentages de ratings parfaits/négatifs, et stabilité par saison.",
        },
        # Chart titles
        "distribution_volumes_mensuels": {
            "en": "Monthly volume distribution",
            "fr": "Distribution des volumes mensuels",
        },
        "evolution_poids_temps": {
            "en": "Weight evolution over time",
            "fr": "Évolution des poids dans le temps",
        },
        "ratings_ponderes_volume": {
            "en": "Ratings weighted by volume",
            "fr": "Ratings pondérés par volume",
        },
        "variance_ratings": {"en": "Rating variance", "fr": "Variance des ratings"},
        "evolution_ratings_tendance": {
            "en": "Rating evolution - Weighted trend",
            "fr": "Évolution des ratings - Tendance pondérée",
        },
        "volume_interactions": {
            "en": "Interaction volume",
            "fr": "Volume d'interactions",
        },
        "stabilite_ratings": {"en": "Rating stability", "fr": "Stabilité des ratings"},
        "correlation_volume_qualite": {
            "en": "Volume-quality correlation",
            "fr": "Corrélation volume-qualité",
        },
        "distribution_interactions_saison": {
            "en": "Interaction distribution by season",
            "fr": "Distribution des interactions par saison",
        },
        "statistiques_rating_saison": {
            "en": "Rating statistics by season",
            "fr": "Statistiques de rating par saison",
        },
        "variations_saisonnieres_radar": {
            "en": "Seasonal variations (Radar)",
            "fr": "Variations saisonnières (Radar)",
        },
        "rating_moyen_saison": {
            "en": "Average rating by season",
            "fr": "Rating moyen par saison",
        },
        "ratings_parfaits_5_stars": {
            "en": "% Perfect ratings (5★)",
            "fr": "% Ratings parfaits (5★)",
        },
        "ratings_negatifs_1_2_stars": {
            "en": "% Negative ratings (1-2★)",
            "fr": "% Ratings négatifs (1-2★)",
        },
        "ecart_type_ratings": {"en": "Rating std dev", "fr": "Écart-type des ratings"},
        # Metrics
        "moyenne_ponderee": {"en": "WEIGHTED AVERAGE", "fr": "MOYENNE PONDÉRÉE"},
        "ic_95": {"en": "95% CI", "fr": "IC 95%"},
        "corr_volume_qualite": {
            "en": "CORR. VOLUME-QUALITY",
            "fr": "CORR. VOLUME-QUALITÉ",
        },
        "slope_weighted": {"en": "Slope (weighted)", "fr": "Pente (pondérée)"},
        "r2_weighted_metric": {"en": "R² (weighted)", "fr": "R² (pondéré)"},
        "cv_volumes": {"en": "CV VOLUMES", "fr": "CV VOLUMES"},
        "biais_pente": {"en": "SLOPE BIAS", "fr": "BIAIS PENTE"},
        "r2_pondere": {"en": "WEIGHTED R²", "fr": "R² PONDÉRÉ"},
        "p_value_wls": {"en": "P-VALUE WLS", "fr": "P-VALUE WLS"},
        "pente_ponderee": {"en": "WEIGHTED SLOPE", "fr": "PENTE PONDÉRÉE"},
        "ratio_max_min": {"en": "MAX/MIN RATIO", "fr": "RATIO MAX/MIN"},
        "volume_total": {"en": "TOTAL VOLUME", "fr": "VOLUME TOTAL"},
        "saisons": {"en": "SEASONS", "fr": "SAISONS"},
        "anova_f_stat": {"en": "ANOVA F-STAT", "fr": "ANOVA F-STAT"},
        "p_value": {"en": "P-VALUE", "fr": "P-VALUE"},
        "meilleure_saison": {"en": "BEST SEASON", "fr": "MEILLEURE SAISON"},
        "ecart_max": {"en": "MAX RANGE", "fr": "ÉCART MAX"},
        # Axis labels
        "nombre_interactions_mensuelles": {
            "en": "Number of monthly interactions",
            "fr": "Nombre d'interactions mensuelles",
        },
        "poids_normalises": {"en": "Normalized weights", "fr": "Poids normalisés"},
        "rating_moyen": {"en": "Average rating", "fr": "Rating moyen"},
        "ecart_type": {"en": "Std dev", "fr": "Écart-type"},
        "nombre_milliers": {"en": "Number (thousands)", "fr": "Nombre (milliers)"},
        "nombre_interactions": {
            "en": "Number of interactions",
            "fr": "Nombre d'interactions",
        },
        # Expander labels
        "voir_statistiques_detaillees": {
            "en": "View detailed statistics",
            "fr": "Voir les statistiques détaillées",
        },
        # Graph titles
        "temporal_evolution_overview": {
            "fr": "Évolution temporelle - Vue d'ensemble",
            "en": "Temporal evolution - Overview",
        },
        "temporal_evolution_zoomed": {
            "fr": "Évolution temporelle - Vue zoomée",
            "en": "Temporal evolution - Zoomed view",
        },
        "correlation_volume_quality": {
            "fr": "Corrélation volume-qualité",
            "en": "Volume-quality correlation",
        },
        "detailed_analysis_confidence": {
            "fr": "Analyse détaillée avec bandes de confiance",
            "en": "Detailed analysis with confidence bands",
        },
        # Interpretation blocks
        "ratings_info_detailed_full": {
            "fr": """💡 **Interprétation statistique**

L'analyse détaillée confirme la **très forte stabilité** des ratings, avec une **moyenne pondérée** se situant à
**{mean_rating_weighted:.3f}**. Les **bandes de confiance à 95%** calculées sur la moyenne pondérée sont **extrêmement resserrées**
(IC 95% = **±{ci_95:.4f}**), ce qui démontre une **variance globale très faible** et une
**grande prévisibilité** du comportement de notation. Visuellement, bien que les notes mensuelles individuelles fluctuent légèrement,
elles restent **constamment groupées** autour de cette moyenne stable, renforçant la conclusion d'une **absence totale de tendance significative**
à long terme.""",
            "en": """💡 **Statistical Interpretation**

The detailed analysis confirms the **very strong stability** of ratings, with a **weighted average** of
**{mean_rating_weighted:.3f}**. The **95% confidence bands** calculated on the weighted average are **extremely tight**
(95% CI = **±{ci_95:.4f}**), demonstrating a **very low global variance** and
**high predictability** of rating behavior. Visually, although individual monthly ratings fluctuate slightly,
they remain **consistently clustered** around this stable average, reinforcing the conclusion of a **complete absence of significant trend**
in the long term.""",
        },
        "ratings_seasonal_interpretation": {
            "fr": """💡 **Interprétation statistique**

Les tests statistiques (ANOVA F={f_stat:.3f} et Kruskal-Wallis H={h_stat:.3f}) révèlent des
**différences statistiquement significatives** entre les saisons (p < 0.0001), **confirmant l'existence d'une variation saisonnière**.""",
            "en": """💡 **Statistical Interpretation**

Statistical tests (ANOVA F={f_stat:.3f} and Kruskal-Wallis H={h_stat:.3f}) reveal
**statistically significant differences** between seasons (p < 0.0001), **confirming the existence of seasonal variation**.""",
        },
        "ratings_info_methodology": {
            "fr": """💡 **Interprétation statistique**

L'analyse méthodologique révèle une **hétérogénéité extrême des volumes d'interactions** mensuels
(Coefficient de variation = **{cv_volumes:.2f}**), ce qui rend les tests statistiques standards **non fiables**.
Les tests non-pondérés s'avèrent **fortement biaisés** (biais de pente de **+{bias_slope:.1f}%**), car ils donnent une importance
disproportionnée aux périodes de **très forte activité** (comme 2008-2009), écrasant l'influence des autres périodes.
L'utilisation de **méthodes pondérées** (comme la régression WLS et le Spearman pondéré) est donc **indispensable** pour corriger
ce biais et obtenir une **interprétation juste et robuste** des tendances réelles du comportement utilisateur.""",
            "en": """💡 **Statistical Interpretation**

The methodological analysis reveals **extreme heterogeneity in monthly interaction volumes**
(Coefficient of variation = **{cv_volumes:.2f}**), making standard statistical tests **unreliable**.
Unweighted tests prove **strongly biased** (slope bias of **+{bias_slope:.1f}%**), as they give disproportionate
importance to periods of **very high activity** (such as 2008-2009), overwhelming the influence of other periods.
The use of **weighted methods** (such as WLS regression and weighted Spearman) is therefore **essential** to correct
this bias and obtain a **fair and robust interpretation** of actual user behavior trends.""",
        },
        "ratings_info_temporal": {
            "fr": """💡 **Interprétation statistique**

L'analyse temporelle pondérée révèle une **stabilité remarquable des notes moyennes** sur le long terme,
contredisant l'intuition d'une éventuelle dégradation ou amélioration.
La tendance observée est **statistiquement non significative** (pente annuelle = **{slope_year:.4f} points/an**,
p-value = **{p_value:.2f}**). Le R² pondéré de **{r2_weighted:.3f}** confirme que le temps n'explique quasiment
**aucune variance** dans les notes. On observe également une **faible corrélation négative** entre le **volume** d'interactions et
la **qualité** perçue (ρ = **{vol_qual_weighted:.3f}**), suggérant que les mois de **plus forte activité** sont associés à des
**notes moyennes très légèrement plus basses**. Cette stabilité globale confirme que le **comportement de notation des utilisateurs**
est **extrêmement constant** depuis 2005.""",
            "en": """💡 **Statistical Interpretation**

The weighted temporal analysis reveals **remarkable stability in average ratings** over the long term,
contradicting the intuition of potential degradation or improvement.
The observed trend is **statistically non-significant** (annual slope = **{slope_year:.4f} points/year**,
p-value = **{p_value:.2f}**). The weighted R² of **{r2_weighted:.3f}** confirms that time explains virtually
**no variance** in ratings. We also observe a **weak negative correlation** between interaction **volume** and
perceived **quality** (ρ = **{vol_qual_weighted:.3f}**), suggesting that months of **higher activity** are associated with
**slightly lower average ratings**. This overall stability confirms that **user rating behavior**
has been **extremely constant** since 2005.""",
        },
        "ratings_seasonal_stats_desc": {
            "fr": """💡 **Interprétation statistique**

Les statistiques descriptives confirment la **validité de l'analyse saisonnière**.
Le volume d'interactions est **remarquablement bien équilibré** entre les quatre saisons, chacune représentant environ **25%** du total.
Le **Coefficient de Variation ({cv_volumes:.3f})** et le **ratio max/min ({ratio_max_min:.2f}:1)** des volumes sont **extrêmement faibles**,
indiquant qu'aucune saison ne pèse indûment sur l'analyse. Les comparaisons entre saisons seront donc **fiables et robustes**.""",
            "en": """💡 **Statistical Interpretation**

The descriptive statistics confirm the **validity of the seasonal analysis**.
Interaction volume is **remarkably well balanced** across the four seasons, each representing approximately **25%** of the total.
The **Coefficient of Variation ({cv_volumes:.3f})** and **max/min ratio ({ratio_max_min:.2f}:1)** of volumes are **extremely low**,
indicating that no season unduly weighs on the analysis. Comparisons between seasons will therefore be **reliable and robust**.""",
        },
    },
    # ===== SEASONS (valeurs des saisons - données) =====
    "seasons": {
        "winter": {"en": "Winter", "fr": "Hiver"},
        "spring": {"en": "Spring", "fr": "Printemps"},
        "summer": {"en": "Summer", "fr": "Été"},
        "autumn": {"en": "Autumn", "fr": "Automne"},
    },
    # ===== DAYS (valeurs des jours de la semaine - données) =====
    "days": {
        "monday": {"en": "Monday", "fr": "Lundi"},
        "tuesday": {"en": "Tuesday", "fr": "Mardi"},
        "wednesday": {"en": "Wednesday", "fr": "Mercredi"},
        "thursday": {"en": "Thursday", "fr": "Jeudi"},
        "friday": {"en": "Friday", "fr": "Vendredi"},
        "saturday": {"en": "Saturday", "fr": "Samedi"},
        "sunday": {"en": "Sunday", "fr": "Dimanche"},
        # Abréviations (pour les graphiques)
        "mon": {"en": "Mon", "fr": "Lun"},
        "tue": {"en": "Tue", "fr": "Mar"},
        "wed": {"en": "Wed", "fr": "Mer"},
        "thu": {"en": "Thu", "fr": "Jeu"},
        "fri": {"en": "Fri", "fr": "Ven"},
        "sat": {"en": "Sat", "fr": "Sam"},
        "sun": {"en": "Sun", "fr": "Dim"},
    },
}
