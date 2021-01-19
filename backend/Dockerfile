# Use python image
FROM python:3.9.1-alpine

# set workdir
WORKDIR /flask-app

# flask env vars
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# move app files
COPY . /flask-app

# install python packages
RUN pip install -r requirements.txt

# expose port to other services only
EXPOSE 5000

# start flask
CMD ["flask", "run"]
