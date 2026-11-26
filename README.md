# OptiStack : SaaS d'Optimisation des Licences Logicielles

## 🚀 À propos du projet

OptiStack est un mini-SaaS B2B conçu dans le cadre de notre projet fil rouge universitaire. Notre mission est d'aider les entreprises à réduire leurs coûts informatiques en analysant leur pile logicielle (stack) et en recommandant des alternatives viables, open-source ou moins onéreuses (ex : Apache Superset au lieu de Power BI).

Ce projet met en pratique l'utilisation des agents IA, la gestion de projet Agile (Scrum), la modélisation UML et la gestion de versioning avancée avec Git.

## 👥 L'équipe

- **Yassine** : Product Owner & Responsable UML
- **Arsène** : Product Manager & Scrum Master
- **Sami** : Pilote d'Agent IA & Développeur Backend
- **Soriba** : Reviewer & Développeur Frontend / QA

## 🎯 Problème et Proposition de Valeur

- **Problème** : Le *Software Bloat*. Les entreprises paient des licences coûteuses pour des logiciels sous-utilisés alors qu'il existe des alternatives performantes. Elles manquent de temps pour faire ces benchmarks.
- **Utilisateur principal** : DSI, CTO, ou Responsable des achats IT d'une PME.
- **Solution** : Un tableau de bord interactif générant un rapport automatisé de recommandations logicielles et calculant le Retour sur Investissement (ROI) de la transition.
- **Hors périmètre** : La migration automatique des données entre les logiciels n'est pas gérée par notre outil (uniquement du conseil et de l'analyse financière).

## 📁 Structure du dépôt

```text
├── data/                       # Jeux de données et catalogue d'alternatives
│   ├── alternatives_seed.json
│   └── sample_inventory.csv
├── docs/                       # Documentation (Cadrage, UML, Gantt, Architecture)
│   ├── architecture.md
│   ├── automatisation.md
│   ├── class_diagram.puml
│   ├── gantt_v1.md
│   ├── sequence_analysis.puml
│   └── use_cases.puml
├── src/                        # Code source de l'application
│   ├── backend/                # API FastAPI, SQLAlchemy, moteur ROI & tests pytest
│   └── frontend/               # Interface React + Vite
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── CONTRIBUTING.md
├── docker-compose.yml
└── README.md
```

## 🛠️ Stack Technique

- **Gestion de projet** : GitHub Projects, Git
- **Modélisation** : UML (PlantUML)
- **Assistance IA** : Agents LLM intégrés pour la génération de code et le benchmark de logiciels
- **Backend (cible V1)** : Python, FastAPI, SQLAlchemy, PostgreSQL (auth JWT)
- **Frontend (cible V1)** : React, Vite

## 📦 V1 - MVP (Version minimale viable)

La V1 d'OptiStack doit permettre à un client PME de :
- importer ou saisir son parc logiciel,
- visualiser les coûts de licences actuels,
- comparer les solutions avec des alternatives plus abordables,
- obtenir un rapport de recommandations avec un calcul de ROI,
- exporter le résultat sous format simple (CSV/PDF).

### Périmètre fonctionnel V1
- Authentification simple en mode SaaS interne,
- Ajout d'un inventaire logiciel via CSV ou formulaire,
- Analyse des coûts et de l'usage logiciel,
- Benchmark de 3 alternatives recommandées,
- Tableau de bord avec indicateurs clés,
- Génération d'un rapport de recommandations,
- Export des résultats.

### Hors périmètre de la V1
- migration automatique des données,
- intégration SSO / IAM avancé,
- analyse multi-entreprise complète,
- agents IA autonomes de type orchestration avancée,
- modules de facturation ou paie.

### Critères de succès V1
- un utilisateur peut importer un fichier de parc logiciel en moins de 5 minutes,
- le système propose au moins 3 recommandations exploitables,
- le ROI est calculé et visible sur le dashboard,
- le rapport peut être exporté et présenté à un décideur.

Voir l'architecture et les spécifications dans [docs/architecture.md](docs/architecture.md), le planning détaillé dans [docs/gantt_v1.md](docs/gantt_v1.md), et les diagrammes UML dans [docs/use_cases.puml](docs/use_cases.puml), [docs/class_diagram.puml](docs/class_diagram.puml) et [docs/sequence_analysis.puml](docs/sequence_analysis.puml).

## 📝 Livrables de la Séance 1

- [x] Dépôt GitHub initialisé
- [x] Fiche d'identité et README rédigés
- [x] RACI et rôles définis
- [x] Premier commit de groupe
