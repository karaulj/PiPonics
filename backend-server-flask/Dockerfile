# Use python image
FROM python:3.9.1-slim

# set workdir
WORKDIR /home

# create common dir
RUN mkdir /common

# flask env vars
ENV FLASK_APP=/home/app
ENV FLASK_RUN_HOST=0.0.0.0
#ENV FLASK_ENV=development

# move app files
COPY main.py /home/main.py
COPY entity_utils.py /home/entity_utils.py
COPY requirements.txt /home/requirements.txt
#COPY . /home
#COPY . .

# install python packages
RUN pip install -r requirements.txt

# expose port to other services only
EXPOSE 5000

# run flask app
RUN ls -al /home
CMD ["python", "main.py"]
#CMD ["flask", "run"]
