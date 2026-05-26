from flask import Blueprint, render_template
from app.utils import require_role
from app.models.database import get_db
from app.transactions.verifier import verify_tx_chain

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@require_role('admin')
def dashboard():
    conn = get_db()
    
    # Nombre de comptes
    nb_comptes = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    
    # Vérification intégrité de la chaîne de transactions
    tx_ok, tx_corrupt_id = verify_tx_chain(conn)
    statut_tx = "VALID" if tx_ok else f"COMPROMIS (tx #{tx_corrupt_id})"
    
    conn.close()
    
    return render_template(
        'admin/dashboard.html',
        nb_comptes=nb_comptes,
        statut_tx=statut_tx
    )