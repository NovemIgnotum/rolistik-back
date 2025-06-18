"""
Dépendances communes utilisées dans les endpoints FastAPI
Ce fichier centralise toutes les dépendances réutilisables de l'application
"""

from typing import Optional, Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from motor.motor_asyncio import AsyncIOMotorClient

from app.config.settings import settings
from app.config.database import db
from app.core.security import SecurityConfig
from app.models.users import User
from app.services.user_service import UserService
from app.repositories.user import UserRepository

# Configuration du bearer token
security = HTTPBearer()

# ==================== AUTHENTIFICATION ====================

async def get_current_user_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Extrait et valide le token JWT depuis le header Authorization
    
    Args:
        credentials: Credentials HTTP Bearer
        
    Returns:
        str: Token JWT validé
        
    Raises:!
        HTTPException: Si le token est invalide
    """
    token = credentials.credentials
    
    try:
        # Décode le token sans vérifier l'expiration pour le moment
        payload = jwt.decode(
            token, 
            SecurityConfig.SECRET_KEY, 
            algorithms=[SecurityConfig.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token

async def get_current_user(
    token: str = Depends(get_current_user_token)
) -> User:
    """
    Récupère l'utilisateur actuel à partir du token JWT
    
    Args:
        token: Token JWT validé
        
    Returns:
        User: Utilisateur authentifié
        
    Raises:
        HTTPException: Si l'utilisateur n'existe pas ou est inactif
    """
    try:
        # Décode le payload du token
        payload = jwt.decode(
            token, 
            SecurityConfig.SECRET_KEY, 
            algorithms=[SecurityConfig.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide"
            )
            
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide"
        )
    
    # Récupère l'utilisateur depuis la base de données
    user_repository = UserRepository()
    user = await user_repository.get(user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non trouvé"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur inactif"
        )
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Récupère l'utilisateur actuel et vérifie qu'il est actif
    (Redondant avec get_current_user mais plus explicite)
    
    Args:
        current_user: Utilisateur actuel
        
    Returns:
        User: Utilisateur actif
    """
    return current_user

async def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Récupère l'utilisateur actuel et vérifie qu'il est super-utilisateur
    
    Args:
        current_user: Utilisateur actuel
        
    Returns:
        User: Super-utilisateur
        
    Raises:
        HTTPException: Si l'utilisateur n'est pas super-utilisateur
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes"
        )
    return current_user

# ==================== AUTHENTIFICATION OPTIONNELLE ====================

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[User]:
    """
    Récupère l'utilisateur actuel de manière optionnelle
    Utile pour les endpoints qui peuvent fonctionner avec ou sans auth
    
    Args:
        credentials: Credentials optionnelles
        
    Returns:
        Optional[User]: Utilisateur si authentifié, None sinon
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token, 
            SecurityConfig.SECRET_KEY, 
            algorithms=[SecurityConfig.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        
        if user_id is None:
            return None
            
        user_repository = UserRepository()
        user = await user_repository.get(user_id)
        
        if user and user.is_active:
            return user
            
    except JWTError:
        pass
    
    return None

# ==================== INJECTION DE SERVICES ====================

def get_user_service() -> UserService:
    """
    Factory pour le service utilisateur
    
    Returns:
        UserService: Instance du service utilisateur
    """
    return UserService()


# ==================== INJECTION DE REPOSITORIES ====================

def get_user_repository() -> UserRepository:
    """
    Factory pour le repository utilisateur
    
    Returns:
        UserRepository: Instance du repository utilisateur
    """
    return UserRepository()

# ==================== BASE DE DONNÉES ====================

async def get_database() -> AsyncIOMotorClient:
    """
    Récupère la connexion à la base de données
    
    Returns:
        AsyncIOMotorClient: Client MongoDB
    """
    return db.client

# ==================== PAGINATION ====================

class PaginationParams:
    """Paramètres de pagination réutilisables"""
    
    def __init__(self, skip: int = 0, limit: int = 100):
        self.skip = max(0, skip)  # Skip ne peut pas être négatif
        self.limit = min(max(1, limit), 1000)  # Limite entre 1 et 1000

def get_pagination_params(
    skip: int = 0, 
    limit: int = 100
) -> PaginationParams:
    """
    Dépendance pour les paramètres de pagination
    
    Args:
        skip: Nombre d'éléments à ignorer
        limit: Nombre maximum d'éléments à retourner
        
    Returns:
        PaginationParams: Paramètres de pagination validés
    """
    return PaginationParams(skip=skip, limit=limit)

# ==================== VALIDATION DES PARAMÈTRES ====================

def validate_object_id(object_id: str) -> str:
    """
    Valide qu'un string est un ObjectId MongoDB valide
    
    Args:
        object_id: ID à valider
        
    Returns:
        str: ID validé
        
    Raises:
        HTTPException: Si l'ID n'est pas valide
    """
    from bson import ObjectId
    from bson.errors import InvalidId
    
    try:
        ObjectId(object_id)
        return object_id
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID invalide"
        )

# ==================== DÉPENDANCES DE RECHERCHE ====================

class SearchParams:
    """Paramètres de recherche réutilisables"""
    
    def __init__(
        self, 
        q: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ):
        self.query = q
        self.sort_by = sort_by
        self.sort_order = 1 if sort_order.lower() == "asc" else -1

def get_search_params(
    q: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc"
) -> SearchParams:
    """
    Dépendance pour les paramètres de recherche
    
    Args:
        q: Terme de recherche
        sort_by: Champ de tri
        sort_order: Ordre de tri (asc/desc)
        
    Returns:
        SearchParams: Paramètres de recherche
    """
    # Validation des champs de tri autorisés
    allowed_sort_fields = ["created_at", "updated_at", "name", "email"]
    if sort_by not in allowed_sort_fields:
        sort_by = "created_at"
    
    return SearchParams(q=q, sort_by=sort_by, sort_order=sort_order)

# ==================== DÉPENDANCES DE FILTRAGE ====================

class UserFilterParams:
    """Paramètres de filtrage pour les utilisateurs"""
    
    def __init__(
        self,
        is_active: Optional[bool] = None,
        is_superuser: Optional[bool] = None,
        created_after: Optional[str] = None
    ):
        self.is_active = is_active
        self.is_superuser = is_superuser
        self.created_after = created_after

def get_user_filter_params(
    is_active: Optional[bool] = None,
    is_superuser: Optional[bool] = None,
    created_after: Optional[str] = None
) -> UserFilterParams:
    """
    Dépendance pour les filtres utilisateur
    
    Args:
        is_active: Filtre sur le statut actif
        is_superuser: Filtre sur le statut superuser
        created_after: Date de création minimum
        
    Returns:
        UserFilterParams: Paramètres de filtrage
    """
    return UserFilterParams(
        is_active=is_active,
        is_superuser=is_superuser,
        created_after=created_after
    )

# ==================== DÉPENDANCES DE RATE LIMITING ====================

from collections import defaultdict
from datetime import datetime, timedelta

# Cache simple pour le rate limiting (en production, utiliser Redis)
rate_limit_cache = defaultdict(list)

def rate_limit_dependency(max_requests: int = 100, window_minutes: int = 15):
    """
    Factory pour créer des dépendances de rate limiting
    
    Args:
        max_requests: Nombre maximum de requêtes
        window_minutes: Fenêtre de temps en minutes
        
    Returns:
        Function: Dépendance de rate limiting
    """
    def rate_limit(
        request,  # FastAPI Request
        current_user: Optional[User] = Depends(get_current_user_optional)
    ):
        # Utilise l'ID utilisateur ou l'IP comme clé
        key = current_user.id if current_user else request.client.host
        
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=window_minutes)
        
        # Nettoie les anciennes requêtes
        rate_limit_cache[key] = [
            req_time for req_time in rate_limit_cache[key] 
            if req_time > window_start
        ]
        
        # Vérifie la limite
        if len(rate_limit_cache[key]) >= max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Trop de requêtes"
            )
        
        # Enregistre cette requête
        rate_limit_cache[key].append(now)
        
        return True
    
    return rate_limit

# ==================== DÉPENDANCES D'AUTORISATION ====================

def require_permissions(*permissions: str):
    """
    Factory pour créer des dépendances de vérification de permissions
    
    Args:
        permissions: Liste des permissions requises
        
    Returns:
        Function: Dépendance de vérification des permissions
    """
    def check_permissions(
        current_user: User = Depends(get_current_user)
    ) -> User:
        # Ici tu peux implémenter ton système de permissions
        # Par exemple, vérifier que l'utilisateur a les bonnes permissions
        
        # Exemple simple : seuls les superusers ont toutes les permissions
        if not current_user.is_superuser and permissions:
            # Tu peux implémenter une logique plus complexe ici
            # avec des rôles et permissions stockés en base
            user_permissions = getattr(current_user, 'permissions', [])
            if not all(perm in user_permissions for perm in permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Permissions insuffisantes"
                )
        
        return current_user
    
    return check_permissions