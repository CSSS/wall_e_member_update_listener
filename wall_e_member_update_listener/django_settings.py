import os


ENVIRONMENT = os.environ['basic_config__ENVIRONMENT']

POSTGRES_SQL = os.environ['database_config__TYPE'] == 'postgreSQL'
if POSTGRES_SQL:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ['database_config__WALL_E_DB_DBNAME'],
            'USER': os.environ['database_config__WALL_E_DB_USER'],
            'PASSWORD': os.environ['database_config__WALL_E_DB_PASSWORD']
        }
    }

    if os.environ['basic_config__DOCKERIZED'] == '1':
        DATABASES['default']['HOST'] = (
            f"{os.environ['basic_config__COMPOSE_PROJECT_NAME']}_wall_e_db"
        )
    else:
        DATABASES['default']['PORT'] = os.environ['database_config__DB_PORT']
        DATABASES['default']['HOST'] = os.environ['database_config__HOST']

else:
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }


INSTALLED_APPS = (
    'wall_e_models',
)

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

TIME_ZONE = 'Canada/Pacific'

USE_TZ = True

# Write a random secret key here
SECRET_KEY = '4e&6aw+(5&cg^_!05r(&7_#dghg_pdgopq(yk)xa^bog7j)^*j'
