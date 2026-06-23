from flask import request, session, redirect, url_for, flash, render_template
from app.models.database import get_db
import pyotp

@mfa_bp.route('/verify', methods=['GET', 'POST'])
def verify():
    if 'user_id' not in session:
        flash('Veuillez vous connecter d\'abord.', 'warning')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        code = request.form.get('code')
        secret = session.get('mfa_temp_secret')

        if not secret:
            flash('Session MFA expirée. Veuillez recommencer.', 'danger')
            return redirect(url_for('mfa.setup'))

        totp = pyotp.TOTP(secret)
        if totp.verify(code):
            conn = get_db()
            conn.execute('UPDATE users SET mfa_secret = ? WHERE id = ?', (secret, session['user_id']))
            conn.commit()
            conn.close()

            session.pop('mfa_temp_secret', None)
            flash('MFA activé avec succès !', 'success')
            return redirect(url_for('client.dashboard'))
        else:
            flash('Code MFA invalide. Veuillez réessayer.', 'danger')

    return render_template('mfa_verify.html')
