<<<<<<< HEAD
# SenPay
Systeme de paiement mobile securise
=======
# 🔐 SenPay

> Systeme de paiement mobile securise avec contrôle d'accès par rôles

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![CI](https://github.com/[username]/secvault-dic2-ssi/actions/workflows/ci.yml/badge.svg)](https://github.com/[username]/secvault-dic2-ssi/actions)

**Projet de Programmation Sécurisée – DevSecOps**  
École Supérieure Polytechnique de Dakar · DIC2 – SSI · 2025–2026  
Professeur : Dr. Doudou Fall

---

## 👥 Équipe

| Nom | Email | Rôle |
|-----|-------|------|
| Salimata Sène Diop | salimatasenediop@esp.sn | Cryptographie & Chiffrement AES-GCM |
| Awa Niasse | awaniasse1@esp.sn | Authentification 2FA & Journal d'audit |
| Serigne Mame Sarr | serignemamesarr@esp.sn | RBAC, CLI & Architecture du système |

---

## 📌 Description

**SecVault** est un gestionnaire de secrets chiffré en ligne de commande, conçu pour stocker, consulter et gérer des informations sensibles (mots de passe, clés API, notes confidentielles) avec une sécurité de niveau professionnel.

Inspiré de [HashiCorp Vault](https://www.vaultproject.io/), il garantit que :
- Chaque secret est **chiffré au repos** avec AES-256-GCM
- Tout accès est **journalisé** de manière non répudiable (HMAC-SHA256)
- Les utilisateurs n'accèdent qu'aux secrets correspondant à leur **rôle** (RBAC)
- L'authentification est **forte** : mot de passe + TOTP (2FA)

---

## 🏗️ Architecture du projet

```
secvault/
├── src/
│   ├── auth/          # Authentification (MDP + TOTP 2FA)
│   ├── crypto/        # Chiffrement AES-256-GCM, dérivation Argon2id
│   ├── rbac/          # Contrôle d'accès par rôles
│   ├── audit/         # Journal d'audit signé HMAC-SHA256
│   └── cli/           # Interface en ligne de commande
├── tests/
│   ├── unit/          # Tests unitaires par module
│   └── integration/   # Tests d'intégration end-to-end
├── docs/              # Documentation technique
├── scripts/           # Scripts utilitaires (setup, migration)
├── .github/
│   └── workflows/     # CI/CD GitHub Actions
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

---

## 🔒 Éléments de sécurité implémentés

| Élément | Implémentation |
|---------|---------------|
| **Authentification** | Argon2id (KDF) + TOTP RFC 6238 (2FA via `pyotp`) |
| **Autorisation** | RBAC (admin / user / viewer) stocké chiffré en base |
| **Audit** | Journal horodaté, signé HMAC-SHA256, non répudiable |
| **Confidentialité** | AES-256-GCM pour tous les secrets au repos |
| **Intégrité** | MAC sur chaque entrée + vérification à la lecture |

---

## 🚀 Installation

### Prérequis
- Python 3.11+
- pip

### Installation

```bash
# Cloner le dépôt
git clone https://github.com/[username]/secvault-dic2-ssi.git
cd secvault-dic2-ssi

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate.bat    # Windows

# Installer les dépendances
pip install -r requirements.txt

# Initialiser SecVault (premier lancement)
python -m src.cli.main init
```

---

## 💻 Utilisation

```bash
# Créer un compte
python -m src.cli.main register

# Se connecter (MDP + code TOTP)
python -m src.cli.main login

# Ajouter un secret
python -m src.cli.main secret add --name "github_token" --value "ghp_..."

# Lister ses secrets
python -m src.cli.main secret list

# Consulter un secret
python -m src.cli.main secret get --name "github_token"

# Voir le journal d'audit
python -m src.cli.main audit logs
```

---

## 🧪 Tests

```bash
# Installer les dépendances de développement
pip install -r requirements-dev.txt

# Lancer tous les tests
pytest tests/ -v

# Avec couverture de code
pytest tests/ --cov=src --cov-report=html
```

---

## 🌿 Convention de branches

| Branche | Usage |
|---------|-------|
| `main` | Code stable, protégé (merge via PR uniquement) |
| `feature/auth` | Module d'authentification |
| `feature/crypto` | Module de chiffrement |
| `feature/rbac` | Contrôle d'accès par rôles |
| `feature/audit` | Journal d'audit |
| `feature/cli` | Interface CLI |

---

## 📅 Planning des sprints

| Livrable | Date limite | Focus |
|----------|-------------|-------|
| **Charte** | 14 avril 2026 | Définition du projet |
| **Document des exigences** | 05 mai 2026 | User stories, menaces, objectifs |
| **Sprint Alpha** | 26 mai 2026 | Audit, crypto, structure de base |
| **Sprint Beta** | 16 juin 2026 | Authentification, RBAC, CLI complète |
| **Soumission finale** | 23 juin 2026 | Code final + rapport |

---

## 📚 Bibliothèques utilisées

| Bibliothèque | Usage |
|-------------|-------|
| `cryptography` (PyCA) | AES-256-GCM, HMAC-SHA256 |
| `argon2-cffi` | Dérivation de clé (Argon2id) |
| `pyotp` | TOTP 2FA (RFC 6238) |
| `sqlite3` (stdlib) | Base de données locale chiffrée |

---

## 📄 Licence

Ce projet est développé à des fins académiques dans le cadre du cours DevSecOps – DIC2 SSI, ESP Dakar.  
© 2025–2026 Salimata Sène Diop, Awa Niasse, Serigne Mame Sarr.
>>>>>>> df0efaf (feat: initialisation du projet SecVault)
