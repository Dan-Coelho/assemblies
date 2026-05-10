from typing import Optional

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.base_user import AbstractBaseUser
from django.http import HttpRequest

User = get_user_model()


class EmailAuthBackend(BaseBackend):
    """
    Backend de autenticação que usa e-mail ao invés de username.

    Permite que usuários se autentiquem fornecendo seu endereço de e-mail
    e senha, substituindo o comportamento padrão do Django que usa username.
    """

    def authenticate(
        self,
        request: Optional[HttpRequest],
        username: Optional[str] = None,
        password: Optional[str] = None,
        **kwargs,
    ) -> Optional[AbstractBaseUser]:
        """
        Autentica um usuário pelo e-mail e senha.

        O parâmetro `username` é mantido por compatibilidade com a interface
        padrão do Django, mas seu valor é tratado como endereço de e-mail.

        Returns:
            O objeto User se as credenciais forem válidas, None caso contrário.
        """
        if username is None or password is None:
            return None

        try:
            user: AbstractBaseUser = User.objects.get(email=username)
        except User.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None

    def get_user(self, user_id: int) -> Optional[AbstractBaseUser]:
        """
        Retorna o usuário pelo seu ID primário.

        Returns:
            O objeto User se encontrado, None caso contrário.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
