#!/usr/bin/env bash
set -o errexit

pip install -r clinical_differential_support/requirements.txt
python clinical_differential_support/manage.py collectstatic --no-input
python clinical_differential_support/manage.py migrate --run-syncdb
python clinical_differential_support/manage.py createcachetable
python clinical_differential_support/manage.py loaddata headache_mvp chest_pain_mvp abdominal_pain_mvp dyspnea_mvp
