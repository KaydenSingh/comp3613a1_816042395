from typing import Optional

from app.repositories.user import UserRepository
from app.schemas.user import RegularUserCreate
from app.utilities.security import create_access_token, encrypt_password, verify_password


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def get_all_users(self):
        return self.user_repo.get_all_users()

    def get_user_by_id(self, user_id: int):
        return self.user_repo.get_by_id(user_id)

    def get_connections(self, user_id: int):
        return self.user_repo.get_connections(user_id)

    def connect_users(self, user_id: int, target_user_id: int):
        return self.user_repo.connect_users(user_id, target_user_id)

    def disconnect_users(self, user_id: int, target_user_id: int):
        return self.user_repo.disconnect_users(user_id, target_user_id)
    