from api import models
from django.test import Client
from django.contrib.auth import login
from django.test import TestCase, Client
from rest_framework.test import force_authenticate, APIRequestFactory, APIClient
from django.urls import reverse
from .factories import UserFactory, ItemFactory, GroupFactory, CollectionFactory, MeetingFactory


class SimpleTest(TestCase):
    meetings_url = '/collection/1'

    def setUp(self):
        # The person
        owner = models.User()
        owner.first_name = "Alice"
        owner.last_name = "Owner"
        owner.username = "owner"
        owner.set_password("password123")
        owner.save()
        self.owner = owner

        c = models.Collection()
        c.created_by = owner
        c.settings = {}
        c.title = "My Cool Collection"
        c.description = "So cool you could call it... a coollection."
        c.save()
        self.collection = c

        rando = models.User()
        rando.username = "rando"
        rando.first_name = "Beth"
        rando.last_name = "Rando"
        rando.set_password("password123")
        rando.save()
        self.rando = rando

        submitter = models.User()
        submitter.username = "submitter"
        submitter.first_name = "Claire"
        submitter.last_name = "Submitter"
        submitter.set_password("password123")
        submitter.save()
        self.submitter = submitter

        # with factory_boy, you can create a single item (you must specify its foreign keys)
        i = ItemFactory(collection=c, created_by=submitter)
        i.save()

        # you can also create a batch of items, so long as you still specify foreign keys
        items = ItemFactory.build_batch(100, collection=c, created_by=submitter)
        for i in items:
            i.save()

        m = MeetingFactory(created_by=owner)
        m.save()

        items = ItemFactory.build_batch(100, collection=m, created_by=submitter)
        for i in items:
            i.save()

        self.factory = APIRequestFactory()

    def test_cant_post_collection_unless_logged_in(self):
        client = APIClient()
        client.login(username="owner", password="password123")
        response = client.post(reverse('collection-list'),
                                {'title': 't', 'description': 'd', 'source': 'mst3k', 'tags': ''})
        self.assertEqual(response.status_code, 201)
        client.logout()
        response = client.post(reverse('collection-list'),
                                {'title': 't', 'description': 'd', 'source': 'mst3k', 'tags': ''})
        self.assertEqual(response.status_code, 401)
