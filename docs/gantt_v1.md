# Gantt - V1 OptiStack

## Objectif
Le Gantt ci-dessous décrit la mise en place de la V1 du projet OptiStack, centrée sur un MVP SaaS B2B pour l’analyse et la recommandation d’alternatives logicielles.

## Planning proposé (4 semaines)

```mermaid
gantt
    title OptiStack - V1 (4 semaines)
    dateFormat  YYYY-MM-DD
    axisFormat %d/%m

    section 1. Cadrage
    Analyse du besoin              :a1, 2026-09-17, 3d
    Définition du MVP              :a2, after a1, 3d
    Rédaction du backlog V1        :a3, after a2, 2d

    section 2. UX & Design
    Maquettes écran principal      :b1, after a3, 4d
    Validation UX                  :b2, after b1, 2d

    section 3. Backend
    Définition API                 :c1, after b2, 3d
    Modèle de données              :c2, after c1, 3d
    Import CSV / données           :c3, after c2, 4d
    Calcul coûts & ROI             :c4, after c3, 4d
    Endpoint rapport               :c5, after c4, 3d

    section 4. Frontend
    Dashboard MVP                  :d1, after c2, 5d
    Formulaire d’import            :d2, after d1, 3d
    Affichage résultats            :d3, after d2, 4d
    Export PDF/CSV                 :d4, after d3, 3d

    section 5. Tests & Intégration
    Tests unitaires                :e1, after d4, 3d
    Tests d’intégration            :e2, after e1, 3d
    Correction bugs               :e3, after e2, 3d

    section 6. Livraison
    Préparation démo               :f1, after e3, 2d
    Validation client interne      :f2, after f1, 2d
    Livrable V1                    :f3, after f2, 1d
```

## Délivrables attendus à la fin de la V1
- Dashboard fonctionnel avec coût actuel et recommandations
- Formulaire/import d’inventaire logiciel
- Calcul de ROI sur les alternatives proposées
- Rapport exportable
- Démo fonctionnelle de la solution

## Risques à surveiller
- Sous-estimation du temps de calcul de benchmark
- Qualité des données de parc logiciel insuffisante
- Réticence utilisateur sur le niveau de précision des recommandations

## Hypothèses de travail
- Les données de coûts et d’usage sont saisies ou importées dans un format standardisé
- Le MVP ne cible qu’une PME avec un parc logiciel modéré
- L’intelligence artificielle est utilisée comme aide à la recommandation, pas comme automatisation de migration
