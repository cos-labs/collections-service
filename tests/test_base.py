from api import models


class TestPermissionsClass:
    def setup(self):
        # make a collection owner
        # make a rando user
        # make an item submitter
        owner = models.User()
        owner.first_name = "Alice"
        owner.last_name = "Owner"
        owner.username = "owner"
        owner.set_password("password123")
        owner.save()

        rando = models.User()
        rando.username = "rando"
        rando.first_name = "Beth"
        rando.last_name = "Rando"
        rando.set_password("password123")
        rando.save()

        submitter = models.User()
        submitter.username = "submitter"
        submitter.first_name = "Claire"
        submitter.last_name = "Submitter"
        submitter.set_password("password123")
        submitter.save()

    def test_owner_can_edit_project_name(self):
        assert True
