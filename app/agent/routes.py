from flask import Blueprint, render_template, request, session
from app.auth.decorators import require_role
from app.models.database import get_db
from app.transactions.recharge import execute_recharge

agent_bp = Blueprint('agent', __name__, url_prefix='/agent')

@agent_bp.route('/dashboard')
@require_role('agent', 'admin')
def dashboard():
    return render_template('agent/dashboard.html')

@agent_bp.route('/recharge', methods=['GET', 'POST'])
@require_role('agent', 'admin')
def recharge():
    if request.method == 'POST':
        client_phone = request.form.get('client_phone')
        amount = float(request.form.get('amount', 0))
        
        conn = get_db()
        success, message = execute_recharge(conn, session['user_id'], client_phone, amount)
        conn.close()
        
        if success:
            return render_template('agent/recharge.html', message=message)
        else:
            return render_template('agent/recharge.html', error=message)
    
    return render_template('agent/recharge.html')

@agent_bp.route('/history')
@require_role('agent', 'admin')
def history():
    conn = get_db()
    recharges = conn.execute(
        'SELECT id, amount, receiver_id, timestamp FROM transactions '
        'WHERE sender_id = ? AND tx_type = "recharge" ORDER BY timestamp DESC LIMIT 50',
        (session['user_id'],)
    ).fetchall()
    conn.close()
    return render_template('agent/history.html', recharges=recharges)
