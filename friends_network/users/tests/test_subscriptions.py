from django.test import TestCase
from django.contrib.auth.models import User
from users.exceptions import ClientError, ConflictError, ObjectNotFound

from users.domain.services.subscriptions_service import (
    CreateSubscriptionRequest,
    SubscriptionsService,
)


class SubscriptionsTestCase(TestCase):
    def setUp(self):
        self.service = SubscriptionsService()

    def test_user_can_subscribe(self):
        test_user = User.objects.create_user("username", None, "password")
        test_user_2 = User.objects.create_user("username_2", None, "password")

        subscriber_subs = self.service.list_user_subscriptions(test_user.pk)
        subscribed_subs = self.service.list_user_subscriptions(test_user_2.pk)

        self.assertEqual(len(subscriber_subs.subscriptions), 0)
        self.assertEqual(len(subscriber_subs.subscribers), 0)
        self.assertEqual(len(subscriber_subs.friends), 0)
        self.assertEqual(len(subscriber_subs.incoming_friend_requests), 0)

        self.assertEqual(len(subscribed_subs.subscriptions), 0)
        self.assertEqual(len(subscribed_subs.subscribers), 0)
        self.assertEqual(len(subscribed_subs.friends), 0)
        self.assertEqual(len(subscribed_subs.incoming_friend_requests), 0)

        self.service.subscribe(
            CreateSubscriptionRequest(
                subscriber_id=test_user.pk,
                username=test_user_2.username,
            )
        )

        subscriber_subs = self.service.list_user_subscriptions(test_user.pk)
        subscribed_subs = self.service.list_user_subscriptions(test_user_2.pk)

        self.assertEqual(len(subscriber_subs.subscriptions), 1)
        self.assertEqual(len(subscriber_subs.subscribers), 0)
        self.assertEqual(len(subscriber_subs.friends), 0)
        self.assertEqual(len(subscriber_subs.incoming_friend_requests), 0)

        self.assertEqual(len(subscribed_subs.subscriptions), 0)
        self.assertEqual(len(subscribed_subs.subscribers), 1)
        self.assertEqual(len(subscribed_subs.friends), 0)
        self.assertEqual(len(subscribed_subs.incoming_friend_requests), 1)

    def test_user_can_decline_friend_request(self):
        test_user = User.objects.create_user("username", None, "password")
        test_user_2 = User.objects.create_user("username_2", None, "password")

        self.service.subscribe(
            CreateSubscriptionRequest(
                subscriber_id=test_user.pk,
                username=test_user_2.username,
            )
        )

        subscriber_subs = self.service.list_user_subscriptions(test_user.pk)
        subscribed_subs = self.service.list_user_subscriptions(test_user_2.pk)

        self.assertEqual(len(subscriber_subs.subscriptions), 1)
        self.assertEqual(len(subscriber_subs.subscribers), 0)
        self.assertEqual(len(subscriber_subs.friends), 0)
        self.assertEqual(len(subscriber_subs.incoming_friend_requests), 0)

        self.assertEqual(len(subscribed_subs.subscriptions), 0)
        self.assertEqual(len(subscribed_subs.subscribers), 1)
        self.assertEqual(len(subscribed_subs.friends), 0)
        self.assertEqual(len(subscribed_subs.incoming_friend_requests), 1)

        self.service.mark_subscription_as_viewed(
            recipient_id=test_user_2.pk,
            username=test_user.username,
        )

        subscribed_subs = self.service.list_user_subscriptions(test_user_2.pk)

        self.assertEqual(len(subscriber_subs.subscriptions), 1)
        self.assertEqual(len(subscriber_subs.subscribers), 0)
        self.assertEqual(len(subscriber_subs.friends), 0)
        self.assertEqual(len(subscriber_subs.incoming_friend_requests), 0)

        self.assertEqual(len(subscribed_subs.subscriptions), 0)
        self.assertEqual(len(subscribed_subs.subscribers), 1)
        self.assertEqual(len(subscribed_subs.friends), 0)
        self.assertEqual(len(subscribed_subs.incoming_friend_requests), 0)

    def test_user_can_accept_friend_request(self):
        test_user = User.objects.create_user("username", None, "password")
        test_user_2 = User.objects.create_user("username_2", None, "password")

        self.service.subscribe(
            CreateSubscriptionRequest(
                subscriber_id=test_user.pk,
                username=test_user_2.username,
            )
        )

        subscriber_subs = self.service.list_user_subscriptions(test_user.pk)
        subscribed_subs = self.service.list_user_subscriptions(test_user_2.pk)

        self.assertEqual(len(subscriber_subs.subscriptions), 1)
        self.assertEqual(len(subscriber_subs.subscribers), 0)
        self.assertEqual(len(subscriber_subs.friends), 0)
        self.assertEqual(len(subscriber_subs.incoming_friend_requests), 0)

        self.assertEqual(len(subscribed_subs.subscriptions), 0)
        self.assertEqual(len(subscribed_subs.subscribers), 1)
        self.assertEqual(len(subscribed_subs.friends), 0)
        self.assertEqual(len(subscribed_subs.incoming_friend_requests), 1)

        self.service.subscribe(
            CreateSubscriptionRequest(
                subscriber_id=test_user_2.pk,
                username=test_user.username,
            )
        )

        subscriber_subs = self.service.list_user_subscriptions(test_user.pk)
        subscribed_subs = self.service.list_user_subscriptions(test_user_2.pk)

        self.assertEqual(len(subscriber_subs.subscriptions), 1)
        self.assertEqual(len(subscriber_subs.subscribers), 1)
        self.assertEqual(len(subscriber_subs.friends), 1)
        self.assertEqual(len(subscriber_subs.incoming_friend_requests), 0)

        self.assertEqual(len(subscribed_subs.subscriptions), 1)
        self.assertEqual(len(subscribed_subs.subscribers), 1)
        self.assertEqual(len(subscribed_subs.friends), 1)
        self.assertEqual(len(subscribed_subs.incoming_friend_requests), 0)

    def test_user_cant_subscribe_multiple_times(self):
        test_user = User.objects.create_user("username", None, "password")
        test_user_2 = User.objects.create_user("username_2", None, "password")

        self.service.subscribe(
            CreateSubscriptionRequest(
                subscriber_id=test_user.pk,
                username=test_user_2.username,
            )
        )

        with self.assertRaises(ConflictError):
            self.service.subscribe(
                CreateSubscriptionRequest(
                    subscriber_id=test_user.pk,
                    username=test_user_2.username,
                )
            )

    def test_user_cant_subscribe_nonexistent_user(self):
        test_user = User.objects.create_user("username", None, "password")

        with self.assertRaises(ObjectNotFound):
            self.service.subscribe(
                CreateSubscriptionRequest(
                    subscriber_id=test_user.pk,
                    username="obviously_nonexistent_user",
                )
            )

    def test_user_cant_subscribe_himself(self):
        test_user = User.objects.create_user("username", None, "password")

        with self.assertRaises(ClientError):
            self.service.subscribe(
                CreateSubscriptionRequest(
                    subscriber_id=test_user.pk,
                    username=test_user.username,
                )
            )

    def test_user_cant_decline_already_declined_friend_request(self):
        test_user = User.objects.create_user("username", None, "password")
        test_user_2 = User.objects.create_user("username_2", None, "password")

        self.service.subscribe(
            CreateSubscriptionRequest(
                subscriber_id=test_user.pk,
                username=test_user_2.username,
            )
        )

        self.service.mark_subscription_as_viewed(
            recipient_id=test_user_2.pk,
            username=test_user.username,
        )
        with self.assertRaises(ClientError):
            self.service.mark_subscription_as_viewed(
                recipient_id=test_user_2.pk,
                username=test_user.username,
            )

    def test_user_cant_decline_nonexistent_friend_request(self):
        test_user = User.objects.create_user("username", None, "password")
        test_user_2 = User.objects.create_user("username_2", None, "password")

        with self.assertRaises(ObjectNotFound):
            self.service.mark_subscription_as_viewed(
                recipient_id=test_user_2.pk,
                username=test_user.username,
            )

    def test_user_can_unsubscribe(self):
        test_user = User.objects.create_user("username", None, "password")
        test_user_2 = User.objects.create_user("username_2", None, "password")

        subscriber_subs = self.service.list_user_subscriptions(test_user.pk)
        subscribed_subs = self.service.list_user_subscriptions(test_user_2.pk)

        self.service.subscribe(
            CreateSubscriptionRequest(
                subscriber_id=test_user.pk,
                username=test_user_2.username,
            )
        )

        subscriber_subs = self.service.list_user_subscriptions(test_user.pk)
        subscribed_subs = self.service.list_user_subscriptions(test_user_2.pk)

        self.assertEqual(len(subscriber_subs.subscriptions), 1)
        self.assertEqual(len(subscriber_subs.subscribers), 0)
        self.assertEqual(len(subscriber_subs.friends), 0)
        self.assertEqual(len(subscriber_subs.incoming_friend_requests), 0)

        self.assertEqual(len(subscribed_subs.subscriptions), 0)
        self.assertEqual(len(subscribed_subs.subscribers), 1)
        self.assertEqual(len(subscribed_subs.friends), 0)
        self.assertEqual(len(subscribed_subs.incoming_friend_requests), 1)

        self.service.unsubscribe(
            subscriber_id=test_user.pk,
            username=test_user_2.username,
        )

        subscriber_subs = self.service.list_user_subscriptions(test_user.pk)
        subscribed_subs = self.service.list_user_subscriptions(test_user_2.pk)

        self.assertEqual(len(subscriber_subs.subscriptions), 0)
        self.assertEqual(len(subscriber_subs.subscribers), 0)
        self.assertEqual(len(subscriber_subs.friends), 0)
        self.assertEqual(len(subscriber_subs.incoming_friend_requests), 0)

        self.assertEqual(len(subscribed_subs.subscriptions), 0)
        self.assertEqual(len(subscribed_subs.subscribers), 0)
        self.assertEqual(len(subscribed_subs.friends), 0)
        self.assertEqual(len(subscribed_subs.incoming_friend_requests), 0)

    def test_user_cant_unsubscribe_without_subscription(self):
        test_user = User.objects.create_user("username", None, "password")
        test_user_2 = User.objects.create_user("username_2", None, "password")

        with self.assertRaises(ObjectNotFound):
            self.service.unsubscribe(
                subscriber_id=test_user.pk,
                username=test_user_2.username,
            )
