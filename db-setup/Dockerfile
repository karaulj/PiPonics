# use python image
FROM python:3.9.1-slim

# create dir for sharing sql file
RUN mkdir /sql

# create dir for holding logs
RUN mkdir /logs

# set WORKDIR
#WORKDIR /home

# copy only python file
COPY db-setup.py /home/db-setup.py

# run db setup
CMD ["python", "/home/db-setup.py"]
