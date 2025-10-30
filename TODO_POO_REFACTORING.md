# TODO: Refactoring POO - Mangetamain Analytics

**Date**: 2025-10-28
**Objectif**: Renforcer l'usage de la Programmation Orientée Objet dans le projet pour conformité académique

## État Actuel

### Classes Existantes (3)
- `DatabaseManager` - Gestion DuckDB avec cache Streamlit (`models_database.py`)
- `QueryTemplates` - Templates SQL (`models_database.py`)
- `LoggerConfig` - Configuration Loguru (`utils_logger.py`)

### Code Procédural (~7730 lignes)
- `analyse_trendlines_v2.py` - 9 fonctions d'analyse
- `analyse_seasonality.py` - Patterns saisonniers
- `analyse_weekend.py` - Analyse hebdomadaire
- `analyse_ratings.py` - Distribution ratings
- **Duplication estimée**: ~80% de code structurel identique entre modules

### Opportunités Identifiées
- `colors.py` : 210 lignes de constantes, pas de classe
- Pas d'exceptions personnalisées
- Pas de hiérarchie de classes pour analyses
- Calculs statistiques dupliqués
- Construction graphiques répétitive

---

## Plan de Refactoring POO

### Phase 1: Fondations (2-3h)

#### 1.1 Classe ColorTheme
**Fichier**: `src/mangetamain_analytics/utils/color_theme.py`

**Objectif**: Encapsuler les 210 lignes de constantes de `colors.py`

**Design**:
```python
class ColorTheme:
    """Thème de couleurs 'Back to the Kitchen' avec accesseurs typés."""

    # Couleurs principales
    ORANGE_PRIMARY: str = "#FF8C00"
    ORANGE_SECONDARY: str = "#E24E1B"
    BACKGROUND_MAIN: str = "#1E1E1E"
    # ... autres constantes

    # Palettes
    SEASONAL_COLORS: dict[str, str] = {
        "Automne": "#FF8C00",
        "Hiver": "#4682B4",
        # ...
    }

    @classmethod
    def get_seasonal_color(cls, season: str) -> str:
        """Retourne la couleur pour une saison donnée."""
        return cls.SEASONAL_COLORS.get(season, cls.ORANGE_PRIMARY)

    @classmethod
    def to_rgba(cls, hex_color: str, alpha: float = 1.0) -> str:
        """Convertit HEX en RGBA avec validation."""
        # Déplacer logique depuis get_rgba()
        pass

    @classmethod
    def get_plotly_theme(cls) -> dict:
        """Retourne le thème Plotly complet."""
        return {
            "layout": {
                "paper_bgcolor": "rgba(0,0,0,0)",
                "plot_bgcolor": "rgba(0,0,0,0)",
                "font": {"color": cls.TEXT_PRIMARY},
                # ...
            }
        }
```

**Bénéfices**:
- Centralisation des couleurs
- Élimination des duplications (ORANGE_PRIMARY vs PRIMARY)
- Méthodes d'accès avec validation
- Type hints complets

**Migration**:
```python
# Avant
from utils.colors import ORANGE_PRIMARY, SEASONAL_COLORS
bar_color = ORANGE_PRIMARY

# Après
from utils.color_theme import ColorTheme
bar_color = ColorTheme.ORANGE_PRIMARY
```

---

#### 1.2 Dataclass AnalysisConfig
**Fichier**: `src/mangetamain_analytics/utils/analysis_config.py`

**Objectif**: Value object pour configuration réutilisable

**Design**:
```python
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class AnalysisConfig:
    """Configuration immuable pour analyses."""

    year_range: tuple[int, int]
    show_values: bool = True
    show_stats: bool = True
    bar_color: str = ColorTheme.ORANGE_PRIMARY
    fig_height: int = 600
    cache_ttl: int = 3600

    def validate(self) -> None:
        """Valide la configuration."""
        if self.year_range[0] > self.year_range[1]:
            raise ValueError("year_range invalide")
        if self.fig_height < 200:
            raise ValueError("fig_height trop petit")
```

**Bénéfices**:
- Immuabilité (frozen=True)
- Validation centralisée
- Réutilisable entre modules
- Documentation via types

---

#### 1.3 Hiérarchie Exceptions
**Fichier**: `src/mangetamain_analytics/exceptions.py`

**Objectif**: Exceptions métier avec messages clairs

**Design**:
```python
class MangetamainError(Exception):
    """Exception de base du projet."""
    pass

class DataLoadError(MangetamainError):
    """Erreur chargement données S3/DuckDB."""
    def __init__(self, source: str, detail: str):
        super().__init__(f"Échec chargement {source}: {detail}")
        self.source = source
        self.detail = detail

class AnalysisError(MangetamainError):
    """Erreur calcul/analyse statistique."""
    pass

class ConfigurationError(MangetamainError):
    """Configuration invalide."""
    pass

class DatabaseError(MangetamainError):
    """Erreur DuckDB."""
    pass
```

**Usage**:
```python
# Au lieu de
try:
    data = load_from_s3(bucket, key)
except Exception as e:
    st.error(f"Erreur: {e}")

# Faire
try:
    data = load_from_s3(bucket, key)
except DataLoadError as e:
    st.error(f"📥 {e}")
    logger.error(f"S3 load failed", source=e.source, detail=e.detail)
```

---

### Phase 2: Architecture Analyses (4-5h)

#### 2.1 Classe Abstraite BaseAnalysis
**Fichier**: `src/mangetamain_analytics/analysis/base_analysis.py`

**Objectif**: Template Method pattern pour éliminer duplication ~500 lignes

**Design**:
```python
from abc import ABC, abstractmethod
import streamlit as st
import polars as pl

class BaseAnalysis(ABC):
    """Classe abstraite pour toutes les analyses.

    Implémente le Template Method pattern pour standardiser:
    - Chargement données
    - Widgets Streamlit
    - Filtrage
    - Statistiques
    - Visualisation
    """

    def __init__(self, config: AnalysisConfig):
        self.config = config
        self.data: Optional[pl.DataFrame] = None
        self.filtered_data: Optional[pl.DataFrame] = None

    def run(self) -> None:
        """Template method: orchestration complète."""
        try:
            self.load_data()
            self.render_widgets()
            self.apply_filters()
            self.compute_statistics()
            self.render_visualization()
            self.render_interpretation()
        except MangetamainError as e:
            st.error(f"❌ Erreur: {e}")
            logger.exception("Analysis failed")

    @abstractmethod
    def load_data(self) -> None:
        """Charge les données (S3, cache)."""
        pass

    @abstractmethod
    def render_widgets(self) -> None:
        """Affiche les widgets Streamlit (sliders, checkboxes)."""
        pass

    @abstractmethod
    def apply_filters(self) -> None:
        """Applique les filtres utilisateur."""
        pass

    def compute_statistics(self) -> dict:
        """Calcule stats basiques (optionnel, override si besoin)."""
        if self.filtered_data is None:
            return {}
        return {
            "count": len(self.filtered_data),
            "mean": self.filtered_data.select(pl.mean(self.metric_column)),
            # ...
        }

    @abstractmethod
    def render_visualization(self) -> None:
        """Crée et affiche le graphique Plotly."""
        pass

    @abstractmethod
    def render_interpretation(self) -> None:
        """Affiche l'interprétation métier."""
        pass
```

**Exemple Implémentation**:
```python
class TrendlineAnalysis(BaseAnalysis):
    """Analyse tendances volume recettes."""

    def load_data(self) -> None:
        self.data = load_and_prepare_data()

    def render_widgets(self) -> None:
        col1, col2, col3 = st.columns(3)
        with col1:
            self.year_range = st.slider(
                "📅 Plage d'années",
                min_value=1999,
                max_value=2018,
                value=self.config.year_range
            )
        # ...

    def apply_filters(self) -> None:
        self.filtered_data = self.data.filter(
            (pl.col("year") >= self.year_range[0]) &
            (pl.col("year") <= self.year_range[1])
        )

    def render_visualization(self) -> None:
        fig = go.Figure()
        # ... construction graphique
        chart_theme.apply_chart_theme(fig, title="Volume de recettes")
        st.plotly_chart(fig, use_container_width=True)

    def render_interpretation(self) -> None:
        st.info("""
        💡 **Interprétation**: Pic en 2007, déclin ensuite...
        """)
```

**Bénéfices**:
- Élimine ~500 lignes de duplication
- Structure uniforme entre analyses
- Facilite ajout nouvelles analyses
- Tests unitaires simplifiés (mock abstract methods)

---

#### 2.2 Classe StatisticalAnalyzer
**Fichier**: `src/mangetamain_analytics/analysis/statistical_analyzer.py`

**Objectif**: Centraliser calculs statistiques réutilisables

**Design**:
```python
from scipy import stats
import statsmodels.api as sm
import numpy as np

class StatisticalAnalyzer:
    """Analyseur statistique réutilisable."""

    @staticmethod
    def test_normality(data: np.ndarray, alpha: float = 0.05) -> dict:
        """Test Shapiro-Wilk + Anderson-Darling."""
        shapiro_stat, shapiro_p = stats.shapiro(data)
        anderson_result = stats.anderson(data)

        return {
            "shapiro": {"stat": shapiro_stat, "p_value": shapiro_p, "is_normal": shapiro_p > alpha},
            "anderson": {"stat": anderson_result.statistic, "critical_values": anderson_result.critical_values},
            "conclusion": "Normal" if shapiro_p > alpha else "Non normal"
        }

    @staticmethod
    def compute_qq_plot_data(data: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Prépare données Q-Q plot."""
        return stats.probplot(data, dist="norm")

    @staticmethod
    def fit_lowess(x: np.ndarray, y: np.ndarray, frac: float = 0.3) -> np.ndarray:
        """Lissage LOWESS."""
        return sm.nonparametric.lowess(y, x, frac=frac)[:, 1]

    @staticmethod
    def compute_summary_stats(data: np.ndarray) -> dict:
        """Stats descriptives complètes."""
        return {
            "mean": np.mean(data),
            "median": np.median(data),
            "std": np.std(data),
            "min": np.min(data),
            "max": np.max(data),
            "q25": np.percentile(data, 25),
            "q75": np.percentile(data, 75),
        }
```

**Bénéfices**:
- Réutilisabilité entre modules
- Tests unitaires faciles
- Documentation centralisée
- Évite code dupliqué

---

### Phase 3: Builder Pattern (2-3h)

#### 3.1 Classe ChartBuilder
**Fichier**: `src/mangetamain_analytics/visualization/chart_builder.py`

**Objectif**: Builder pattern avec fluent API pour graphiques Plotly

**Design**:
```python
class ChartBuilder:
    """Builder pour graphiques Plotly avec fluent API."""

    def __init__(self, chart_type: str = "bar"):
        self.fig = go.Figure()
        self.chart_type = chart_type
        self._title: Optional[str] = None
        self._height: int = 600

    def with_title(self, title: str) -> "ChartBuilder":
        """Définit le titre."""
        self._title = title
        return self

    def with_height(self, height: int) -> "ChartBuilder":
        """Définit la hauteur."""
        self._height = height
        return self

    def add_bar_trace(
        self,
        x: list,
        y: list,
        name: str = "",
        color: Optional[str] = None
    ) -> "ChartBuilder":
        """Ajoute trace barre."""
        self.fig.add_trace(go.Bar(
            x=x,
            y=y,
            name=name,
            marker_color=color or ColorTheme.ORANGE_PRIMARY
        ))
        return self

    def add_scatter_trace(
        self,
        x: list,
        y: list,
        mode: str = "lines",
        name: str = "",
        color: Optional[str] = None
    ) -> "ChartBuilder":
        """Ajoute trace scatter/line."""
        self.fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode=mode,
            name=name,
            line=dict(color=color or ColorTheme.STEELBLUE)
        ))
        return self

    def add_hline(
        self,
        y: float,
        annotation: str = "",
        color: Optional[str] = None
    ) -> "ChartBuilder":
        """Ajoute ligne horizontale."""
        self.fig.add_hline(
            y=y,
            line_dash="dash",
            line_color=color or ColorTheme.SECONDARY_ACCENT,
            annotation_text=annotation
        )
        return self

    def build(self) -> go.Figure:
        """Construit le graphique final avec thème."""
        chart_theme.apply_chart_theme(self.fig, title=self._title)
        self.fig.update_layout(height=self._height)
        return self.fig
```

**Usage**:
```python
# Avant (répétitif)
fig = go.Figure()
fig.add_trace(go.Bar(x=years, y=counts, marker_color=ORANGE_PRIMARY))
fig.add_hline(y=mean_val, line_dash="dash", line_color=SECONDARY_ACCENT, annotation_text="Moyenne")
chart_theme.apply_chart_theme(fig, title="Volume")
fig.update_layout(height=600)
st.plotly_chart(fig, use_container_width=True)

# Après (fluent API)
fig = (ChartBuilder("bar")
    .with_title("Volume de recettes")
    .with_height(600)
    .add_bar_trace(x=years, y=counts)
    .add_hline(y=mean_val, annotation="Moyenne")
    .build())
st.plotly_chart(fig, use_container_width=True)
```

**Bénéfices**:
- Chaînage méthodes (fluent API)
- Moins de répétition
- Validation centralisée
- Meilleure lisibilité

---

## Estimation Temps

| Phase | Tâches | Temps |
|-------|--------|-------|
| Phase 1 | ColorTheme, AnalysisConfig, Exceptions | 2-3h |
| Phase 2 | BaseAnalysis, StatisticalAnalyzer, Migration 1 module | 4-5h |
| Phase 3 | ChartBuilder, Tests, Documentation | 2-3h |
| **Total** | | **8-11h** |

---

## Impact sur Conformité Académique

### Avant
- **POO**: 3 classes (court pour un projet de cette taille)
- **Code procédural**: ~7730 lignes
- **Duplication**: ~80% entre modules

### Après
- **POO**: 9-10 classes avec hiérarchie
  - 3 classes existantes
  - 6 nouvelles classes (ColorTheme, AnalysisConfig, BaseAnalysis, StatisticalAnalyzer, ChartBuilder, + Exceptions)
- **Héritage**: BaseAnalysis → TrendlineAnalysis, SeasonalityAnalysis, etc.
- **Encapsulation**: ColorTheme, AnalysisConfig
- **Polymorphisme**: Abstract methods dans BaseAnalysis
- **Design patterns**: Template Method, Builder, Value Object
- **Réduction duplication**: -500 lignes estimées

---

## Priorités

1. **Phase 1.3 (Exceptions)** - Impact immédiat, faible effort (1h)
2. **Phase 1.1 (ColorTheme)** - Élimine duplications colors.py (1h)
3. **Phase 2.1 (BaseAnalysis)** - Plus grand impact (-500 lignes duplication) (3h)
4. **Phase 1.2 (AnalysisConfig)** - Support pour BaseAnalysis (1h)
5. **Phase 2.2 (StatisticalAnalyzer)** - Réutilisabilité stats (2h)
6. **Phase 3.1 (ChartBuilder)** - Optionnel, amélioration lisibilité (2h)

---

## Tests à Ajouter

```python
# tests/unit/test_color_theme.py
def test_color_theme_seasonal():
    assert ColorTheme.get_seasonal_color("Automne") == "#FF8C00"

def test_color_theme_rgba():
    rgba = ColorTheme.to_rgba("#FF8C00", 0.5)
    assert rgba == "rgba(255, 140, 0, 0.5)"

# tests/unit/test_analysis_config.py
def test_config_validation():
    with pytest.raises(ValueError):
        AnalysisConfig(year_range=(2018, 1999))

# tests/unit/test_base_analysis.py
def test_base_analysis_template():
    class MockAnalysis(BaseAnalysis):
        # Mock abstract methods
        pass

    analysis = MockAnalysis(config)
    analysis.run()
    # Assert workflow executed

# tests/unit/test_statistical_analyzer.py
def test_normality_test():
    data = np.random.normal(0, 1, 1000)
    result = StatisticalAnalyzer.test_normality(data)
    assert result["shapiro"]["is_normal"] == True
```

---

## Notes

- **Pas de sur-ingénierie**: Les classes proposées ont une utilité réelle (éliminer duplication, centraliser logique)
- **Migration incrémentale**: Commencer par 1 module (trendlines), puis généraliser
- **Tests obligatoires**: Chaque nouvelle classe doit avoir tests unitaires
- **Documentation**: Docstrings Google Style sur toutes les classes/méthodes
- **Compatibilité**: Garder backward compatibility pendant migration

---

**Auteur**: Analyse réalisée le 2025-10-28
**Statut**: En cours - Phase 1 complétée

---

## État d'avancement (2025-10-30)

### ✅ Phase 1.1 - ColorTheme (COMPLÉTÉ)
**Date**: 2025-10-30
**Fichier**: `src/mangetamain_analytics/utils/color_theme.py` (262 lignes)

**Implémentation**:
- Classe ColorTheme avec 40+ constantes couleurs typées
- Méthodes: `to_rgba()`, `get_plotly_theme()`, `get_seasonal_colors()`, `get_seasonal_color()`
- Validation entrées (ValueError si hex/alpha invalide)

**Tests**:
- Fichier: `tests/unit/test_color_theme.py` (35 tests)
- Coverage: 97%
- Classes de tests: TestColorThemeConstants, TestColorThemeToRgba, TestColorThemePlotlyTheme, TestColorThemeSeasonalColors

**Migration**:
- 7 fichiers migrés (~129 occurrences)
- utils/chart_theme.py, main.py, analyse_ratings.py, analyse_trendlines_v2.py, analyse_weekend.py, analyse_seasonality.py, tests/unit/test_chart_theme.py
- 3 hotfixes production appliqués

**Documentation**:
- CHANGELOG_DOC.md Version 2.1 créé
- 8 fichiers RST documentation Sphinx mis à jour
- Sphinx build validé

**Commits**: 5 commits (8a6a887...128c66a)

---

### ✅ Phase 1.3 - Hiérarchie Exceptions (COMPLÉTÉ)
**Date**: 2025-10-28
**Fichier**: `src/mangetamain_analytics/exceptions.py` (3649 octets)

**Implémentation**:
- 6 classes d'exceptions avec hiérarchie
- MangetamainError (base)
- DataLoadError, AnalysisError, ConfigurationError, DatabaseError, ValidationError
- Messages d'erreur structurés avec contexte

**Classe DataLoader**:
- Fichier: `src/mangetamain_analytics/data/loaders.py`
- Utilise les exceptions personnalisées
- Méthodes: `load_recipes()`, `load_ratings()`
- Intégré avec cached_loaders.py pour Streamlit

**Tests**: Validés en production (voir tests background bash)

---

### 📋 À FAIRE - Phase 1.2 - AnalysisConfig

**Priorité**: MOYENNE (support pour Phase 2.1)
**Effort estimé**: 1h
**Fichier à créer**: `src/mangetamain_analytics/utils/analysis_config.py`

**Design restant identique au plan initial** (voir lignes 99-133)

---

### 📋 À FAIRE - Phase 2.1 - BaseAnalysis

**Priorité**: HAUTE - PLUS GRAND IMPACT
**Effort estimé**: 3h
**Fichier à créer**: `src/mangetamain_analytics/analysis/base_analysis.py`

**Impact**: Élimine ~500 lignes de duplication

**Design restant identique au plan initial** (voir lignes 185-305)

---

### 📋 À FAIRE - Phase 2.2 - StatisticalAnalyzer

**Priorité**: MOYENNE
**Effort estimé**: 2h
**Fichier à créer**: `src/mangetamain_analytics/analysis/statistical_analyzer.py`

**Design restant identique au plan initial** (voir lignes 307-363)

---

### 📋 À FAIRE - Phase 3.1 - ChartBuilder

**Priorité**: BASSE (optionnel, amélioration lisibilité)
**Effort estimé**: 2h
**Fichier à créer**: `src/mangetamain_analytics/visualization/chart_builder.py`

**Design restant identique au plan initial** (voir lignes 367-475)

---

## Progression

| Phase | Statut | Date | Commits |
|-------|--------|------|---------|
| Phase 1.1 - ColorTheme | ✅ COMPLÉTÉ | 2025-10-30 | 8a6a887...128c66a |
| Phase 1.3 - Exceptions + DataLoader | ✅ COMPLÉTÉ | 2025-10-28 | (à identifier) |
| Phase 1.2 - AnalysisConfig | 📋 À FAIRE | - | - |
| Phase 2.1 - BaseAnalysis | 📋 À FAIRE | - | - |
| Phase 2.2 - StatisticalAnalyzer | 📋 À FAIRE | - | - |
| Phase 3.1 - ChartBuilder | 📋 À FAIRE | - | - |

**Temps écoulé**: ~4h (Phases 1.1 + 1.3)
**Temps restant estimé**: 6-8h

---

## Impact Académique Actuel

### Avant refactoring
- **POO**: 3 classes (DatabaseManager, QueryTemplates, LoggerConfig)
- **Code procédural**: ~7730 lignes

### Après Phases 1.1 + 1.3
- **POO**: 8 classes
  - 3 classes existantes
  - **ColorTheme** (nouvelle)
  - **6 exceptions** (MangetamainError + 5 sous-classes)
  - **DataLoader** (nouvelle)
- **Encapsulation**: ColorTheme centralise 210 lignes constantes
- **Hiérarchie**: Exceptions avec héritage
- **Réduction duplication**: -129 occurrences colors.py

### Après complétion Phase 2+3 (estimé)
- **POO**: 11-12 classes avec hiérarchie complète
- **Héritage**: BaseAnalysis → analyses concrètes
- **Polymorphisme**: Abstract methods
- **Design patterns**: Template Method, Builder, Value Object
- **Réduction duplication estimée**: -500 lignes

---

**Prochaines étapes recommandées**:
1. Phase 1.2 - AnalysisConfig (1h)
2. Phase 2.1 - BaseAnalysis (3h) - Plus grand impact
3. Phase 2.2 - StatisticalAnalyzer (2h)
4. Phase 3.1 - ChartBuilder (optionnel, 2h)
