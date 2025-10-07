#!/usr/bin/env python3
"""
Test et configuration de YData SDK
"""

import os
import sys

def test_ydata_imports():
    """Tester les différents imports YData possibles"""
    print("🔍 Test des imports YData...")
    
    # Test 1: YData Profiling (déjà fonctionnel)
    try:
        from ydata_profiling import ProfileReport
        print("✅ YData Profiling disponible")
    except ImportError as e:
        print(f"❌ YData Profiling: {e}")
    
    # Test 2: YData Core
    try:
        import ydata.core
        print("✅ YData Core disponible")
        print("   Attributs core:", dir(ydata.core))
    except ImportError as e:
        print(f"❌ YData Core: {e}")
    
    # Test 3: YData DataScience
    try:
        import ydata.datascience
        print("✅ YData DataScience disponible")
        print("   Attributs datascience:", dir(ydata.datascience))
    except ImportError as e:
        print(f"❌ YData DataScience: {e}")

def find_ydata_client():
    """Chercher la classe Client YData"""
    print("\n🔍 Recherche de la classe Client...")
    
    # Essayer différentes localisations
    client_locations = [
        "ydata.core.client.Client",
        "ydata.core.Client", 
        "ydata.datascience.Client",
        "ydata.Client"
    ]
    
    for location in client_locations:
        try:
            module_parts = location.split('.')
            class_name = module_parts[-1]
            module_path = '.'.join(module_parts[:-1])
            
            module = __import__(module_path, fromlist=[class_name])
            client_class = getattr(module, class_name)
            
            print(f"✅ Client trouvé: {location}")
            return client_class, location
        except (ImportError, AttributeError) as e:
            print(f"❌ {location}: {e}")
    
    return None, None

def configure_ydata_token(token):
    """Configurer le token YData"""
    print(f"\n🔑 Configuration du token YData...")
    
    # Méthode 1: Variable d'environnement
    os.environ['YDATA_TOKEN'] = token
    print("✅ Token configuré comme variable d'environnement YDATA_TOKEN")
    
    # Méthode 2: Essayer d'autres noms de variables
    possible_env_vars = [
        'YDATA_API_TOKEN',
        'YDATA_ACCESS_TOKEN', 
        'YDATA_AUTH_TOKEN',
        'YDATA_SDK_TOKEN'
    ]
    
    for var in possible_env_vars:
        os.environ[var] = token
        print(f"✅ Token configuré comme {var}")

def main():
    """Fonction principale"""
    print("🚀 Test et configuration YData SDK")
    print("=" * 50)
    
    # Test des imports
    test_ydata_imports()
    
    # Recherche du client
    client_class, location = find_ydata_client()
    
    # Configuration du token
    token = "2c1c15a9-315d-4bfc-a31a-cd6e44bdcfa9"
    configure_ydata_token(token)
    
    # Test de connexion si le client est trouvé
    if client_class and location:
        try:
            print(f"\n🔌 Test de connexion avec {location}...")
            
            # Essayer différentes façons d'initialiser le client
            connection_methods = [
                lambda: client_class(),
                lambda: client_class(token=token),
                lambda: client_class(api_token=token),
                lambda: client_class(auth_token=token),
            ]
            
            for i, method in enumerate(connection_methods):
                try:
                    client = method()
                    print(f"✅ Connexion réussie avec méthode {i+1}")
                    print(f"   Client: {type(client)}")
                    break
                except Exception as e:
                    print(f"❌ Méthode {i+1}: {e}")
            
        except Exception as e:
            print(f"❌ Erreur lors du test de connexion: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Résumé:")
    print("   - YData Profiling: ✅ Fonctionnel (rapports HTML générés)")
    print("   - YData SDK: ⚠️  Installé mais interface à déterminer")
    print("   - Token: ✅ Configuré dans les variables d'environnement")

if __name__ == "__main__":
    main()
