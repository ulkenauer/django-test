from dataclasses import dataclass
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from users.exceptions import ClientError, ConflictError, ObjectNotFound
from users.models import Subscription, SubscriptionStatus


@dataclass
class CreateSubscriptionRequest:
    subscriber_id: int
    username: str


@dataclass
class SubscriptionEntity:
    id: int
    subscribed_id: int
    subscribed_username: str


@dataclass
class SubscriberEntity:
    id: int
    subscription_id: int
    username: str


@dataclass
class IncomingFriendInviteEntity:
    subscription_id: int
    subscriber_id: int
    subscriber_username: str


@dataclass
class OutgoingFriendInviteEntity:
    subscription_id: int
    subscribed_id: int
    subscribed_username: str


@dataclass
class SubscriptionsListResponse:
    subscriptions: list[SubscriptionEntity]
    subscribers: list[SubscriberEntity]
    friends: list[SubscriberEntity]
    incoming_friend_requests: list[IncomingFriendInviteEntity]
    outgoing_friend_requests: list[OutgoingFriendInviteEntity]


class SubscriptionsService:
    def subscribe(self, request: CreateSubscriptionRequest) -> None:
        try:
            subscribed = User.objects.get(username=request.username)
            subscriber = User.objects.get(id=request.subscriber_id)

            if subscribed.pk == subscriber.pk:
                raise ClientError(code="cant_subscribe_yourself", msg="")

            new_subscription_status = SubscriptionStatus.new.value

            try:
                reverse_sub = Subscription.objects.get(
                    subscriber=subscribed,
                    subscribed=subscriber,
                )
                reverse_sub.status = SubscriptionStatus.viewed.value
                new_subscription_status = SubscriptionStatus.viewed.value
                reverse_sub.save()
            except Subscription.DoesNotExist:
                ...

            subscription = Subscription(
                subscriber=subscriber,
                subscribed=subscribed,
                status=new_subscription_status,
            )

            try:
                subscription.save()
            except IntegrityError:
                raise ConflictError(code="already_subscribed", msg="")

        except User.DoesNotExist:
            raise ObjectNotFound(code="user_not_found", msg="")

    def list_user_subscriptions(self, user_id: int):
        my_subscriptions = (
            Subscription.objects.filter(
                subscriber_id=user_id,
            )
            .select_related("subscribed")
            .all()
        )

        my_subscribers_subscriptions = (
            Subscription.objects.filter(
                subscribed_id=user_id,
            )
            .select_related("subscriber")
            .all()
        )

        subscriptions = [
            SubscriptionEntity(
                id=subscription.pk,
                subscribed_username=subscription.subscribed.username,
                subscribed_id=subscription.subscribed.pk,
            )
            for subscription in my_subscriptions
        ]

        outgoing_friend_requests = [
            OutgoingFriendInviteEntity(
                subscription_id=subscription.pk,
                subscribed_username=subscription.subscribed.username,
                subscribed_id=subscription.subscribed.pk,
            )
            for subscription in my_subscriptions
            if subscription.status == SubscriptionStatus.new.value
        ]

        subscribers = [
            SubscriberEntity(
                subscription_id=subscription.pk,
                username=subscription.subscriber.username,
                id=subscription.subscriber.pk,
            )
            for subscription in my_subscribers_subscriptions
        ]

        subscriptions_by_subscribed_id = {}
        friends = []
        for subscription in my_subscriptions:
            subscriptions_by_subscribed_id[subscription.subscribed_id] = subscription

        for subscriber in subscribers:
            if subscriber.id in subscriptions_by_subscribed_id:
                friends.append(subscriber)

        return SubscriptionsListResponse(
            subscriptions=subscriptions,
            subscribers=subscribers,
            friends=friends,
            outgoing_friend_requests=outgoing_friend_requests,
            incoming_friend_requests=[
                IncomingFriendInviteEntity(
                    subscription_id=subscription.pk,
                    subscriber_username=subscription.subscriber.username,
                    subscriber_id=subscription.subscriber.pk,
                )
                for subscription in my_subscribers_subscriptions
                if subscription.status == SubscriptionStatus.new.value
            ],
        )

    def mark_subscription_as_viewed(self, username: str, recipient_id: int) -> None:
        try:
            subscribed = User.objects.get(username=username)
            subscription = Subscription.objects.get(
                subscriber=subscribed,
                subscribed_id=recipient_id,
            )

            if subscription.status == SubscriptionStatus.viewed.value:
                raise ClientError(code="subscription_already_viewed", msg="")

            subscription.status = SubscriptionStatus.viewed.value
            subscription.save()
        except User.DoesNotExist:
            raise ObjectNotFound(code="user_not_found", msg="")
        except Subscription.DoesNotExist:
            raise ObjectNotFound(code="subscription_not_found", msg="")

    def unsubscribe(self, username: str, subscriber_id: int) -> None:
        try:
            subscribed = User.objects.get(username=username)
            subscription = Subscription.objects.get(
                subscriber=subscriber_id,
                subscribed_id=subscribed.pk,
            )
        except Subscription.DoesNotExist:
            raise ObjectNotFound(code="subscription_not_found", msg="")

        subscription.delete()
