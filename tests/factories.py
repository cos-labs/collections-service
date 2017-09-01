import factory
from api import models
import pytz
import random
from . import resources

# TODO: move to sublcassing factory.django.DjangoModelFactory instead of factory.Factory


class UserFactory(factory.Factory):
    class Meta:
        model = models.User

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    username = factory.LazyAttribute(
        lambda u: (str(u.first_name)[0] + str(u.last_name)).lower()
    )
    password = factory.PostGenerationMethodCall('set_password', 'password123')


class ItemFactory(factory.Factory):
    class Meta:
        model = models.Item

    title = factory.Faker('text', max_nb_chars=75)
    description = factory.Faker('text', max_nb_chars=500)
    status = 'approved'
    source_id = 'fxsa9'


class GroupFactory(factory.Factory):
    class Meta:
        model = models.Group

    title = factory.Faker('text', max_nb_chars=25)
    description = factory.Faker('text', max_nb_chars=125)


class CollectionFactory(factory.Factory):
    class Meta:
        model = models.Collection

    title = factory.Faker('text', max_nb_chars=25)
    description = factory.Faker('text', max_nb_chars=125)
    tags = "foo, bar, baz"
    settings = {}
    submission_settings = {}
    collection_type = "Meeting"


class MeetingFactory(factory.Factory):
    class Meta:
        model = models.Meeting

    address = factory.Faker('address')
    location = factory.Faker('city')
    title = factory.Faker('text', max_nb_chars=25)
    description = factory.Faker('text', max_nb_chars=125)
    tags = random.choice(["foo", "bar", "baz"])
    start_date = factory.Faker('date_time_between', start_date="-1w", end_date="-1d", tzinfo=pytz.timezone('US/Eastern'))
    end_date = factory.Faker('date_time_between', start_date="+1d", end_date="+1w", tzinfo=pytz.timezone('US/Eastern'))
    settings = resources.meetings_json
    submission_settings = {}
