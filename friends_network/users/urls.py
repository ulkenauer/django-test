from django.urls import path

from . import views

from rest_framework.routers import DefaultRouter

urlpatterns = [
    # path("auth", views.auth, name="auth"),
    # path("profile", views.UserViewSet.as_view({'get': 'get_profile'}), name="profile"),
    # path("register", views.register, name="register"),
    # path("subscribe", views.subscribe, name="subscribe"),
    # path(
    #     "answer_friend_request",
    #     views.answer_friend_request,
    #     name="answer_friend_request",
    # ),
]

router = DefaultRouter()
router.register(r"users", views.UsersViewSet, basename="profile")
router.register(r"subscriptions", views.SubscriptionsViewSet, basename="subscriptions")

urlpatterns = urlpatterns + router.urls
