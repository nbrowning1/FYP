# FYP
Final Year Project for student attendance & feedback functions.
[Build:](https://travis-ci.org/nbrowning1/FYP) ![build status](https://travis-ci.org/nbrowning1/FYP.svg?branch=master)
### Setup Instructions
1. Make sure Python3 and pip are installed: https://www.python.org/downloads/ - these commands assume python3 is your default python installation
2. Find a comfy directory, and clone this repository: `git clone https://github.com/nbrowning1/FYP.git`
3. Install Django: `pip install django`
4. Install project dependencies: `pip install -r requirements.txt`
5. Generate field encryption key (set output from below (minus the "b''") as value for FIELD_ENCRYPTION_KEY environment variable (may need to start new terminal session if on Windows)):
    ```
    python manage.py shell
    >>> from cryptography.fernet import Fernet
    >>> print(Fernet.generate_key())
    ```
    or easier, from terminal:
    `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
6. Apply migrations: `python manage.py migrate`
7. Load initial data into the system by using the `init_test_data` command.
  * For minimal data loading, `python manage.py init_test_data --load-minimal`. This will load a single staff user 'admin' and will output a generated password for use
  * For a large batch of initial data, `python manage.py init_test_data --load-all`. This will load a good amount of data for development purposes, with all user passwords set to 'Django123' for easier testing. The data loaded here can be found in the files at tool/test_data/.
8. Start the server: `python manage.py runserver`
9. Go to http://127.0.0.1:8000/tool/ to access the project. If you haven't already, you will have to log in as a valid user

### Testing
##### Running unit tests
Run command: `python manage.py test tool/`
##### Running automated tests
There are a few pre-requisites to run the automated tests, which can be followed at https://pypi.python.org/pypi/selenium
Summarised (assumes Firefox):
1. Download geckodriver from https://github.com/mozilla/geckodriver/releases and add it to PATH (as of writing, v0.20.0 is used)
2. Download Firefox (at time of writing, FF Quantum 59.0.2 is used)
3. Run the tests! `python manage.py test tool.tests_automation`

### Libraries Used
##### Graphos
https://github.com/agiliq/django-graphos
##### xlrd
https://github.com/python-excel/xlrd
##### django-encrypted-model-fields
https://github.com/lanshark/django-encrypted-model-fields
##### selenium webdriver
https://github.com/SeleniumHQ/selenium
