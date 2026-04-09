Step-by-Step Deployment and Handover Guide:

Installation Instruction:
Complete, unambiguous, step-by-step setup procedures for running the system from scratch using Docker.
Prerequisites: Install Docker, Git, and Python.
Open your terminal.
Login to your Github account on your local machine.
Clone the repository by running: git clone https://github.com/KeirPar/CrewSquad_310.git
Navigate into the project directory: “cd CrewSquad_310”
Build the Docker containers: “docker compose up --build”
Open the website at http://localhost:3000/

To Run Automated Tests: 
While the containers are running, execute the following command in a new terminal window:
“docker compose exec backend python -m pytest testing-documents/”

Dependencies: 
A comprehensive list of all required external tools and services. No external APIs are required to run this application; all payment and notification logic is simulated internally.


Tools:
Python 3.10 (Download at: https://www.python.org/downloads/)
Docker Desktop (Download at: https://www.docker.com/)


Python Libraries: 
annotated-doc==0.0.4, annotated-types==0.7.0, anyio==4.12.1, certifi==2026.2.25, charset-normalizer==3.4.4, click==8.3.1, colorama==0.4.6, dnspython==2.8.0, email-validator==2.3.0, fastapi==0.135.1, fastapi-cli==0.0.24, fastapi-cloud-cli==0.14.0, fastar==0.8.0, h11==0.16.0, httpcore==1.0.9, httptools==0.7.1, httpx==0.28.1, idna==3.11, Jinja2==3.1.6, markdown-it-py==4.0.0, MarkupSafe==3.0.3, mdurl==0.1.2, pydantic==2.12.5, pydantic-extra-types==2.11.0, pydantic-settings==2.13.1, pydantic_core==2.41.5, Pygments==2.19.2, python-dotenv==1.2.2, python-multipart==0.0.22, PyYAML==6.0.3, requests==2.32.5, rich==14.3.3, rich-toolkit==0.19.7, rignore==0.7.6, sentry-sdk==2.54.0, shellingham==1.5.4, starlette==0.52.1, typer==0.24.1, typing-inspection==0.4.2, typing_extensions==4.15.0, urllib3==2.6.3, uvicorn==0.41.0, watchfiles==1.1.1, websockets==16.0, pytest, bcrypt, PyJWT, pytest-cov
(To install Python libraries/libraries, run “pip install -r “./requirements.txt””, you don’t have to manually install the Python libraries/libraries if you are using Docker)

Credentials & Ongoing Maintenance: 
Detailed instructions are provided for ongoing system maintenance, including account credentials.
Admin Account: 
Use this account to access the Owner/Admin dashboard for testing restaurant creation and queue management:
Email: admin@example.com
Password: dOyOUkNOWiMaNaDMIN? (Note: Password includes the question mark at the end)

Data Management Procedures: All system data (users, restaurants, orders, reviews) is persistently stored in local JSON files within the backend/app/data/ directory. To perform routine maintenance or reset the system to a clean state, these JSON files can be manually cleared or restored from default templates. Since payment and notification gateways are simulated internally, there is no configuration needed for external APIs.
