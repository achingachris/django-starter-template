conda create -n django-starter python=3.12

conda env export > environment.yml


Now, you can create and apply the migrations, which will create a new database that uses the custom user model. Before we do that, let's look at what the migration will actually look like without creating the migration file, with the --dry-run flag:

./manage.py makemigrations --dry-run --verbosity 3


git reset --soft HEAD~1