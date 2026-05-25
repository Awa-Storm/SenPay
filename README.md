# SenPay — Système de Paiement Mobile Sécurisé

## Lancement

```bash
export SENPAY_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
pip install -r requirements.txt
python run.py
```
