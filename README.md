# Hutbee

<img src="https://user-images.githubusercontent.com/1587877/67436463-bb01f500-f5ee-11e9-88c3-06f1800041b3.png" alt="drawing" width="200" style="float:right"/>

This project is a solution for remotely monitoring and controlling a mountain
hut. The main goals are to monitor inside and outside temperatures, CO₂ levels,
and the weather (with a webcam), as well as to control heating to preheat the
hut before going there.

## Deployment

To deploy the frontend and backend, you will need a recent and working version
of `docker` and `docker-compose` installed.

1. Copy the `.env.template` file to `.env` and edit it variable with **production**
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

## Development setup

In order to work on this project on your local machine, you will need a working
installation of `python>=3.7` and recent version of `npm/node.js`.

1. Copy the `.env.template` file to `.env` and edit it variable with **development**
   values:
   
   ```
   cp .env.template .env
   vim .env
   ```
   
2. Open a terminal and run the frontend:

   ```
   cd frontend
   npm run serve
   ```

   Note: The frontend supports hot-reloads, no need to restart after saving.
   
3. Open a terminal and run the backend:

   ```
   cd backend
   pip install -e .
   python -m hutbee
   ```

   Note: The backend supports hot-reloads, no need to restart after saving.
