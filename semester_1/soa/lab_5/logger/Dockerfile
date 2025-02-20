FROM node:14

WORKDIR /server
COPY package.json ./
RUN npm install
COPY src src

CMD ["node", "src/main.js"]
