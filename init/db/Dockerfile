# use python image
FROM python:3.9.1-slim

# set workdir to home dir
WORKDIR /home

# create dir for sharing sql file
RUN mkdir /sql

# copy only python file
COPY db_setup.py /home/db_setup.py

# run python program
CMD ["python", "db_setup.py"]
