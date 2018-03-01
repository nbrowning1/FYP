# FYP
Final Year Project for student attendance & feedback functions.
[Build:](https://travis-ci.org/nbrowning1/FYP) ![build status](https://travis-ci.org/nbrowning1/FYP.svg?branch=master)
### Setup Instructions
1. Make sure Python3 and pip are installed: https://www.python.org/downloads/
2. Find a comfy directory, and clone this repository: `git clone https://github.com/nbrowning1/FYP.git`
3. Install Django: `pip install django`
4. Install project dependencies: `pip install -r requirements.txt`
5. Generate field encryption key (set output from below (minus the "b''") as value for FIELD_ENCRYPTION_KEY environment variable (may need to start new terminal session if on Windows)):
    ```
    python manage.py shell
    >>> from cryptography.fernet import Fernet
    >>> print(Fernet.generate_key())
    ```
6. Apply migrations: `python manage.py migrate`
7. Create an admin user: `python manage.py createsuperuser`
8. Start the server: `python manage.py runserver`
9. Go to the Django admin panel at http://127.0.0.1:8000/admin in your browser of choice. You can log in here with your newly created admin user and manually add users
10. Go to http://127.0.0.1:8000/tool/ to access the project. If you haven't already, you will have to log in as a valid user

### Testing
##### Running unit tests
Run command: `python manage.py test tool/`

### Libraries Used
##### Graphos
https://github.com/agiliq/django-graphos
##### xlrd
https://github.com/python-excel/xlrd
##### django-encrypted-model-fields
https://github.com/lanshark/django-encrypted-model-fields