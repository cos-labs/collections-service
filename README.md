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

    $ git clone git@github.com:cos-labs/collections.git
    $ cd collections/service

#### Install Dependencies:
Setting up a virtual environment for Python 3 is recommended.

    $ pyenv virtualenv 3.6.0 osf-collections
    $ pip install -r requirements.txt
    $ cd ../client
    $ yarn install
    $ bower install


## Running

#### Start Postgres:

Using a package manager like brew is recommended.

    $ brew services postgres start
    $ cd {collections}/
    $ ./manage.py makemigrations
    $ ./manage.py migrate

#### Run the service

    $ python manage.py runserver

Visit the api at `http://localhost:8000/api/` or admin panel at `http://localhost:8000/admin/`.

#### Run the client

    $ ember serve

Visit your app at [http://localhost:4200](http://localhost:4200).


## Configuration

Set up the backend to use either staging or prod. Do this in the sessions for both the client and the service. `export BACKEND=prod` or `export BACKEND=stage`

#### Create a developer app at [https://staging.osf.io/settings/applications/](https://staging.osf.io/settings/applications/) with the following settings:
* Project homepage URL: http://localhost:8000/
* Callback URL: http://localhost:8000/accounts/osf/login/callback/

### create a django super user:
` $ python manage.py createsuperuser`

#### Create a new Site with domain name: http://localhost:8000/admin/sites/ in the django 

* Note: The site id must match the `SITE_ID` variable defined in  `SITE_ID` should be set to the site id in `collections/service/service/settings/local.py`
* The SITE_ID can be found in the URL 
* you may have to define SITE_ID in the local.py file 

#### Create a SocialAccount in the django admin panel:
* Set provider to "Open Science Framework"
* Set the client id and secret key to the ones defined in your developer app
* Select http://localhost:8000/ as the site

### Running Tests

* `ember test`
* `ember test --server`

### Building

* `ember build` (development)
* `ember build --environment production` (production)

### Deploying

`export BACKEND=prod`

## Further Reading / Useful Links

* [ember.js](http://emberjs.com/)
* [ember-cli](http://ember-cli.com/)
* Development Browser Extensions
  * [ember inspector for chrome](https://chrome.google.com/webstore/detail/ember-inspector/bmdblncegkenkacieihfhpjfppoconhi)
  * [ember inspector for firefox](https://addons.mozilla.org/en-US/firefox/addon/ember-inspector/)

