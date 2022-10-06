from django.contrib.auth.backends import BaseBackend
from users.models import MyUser


class SettingsBackend(BaseBackend):
    """Custom authentication model for wallet

    """

    def authenticate(self, request, wallet=None, password=None, has_nft=None):
        """get user model for user or create new user

        :param request:
        :param wallet: wallet address
        :param password: Not needed
        :param has_nft: if user has nft
        :return:
        """
        has_nft_parsed = True if has_nft == "true" else False
        try:
            user = MyUser.objects.get(wallet=wallet)
            user.has_nft = has_nft_parsed
            user.save()
        except MyUser.DoesNotExist:
            user = MyUser(wallet=wallet, has_nft=has_nft_parsed)
            user.save()
        return user

    def get_user(self, user_id):
        try:
            return MyUser.objects.get(pk=user_id)
        except MyUser.DoesNotExist:
            return None
