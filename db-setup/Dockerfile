# use python image
FROM python:3.9.1-slim

# create dir for sharing sql file
RUN mkdir /sql

# create dir for sharing table info
RUN mkdir /common

# copy only python file
COPY db_setup.py db_setup.py

# run db setup
CMD ["python", "db_setup.py"]
