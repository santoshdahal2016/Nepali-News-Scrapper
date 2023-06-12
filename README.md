# Django DRF API template

#### API base project made with Django Rest Framework .


## Project setup

Use [git](https://git-scm.com/) to clone the project:

```bash
git clone https://github.com/Joabsonlg/django-api-template
```
Enter the project:
```bash
cd django-drf-api-template
```
Create a virtual environment. (replace 'X' with your python version):
```bash
pythonX -m venv venv
```


Enter the virtual environment:
```bash
source venv/bin/activate
```

Add the environment variables: (copy '.env.example' to  '.env' file and change the value)


Install the dependencies:
```bash
pip install -r requirements.txt
```

Create a superuser
```bash
python manage.py createsuperuser
```


## Usage

Run the API
```bash
python manage.py runserver
```


##Folder Structure 
```
|-- app 
|    |-- api : contanins all the viewsets : (only use APIVIEW Set)
|    |-- migrations
|    |-- models
|    |-- selectors : contain code for retriving information form database
|    |-- services : contain code for saving information in database
|    |-- templates
|    |-- tests : contains all tests
|    |-- utils
|    |-- admin.py
|    |-- apps.py
|    |-- urls.py 
|
|-- config
|    |-- settings
|    |-- asgi.py
|    |-- urls.py
|    |-- wsgi.py
```


## Styleguide


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.
