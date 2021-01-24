# use python image
FROM python:3.9.1-slim

# set WORKDIR
WORKDIR /home

# copy app files
COPY ./db-setup.py /home/db-setup.py

# run db setup
CMD ["python", "db-setup.py"]
