# Django Starter (with Docker)

A starter template for Django projects, configured with Docker and Nginx for production.

## Conda Environment

### Activating the Environment

To activate the environment, run:

```shell
conda activate django-docker
```

### Deactivating the Environment

To deactivate the environment, run:

```shell
conda deactivate
```

## Docker Setup

### Development Containers

To start development containers, use:

```shell
docker-compose up --build
```

Alternatively:

```shell
docker compose up -d
```

To stop and remove development containers, use:

```shell
docker-compose down
```

To view active Docker images, run:

```shell
docker image ls
```

### Database Verification

To ensure default Django tables are created, run:

```shell
docker-compose exec db psql --username=hello_django --dbname=hello_django_dev
```

To list tables:

```shell
\l
```

To exit the shell:

```shell
\q
```

## Production Setup

### Starting Production Containers

To start production containers, use:

```shell
docker-compose -f docker-compose.prod.yml up -d --build
```

If the container fails to start, check the logs with:

```shell
docker-compose -f docker-compose.prod.yml logs -f
```

### Running Production Scripts

Make the production entrypoint script executable:

```shell
chmod +x app/entrypoint.prod.sh
```

### Managing Production Containers

To manage production containers, use:

```shell
docker-compose -f docker-compose.prod.yml down -v
docker-compose -f docker-compose.prod.yml up -d --build
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input --clear
```

### Stopping Development Containers

To stop and remove development containers, use:

```shell
docker-compose down -v
```

### Stopping Production Containers

To stop and remove production containers, use:

```shell
docker-compose -f docker-compose.prod.yml down -v
```

## Docker Resources

**Python Image Used:**

[Python Docker Hub](https://hub.docker.com/_/python/)

```txt
python:3.12.5-bullseye
```

**Docker Compose File Options:**

[Docker Compose Documentation](https://docs.docker.com/reference/compose-file/)
