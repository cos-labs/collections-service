from .test_base import TestBase
from django.urls import reverse


class CollectionTest(TestBase):
    def test_logged_in_user_can_post_collection(self):
        # log in as owner
        self.client.login(username="owner", password="password123")
        # try to post a collection
        response = self.client.post(reverse('collection-list'),
                                    {'title': 't', 'description': 'd', 'source': 'mst3k', 'tags': ''})
        # assert success
        self.assertEqual(response.status_code, 201)

    def test_user_can_edit_own_collection(self):
        # log in as owner
        self.client.login(username="owner", password="password123")
        # attempt to patch collection
        response = self.client.patch(reverse('collection-detail', args=[self.collection.id]),
                                     {'title': 'New Title'})
        # assert success
        self.assertEqual(response.status_code, 200)

    def test_user_cannot_edit_others_collections(self):
        # log in as random user
        self.client.login(username="random", password="password123")
        # attempt to patch owner's collection
        response = self.client.patch(reverse('collection-detail', args=[self.collection.id]),
                                     {'title': 'New Title 2'})
        # assert failure
        self.assertNotEqual(response.status_code, 200)

    def test_user_can_delete_own_collection(self):
        # log in as collection's owner
        self.client.login(username="owner", password="password123")
        # attempt to delete owner's collection
        response = self.client.delete(reverse('collection-detail', args=[self.collection.id]))
        # assert success
        self.assertEqual(response.status_code, 204)

    def test_logged_out_cannot_post_collection(self):
        self.client.logout()
        response = self.client.post(reverse('collection-list'),
                                    {'title': 't', 'description': 'd', 'source': 'mst3k', 'tags': ''})
        self.assertEqual(response.status_code, 401)

    def test_cannot_delete_other_users_collection(self):
        self.client.login(username="random", password="password123")
        response = self.client.delete(reverse('collection-detail', args=[self.collection.id]))
        self.assertNotEqual(response.status_code, 204)

        self.client.logout()
        response = self.client.delete(reverse('collection-detail', args=[self.collection.id]))
        self.assertNotEqual(response.status_code, 204)
