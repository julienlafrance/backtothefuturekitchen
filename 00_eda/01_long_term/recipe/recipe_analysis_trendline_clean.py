import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression, TheilSenRegressor
from _data_utils import *
import warnings

def load_recipes_data():
    warnings.filterwarnings('ignore')
    sns.set_style('whitegrid')
    plt.rcParams['figure.figsize'] = (14, 6)
    plt.rcParams['font.size'] = 10
    df = load_recipes_clean()
    return df

def analyse_trendline_1():
    df = load_recipes_data()
    plt.show()
    # <INTERPRÉTATION>
    # Interprétation de l'analyse : Evolution du volume de recette
    # </INTERPRÉTATION>

def analyse_trendline_2():
    df = load_recipes_data()
    plt.show()
    # <INTERPRÉTATION>
    # Interprétation de l'analyse : Evolution de la durée moyenne
    # </INTERPRÉTATION>

def analyse_trendline_3():
    df = load_recipes_data()
    plt.show()
    # <INTERPRÉTATION>
    # Interprétation de l'analyse : Evolution de la complexité
    # </INTERPRÉTATION>

def analyse_trendline_4():
    df = load_recipes_data()
    plt.show()
    # <INTERPRÉTATION>
    # Interprétation de l'analyse : Evolution nutritionnelles
    # </INTERPRÉTATION>

def analyse_trendline_5():
    df = load_recipes_data()
    plt.show()
    # <INTERPRÉTATION>
    # Interprétation de l'analyse : Evolution des ingrédients
    # </INTERPRÉTATION>

def analyse_trendline_6():
    df = load_recipes_data()
    plt.show()
    # <INTERPRÉTATION>
    # Interprétation de l'analyse : Evolution des tags
    # </INTERPRÉTATION>
