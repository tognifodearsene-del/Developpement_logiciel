# CONTRIBUTING

Bienvenue les développeurs !

## Setup

1. Cloner le dépôt : `git clone <url-du-repo>`
2. Activer les hooks pre-commit : `pip install pre-commit && pre-commit install`
3. Backend :
   - Linux / macOS : `python -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
   - Windows (PowerShell) : `python -m venv venv && .\venv\Scripts\Activate.ps1 && pip install -r requirements.txt`
4. Frontend : `npm install`

## Git Workflow

1. Créer une branche : `git checkout -b feature/us-XX-description`
2. Développer et tester
3. Commit : `git commit -m "feat: description"`
4. Push : `git push origin feature/us-XX-description`
5. Créer une Pull Request sur GitHub

## Standards

- Python : PEP 8 + tests > 70% coverage
- JavaScript : ESLint + Prettier
- Code review requis avant merge

Pour plus de détails, voir `docs/`.
