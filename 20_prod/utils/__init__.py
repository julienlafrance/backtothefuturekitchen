"""
Module utilitaire pour les connexions S3 et DuckDB
"""
from .utils_s3 import get_s3_client, get_duckdb_s3_connection, is_on_local_network

__all__ = ['get_s3_client', 'get_duckdb_s3_connection', 'is_on_local_network']
