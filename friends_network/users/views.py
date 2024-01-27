from dataclasses import dataclass
import datetime
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from rest_framework.request import Request
from rest_framework import viewsets
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from django.db.utils import IntegrityError
from drf_spectacular.utils import extend_schema_view

from django.contrib.auth import authenticate
import jwt

from friends_network import settings
from users.exceptions import CustomException
from users.domain.services.subscriptions_service import (
    CreateSubscriptionRequest,
    SubscriptionsService,
)
from users.utils.extend_schema_with_no_defaults import (
    extend_schema_view_no_defaults,
)
from users.utils.jwt_auth_check import jwt_auth_check

from users.models import Subscription

from rest_framework import serializers


class ProfileSerializer(serializers.Serializer):
    username = serializers.CharField()


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class AuthSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


@dataclass
class Profile:
    username: str


@extend_schema_view_no_defaults()
class UsersViewSet(viewsets.ModelViewSet):
    queryset = None
    serializer_class = ProfileSerializer

    @jwt_auth_check
    @extend_schema(
        responses={200: ProfileSerializer, 401: None},
    )
    @action(detail=False, methods=["get"])
    def profile(self, request: Request):
        profile = Profile(
            username=request.user.username,
        )

        return JsonResponse(
            ProfileSerializer(profile).data,
            status=200,
        )

    @extend_schema(
        request=AuthSerializer,
        responses={200: None, 401: None},
    )
    @action(detail=False, methods=["post"])
    def auth(self, request: Request):
        self.serializer_class = None

        user = authenticate(
            username=request.data["username"], password=request.data["password"]
        )

        if user is not None:
            dt = datetime.datetime.now() + datetime.timedelta(days=1)
            token = jwt.encode(
                {"id": user.pk, "exp": int(dt.strftime("%s"))},
                settings.SECRET_KEY,
                algorithm="HS256",
            )

            return JsonResponse({"token": token})
        else:
            return HttpResponse(status=401)

    @extend_schema(
        responses={200: None, 401: None},
        request=RegisterSerializer,
    )
    @action(detail=False, methods=["post"])
    def register(self, request):
        try:
            User.objects.create_user(
                request.data["username"],
                request.data.get("email"),
                request.data["password"],
            )
        except IntegrityError:
            return HttpResponse(status=409)

        return HttpResponse()


class SubscriptionEntitySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    subscribed_id = serializers.IntegerField()
    subscribed_username = serializers.CharField()


class SubscriberEntitySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    subscription_id = serializers.IntegerField()
    username = serializers.CharField()


class IncomingFriendInviteEntitySerializer(serializers.Serializer):
    subscription_id = serializers.IntegerField()
    subscriber_id = serializers.IntegerField()
    subscriber_username = serializers.CharField()


class OutgoingFriendInviteEntitySerializer(serializers.Serializer):
    subscription_id = serializers.IntegerField()
    subscribed_id = serializers.IntegerField()
    subscribed_username = serializers.CharField()


class SubscriptionsListResponseSerializer(serializers.Serializer):
    subscriptions = SubscriptionEntitySerializer(many=True)
    subscribers = SubscriberEntitySerializer(many=True)
    friends = SubscriberEntitySerializer(many=True)
    incoming_friend_requests = IncomingFriendInviteEntitySerializer(many=True)
    outgoing_friend_requests = OutgoingFriendInviteEntitySerializer(many=True)


class SubscribeRequestSerializer(serializers.Serializer):
    username = serializers.CharField()


class MarkAsViewedRequestSerializer(serializers.Serializer):
    username = serializers.CharField()


class UnsubscribeRequestSerializer(serializers.Serializer):
    username = serializers.CharField()


@extend_schema_view(
    retrieve=extend_schema(exclude=True),
    update=extend_schema(exclude=True),
    partial_update=extend_schema(exclude=True),
    destroy=extend_schema(exclude=True),
)
class SubscriptionsViewSet(viewsets.ModelViewSet):
    queryset = ""

    def __init__(self, *args, **kwargs):
        self.service = SubscriptionsService()
        super().__init__(*args, **kwargs)

    @jwt_auth_check
    @extend_schema(
        request=SubscribeRequestSerializer,
        responses={200: None, 400: None, 401: None, 404: None},
    )
    def create(self, request: Request):
        service = self.service

        username = request.data["username"]

        try:
            service.subscribe(
                CreateSubscriptionRequest(
                    username=username,
                    subscriber_id=request.user.pk,
                )
            )
        except CustomException as ex:
            return ex.to_json_response()

        return HttpResponse(status=201)

    @jwt_auth_check
    @extend_schema(
        responses={200: SubscriptionsListResponseSerializer, 401: None},
    )
    def list(self, request: Request):
        service = self.service

        response = service.list_user_subscriptions(user_id=request.user.pk)

        return JsonResponse(
            SubscriptionsListResponseSerializer(response).data,
            status=200,
        )

    @jwt_auth_check
    @extend_schema(
        request=UnsubscribeRequestSerializer,
        responses={200: None, 401: None},
    )
    @action(detail=False, methods=["post"])
    def unsubscribe(self, request: Request):
        service = self.service

        username = request.data["username"]

        try:
            service.unsubscribe(subscriber_id=request.user.pk, username=username)
        except CustomException as ex:
            return ex.to_json_response()

        return HttpResponse(status=204)

    @jwt_auth_check
    @extend_schema(
        request=MarkAsViewedRequestSerializer,
        responses={200: None, 401: None},
    )
    @action(detail=False, methods=["patch"])
    def mark_as_viewed(self, request: Request):
        service = self.service

        username = request.data["username"]

        try:
            service.mark_subscription_as_viewed(
                recipient_id=request.user.pk, username=username
            )
        except CustomException as ex:
            return ex.to_json_response()

        return HttpResponse(status=204)
