from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import Group as DjangoGroup
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from app.models import BaseModel
from app.validators.doc import CpfValidator

from .consts import Role


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra):
        user = self.model(email=self.normalize_email(email), **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra):
        user = self.create_user(email, password=password, **extra)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    username = None  # Removes username field
    full_name = models.CharField(_("full name"), max_length=255)
    email = models.EmailField(_("email address"), unique=True)
    role = models.CharField(
        verbose_name=_("role"),
        choices=Role.choices,
        default=Role.ADMIN,
        max_length=8,
    )
    cpf = models.CharField(
        verbose_name=_("cpf"),
        unique=True,
        max_length=11,
        error_messages={"unique": _("A user with this CPF already exists")},
        validators=[CpfValidator()],
    )
    # Permissions
    is_active = models.BooleanField(
        _("is active"),
        help_text=_("Inactive users can't login. Use this instead of deleting the user."),
        default=True,
    )
    is_staff = models.BooleanField(
        _("is staff"),
        help_text=_("Only staff users can access the admin"),
        default=False,
    )
    is_superuser = models.BooleanField(
        _("is admin"),
        help_text=_("Super users have all permissions"),
        default=False,
    )

    # Meta
    date_joined = models.DateTimeField(_("date joined"), auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "full_name",
    ]

    def __str__(self):
        return f"{self.email}"

    def get_short_name(self):
        return self.full_name.split(" ")[0]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")


class Group(DjangoGroup):
    """Defining this here allow to group the django model `Group`
    together in this users app."""

    class Meta:
        proxy = True
        verbose_name = _("user group")
        verbose_name_plural = _("user groups")
