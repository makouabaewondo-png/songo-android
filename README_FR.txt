SONGO POUR ANDROID — GUIDE SANS PROGRAMMATION

Le projet comprend une interface tactile Kivy et réutilise le programme Python Songo fourni.

MÉTHODE RECOMMANDÉE : obtenir l'APK via GitHub Actions
Cette méthode demande un compte GitHub gratuit et se fait dans un navigateur, mais la compilation est automatique.

1. Téléchargez et décompressez Songo_Android_Projet.zip sur un ordinateur.
2. Connectez-vous ou créez un compte sur https://github.com/.
3. Créez un nouveau dépôt (repository) nommé Songo-Android. Vous pouvez le laisser privé.
4. Sur la page du dépôt, choisissez « Add file » puis « Upload files » et téléversez le CONTENU du dossier Songo_Android décompressé, y compris le dossier caché .github.
   IMPORTANT : si le dossier .github n'apparaît pas dans votre gestionnaire de fichiers, activez l'affichage des fichiers cachés. Le workflow doit se trouver exactement à .github/workflows/build-apk.yml.
5. Validez avec « Commit changes » sur la branche main.
6. Ouvrez l'onglet « Actions », sélectionnez « Construire APK Android » et attendez la fin du travail (cela peut prendre plusieurs minutes).
7. Lorsque le travail est terminé avec une coche verte, ouvrez son détail. En bas de la page, téléchargez l'artefact « SONGO-Android-APK ».
8. Décompressez cet artefact : il contient le fichier .apk. Transférez-le sur votre téléphone Android et ouvrez-le pour l'installer.
9. Android peut demander d'autoriser l'installation d'applications provenant de cette source. N'autorisez cette source que si vous avez confiance dans le fichier que vous venez de compiler.

DÉPANNAGE
- Vérifiez que le dépôt contient bien main.py, songo_logic.py, buildozer.spec et .github/workflows/build-apk.yml à sa racine (sauf le workflow dans son sous-dossier).
- Si la compilation échoue, ouvrez le travail rouge dans Actions et copiez les dernières lignes du journal pour obtenir de l'aide.
- Le fichier produit est un APK de test (debug), non signé pour publication sur Google Play.

TEST DIRECT SUR ANDROID (alternative)
Il est aussi possible d'essayer le projet dans Pydroid 3 avec prise en charge Kivy, en plaçant main.py et songo_logic.py dans le même dossier. La compatibilité dépend de la version d'Android et de Pydroid.
