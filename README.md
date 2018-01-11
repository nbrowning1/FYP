# FYP
Final Year Project for student attendance & feedback functions.
[Build:](https://travis-ci.org/nbrowning1/FYP) ![build status](https://travis-ci.org/nbrowning1/FYP.svg?branch=master)
### Setup Instructions
1. Make sure Python3 and pip are installed: https://www.python.org/downloads/
2. Find a comfy directory, and clone this repository: `git clone https://github.com/nbrowning1/FYP.git`
3. Install Django: `pip install django`
4. Install project dependencies: `pip install -r requirements.txt`
5. Apply migrations: `python manage.py migrate`
6. Create an admin user: `python manage.py createsuperuser`
7. Start the server: `python manage.py runserver`
8. Go to the Django admin panel at http://127.0.0.1:8000/admin in your browser of choice. You can log in here with your newly created admin user and manually add users
9. Go to http://127.0.0.1:8000/tool/ to access the project. If you haven't already, you will have to log in as a valid user

### Testing
##### Running unit tests
Run command: `python manage.py test tool/`