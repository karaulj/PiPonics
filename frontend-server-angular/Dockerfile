# base image
FROM node:14.15.4

# set workdir
WORKDIR /app
COPY package.json /app/package.json

# install node.js depedencies
RUN npm install
RUN npm install bootstrap
RUN npm install chart.js
RUN npm install @types/chart.js
RUN npm install -g @angular/cli

# move app files to workdir
COPY . /app

# run app
CMD ng serve --host 0.0.0.0
