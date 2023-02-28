from multiprocessing import cpu_count



# Socket Path

bind = 'unix:/var/projects/nlp/gunicorn.sock'



# Worker Options

workers = cpu_count() + 1

worker_class = 'uvicorn.workers.UvicornWorker'



# Logging Options

loglevel = 'debug'

accesslog = '/var/projects/nlp/logs/access.log'

errorlog =  '/var/projects/nlp/logs/error.log'

