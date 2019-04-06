from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class KehubuAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return False


class KehubuSocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        return True

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        provider = sociallogin.account.provider
        user.kehubu_profile.update_by_socialaccount(provider)
        return user
