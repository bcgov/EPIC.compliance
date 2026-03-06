# Compliance-API

A compliance Python flask API application to be used as a template.

## Getting Started

### Development Environment
* Install the following:
    - [Python 2](https://www.python.org/)
    - [Docker](https://www.docker.com/)
    - [Docker-Compose](https://docs.docker.com/compose/install/)
* Install Dependencies
    - Run `make setup` in the root of the project (compliance-api)
* Start the databases
    - Run `docker-compose up` in the root of the project (compliance-api)

## Environment Variables

The development scripts for this application allow customization via an environment file in the root directory called `.env`. See an example of the environment variables that can be overridden in `sample.env`.

## Commands

### Database Data
#### Docker
1. Get the postgres db backup `.dump` from current `dev` in OpenShift.
2. Connect to the docker postgres db
```bash
psql -h localhost -p <DOCKER_POSTGRES_PORT> -U compliance -d compliance-db
```
3. Create the required roles app and doggen:
```sql
CREATE ROLE postgres;
CREATE ROLE docgen;
CREATE ROLE app WITH
  LOGIN
  SUPERUSER
  CREATEDB
  CREATEROLE
  REPLICATION
  BYPASSRLS;
```
4. Restore the db dump
```bash
pg_restore -h localhost -U compliance -p <DOCKER_POSTGRES_PORT> -d compliance-db -v <DEV_DB_BACKUP.DUMP>
```

You should now be able to query the table with the restored data.


### Development

The following commands support various development scenarios and needs.
Before running the following commands run `. venv/bin/activate` to enter into the virtual env.


> `make run`
>
> Runs the python application and runs database migrations.  
Open [http://localhost:5000/api](http://localhost:5000/api) to view it in the browser.<br/>
> The page will reload if you make edits.<br/>
> You will also see any lint errors in the console.

> `make test`
>
> Runs the application unit tests<br>

> `make lint`
>
> Lints the application code.

## Debugging in the Editor

### Visual Studio Code

Ensure the latest version of [VS Code](https://code.visualstudio.com) is installed.

The [`launch.json`](.vscode/launch.json) is already configured with a launch task (Compliance-API Launch) that allows you to launch chrome in a debugging capacity and debug through code within the editor. 