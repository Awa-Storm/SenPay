import secrets
from datetime import datetime, timedelta, timezone
from flask import session

# Durée maximale d'inactivité avant déconnexion automatique
# Fixée à 30 min par l'exigence EF02 du cahier des charges
SESSION_LIFETIME = 30  # minutes


def create_session(user_id, role):
    """Crée une nouvelle session après une connexion réussie
    
    Paramètres :
        user_id → identifiant de l'utilisateur connecté (depuis la table users)
        role    → 'client', 'agent' ou 'admin' (détermine les accès autorisés)
    """
    
    # Stocke l'identifiant pour savoir qui est connecté sur chaque requête
    session['user_id'] = user_id
    
    # Stocke le rôle pour le contrôle d'accès RBAC (vérifié par Serigne)
    session['role'] = role
    
    # Génère un jeton aléatoire de 32 octets (64 caractères hex)
    # secrets est cryptographiquement sûr, contrairement à random
    # Ce jeton est unique à chaque connexion : impossible à deviner
    session['token'] = secrets.token_hex(32)
    
    # Enregistre l'heure exacte de connexion en UTC
    # Servira de référence pour calculer l'inactivité
    session['last_active'] = datetime.now(timezone.utc).isoformat()


def is_session_valid():
    """Vérifie si la session courante est encore active
    
    Retourne True si valide, False si expirée ou inexistante
    À appeler au début de chaque route protégée
    """
    
    # Si last_active n'existe pas → personne n'est connecté
    if 'last_active' not in session:
        return False
    
    # Récupère l'heure de la dernière activité
    last = datetime.fromisoformat(session['last_active'])
    
    # Calcule si 30 min se sont écoulées depuis la dernière action
    expired = datetime.now(timezone.utc) - last > timedelta(minutes=SESSION_LIFETIME)
    
    if expired:
        # Détruit toute la session : le cookie devient inutilisable
        session.clear()
        return False
    
    # Session encore valide : on met à jour l'heure de dernière activité
    # Cela repart le compteur de 30 min à zéro à chaque action
    session['last_active'] = datetime.now(timezone.utc).isoformat()
    return True


def destroy_session():
    """Détruit la session lors d'un logout volontaire
    
    session.clear() supprime toutes les données côté serveur Flask
    Le cookie existant devient inutilisable immédiatement
    """
    session.clear()
