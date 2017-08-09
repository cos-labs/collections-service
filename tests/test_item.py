from .test_base import TestBase
from django.urls import reverse
from . import factories
from guardian.shortcuts import assign_perm
from api import models

class ItemTest(TestBase):

    def test_submitter_can_edit_own_item(self):
        self.client.login(username='submitter', password='password123')
        response = self.client.patch(reverse('collection-item-detail', args=[self.collection.id, self.item.id]),
                                    {'title': 'New Title'})
        self.assertEqual(response.status_code, 200)

    def test_cannot_edit_others_item(self):
        self.client.login(username='rando', password='password123')
        response = self.client.patch(reverse('collection-item-detail', args=[self.collection.id, self.item.id]),
                                    {'title': 'New Title'})
        self.assertNotEqual(response.status_code, 200)

    def test_can_post_item_to_collection(self):
        # log in as owner
        self.client.login(username="owner", password="password123")
        # try to post a collection
        response = self.client.post(reverse('collection-item-list', args=[self.collection.id]),
                                    {'title': 't', 'description': 'd', 'source': 'mst3k', 'tags': '',
                                     'category': 'none', 'status': 'pending', 'type': 'preprint'})
        # assert success
        self.assertEqual(response.status_code, 201)

    def test_cannot_post_item_without_being_logged_in(self):
        # log in as owner
        self.client.logout()
        # try to post a collection
        response = self.client.post(reverse('collection-item-list', args=[self.collection.id]),
                                    {'title': 't', 'description': 'd', 'source': 'mst3k', 'tags': '',
                                     'category': 'none', 'status': 'pending', 'type': 'preprint'})
        # assert success
        self.assertEqual(response.status_code, 401)
    #
    def test_non_collection_owner_cannot_change_item_status(self):
        self.client.login(username="rando", password="password123")
        response = self.client.patch(reverse('collection-item-detail', args=[self.collection.id, self.item.id]),
                                    {'status': 'rejected'})
        self.assertNotEqual(response.status_code, 200)

    # item status can be changed by people with the "approve items" permission or owners of collections
    def collection_owner_can_change_item_status(self):
        self.client.login(username='owner', password='password123')
        response = self.client.patch(reverse('collection-item-detail', args=[self.collection.id], item_id=self.item.id),
                                    {'status': 'rejected'})
        self.assertEqual(response.status_code, 200)

    def test_approve_items_permission_holder_can_change_item_status(self):
        permissions_holder = factories.UserFactory(username="jane")
        permissions_holder.save()
        assign_perm("api.approve_items", permissions_holder, self.collection)
        self.client.login(username="jane", password="password123")
        response = self.client.patch(reverse('collection-item-detail', args=[self.collection.id, self.item.id]),
                                     {'status': 'approved'})
        import pprint; pprint.pprint(response.__dict__)
        self.assertEqual(response.status_code, 200)

    # item status is automatically set to approved if the collection has the "allow_all" setting set to true
    def test_allow_all_setting_auto_accepts_new_items(self):
        self.client.login(username="submitter", password="password123")
        c = factories.CollectionFactory(created_by=self.owner, settings={"allow_all": "True", "collection_type": "meeting"})
        # make new collection
        c.save()
        response = self.client.post(reverse('collection-item-list', args=[c.id]),
                                    {'title': 't', 'description': 'd', 'source': 'mst3k', 'tags': '',
                                     'category': 'none', 'status': 'pending', 'type': 'preprint'})
        item_id = int(response.__dict__['data']['id'])
        i = models.Item.objects.get(pk=item_id)
        self.assertEqual(i.status, "approved")

    # owner of a collection can delete items not theirs from collection
    def collection_owners_can_delete_any_item_from_their_collection(self):
        i = factories.ItemFactory(created_by="submitter", collection=self.collection)
        i.save()
        self.client.login(username="owner", password="password123")
        response = self.client.delete(reverse('collection-item-detail', args=[self.collection.id, i.id]))
        self.assertEqual(response.status_code, 204)

    def test_cannot_delete_others_item(self):
        self.client.login(username="rando", password="password123")
        response = self.client.delete(reverse('collection-item-detail', args=[self.collection.id, self.item.id]))
        self.assertNotEqual(response.status_code, 204)

    def test_can_delete_own_item(self):
        self.client.login(username="submitter", password="password123")
        response = self.client.delete(reverse('collection-item-detail', args=[self.collection.id, self.item.id]))
        self.assertEqual(response.status_code, 204)
