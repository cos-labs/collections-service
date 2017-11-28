# <img src="https://cdn.cos.io/media/images/cos_center_logo_small.original.png" alt="alt text" width="22px" height="22px">  Collections

[![Join the chat at https://gitter.im/cos-labs/collections](https://badges.gitter.im/cos-labs/collections.svg)](https://gitter.im/cos-labs/collections?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Collections is a prototype project at the Center for Open Science. This project is experimental, scope, technologies, code and functionality may change. This app has two main parts. The service stores data about the collection, and the client lets users interact with their collections.


## Prerequisites

You will need the following things properly installed on your computer.

* [Git](http://git-scm.com/)
* [Python3](http://python.org/)
* [Postgresql](http://postgresql.org/)
* [Node.js](http://nodejs.org/) (with NPM)
* [Bower](http://bower.io/)
* [Ember CLI](http://ember-cli.com/)
* [PhantomJS](http://phantomjs.org/)
* [Yarn](https://yarnpkg.com/lang/en/docs/install/)



## Installation

#### Get the code:

    $ git clone git@github.com:cos-labs/collections-service.git
    $ cd collections-service

#### Install Dependencies:

Setting up a virtual environment for Python 3 is recommended.

    $ pyenv virtualenv 3.6.0 osf-collections
    $ pip install -r requirements.txt

#### Set Up Postgres:

##### OSX

    $ brew install postgres
    $ createdb
    $ brew services postgres start

#### Set Up Redis

OSF Collections uses Redis as a database for celery tasks, as well as a cache.

##### OSX

    $ brew install redis
    $ brew services start redis

#### Set Up Tika

Tika is an apache product that allows for scraping text from a very large
variety of file formats. Collections uses it to provide full-text search
on documents that are created in collections.

##### OSX

    $ brew install tika

Note this may require installing xcode command line tools.

Now that tika is installed, create a launch daemon to make starting and
stopping tika more simple, and load it in so launchctl knows about it.

    $ cp <collections-service>/apache.tika.plist /Library/LaunchDaemons/apache.tika.plist
    $ launchctl load /Library/LaunchDaemons/apache.tika.plist

Now tika can be started and stopped using

    $ launchctl start apache.tika
    $ launchctl stop apache.tika

#### Set Up Email

##### Sendgrid

Simply export the Sendgrid token in the environment so Django can pick it up

    export SENDGRID_API_KEY='SG.the_key_given_to_you_by_sendgrid'

## Running

    $ cd {collections}/

#### Set up `local.py` settings

```
SA_CLIENT_ID = "55b229c83f6946fe8c16b86217781028"
SA_CLIENT_SECRET = "70z9QBGWmYlFoXUr6HYZoi3QPr4ksafSEbJvTyNr"
SA_APPLICATION_NAME = "Collections"
SA_SITE_ID = 1
SA_PROVIDER_NAME = "osf"

SU_USERNAME = "admin"
SU_PASSWORD = "password"
SU_EMAIL = ""
```

#### Run migrations, create SocialApp login rewuirements

    $ ./manage.py migrate
    $ ./reset

#### Run the service

    $ python manage.py runserver

Visit the api at `http://localhost:8000/api/` or admin panel at `http://localhost:8000/admin/`.

#### Run the client

Follow the set-up instructions in the README for https://github.com/cos-labs/collections.

Visit your app at [http://localhost:4200](http://localhost:4200).

## Configuration

Set up the backend to use either staging or prod. Do this in the sessions for both the client and the service. `export BACKEND=prod` or `export BACKEND=stage`

#### Create a developer app at [https://staging.osf.io/settings/applications/](https://staging.osf.io/settings/applications/) with the following settings:
* Project homepage URL: http://localhost:8000/
* Callback URL: http://localhost:8000/accounts/osf/login/callback/

### Create a django super user:
` $ python manage.py createsuperuser`

#### Create a new Site with domain name: http://localhost:8000/ in the django admin panel:

* Note: The site id must match the `SITE_ID` variable defined in  `SITE_ID` should be set to the site id in `collections-service/service/settings/local.py`
* The SITE_ID can be found in the URL 
* You may have to define SITE_ID in the local.py file 

#### Create a SocialApplication in the django admin panel:
* Set provider to "Open Science Framework"
* Set the client id and secret key to the ones defined in your developer app
* Select http://localhost:8000/ as the site

## Build the search index
* `python manage.py rebuild_index`
* This needs to be done on first run / population and then on a semi-regular basis when running the API to index new content from the API.

## Populating the database
* Before moving forward, make sure you've logged into the test server using your OSF staging credentials.
* To populate the database with users, meetings, collections, and items, run `$ python populate.py` from the project root.

### Running Tests

* `python manage.py test`
