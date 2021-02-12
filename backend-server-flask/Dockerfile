# Use python image
FROM python:3.9.1

# set workdir for local python modules
WORKDIR /home

# create common dir
RUN mkdir /common

# move app files
COPY main.py /home/main.py
COPY db_helper.py /home/db_helper.py
COPY requirements.txt /home/requirements.txt

# install python packages
RUN pip install -r requirements.txt

# expose port to other services only
EXPOSE 5000

# run flask app
CMD ["python", "main.py"]
