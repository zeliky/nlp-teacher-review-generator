# NLP Teacher Review Generator

The app can run as uvicorn / gunicorn web service
## installation

$ pip install virtualenv

$ virtualenv venv

$ source venv/bin/activate

$ pip install -r requirements.txt




$ pip install -r requirements.txt



## uvicon single thread
$ uvicorn main:app --reload

## gunicorn
$ venv/bin/gunicorn -c gunicorn_conf.py main:app


### service
copy the file etc_systemd_system/nlp_reviews.service to /etc/systemd/system/nlp_reviews.service
(change pathes if needed

$ sudo systemctl daemon-reload


the keys are missing in theis repository - need to set open_ai key in lib/review_generator.py
and need to add the gcloud key to 
.gcloud/nlp-reviews-generator-f5a59c3de91a.json


