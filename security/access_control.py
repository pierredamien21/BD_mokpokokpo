from fastapi import Depends, HTTPException, status
from security.dependencies import get_current_user
from schema.enums import RoleEnum
from models.model import Utilisateur

class RoleChecker:
    def __init__(self, allowed_roles: list[RoleEnum]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: Utilisateur = Depends(get_current_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous n'avez pas les droits nécessaires"
            )
        return user
