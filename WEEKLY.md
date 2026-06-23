# WEEKLY.md — Sprint Beta Final

## 📅 Période
Sprint Beta — Semaines 5 à 8 + Améliorations post-Beta

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

### 5. Pages d'affichage
- [x] Journal d'audit paginé (/admin/audit)
- [x] Liste des utilisateurs (/admin/users)
- [x] Historique client (/client/history)
- [x] Historique agent (/agent/history)
- [x] Vérification d'intégrité (/admin/verify)

### 6. Sécurité
- [x] Middleware : HSTS, X-Content-Type-Options, X-Frame-Options, CSP
- [x] Protection CSRF (tokens dans formulaires + validation)
- [x] Intégrité de la chaîne de transactions (SHA-256) : **VALID**
- [x] Intégrité du journal d'audit (HMAC-SHA256)

### 7. Interface utilisateur
- [x] Design moderne style app de paiement (orange / jaune)
- [x] Pages responsives avec tableau propre

### 8. Base de données
- [x] Tables users, 	ransactions, udit_log, sessions
- [x] Soldes chiffrés en base (alance_enc, alance_iv, alance_tag)
- [x] Colonne orce_pin_change

---

## ✅ Améliorations post-Sprint Beta

| Amélioration | Description |
|--------------|-------------|
| Création de comptes | Pages /register pour client, agent, admin |
| MFA | Double authentification TOTP avec Google Authenticator |
| Gestion des comptes admin | Bloquer, débloquer, supprimer, forcer PIN |
| Design moderne | Refonte CSS, pages centrées, interface épurée |
| Middlewares sécurité | HSTS, CSP, X-Frame-Options, X-Content-Type |
| Protection CSRF | Tokens synchronisés dans tous les formulaires |
| Correction intégrité | Chaîne transactions SHA-256 validée |

---

## 📊 Résultats des tests

`ash
python -m pytest tests/ -v
MembreTestsStatut
Awa9/9✅
Salimata4/4✅
Serigne5/5✅
TOTAL18/18✅
🚀 Prochaines étapes (Soumission Finale)
Rédaction du rapport final

Packaging .zip avec exécutable

Dépôt sur Drive

Validé par :
Serigne Mame SARR
Responsable RBAC, transactions et architecture Flask

Date : 23 juin 2026
