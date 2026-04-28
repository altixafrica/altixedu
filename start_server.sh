#!/bin/bash
cd ~/Documents/altixedu-backend/altixedu
python manage.py migrate --noinput
python manage.py seed_billing_catalog
python manage.py runserver 0.0.0.0:8000
