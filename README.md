# Hutbee

<img src="images/hutbee.png" alt="drawing" width="200" align="right"/>

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
   
2. Create an `acme.json` file and set the mode to `600`:
   
   ```
   touch acme.json
   chmod 600 acme.json
   ```
   
3. Start the service with:

   ```
   docker-compose up -d
   ```
