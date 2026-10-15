# Dossier de preuves : Automatisation

## Exercice 1 : Explication de la configuration pre-commit
Analyse de notre fichier `.pre-commit-config.yaml` :

1. **Quand ? (Moment d'exécution)**
   Le contrôle s'exécute localement juste avant la création du commit (sur l'événement `pre-commit`). Si un défaut est détecté, la commande `git commit` est interrompue.
2. **Quoi ? (Hooks sélectionnés et défauts cherchés)**
   - `trailing-whitespace` : Cherche et supprime les espaces ou tabulations inutiles à la fin des lignes.
   - `end-of-file-fixer` : S'assure que chaque fichier se termine par une seule ligne vide.
3. **Où ? (Fichiers concernés)**
   Par défaut (sans règle `files` spécifiée), ces hooks s'exécutent sur tous les fichiers modifiés et indexés (ajoutés avec `git add`) dans le dépôt.

## Exercice 2 : Preuve du refus local
*(Ajoutez ici votre capture d'écran du terminal de VS Code avec le texte en rouge montrant le blocage de trailing-whitespace)*
