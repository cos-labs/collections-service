from .test_base import TestBase
from django.urls import reverse


class CollectionTest(TestBase):
    def test_logged_in_user_can_post_collection(self):
        self.client.login(username="owner", password="password123")
        # try to post a collection
        response = self.client.post(reverse('collection-list'),
                                    {'title': 't', 'description': 'd', 'source': 'mst3k', 'tags': ''})
        self.assertEqual(response.status_code, 201)

    def test_user_can_edit_own_collection(self):
        self.client.login(username="owner", password="password123")
        # attempt to patch collection
        response = self.client.patch(reverse('collection-detail', args=[self.collection.id]),
                                     {'title': 'New Title'})
        self.assertEqual(response.status_code, 200)

    def test_user_cannot_edit_others_collections(self):
        self.client.login(username="random", password="password123")
        # attempt to patch owner's collection
        response = self.client.patch(reverse('collection-detail', args=[self.collection.id]),
                                     {'title': 'New Title 2'})
        self.assertEqual(response.status_code, 403)

    def test_user_can_delete_own_collection(self):
        self.client.login(username="owner", password="password123")
        # attempt to delete own collection
        response = self.client.delete(reverse('collection-detail', args=[self.collection.id]))
        self.assertEqual(response.status_code, 204)

    def test_logged_out_cannot_post_collection(self):
        self.client.logout()
        response = self.client.post(reverse('collection-list'),
                                    {'title': 't', 'description': 'd', 'source': 'mst3k', 'tags': ''})
        self.assertEqual(response.status_code, 401)

    def test_cannot_delete_other_users_collection(self):
        self.client.login(username="random", password="password123")
        response = self.client.delete(reverse('collection-detail', args=[self.collection.id]))
        self.assertEqual(response.status_code, 403)

    def test_logged_out_user_cannot_delete_collection(self):
        self.client.logout()
        response = self.client.delete(reverse('collection-detail', args=[self.collection.id]))
        self.assertNotEqual(response.status_code, 204)
