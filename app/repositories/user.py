"""
Repository pour la gestion des utilisateurs - Couche d'accès aux données
Contient toutes les requêtes MongoDB spécifiques aux utilisateurs
"""

from typing import Optional, List
from beanie.operators import In, RegEx
from app.models.users import User
from app.repositories.base import BaseRepository
from app.schemas.user import UserCreate, UserUpdate

class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """Repository pour les opérations CRUD sur les utilisateurs"""
    
    def __init__(self):
        super().__init__(User)
    
    # ==================== RECHERCHES SPÉCIFIQUES ====================
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Trouve un utilisateur par son email
        
        Args:
            email: Email de l'utilisateur
            
        Returns:
            User ou None si non trouvé
        """
        return await User.find_one(User.email == email)
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Trouve un utilisateur par son nom d'utilisateur
        
        Args:
            username: Nom d'utilisateur
            
        Returns:
            User ou None si non trouvé
        """
        return await User.find_one(User.username == username)
    
    async def get_by_email_or_username(self, identifier: str) -> Optional[User]:
        """
        Trouve un utilisateur par email OU username
        Utile pour la connexion
        
        Args:
            identifier: Email ou username
            
        Returns:
            User ou None si non trouvé
        """
        return await User.find_one(
            {"$or": [
                {"email": identifier},
                {"username": identifier}
            ]}
        )
    
    # ==================== FILTRES ET RECHERCHES ====================
    
    async def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Récupère tous les utilisateurs actifs
        
        Args:
            skip: Nombre d'éléments à ignorer (pagination)
            limit: Nombre maximum d'éléments à retourner
            
        Returns:
            Liste des utilisateurs actifs
        """
        return await User.find(User.is_active == True).skip(skip).limit(limit).to_list()
    
    async def get_inactive_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Récupère tous les utilisateurs inactifs
        
        Args:
            skip: Nombre d'éléments à ignorer
            limit: Nombre maximum d'éléments à retourner
            
        Returns:
            Liste des utilisateurs inactifs
        """
        return await User.find(User.is_active == False).skip(skip).limit(limit).to_list()
    
    async def get_superusers(self) -> List[User]:
        """
        Récupère tous les super-utilisateurs
        
        Returns:
            Liste des super-utilisateurs
        """
        return await User.find(User.is_superuser == True).to_list()
    
    async def search_users(self, query: str, skip: int = 0, limit: int = 20) -> List[User]:
        """
        Recherche textuelle dans les utilisateurs
        Cherche dans username, email et full_name
        
        Args:
            query: Terme de recherche
            skip: Pagination
            limit: Limite de résultats
            
        Returns:
            Liste des utilisateurs correspondants
        """
        # Recherche par regex (insensible à la casse)
        regex_pattern = RegEx(pattern=query, options="i")
        
        return await User.find({
            "$or": [
                {"username": regex_pattern},
                {"email": regex_pattern},
                {"full_name": regex_pattern}
            ]
        }).skip(skip).limit(limit).to_list()
    
    # ==================== STATISTIQUES ET COMPTEURS ====================
    
    async def count_active_users(self) -> int:
        """
        Compte le nombre d'utilisateurs actifs
        
        Returns:
            Nombre d'utilisateurs actifs
        """
        return await User.find(User.is_active == True).count()
    
    async def count_total_users(self) -> int:
        """
        Compte le nombre total d'utilisateurs
        
        Returns:
            Nombre total d'utilisateurs
        """
        return await User.find_all().count()
    
    async def count_new_users_today(self) -> int:
        """
        Compte les nouveaux utilisateurs créés aujourd'hui
        
        Returns:
            Nombre d'utilisateurs créés aujourd'hui
        """
        from datetime import datetime, time
        
        today = datetime.now().date()
        start_of_day = datetime.combine(today, time.min)
        end_of_day = datetime.combine(today, time.max)
        
        return await User.find({
            "created_at": {
                "$gte": start_of_day,
                "$lte": end_of_day
            }
        }).count()
    
    # ==================== OPÉRATIONS MÉTIER ====================
    
    async def activate_user(self, user_id: str) -> Optional[User]:
        """
        Active un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            User mis à jour ou None
        """
        user = await self.get(user_id)
        if user:
            user.is_active = True
            await user.save()
        return user
    
    async def deactivate_user(self, user_id: str) -> Optional[User]:
        """
        Désactive un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            User mis à jour ou None
        """
        user = await self.get(user_id)
        if user:
            user.is_active = False
            await user.save()
        return user
    
    async def update_password(self, user_id: str, new_hashed_password: str) -> Optional[User]:
        """
        Met à jour le mot de passe d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            new_hashed_password: Nouveau mot de passe hashé
            
        Returns:
            User mis à jour ou None
        """
        user = await self.get(user_id)
        if user:
            user.hashed_password = new_hashed_password
            await user.save()
        return user
    
    async def update_last_login(self, user_id: str) -> Optional[User]:
        """
        Met à jour la dernière connexion d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            User mis à jour ou None
        """
        from datetime import datetime
        
        user = await self.get(user_id)
        if user:
            # Supposons qu'on ajoute un champ last_login au modèle User
            user.last_login = datetime.utcnow()
            await user.save()
        return user
    
    # ==================== VÉRIFICATIONS D'EXISTENCE ====================
    
    async def email_exists(self, email: str) -> bool:
        """
        Vérifie si un email existe déjà
        
        Args:
            email: Email à vérifier
            
        Returns:
            True si l'email existe
        """
        user = await User.find_one(User.email == email)
        return user is not None
    
    async def username_exists(self, username: str) -> bool:
        """
        Vérifie si un nom d'utilisateur existe déjà
        
        Args:
            username: Username à vérifier
            
        Returns:
            True si le username existe
        """
        user = await User.find_one(User.username == username)
        return user is not None
    
    async def email_exists_exclude_user(self, email: str, user_id: str) -> bool:
        """
        Vérifie si un email existe déjà (en excluant un utilisateur spécifique)
        Utile pour les mises à jour
        
        Args:
            email: Email à vérifier
            user_id: ID de l'utilisateur à exclure
            
        Returns:
            True si l'email existe chez un autre utilisateur
        """
        user = await User.find_one({
            "email": email,
            "_id": {"$ne": user_id}
        })
        return user is not None
    
    # ==================== OPÉRATIONS EN LOT ====================
    
    async def get_users_by_ids(self, user_ids: List[str]) -> List[User]:
        """
        Récupère plusieurs utilisateurs par leurs IDs
        
        Args:
            user_ids: Liste des IDs utilisateurs
            
        Returns:
            Liste des utilisateurs trouvés
        """
        return await User.find(In(User.id, user_ids)).to_list()
    
    async def bulk_activate_users(self, user_ids: List[str]) -> int:
        """
        Active plusieurs utilisateurs en une fois
        
        Args:
            user_ids: Liste des IDs à activer
            
        Returns:
            Nombre d'utilisateurs activés
        """
        result = await User.find(In(User.id, user_ids)).update(
            {"$set": {"is_active": True}}
        )
        return result.modified_count
    
    async def bulk_deactivate_users(self, user_ids: List[str]) -> int:
        """
        Désactive plusieurs utilisateurs en une fois
        
        Args:
            user_ids: Liste des IDs à désactiver
            
        Returns:
            Nombre d'utilisateurs désactivés
        """
        result = await User.find(In(User.id, user_ids)).update(
            {"$set": {"is_active": False}}
        )
        return result.modified_count
    
    # ==================== REQUÊTES COMPLEXES ====================
    
    async def get_users_with_filters(
        self,
        is_active: Optional[bool] = None,
        is_superuser: Optional[bool] = None,
        created_after: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """
        Récupère des utilisateurs avec des filtres multiples
        
        Args:
            is_active: Filtre sur le statut actif
            is_superuser: Filtre sur le statut superuser
            created_after: Date de création minimum (ISO string)
            skip: Pagination
            limit: Limite de résultats
            
        Returns:
            Liste des utilisateurs filtrés
        """
        filters = {}
        
        if is_active is not None:
            filters["is_active"] = is_active
            
        if is_superuser is not None:
            filters["is_superuser"] = is_superuser
            
        if created_after:
            from datetime import datetime
            date_filter = datetime.fromisoformat(created_after)
            filters["created_at"] = {"$gte": date_filter}
        
        if not filters:
            return await User.find_all().skip(skip).limit(limit).to_list()
        
        return await User.find(filters).skip(skip).limit(limit).to_list()
    
    # ==================== MÉTHODES D'AGRÉGATION ====================
    
    async def get_user_stats(self) -> dict:
        """
        Statistiques générales sur les utilisateurs
        
        Returns:
            Dictionnaire avec les statistiques
        """
        total = await self.count_total_users()
        active = await self.count_active_users()
        superusers = len(await self.get_superusers())
        
        return {
            "total_users": total,
            "active_users": active,
            "inactive_users": total - active,
            "superusers": superusers,
            "activation_rate": (active / total * 100) if total > 0 else 0
        }