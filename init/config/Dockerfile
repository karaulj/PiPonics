# use python image
FROM python:3.9.1-slim

# set workdir to home dir
WORKDIR /home

# create dir for sharing table info
RUN mkdir /common

# copy only python file
COPY description_gen.py /home/description_gen.py

# run python program
CMD ["python", "description_gen.py"]
