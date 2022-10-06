from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
import math
import random


# TODO: check
class MyUserManager(BaseUserManager):
    def create_user(self, wallet, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not wallet:
            raise ValueError('Users must have a wallet')

        user = self.model(
            wallet=wallet
        )
        if password is not None:
            user.set_password(password)

        user.save(using=self._db)
        return user

    def create_superuser(self, wallet, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            wallet=wallet, password=password
        )
        user.is_admin = True
        user.is_active = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    """User model

    """
    wallet = models.CharField(
        verbose_name='wallet',
        max_length=255,
        unique=True,
    )
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    has_nft = models.BooleanField(default=False)
    nonce = models.IntegerField(default=math.floor(random.random() * 1000000))
    objects = MyUserManager()

    USERNAME_FIELD = 'wallet'

    REQUIRED_FIELDS = []

    def __str__(self):
        return self.wallet

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
