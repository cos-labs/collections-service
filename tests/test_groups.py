from django.urls import reverse
from .test_base import TestBase
from .factories import GroupFactory


class TestCollectionGroup(TestBase):

    def setUp(self):
        TestBase.setUp(self)
        self.collection_group_list_url = reverse('collection-group-list', args=[self.collection.id])
        self.group_payload = {'title': 'Group', 'description': 'Group description'}
        self.group = GroupFactory(created_by=self.owner, collection=self.collection)
        self.group.save()
        self.collection_group_detail_url = reverse('collection-group-detail', args=[self.collection.id, self.group.id])

    def test_collection_creator_can_view_groups(self):
        self.client.login(username="owner", password="password123")
        response = self.client.get(self.collection_group_list_url)
        self.assertEqual(response.status_code, 200)

    def test_logged_in_users_can_view_groups(self):
        self.client.login(username="random", password="password123")
        response = self.client.get(self.collection_group_list_url)
        self.assertEqual(response.status_code, 200)

    def test_logged_out_user_can_view_groups(self):
        self.client.logout()
        response = self.client.get(self.collection_group_list_url)
        self.assertEqual(response.status_code, 200)

    def test_collection_creator_can_create_groups(self):
        self.client.login(username="owner", password="password123")
        response = self.client.post(self.collection_group_list_url, self.group_payload)
        self.assertEqual(response.status_code, 201)

    # TODO: Only collection owners should be able to add groups
    def test_user_cannot_create_groups(self):
        self.client.login(username="random", password="password123")
        response = self.client.post(self.collection_group_list_url, self.group_payload)
        self.assertEqual(response.status_code, 403)

    def test_logged_out_user_cannot_create_group(self):
        self.client.logout()
        response = self.client.post(self.collection_group_list_url, self.group_payload)
        self.assertEqual(response.status_code, 401)

    def test_group_creator_can_view_group_detail(self):
        self.client.login(username="owner", password="password123")
        response = self.client.get(self.collection_group_detail_url)
        self.assertEqual(response.status_code, 200)

    def test_logged_in_users_can_view_group_detail(self):
        self.client.login(username="random", password="password123")
        response = self.client.get(self.collection_group_detail_url)
        self.assertEqual(response.status_code, 200)

    def test_logged_out_users_can_view_group_detail(self):
        self.client.logout()
        response = self.client.get(self.collection_group_detail_url)
        self.assertEqual(response.status_code, 200)

    def test_group_creator_can_update_group(self):
        self.client.login(username="owner", password="password123")
        response = self.client.patch(self.collection_group_detail_url, {'title': 'New title'})
        self.assertEqual(response.status_code, 200)

    # TODO: Only collection owners should be able to update the groups
    def test_non_group_creator_cannot_update_group(self):
        self.client.login(username="random", password="password123")
        response = self.client.patch(self.collection_group_detail_url, {'title': 'New title'})
        self.assertEqual(response.status_code, 403)

    def test_logged_out_user_cannot_update_group(self):
        self.client.logout()
        response = self.client.patch(self.collection_group_detail_url, {'title': 'New title'})
        self.assertEqual(response.status_code, 401)

    def test_group_creator_can_delete_group(self):
        self.client.login(username="owner", password="password123")
        response = self.client.delete(self.collection_group_detail_url)
        self.assertEqual(response.status_code, 204)

    # TODO: Only group creator/collection owner should be able to delete group
    def test_non_group_creator_cannot_delete_group(self):
        self.client.login(username="random", password="password123")
        response = self.client.delete(self.collection_group_detail_url)
        self.assertEqual(response.status_code, 204)

    def test_logged_out_user_cannot_delete_group(self):
        self.client.logout()
        response = self.client.delete(self.collection_group_detail_url)
        self.assertEqual(response.status_code, 401)
