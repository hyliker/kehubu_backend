from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class KehubuAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return False


class KehubuSocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        return True
