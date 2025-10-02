#!/usr/bin/env python3
"""
Analyse temporelle complète avec graphiques et détection de patterns
"""

import duckdb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuration plots
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def analyze_temporal_patterns(df, date_col, table_name):
    """Analyse temporelle complète d'une table"""
    
    print(f"\n{'='*80}")
    print(f"📊 ANALYSE TEMPORELLE: {table_name}")
    print(f"{'='*80}")
    
    # Convertir en datetime si nécessaire
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col)
    
    # Période
    min_date = df[date_col].min()
    max_date = df[date_col].max()
    duration = (max_date - min_date).days
    
    print(f"\n🕒 Période: {min_date.date()} → {max_date.date()} ({duration} jours)")
    print(f"📈 Volume: {len(df):,} enregistrements")
    
    # Créer figure avec subplots
    fig = plt.figure(figsize=(20, 12))
    
    # 1. Timeline - Volume par jour
    ax1 = plt.subplot(3, 3, 1)
    daily = df.groupby(df[date_col].dt.date).size()
    daily.plot(ax=ax1, color='steelblue', linewidth=1)
    ax1.set_title('Volume quotidien', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Nombre')
    
    # 2. Volume par année
    ax2 = plt.subplot(3, 3, 2)
    yearly = df.groupby(df[date_col].dt.year).size()
    yearly.plot(kind='bar', ax=ax2, color='coral')
    ax2.set_title('Volume par année', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Année')
    ax2.set_ylabel('Nombre')
    print(f"\n📅 Volume par année:")
    for year, count in yearly.items():
        print(f"  {year}: {count:,}")
    
    # 3. Volume par mois de l'année (saisonnalité)
    ax3 = plt.subplot(3, 3, 3)
    monthly = df.groupby(df[date_col].dt.month).size()
    months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
    ax3.bar(range(1, 13), [monthly.get(i, 0) for i in range(1, 13)], color='lightgreen')
    ax3.set_xticks(range(1, 13))
    ax3.set_xticklabels(months, rotation=45)
    ax3.set_title('Saisonnalité mensuelle', fontsize=14, fontweight='bold')
    ax3.set_ylabel('Nombre total')
    
    # 4. Volume par jour de la semaine
    ax4 = plt.subplot(3, 3, 4)
    weekday = df.groupby(df[date_col].dt.dayofweek).size()
    days = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
    ax4.bar(range(7), [weekday.get(i, 0) for i in range(7)], color='skyblue')
    ax4.set_xticks(range(7))
    ax4.set_xticklabels(days)
    ax4.set_title('Patterns hebdomadaires', fontsize=14, fontweight='bold')
    ax4.set_ylabel('Nombre total')
    
    # 5. Heatmap mois × jour
    ax5 = plt.subplot(3, 3, 5)
    heatmap_data = df.groupby([df[date_col].dt.month, df[date_col].dt.day]).size().unstack(fill_value=0)
    sns.heatmap(heatmap_data, cmap='YlOrRd', ax=ax5, cbar_kws={'label': 'Volume'})
    ax5.set_title('Heatmap Mois × Jour', fontsize=14, fontweight='bold')
    ax5.set_xlabel('Jour du mois')
    ax5.set_ylabel('Mois')
    
    # 6. Distribution horaire (si disponible)
    if df[date_col].dt.hour.nunique() > 1:
        ax6 = plt.subplot(3, 3, 6)
        hourly = df.groupby(df[date_col].dt.hour).size()
        ax6.bar(range(24), [hourly.get(i, 0) for i in range(24)], color='mediumpurple')
        ax6.set_title('Distribution horaire', fontsize=14, fontweight='bold')
        ax6.set_xlabel('Heure')
        ax6.set_ylabel('Nombre')
    
    # 7. Tendance (moyenne mobile)
    ax7 = plt.subplot(3, 3, 7)
    weekly = df.groupby(pd.Grouper(key=date_col, freq='W')).size()
    weekly_ma = weekly.rolling(window=4, center=True).mean()
    ax7.plot(weekly.index, weekly.values, alpha=0.3, label='Hebdomadaire', color='lightblue')
    ax7.plot(weekly_ma.index, weekly_ma.values, label='Tendance (MA 4 sem.)', color='darkblue', linewidth=2)
    ax7.set_title('Tendance temporelle', fontsize=14, fontweight='bold')
    ax7.set_xlabel('Date')
    ax7.set_ylabel('Volume hebdomadaire')
    ax7.legend()
    
    # 8. Statistiques par rating (si existe)
    if 'rating' in df.columns:
        ax8 = plt.subplot(3, 3, 8)
        rating_by_year = df.groupby([df[date_col].dt.year, 'rating']).size().unstack(fill_value=0)
        rating_by_year.plot(kind='bar', stacked=True, ax=ax8, colormap='viridis')
        ax8.set_title('Rating par année', fontsize=14, fontweight='bold')
        ax8.set_xlabel('Année')
        ax8.set_ylabel('Volume')
        ax8.legend(title='Rating', bbox_to_anchor=(1.05, 1))
        
        # Stats rating
        print(f"\n⭐ Distribution ratings:")
        rating_dist = df['rating'].value_counts().sort_index()
        for rating, count in rating_dist.items():
            pct = count / len(df) * 100
            print(f"  Rating {rating}: {count:,} ({pct:.1f}%)")
    
    # 9. Croissance cumulative
    ax9 = plt.subplot(3, 3, 9)
    cumulative = df.groupby(df[date_col].dt.to_period('M')).size().cumsum()
    cumulative.plot(ax=ax9, color='darkgreen', linewidth=2)
    ax9.set_title('Croissance cumulative', fontsize=14, fontweight='bold')
    ax9.set_xlabel('Date')
    ax9.set_ylabel('Total cumulé')
    ax9.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Sauvegarder
    output_path = f"ydata_analysis/temporal_detailed_{table_name}.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n💾 Graphique sauvé: {output_path}")
    plt.close()
    
    # Statistiques détaillées
    print(f"\n📊 STATISTIQUES TEMPORELLES:")
    print(f"  • Nombre total d'enregistrements: {len(df):,}")
    print(f"  • Moyenne par jour: {len(df) / duration:.1f}")
    print(f"  • Jour le plus actif: {daily.idxmax()} ({daily.max()} enregistrements)")
    print(f"  • Jour le moins actif: {daily.idxmin()} ({daily.min()} enregistrements)")
    
    return {
        'table': table_name,
        'period': f"{min_date.date()} → {max_date.date()}",
        'duration_days': duration,
        'total_records': len(df),
        'avg_per_day': len(df) / duration,
        'yearly_volumes': yearly.to_dict(),
        'monthly_pattern': monthly.to_dict(),
        'weekday_pattern': weekday.to_dict()
    }

# Connexion DuckDB
conn = duckdb.connect('/home/dataia25/mangetamain/10_prod/data/mangetamain.duckdb')

print("🚀 ANALYSE TEMPORELLE DÉTAILLÉE")
print("=" * 80)

# Tables temporelles
temporal_tables = {
    'RAW_interactions': 'date',
    'RAW_recipes': 'submitted'
}

results = []

for table_name, date_col in temporal_tables.items():
    try:
        # Charger données (échantillon si trop gros)
        count = conn.execute(f'SELECT COUNT(*) FROM {table_name}').fetchone()[0]
        
        if count > 100000:
            df = conn.execute(f'SELECT * FROM {table_name} USING SAMPLE 100000').df()
            print(f"\n📦 {table_name}: Échantillon 100k sur {count:,}")
        else:
            df = conn.execute(f'SELECT * FROM {table_name}').df()
            print(f"\n📦 {table_name}: {count:,} lignes")
        
        # Analyse
        stats = analyze_temporal_patterns(df, date_col, table_name)
        results.append(stats)
        
    except Exception as e:
        print(f"\n❌ Erreur {table_name}: {e}")
        import traceback
        traceback.print_exc()

conn.close()

print("\n" + "="*80)
print("🎉 ANALYSE TEMPORELLE TERMINÉE")
print("="*80)
print("\n📁 Graphiques générés dans ydata_analysis/:")
print("  - temporal_detailed_RAW_interactions.png")
print("  - temporal_detailed_RAW_recipes.png")
print("\n🔍 Chaque graphique contient:")
print("  • Timeline quotidienne")
print("  • Volume par année")
print("  • Saisonnalité mensuelle")
print("  • Patterns hebdomadaires")
print("  • Heatmap temporelle")
print("  • Tendances et moyennes mobiles")
print("  • Croissance cumulative")
