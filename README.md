# Compliance Setup Instructions

This document outlines the setup instructions for both the backend and front-end components of the project. Ensure you follow the steps in sequence for a smooth setup.

## Backend Setup in WSL

### 1. Install Python 3.10
Ensure Python 3.10 is installed in your WSL environment. Download it from the [official Python website](https://www.python.org/downloads/release/python-3124/).

### 2. Set Up PYTHONPATH
Add the following line to your `.bashrc` or `.zshrc` file to set the `PYTHONPATH` environment variable:
* `export PYTHONPATH="/path/to/compliance-api:${PYTHONPATH}"`

### 3. Configure Environment Variables
Create a `.env` file in your compliance-api with the necessary configurations. Reference sample.env to see what variables you need to configure

### 4. Start Docker Compose
In a separate terminal, launch Docker Compose to set up your containers:
* `docker-compose up`

### 5. Run Setup
Navigate to your project directory and run the setup command to prepare your development environment:
* `make setup`

### 5. Run Server
Once the setup is completed use make run to start the server:
* `make run`


## Backend Setup on Windows

## Step 1: Download the Python 3.10 Version

1. Visit the official Python website: [Python Downloads](https://www.python.org/downloads/)
2. Download and install the latest version of Python for your operating system.


## Step 4: Set Environment Variables

1. Set the `FLASK_APP` and `FLASK_ENV` environment variables:
    - `set FLASK_APP=app.py`
    - `set FLASK_ENV=development`

2. Configure `PYTHONPATH` to your project's folder location up to `compliance-api/src`:
    - `set PYTHONPATH=path\to\compliance-api\src &&    PYTHONPATH=path\to\compliance-api`

## Step 2: Start Docker

1. Open a terminal.
2. Navigate to the `compliance-api` directory:
    * `cd compliance-api`

3. Run the following command to start the services using Docker Compose:
    * `docker-compose up`

## Step 3: Set Up `compliance-api`

1. Open a separate terminal.

2. Navigate to the directory:
    `cd compliance-api`

3. Create a virtual environment. Refer to the official Python documentation on how to create a virtual environment: [Python venv](https://docs.python.org/3/library/venv.html).
    * `python -m venv venv`

4. Activate the virtual environment:
    * `source venv\Scripts\activate`

5. Install the required Python packages from both `dev.txt` and `prod.txt` requirements files:
    * `python -m pip install -r ./requirements/dev.txt`
    * `python -m pip install -r ./requirements/prod.txt`

6. Run your Flask app using the Flask CLI:
    - `python -m flask run -p 5000`

## Front End Setup

### 1. Navigate to Front End Directory
Change to the front-end directory:
* `cd compliance-web`

### 2. Requirements
- [Node.js](https://nodejs.org/en/) 24

### 3. Install Dependencies
Install necessary npm packages:
* `npm install`

### 4. Run Development Server
Launch the development server:
* `npm run dev`

# Helm
In openshift, you should have namespaces as such:
* xxxx-tools
* xxxx-dev
* xxxx-test
* xxxx-prod

After the oc login which can be gotten from the openshift command line tool page
* `install command https://helm.sh/docs/helm/helm_install/`

## Patroni
You can reuse a patroni chart like https://github.com/bcgov/nr-patroni-chart
follow instructions on the link

- if the resource quota was exceeded you can change the values in values.yaml, you can always do that locally and install like this as well `$ helm install -f myvalues.yaml myredis ./redis`


## API

can reuse the charts here https://github.com/bcgov/EPIC.submit/tree/develop/deployment/charts the api and the api-bc

### *api.yml
Install it in the xxxx-dev with name xxx-api. Upon success you will have the DeploymentConfig, Route, Service, Secrets and ConfigMap

### *bc.yml
Install it in a xxxx-tools with bane yourApp-api. Upon success you will have BuildConfig and ImageStream.

The ImageStream is used to host the docker image in openshift registry and point to different build tags: latest, dev, etc.

The Deployment config will reference these builds using the tags

The BuildConfig is run to manually build a docker image and push it to the openshift registry

### Role Binding
You need to give the service account "default" image pulling permissions. Create an image pulling role and bind it to the default service account

### Network Policy

The tools namespace will be common to dev, test and prod and you will need to allow for connections between namespaces via Network policy:

You need a policy to allow pods in xxxx-dev to connect with each other
    spec:

    podSelector: {}

    ingress:

    - from:

    - namespaceSelector:

    matchLabels:

    environment: dev

    name: c8b80a

    policyTypes:

    - Ingress


# Github Workflows
you can find a working example here: https://github.com/bcgov/EPIC.compliance/tree/main/.github/workflows

- create a github-action service account openshift in the tools namespace and bind to it image puller and image pusher roles
- Add the following secrets in the repo settings under repository secrets: OPENSHIFT_IMAGE_REGISTRY (the public image repository, ignore the path just the base  url), OPENSHIFT_LOGIN_REGISTRY (you can pull this from the same place you get your oc login command, OPENSHIFT_REPOSITORY, OPENSHIFT_SA_NAME (github_action), OPENSHIFT_SA_TOKEN(github-action token, find it in secrets)

# Codecov
if you intend to use codecov in your CI workflows, you have to go to the bcgov codecov account and register your app there, get a token and add it as a repo secret with name CODECOV_TOKEN

### JEST
example work yml for jest:
```
  testing:
    needs: setup-job
    runs-on: ubuntu-20.04

    steps:
      - uses: actions/checkout@v3

      - name: Use Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v1
        with:
          node-version: ${{ matrix.node-version }}

      - name: Install dependencies
        run: |
          npm install
        env:
          FONTAWESOME_PACKAGE_TOKEN: ${{ secrets.FONTAWESOME_PACKAGE_TOKEN }}

      - name: Test with jest
        id: test
        run: |
          npm test -- --coverage

      # Set codecov branch name with prefix if pull request
      - name: Sets Codecov branch name
        run: |
          echo "CODECOV_BRANCH=PR_${{github.head_ref}}" >> $GITHUB_ENV
        if: github.event_name == 'pull_request'

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          flags: app-web
          name: codecov-app-web
          fail_ci_if_error: true
          verbose: true
          override_branch: ${{env.CODECOV_BRANCH}}
          token: ${{ secrets.CODECOV_TOKEN }}
```
### Cypress
you have to add a some dev dependencies and set them up in the app and then you can use the below example yml for cypress:
```
      testing:
        needs: setup-job
        runs-on: ubuntu-20.04

        steps:
          - uses: actions/checkout@v2

          - name: Use Node.js ${{ matrix.node-version }}
            uses: actions/setup-node@v1
            with:
              node-version: ${{ matrix.node-version }}

          - name: Install dependencies
            run: |
              npm install

          - name: Test with Cypress
            id: test
            run: |
              npx cypress run --component --headed --browser chrome

          - name: Sets Codecov branch name
            run: |
              echo "CODECOV_BRANCH=PR_${{ github.head_ref }}" >> $GITHUB_ENV
            if: github.event_name == 'pull_request'

          - name: Upload coverage to Codecov
            uses: codecov/codecov-action@v4
            with:
              flags: app-web
              name: codecov-app-web
              fail_ci_if_error: true
              verbose: true
              override_branch: ${{ env.CODECOV_BRANCH }}
              token: ${{ secrets.CODECOV_TOKEN }}
              directory: ./app-web/coverage
```

## Application Overview
![alt text](https://github.com/bcgov/EPIC.compliance/blob/develop/docs/application_overview.png?raw=true)
**EPIC.compliance** is a comprehensive digital platform developed to support Compliance and Enforcement (C&E) officers at the Environmental Assessment Office (EAO). It replaces manual processes—currently managed through Excel spreadsheets, emails, and MS Teams boards—with a centralized, reliable, and efficient solution for managing compliance data.

With EPIC.compliance, C&E officers can:

* Input and manage data related to complaints and inspections in a structured and secure manner.

* Automatically generate case file numbers, enabling seamless linkage between related inspections and enforcement actions.

* Maintain a continuous case history, providing visibility into previous actions and enabling easier handovers and follow-ups by other officers.

* Generate official reports (e.g., inspection records, orders, warning letters) with system-populated fields, ensuring consistency and reducing administrative overhead.

By digitizing and streamlining C&E workflows, EPIC.compliance enhances data integrity, improves collaboration, and enables more effective enforcement across projects regulated by the EAO.

### 👤 Compliance Users
* **Role** : End users (typically C&E officers at the Environmental Assessment Office).
* **Action** : Log in using IDIR credentials (a common BC Government identity management service).
### 🔐 IDIR Login via Keycloak
* **Function** : Handles authentication using Keycloak as the identity provider.

* **Mechanism** : Users are authenticated via IDIR and receive a JSON Web Token (JWT) for secure access.
### 🖥️ Epic.Compliance Web
* **Type** : Frontend application.

* **Built With** :

  - **React** (JS library for building user interfaces)

  - **TypeScript**  (adds type safety to JavaScript)

  - **Material UI** (for consistent, accessible UI components)

* **Purpose** : Provides a user interface for Compliance officers to:

  - Enter and manage data for complaints, inspections, orders, and warning letters.

  - View case file history and generate reports.
### ⚙️ Compliance API

* **Backend Framework** : Flask (Python-based web framework).

* **Responsibilities** :

  - Handles requests from the frontend.

  - Processes business logic and validation.

  - Manages authentication/authorization via Keycloak JWT.

  - Communicates with the database and external services.
### 🗄️ Database (PostgreSQL)
* **Role** : Stores structured compliance data.

* **Technology** : PostgreSQL (relational database).

* **Usage** :

  - Stores data about case files, inspections, orders, warning letters, etc.

  - Accessed by the Compliance API and Epic.Cron job.
### ⏱️ Epic.Cron

* **Type** : Background job or scheduled task.

* **Purpose** : Periodically synchronizes project names and other metadata from Epic.Track to the Compliance Database.

* **Ensures** : Up-to-date and consistent reference data for inspections and case file linkage.
### 📦 EXTERNAL Services
These are separate systems that **EPIC.compliance** interacts with:

**📁 Epic.Track – Project Information**

* **Purpose** : Source of truth for project data.

* **Use** : Compliance API queries this system to fetch project-related metadata (e.g., project name, type, status).

**🧾 Epic.DocGen – Document Generation**

* **Function** : Generates formatted documents (e.g., warning letters, orders) using templates and populated data.

* **Integration** : Triggered by the Compliance API when an enforcement document needs to be created.
**📂 Epic.Documents – Document Processing**
* **Role** : Processes documents (e.g., stamping, validation, transformation).

* **Use** : Acts as a middle layer between document generation and storage.

**☁️ NRS (Object Storage)**

* **Full Form**: Networked Resource Storage.

* **Use** : Stores finalized documents securely (e.g., PDFs of inspection reports or letters).

* **Accessed by** : Epic.Documents and the Compliance API.
