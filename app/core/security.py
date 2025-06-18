"""
Module de sécurité pour l'authentification et l'autorisation
Gère JWT, hashage des mots de passe, et validation des tokens
"""

from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from app.config.settings import settings

# Configuration du contexte de hashage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuration JWT
ALGORITHM = settings.algorithm
SECRET_KEY = settings.secret_key
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie si un mot de passe en clair correspond au hash stocké
    
    Args:
        plain_password: Mot de passe en clair
        hashed_password: Hash du mot de passe stocké
        
    Returns:
        bool: True si le mot de passe est correct
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash un mot de passe avec bcrypt
    
    Args:
        password: Mot de passe en clair
        
    Returns:
        str: Hash du mot de passe
    """
    return pwd_context.hash(password)


def create_access_token(
    data: dict, 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crée un token JWT d'accès
    
    Args:
        data: Données à encoder dans le token
        expires_delta: Durée de vie optionnelle du token
        
    Returns:
        str: Token JWT encodé
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(datetime.timestamp) + expires_delta
    else:
        expire = datetime.now(datetime.timestamp) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def create_refresh_token(
    data: dict, 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crée un token JWT de rafraîchissement
    
    Args:
        data: Données à encoder dans le token
        expires_delta: Durée de vie optionnelle du token (défaut: 7 jours)
        
    Returns:
        str: Token JWT de refresh encodé
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(datetime.timestamp) + expires_delta
    else:
        expire = datetime.now(datetime.timestamp) + timedelta(days=7)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_token(token: str) -> dict:
    """
    Décode et valide un token JWT
    
    Args:
        token: Token JWT à décoder
        
    Returns:
        dict: Payload du token
        
    Raises:
        HTTPException: Si le token est invalide ou expiré
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_user_id_from_token(token: str) -> str:
    """
    Extrait l'ID utilisateur d'un token JWT
    
    Args:
        token: Token JWT
        
    Returns:
        str: ID de l'utilisateur
        
    Raises:
        HTTPException: Si le token est invalide ou ne contient pas d'user_id
    """
    payload = decode_token(token)
    user_id: str = payload.get("sub")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide: pas d'identifiant utilisateur",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id


def validate_token_type(token: str, expected_type: str = "access") -> dict:
    """
    Valide le type d'un token JWT
    
    Args:
        token: Token JWT à valider
        expected_type: Type attendu du token ("access" ou "refresh")
        
    Returns:
        dict: Payload du token si valide
        
    Raises:
        HTTPException: Si le type de token ne correspond pas
    """
    payload = decode_token(token)
    token_type = payload.get("type", "access")  # Par défaut "access"
    
    if token_type != expected_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Type de token invalide. Attendu: {expected_type}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


class TokenData:
    """
    Classe pour structurer les données d'un token
    """
    def __init__(self, user_id: str, username: Optional[str] = None):
        self.user_id = user_id
        self.username = username


def create_token_data(user_id: str, username: Optional[str] = None) -> dict:
    """
    Crée les données à encoder dans un token
    
    Args:
        user_id: ID de l'utilisateur
        username: Nom d'utilisateur optionnel
        
    Returns:
        dict: Données structurées pour le token
    """
    return {
        "sub": user_id,
        "username": username,
        "iat": datetime.now(datetime.timestamp),
    }


# Fonctions utilitaires pour la validation des permissions

def check_user_permissions(
    current_user_id: str, 
    resource_user_id: str, 
    is_superuser: bool = False
) -> bool:
    """
    Vérifie si un utilisateur a les permissions pour accéder à une ressource
    
    Args:
        current_user_id: ID de l'utilisateur courant
        resource_user_id: ID du propriétaire de la ressource
        is_superuser: Si l'utilisateur courant est superuser
        
    Returns:
        bool: True si l'accès est autorisé
    """
    return current_user_id == resource_user_id or is_superuser


def require_superuser(is_superuser: bool) -> None:
    """
    Vérifie si l'utilisateur est superuser
    
    Args:
        is_superuser: Statut superuser de l'utilisateur
        
    Raises:
        HTTPException: Si l'utilisateur n'est pas superuser
    """
    if not is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Privilèges insuffisants"
        )


def require_active_user(is_active: bool) -> None:
    """
    Vérifie si l'utilisateur est actif
    
    Args:
        is_active: Statut actif de l'utilisateur
        
    Raises:
        HTTPException: Si l'utilisateur est inactif
    """
    if not is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Utilisateur inactif"
        )


# Générateur de mots de passe sécurisés (optionnel)
import secrets
import string

def generate_secure_password(length: int = 12) -> str:
    """
    Génère un mot de passe sécurisé aléatoire
    
    Args:
        length: Longueur du mot de passe (défaut: 12)
        
    Returns:
        str: Mot de passe généré
    """
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password


def generate_api_key() -> str:
    """
    Génère une clé API sécurisée
    
    Returns:
        str: Clé API hexadécimale
    """
    return secrets.token_hex(32)


# Validation de la force du mot de passe
import re

def validate_password_strength(password: str) -> dict:
    """
    Valide la force d'un mot de passe
    
    Args:
        password: Mot de passe à valider
        
    Returns:
        dict: Résultat de la validation avec score et suggestions
    """
    score = 0
    feedback = []
    
    # Longueur minimum
    if len(password) >= 8:
        score += 1
    else:
        feedback.append("Le mot de passe doit contenir au moins 8 caractères")
    
    # Contient des minuscules
    if re.search(r'[a-z]', password):
        score += 1
    else:
        feedback.append("Ajoutez des lettres minuscules")
    
    # Contient des majuscules
    if re.search(r'[A-Z]', password):
        score += 1
    else:
        feedback.append("Ajoutez des lettres majuscules")
    
    # Contient des chiffres
    if re.search(r'\d', password):
        score += 1
    else:
        feedback.append("Ajoutez des chiffres")
    
    # Contient des caractères spéciaux
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    else:
        feedback.append("Ajoutez des caractères spéciaux")
    
    # Longueur idéale
    if len(password) >= 12:
        score += 1
    
    strength_levels = {
        0: "Très faible",
        1: "Très faible", 
        2: "Faible",
        3: "Moyen",
        4: "Fort",
        5: "Très fort",
        6: "Excellent"
    }
    
    return {
        "score": score,
        "max_score": 6,
        "strength": strength_levels[score],
        "is_strong": score >= 4,
        "feedback": feedback
    }