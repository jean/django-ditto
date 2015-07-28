from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r"^$",
        view=views.Home.as_view(),
        name='index'
    ),
    url(
        regex=r"^tag/(?P<slug>[-_\w]+)$",
        view=views.TagDetail.as_view(),
        name='tag_detail'
    ),
]

