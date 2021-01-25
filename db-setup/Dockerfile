# use python image
FROM python:3.9.1-slim

# create dir for sharing sql file
RUN mkdir /sql

# set WORKDIR
WORKDIR /home

# copy only python file
COPY db-setup.py /home/db-setup.py
#COPY . /home

RUN ls -al /home

# run python program
#RUN python db-setup.py

# copy generated sql file from container to host
#COPY /home/db-init-test.sql ./sql/db-init-test.sql

#RUN ls -al /sql
# run db setup
CMD ["python", "db-setup.py"]
