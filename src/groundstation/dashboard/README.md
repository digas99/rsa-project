# Dashboard

## Environment Variables

Create a `.env` file with the following content:

```bash
TILE_URL=<MAP_TILE_URL>

DBMS = 'mysql'
USER_NAME = 'root'
PASSWORD = 'password'
HOST = 'localhost'
PORT = 3307
DATABASE = 'groundstation'
```

## Running the Dashboard

```bash
docker-compose up --build
```