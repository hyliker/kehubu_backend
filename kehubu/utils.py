from wechatpy import WeChatClient
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.sites.models import Site


def get_weixin_app(request=None):
    if request is None:
        site = Site.objects.get_current()
    else:
        site = get_current_site(request)

    return site.socialapp_set.get(provider='weixin')


def get_wechat_client(request=None):
    app = get_weixin_app(request)
    return WeChatClient(app.client_id, app.secret)