FROM python:3.9.13-alpine

WORKDIR /src

COPY wall_e_member_update_listener/django_manage.py django_manage.py
COPY wall_e_member_update_listener/django_settings.py django_settings.py
COPY wall_e_member_update_listener/__init__.py __init__.py
COPY wall_e_member_update_listener/main.py main.py
COPY wall_e_member_update_listener/setup_logger.py setup_logger.py
COPY wall_e_member_update_listener/requirements.txt requirements.txt
COPY CI/wait-for-postgres.sh wait-for-postgres.sh
COPY CI/startup.sh startup.sh

RUN apk add postgresql

CMD ["./wait-for-postgres.sh", "./startup.sh"]
#CMD ["sh"]