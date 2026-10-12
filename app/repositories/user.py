import logging
from typing import Optional, Tuple

from sqlmodel import Session, func, select

from app.models.user import User, UserBase
from app.schemas.user import UserUpdate
from app.utilities.pagination import Pagination

logger = logging.getLogger(__name__)


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _parse_connection_ids(value: str | None) -> list[int]:
        if not value:
            return []
        ids: list[int] = []
        for part in str(value).split(","):
            token = part.strip()
            if not token:
                continue
            try:
                ids.append(int(token))
            except ValueError:
                continue
        return ids

    def create(self, user_data: UserBase) -> Optional[User]:
        try:
            user_db = User.model_validate(user_data)
            self.db.add(user_db)
            self.db.commit()
            self.db.refresh(user_db)
            return user_db
        except Exception as e:
            logger.error(f"An error occurred while saving user: {e}")
            self.db.rollback()
            raise

    def search_users(self, query: str, page: int = 1, limit: int = 10) -> Tuple[list[User], Pagination]:
        offset = (page - 1) * limit
        db_qry = select(User)
        if query:
            db_qry = db_qry.where(
                User.username.ilike(f"%{query}%") | User.email.ilike(f"%{query}%")
            )
        count_qry = select(func.count()).select_from(db_qry.subquery())
        count_todos = self.db.exec(count_qry).one()

        users = self.db.exec(db_qry.offset(offset).limit(limit)).all()
        pagination = Pagination(total_count=count_todos, current_page=page, limit=limit)

        return users, pagination

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.exec(select(User).where(User.username == username)).one_or_none()

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.get(User, user_id)

    def get_all_users(self) -> list[User]:
        return self.db.exec(select(User)).all()

    def get_connections(self, user_id: int) -> list[User]:
        user = self.get_by_id(user_id)
        if not user:
            return []
        connection_ids = self._parse_connection_ids(user.connection_ids)
        if not connection_ids:
            return []
        return self.db.exec(select(User).where(User.id.in_(connection_ids))).all()

    def connect_users(self, user_id: int, target_user_id: int) -> User:
        if user_id == target_user_id:
            raise ValueError("A user cannot connect to themselves")
        user = self.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        ids = self._parse_connection_ids(user.connection_ids)
        if target_user_id not in ids:
            ids.append(target_user_id)
        user.connection_ids = ",".join(str(item) for item in ids)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def disconnect_users(self, user_id: int, target_user_id: int) -> User:
        user = self.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        ids = self._parse_connection_ids(user.connection_ids)
        ids = [item for item in ids if item != target_user_id]
        user.connection_ids = ",".join(str(item) for item in ids)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        user = self.db.get(User, user_id)
        if not user:
            raise Exception("Invalid user id given")
        if user_data.username:
            user.username = user_data.username
        if user_data.email:
            user.email = user_data.email
        if user_data.firstname is not None:
            user.firstname = user_data.firstname
        if user_data.lastname is not None:
            user.lastname = user_data.lastname
        if user_data.yeargraduated is not None:
            user.yeargraduated = user_data.yeargraduated
        if user_data.department is not None:
            user.department = user_data.department
        if user_data.profile_description is not None:
            user.profile_description = user_data.profile_description
        if user_data.connection_ids is not None:
            user.connection_ids = user_data.connection_ids

        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception as e:
            logger.error(f"An error occurred while updating user: {e}")
            self.db.rollback()
            raise

    def delete_user(self, user_id: int):
        user = self.db.get(User, user_id)
        if not user:
            raise Exception("User doesn't exist")
        try:
            self.db.delete(user)
            self.db.commit()
        except Exception as e:
            logger.error(f"An error occurred while deleting user: {e}")
            self.db.rollback()
            raise
