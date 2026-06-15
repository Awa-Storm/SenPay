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