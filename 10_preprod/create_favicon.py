#!/usr/bin/env python3
"""Script pour créer le favicon depuis le logo."""

from PIL import Image
import os

# Chemins
logo_path = "src/mangetamain_analytics/assets/back_to_the_kitchen_logo.png"
favicon_dir = "src/mangetamain_analytics/assets/"
favicon_ico_path = os.path.join(favicon_dir, "favicon.ico")
favicon_png_path = os.path.join(favicon_dir, "favicon.png")

print("🎨 Création du favicon depuis le logo...")

# Ouvrir le logo
try:
    logo = Image.open(logo_path)
    print(f"✅ Logo chargé : {logo.size[0]}x{logo.size[1]} pixels")

    # Créer plusieurs tailles pour le .ico (multi-résolution)
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
    icons = []

    for size in sizes:
        icon = logo.copy()
        icon.thumbnail(size, Image.Resampling.LANCZOS)
        icons.append(icon)
        print(f"  - Taille {size[0]}x{size[1]} créée")

    # Sauvegarder le .ico avec toutes les tailles
    icons[0].save(
        favicon_ico_path,
        format='ICO',
        sizes=sizes,
        append_images=icons[1:]
    )
    print(f"✅ Favicon .ico créé : {favicon_ico_path}")

    # Créer aussi un PNG 32x32 pour usage web
    favicon_png = logo.copy()
    favicon_png.thumbnail((32, 32), Image.Resampling.LANCZOS)
    favicon_png.save(favicon_png_path, format='PNG')
    print(f"✅ Favicon .png créé : {favicon_png_path}")

    # Afficher la taille des fichiers
    ico_size = os.path.getsize(favicon_ico_path) / 1024
    png_size = os.path.getsize(favicon_png_path) / 1024
    print(f"\n📊 Tailles fichiers :")
    print(f"  - favicon.ico : {ico_size:.1f} KB (multi-résolution)")
    print(f"  - favicon.png : {png_size:.1f} KB (32x32)")

    print("\n🎉 Favicons créés avec succès !")
    print("\n📝 Pour l'utiliser dans Streamlit, ajouter dans page config :")
    print('   st.set_page_config(page_icon="src/mangetamain_analytics/assets/favicon.png")')

except FileNotFoundError:
    print(f"❌ Erreur : Logo non trouvé à {logo_path}")
except Exception as e:
    print(f"❌ Erreur lors de la création : {e}")
