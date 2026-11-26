# Gantt - V1 OptiStack (Suivi et Mise à Jour)

## Objectif
Ce document suit l'avancement réel de la **V1 (MVP)** du projet OptiStack, compare le planning initial (17 septembre 2026) à la réalisation observée sur le dépôt Git au **26 novembre 2026**, explique les écarts constatés et propose un planning recalé jusqu'à la livraison.

---

## 1. Tableau comparatif : Prévu vs Réalisé

| Phase | Prévu (Gantt initial) | Réalisé constaté (Git) | Écart observé | Statut au 26/11/2026 |
| --- | --- | --- | --- | --- |
| **1. Cadrage & Backlog** | 17/09 → 25/09 (8 j) | 10/09 → 24/09 (README, Gantt, Use Cases UML) | Conforme (réalisé en 2 séances) | Terminé |
| **2. UX & Design (maquettes)** | 25/09 → 01/10 (6 j) | Non formalisé par des maquettes séparées | Phase court-circuitée au profit du prototypage direct | Remplacé par spec + UI directe |
| **3. Outillage Git & Qualité** | Non planifié explicitement | 08/10 → 22/10 (PR #1, `pre-commit`, `automatisation.md`) | +3 semaines consommées sur la mise en place Git/hooks | Terminé (preuve terminal à compléter) |
| **4. Backend (API, DB, ROI, Export)** | 01/10 → 18/10 (17 j) | Démarré le 26/11 (`architecture.md` + `src/backend/`) | Retard de ~5 semaines ; regagné par génération structurée | En cours (socle créé) |
| **5. Frontend (Dashboard, CSV, Export)** | 07/10 → 22/10 (15 j) | Démarré le 26/11 (`src/frontend/` React + Vite) | Retard de ~5 semaines | En cours (socle créé) |
| **6. Tests & Intégration** | 22/10 → 31/10 (9 j) | Suite `pytest` écrite le 26/11 (exécution en cours) | Décalé de ~5 semaines | À finaliser |
| **7. Livraison & Démo V1** | 31/10 → 05/11 (5 j) | Recalé à mi-décembre 2026 | Décalage global d'environ 5 semaines | À venir |

---

## 2. Analyse des écarts

1. **Incohérence interne du Gantt initial (« 4 semaines » vs 7 semaines réelles)** :
   Le titre annonçait 4 semaines (28 jours), mais l'enchaînement en cascade des dépendances `after` étalait en réalité le planning du **17 septembre au 5 novembre 2026** (49 jours calendaires, soit 7 semaines).
2. **Temps absorbé par l'outillage Git et les livrables méthodologiques (08/10 → 22/10)** :
   Les séances d'octobre ont été consacrées à l'apprentissage du workflow Git (branches, Pull Request #1) et à la configuration `pre-commit` (`docs/automatisation.md`), sans démarrage du code applicatif.
3. **Interruption d'activité de 5 semaines (22/10 → 26/11)** :
   Aucun commit n'a été enregistré entre le `22/10/2026` (`3db7af0`) et le `26/11/2026`, ce qui explique l'essentiel du glissement de calendrier.
4. **Dette technique initiale ralentissant la reprise** :
   Lors de la reprise le 26/11, plusieurs blocages de configuration ont dû être corrigés avant de coder : suppression accidentelle de `.pre-commit-config.yaml` lors de la PR #1, guillemets cassés dans `docker-compose.yml`, syntaxe cassée dans `CONTRIBUTING.md`, `README` sans extension `.md`, et gitlink fantôme `Developpement_logiciel`.
5. **Suppression de la phase maquettes UX séparées (`b1`, `b2`)** :
   Pour absorber le retard sans sacrifier le périmètre MVP, l'équipe est passée directement du diagramme de cas d'utilisation ([use_cases.puml](use_cases.puml)) à la spécification d'architecture ([architecture.md](architecture.md)) et à l'implémentation du frontend React.

---

## 3. Gantt actualisé (V1 recalée au 26 novembre 2026)

```mermaid
gantt
    title OptiStack - V1 (Suivi réel & Plan de rattrapage)
    dateFormat  YYYY-MM-DD
    axisFormat %d/%m

    section 1. Cadrage & Modélisation (Réalisé)
    Initialisation README & besoin     :done, r1, 2026-09-10, 8d
    Gantt V1 & fichiers d'env          :done, r2, 2026-09-17, 1d
    Diagramme UML Cas d'utilisation    :done, r3, 2026-09-24, 1d

    section 2. Outillage & Qualité (Réalisé)
    Workflow PR & config pre-commit    :done, r4, 2026-10-08, 15d
    Pause / interruption inter-séances :crit, pause1, 2026-10-23, 34d

    section 3. Reprise & Socle MVP (26/11)
    Assainissement dépôt & configs     :done, s1, 2026-11-26, 1d
    Architecture, API & jeux d'essai   :done, s2, 2026-11-26, 1d
    Backend FastAPI, ROI & Export      :active, s3, 2026-11-26, 3d
    Frontend React + Vite              :active, s4, 2026-11-26, 4d

    section 4. Tests, Intégration & Qualité
    Tests unitaires & API (pytest)     :t1, after s3, 3d
    Build Frontend & lint ESLint       :t2, after s4, 2d
    Preuve pre-commit & CI GitHub      :t3, after s2, 4d
    Intégration PostgreSQL & bugfix    :t4, after t2, 3d

    section 5. Recette & Livraison V1
    Validation critères succès V1      :l1, after t4, 2d
    Préparation démo & Livrable V1     :milestone, l2, after l1, 2d
```

---

## 4. Plan d'actions immédiates pour tenir la livraison

- **Backend (`Sami`)** : valider l'exécution complète de la suite `pytest` (`> 70%` de couverture) et tester la connexion PostgreSQL via `docker-compose.yml`.
- **Frontend (`Soriba`)** : installer les dépendances Node (`npm install` dans `src/frontend/`), vérifier le build Vite et connecter les écrans aux endpoints `/api/*`.
- **UML & Qualité (`Yassine`)** : ajouter le diagramme de classes (aligné sur [architecture.md](architecture.md)) et remplacer la capture d'écran dans [automatisation.md](automatisation.md).
- **Pilotage (`Arsène`)** : suivre les PR sur GitHub (`feature/us-XX-*`), vérifier l'atteinte des 4 critères de succès V1 avec [sample_inventory.csv](../data/sample_inventory.csv) et verrouiller la date de soutenance.

---

## 5. Délivrables, Risques et Hypothèses (mis à jour)

### Délivrables attendus à la fin de la V1
- Dashboard fonctionnel avec coût actuel et recommandations (Top 3+)
- Formulaire / import d'inventaire logiciel CSV (< 5 minutes)
- Calcul de ROI et délai de retour (*payback*) sur les alternatives proposées
- Rapport exportable en CSV et PDF
- Démo fonctionnelle bout-en-bout de la solution

### Risques actualisés à surveiller
- **Contrainte de temps post-interruption** : privilégier la stabilité du MVP existant avant d'ajouter des fonctionnalités hors périmètre (pas d'appel LLM bloquant en V1).
- **Environnements hétérogènes dans l'équipe** : Python/Node/Docker doivent être alignés (`SQLite` en fallback local si Docker n'est pas disponible sur un poste).
- **Qualité des données CSV importées** : validation stricte ligne par ligne côté API déjà intégrée.

### Hypothèses de travail
- Les données de coûts et d'usage sont saisies ou importées dans le format standard défini dans [architecture.md](architecture.md).
- Le MVP cible une PME avec un parc logiciel modéré.
- Le moteur de benchmark V1 s'appuie sur le catalogue déterministe [alternatives_seed.json](../data/alternatives_seed.json) pour garantir des recommandations reproductibles.
