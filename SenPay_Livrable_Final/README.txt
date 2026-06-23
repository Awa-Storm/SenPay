===========================================
SenPay - Paiement Mobile Sécurisé
Soumission Finale - 23 juin 2026
===========================================

📌 LANCEMENT
1. Exécutez run.exe
2. Ouvrez votre navigateur à l'adresse : http://127.0.0.1:5000

🔐 IDENTIFIANTS DE TEST
------------------------------------------------
Rôle       | Téléphone   | PIN
------------------------------------------------
Admin      | 771234567   | 1234
Agent      | 770001122   | 1234
Client 1   | 771234568   | 12345
Client 2   | 779998877   | 1234
Client 3   | 775848630   | 2003
Client 4   | 764277204   | 1999
------------------------------------------------

📱 ACCÈS PAR RÔLE
- Admin  : /admin/dashboard, /admin/users, /admin/audit, /admin/verify
- Agent  : /agent/dashboard, /agent/recharge
- Client : /client/dashboard, /client/transfer, /client/history

✅ FONCTIONNALITÉS IMPLÉMENTÉES
------------------------------------------------
- Authentification bcrypt (coût 12)
- MFA (Double authentification TOTP avec Google Authenticator)
- RBAC (Admin, Agent, Client)
- Transferts sécurisés (100 - 500 000 FCFA, 2M/jour)
- Rechargements agent → client
- Chiffrement AES-256-GCM des soldes
- Journal d'audit HMAC-SHA256 avec chaînage
- Vérification d'intégrité des transactions (SHA-256)
- Protection CSRF (tokens synchronisés)
- Middleware sécurité (HSTS, CSP, X-Frame-Options)
- Session avec expiration 30 min
- Force PIN change
- Gestion des comptes (admin : créer, bloquer, supprimer, forcer PIN)
- Création de comptes client / agent / admin
- Interface moderne (design épuré, centré)

🧪 TESTS
- 18/18 tests unitaires PASSED
- Analyse statique Bandit : 0 HIGH/MEDIUM

📂 CONTENU DU .ZIP
- run.exe : exécutable principal (Windows)
- senpay.db : base de données SQLite

=============================
ESP · DGI · DIC2-SSI · 2026
Projet DevSecOps
=============================
