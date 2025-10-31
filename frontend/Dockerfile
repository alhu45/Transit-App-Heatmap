FROM node:20-slim

WORKDIR /frontend

COPY package*.json ./

RUN npm install 

COPY . .

EXPOSE 6969

CMD ["npm", "run", "dev", "--host", "0.0.0.0", "--port", "6969"]

