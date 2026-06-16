# WEEKLY.md — Sprint Alpha

## 👤 Awa NIASSE
✅ Arborescence GitHub
✅ config.py (MASTER_KEY, SECRET_KEY, DB_PATH)
✅ table users dans schema.sql
✅ session_mgr.py (jetons 32 octets)
✅ compute_hmac() + GENESIS
✅ log_action() avec chaînage HMAC
✅ verify_audit_chain()
✅ Routes /login, /logout
✅ Tests test_audit.py (3/3 PASSED)

## 👤 Salimata SENE DIOP
✅ Module app/crypto/crypto.py
✅ derive_key() via HKDF-SHA256
✅ encrypt_balance() AES-256-GCM
✅ decrypt_balance()
✅ hash_pin() + verify_pin() bcrypt
✅ Tests test_crypto.py (4/4 PASSED)
✅ Tests intégration avec Serigne (2/2 PASSED)
✅ Audit sécurité (grep, pas de clair)

## 👤 Serigne Mame SARR
✅ Schéma SQL (transactions + audit_log)
✅ database.py (init_db, get_db)
✅ Factory Flask create_app()
✅ run.py
✅ Décorateur require_role() RBAC
✅ compute_tx_hash() + verify_tx_chain()
✅ Routes /admin/dashboard, /audit, /verify
✅ Templates (base, dashboard, audit, verify)
✅ Interface moderne (CSS glassmorphisme)
✅ Tests RBAC + tx_chain (5/5 PASSED)

## 📊 Résultats globaux
| Membre | Tests | Statut |
|--------|-------|--------|
| Awa | 3/3 | ✅ |
| Salimata | 6/6 | ✅ |
| Serigne | 5/5 | ✅ |
| **TOTAL** | **14/14** | ✅ |

✅ Journal HMAC-SHA256 opérationnel
✅ Chaîne transactions SHA-256 valide
✅ RBAC fonctionnel (401/403)
✅ Interface administrateur livrée

## 🚀 Prochaines étapes (Sprint Beta)
- Chiffrement des soldes (Salimata → Serigne)
- Expiration session 30 min (Awa)
- Transactions financières entre comptes




 
 # WEEKLY.md — Sprint Beta

## 📅 Période
Semaines 5 à 8 — Sprint Beta

## 👥 Équipe

| Membre | Rôle |
|--------|------|
| **Awa NIASSE** | Authentification, sessions, journal d'audit HMAC‑SHA256 |
| **Salimata SENE DIOP** | Cryptographie AES‑256‑GCM, gestion des clés |
| **Serigne Mame SARR** | RBAC, logique transactions, architecture Flask |

---

## ✅ Travaux réalisés par Serigne Mame SARR

### 1. Authentification & Sessions
- [x] Connexion avec session Flask
- [x] Déconnexion
- [x] Redirection automatique selon rôle (admin/agent/client)

### 2. RBAC (Contrôle d'accès)
- [x] Décorateur @require_role pour admin, agent, client
- [x] Pages admin protégées (/admin/dashboard, /admin/users, /admin/audit, /admin/verify)
- [x] Pages agent protégées (/agent/dashboard, /agent/recharge)
- [x] Pages client protégées (/client/dashboard, /client/transfer, /client/history)

### 3. Transferts & Rechargements
- [x] Transfert entre clients (/client/transfer)
- [x] Rechargement agent → client (/agent/recharge)
- [x] Vérification des limites (montant 100-500 000 FCFA, journalière 2M FCFA)
- [x] Hash SHA-256 et chaînage des transactions
- [x] Atomicité des transactions (BEGIN/COMMIT/ROLLBACK)
- [x] Journalisation des actions (log_action)

### 4. Chiffrement (intégration Salimata)
- [x] Intégration de encrypt_balance() et decrypt_balance()
- [x] Affichage du solde déchiffré dans dashboard client
- [x] Soldes chiffrés en base (AES-256-GCM)

### 5. Pages d'affichage (tableaux)
- [x] Journal d'audit paginé (/admin/audit) avec tableau
- [x] Liste des utilisateurs (/admin/users) avec tableau
- [x] Historique client (/client/history) avec tableau
- [x] Historique agent (/agent/history) avec tableau
- [x] Vérification d'intégrité (/admin/verify) avec badges

### 6. Sécurité
- [x] Middleware : HSTS, X-Content-Type-Options, X-Frame-Options, CSP
- [x] Protection CSRF (tokens dans formulaires + validation)
- [x] Intégrité de la chaîne de transactions (SHA-256) : **VALID**
- [x] Intégrité du journal d'audit (HMAC-SHA256)

### 7. Interface utilisateur
- [x] Design moderne style app de paiement (orange / jaune)
- [x] Footer avec mentions sécurité (HMAC, AES, RBAC)
- [x] Pages responsives avec tableau propre

### 8. Base de données
- [x] Tables users, 	ransactions, udit_log, sessions
- [x] Soldes chiffrés en base (alance_enc, alance_iv, alance_tag)
- [x] Colonne orce_pin_change (prête pour Awa)

---

## ✅ Travaux réalisés par Salimata SENE DIOP

- [x] Chiffrement AES-256-GCM (encrypt_balance / decrypt_balance)
- [x] Dérivation des clés HKDF
- [x] Hachage PIN (bcrypt cost=12)
- [x] Tests crypto (4/4 PASSED)

---

## ✅ Travaux réalisés par Awa NIASSE

- [x] Authentification renforcée (bcrypt cost=12, verrouillage 15 min)
- [x] Gestion des sessions (token 32 octets, expiration 30 min)
- [x] Route /change-pin
- [x] Flag orce_pin_change
- [x] Tests auth (9/9 PASSED)

---

## 📊 Résultats des tests

`ash
python -m pytest tests/ -v
MembreTestsStatut
Awa9/9✅
Salimata4/4✅
Serigne5/5✅
TOTAL18/18✅
🔗 Intégration croisée
DépendanceDe → VersStatut
log_action()Awa → Serigne✅ intégré
verify_audit_chain()Awa → Serigne✅ intégré
encrypt_balance()Salimata → Serigne✅ intégré
decrypt_balance()Salimata → Serigne✅ intégré
🐛 Points bloquants rencontrés et résolus
ProblèmeSolution
CSRF undefined dans les templatesAjout de csrf_token() dans Jinja2 globals
Message COMPROMIS sur transactionsCorrection des hashes et prev_tx_hash
Soldes affichés 0.0Rechiffrement avec la bonne clé
Accès 403 sur pages adminCorrection du décorateur require_role
🚀 Prochaines étapes (Soumission Finale)
Rédaction du rapport final (Soumission Finale)

Documentation de la gestion des secrets

Préparation de la démonstration

Packaging du projet

📌 Engagement de l'équipe
Le Sprint Beta est livré dans les délais avec 100% des livrables critiques implémentés et testés.
Les 18/18 tests passent.
Le compte-rendu WEEKLY.md est tenu à jour sur la branche main du dépôt GitHub.

Validé par :
Serigne Mame SARR
Responsable RBAC, transactions et architecture Flask

Date : 16 juin 2026
