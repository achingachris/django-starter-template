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