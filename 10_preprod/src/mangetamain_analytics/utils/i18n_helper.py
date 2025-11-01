"""i18n helper functions for translations."""

from typing import Any
from mangetamain_analytics.i18n.translations import TRANSLATIONS
from mangetamain_analytics.i18n.language_selector import get_current_language


def t(key: str, category: str = "common", **kwargs: Any) -> str:
    """Translate a key to current language.

    Args:
        key: Translation key
        category: Category in TRANSLATIONS dict (default: "common")
        **kwargs: Format parameters for string interpolation

    Returns:
        Translated string in current language

    Examples:
        >>> t("app_title")
        "Mangetamain Analytics - Retour vers le Futur de la Cuisine"

        >>> t("volume_title", category="trends")
        "Volume d'Interactions"

        >>> t("recipe_count", count=1000)
        "1000 recettes"
    """
    lang = get_current_language()

    try:
        translation = TRANSLATIONS[category][key][lang]
        if kwargs:
            return translation.format(**kwargs)
        return translation
    except KeyError:
        # Fallback: return key if translation missing (helps detect missing translations)
        return f"[{category}.{key}]"


def translate_list(items: list[str], category: str) -> list[str]:
    """Translate a list of items.

    Args:
        items: List of translation keys
        category: Category in TRANSLATIONS dict

    Returns:
        List of translated strings

    Example:
        >>> translate_list(["autumn", "winter", "spring", "summer"], "seasons")
        ["Automne", "Hiver", "Printemps", "Été"]
    """
    lang = get_current_language()
    translated = []
    for item in items:
        try:
            translated.append(TRANSLATIONS[category][item][lang])
        except KeyError:
            translated.append(f"[{category}.{item}]")
    return translated


def get_season_mapping() -> dict[str, str]:
    """Get season translations mapping (French -> English or vice versa).

    Returns mapping from one language to another for data transformation.

    Returns:
        Dictionary mapping season names between languages

    Example:
        >>> # If current language is 'en', returns FR -> EN mapping
        >>> get_season_mapping()
        {"Automne": "Autumn", "Hiver": "Winter", ...}
    """
    lang = get_current_language()

    # Map from stored values (French) to display values
    fr_to_display = {}
    for season_key in ["autumn", "winter", "spring", "summer"]:
        fr_value = TRANSLATIONS["seasons"][season_key]["fr"]
        display_value = TRANSLATIONS["seasons"][season_key][lang]
        fr_to_display[fr_value] = display_value

    return fr_to_display


def get_day_mapping() -> dict[str, str]:
    """Get day of week translations mapping (French -> English or vice versa).

    Returns mapping from one language to another for data transformation.

    Returns:
        Dictionary mapping day names between languages

    Example:
        >>> # If current language is 'en', returns FR -> EN mapping
        >>> get_day_mapping()
        {"Lundi": "Monday", "Mardi": "Tuesday", ...}
    """
    lang = get_current_language()

    # Map from stored values (French) to display values
    fr_to_display = {}
    for day_key in [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]:
        fr_value = TRANSLATIONS["days"][day_key]["fr"]
        display_value = TRANSLATIONS["days"][day_key][lang]
        fr_to_display[fr_value] = display_value

    return fr_to_display
