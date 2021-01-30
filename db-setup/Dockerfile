# use python image
FROM python:3.9.1-slim

# create dir for sharing sql file
RUN mkdir /sql

# copy only python file
COPY db-setup.py db-setup.py

# run db setup
CMD ["python", "db-setup.py"]
