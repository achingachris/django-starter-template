conda create -n django-starter python=3.12

conda env export > environment.yml


Now, you can create and apply the migrations, which will create a new database that uses the custom user model. Before we do that, let's look at what the migration will actually look like without creating the migration file, with the --dry-run flag:

./manage.py makemigrations --dry-run --verbosity 3


git reset --soft HEAD~1

Auth Views:

accounts/login/ [name='login']
accounts/logout/ [name='logout']
accounts/password_change/ [name='password_change']
accounts/password_change/done/ [name='password_change_done']
accounts/password_reset/ [name='password_reset']
accounts/password_reset/done/ [name='password_reset_done']
accounts/reset/<uidb64>/<token>/ [name='password_reset_confirm']
accounts/reset/done/ [name='password_reset_complete']



templates/registration/password_reset_confirm.html
templates/registration/password_reset_form.html
templates/registration/password_reset_done.html



Second, you may want to comment out the database flush and migrate commands in the entrypoint.sh script so they don't run on every container start or re-start:

```shell
#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# python manage.py flush --no-input
# python manage.py migrate

exec "$@"
```

Instead, you can run them manually, after the containers spin up, like so:

```shell
$ docker-compose exec web python manage.py flush --no-input
$ docker-compose exec web python manage.py migrate
```
