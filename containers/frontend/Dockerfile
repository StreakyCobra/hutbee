FROM node:13 as build

COPY ./frontend /app
WORKDIR /app
RUN npm install && npm run build

FROM nginx:1

COPY containers/frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
