# Hutbee

<img src="https://user-images.githubusercontent.com/1587877/67436463-bb01f500-f5ee-11e9-88c3-06f1800041b3.png" alt="drawing" width="200" align="right"/>

This project is a solution for remotely controlling and monitoring a hut.

## Deployement

To deploy the frontend and backend, you will need a recent and working version
of `docker` and `docker-compose` installed.

1. Copy the `.env.template` file to `.env` and edit it variable with production
   values:
   
   ```
   cp .env.template .env
   vim .env
   ```
   
2. Create a file `traefik/acme.json` and set the mode to `600`:
   
   ```
   touch traefik/acme.json
   chmod 600 traefik/acme.json
   ```
   
3. Start the service with:

   ```
   docker-compose up -d
   ```
