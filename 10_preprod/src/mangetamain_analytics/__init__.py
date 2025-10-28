# -*- coding: utf-8 -*-
"""
Mangetamain Analytics - Application d'analyse de donnees Food.com.

Ce package fournit des outils d'analyse et de visualisation pour le dataset Food.com,
incluant l'analyse de tendances, de saisonnalite, et de ratings.
"""

from .exceptions import (
    MangetamainError,
    DataLoadError,
    AnalysisError,
    ConfigurationError,
    DatabaseError,
    ValidationError,
)

__version__ = "1.0.0"

__all__ = [
    "MangetamainError",
    "DataLoadError",
    "AnalysisError",
    "ConfigurationError",
    "DatabaseError",
    "ValidationError",
]
