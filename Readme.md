## To activate this environment, use

    $ conda activate django-docker

## To deactivate an active environment, use

    $ conda deactivate


## Python Docker images:

https://hub.docker.com/_/python/


## Docker composer file options:

https://docs.docker.com/reference/compose-file/

## Docker Commands

Starting Containers:

docker-compose up --build  
docker compose up -d 


Closing Containers:

docker-compose down  

View Containers:
docker image ls 

Ensure the default Django tables were created:
docker-compose exec db psql --username=hello_django --dbname=hello_django_dev

\l
\q

check that the volume was created as well by running:


echo -e "POSTGRES_USER=hello_django\nPOSTGRES_PASSWORD=hello_django\nPOSTGRES_DB=hello_django_prod" >> .env.prod.db

Docker for Production:
docker-compose -f docker-compose.prod.yml up -d --build

If the container fails to start, check for errors in the logs via docker-compose -f docker-compose.prod.yml logs -f.

Run production script
chmod +x app/entrypoint.prod.sh

Docker Poduction:

    $ docker-compose -f docker-compose.prod.yml down -v
    $ docker-compose -f docker-compose.prod.yml up -d --build
    $ docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput

Spin down the development containers:

$ docker-compose down -v


$ docker-compose -f docker-compose.prod.yml up -d --build
$ docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput
$ docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input --clear


bring containers down:
docker-compose -f docker-compose.prod.yml down -v