# COSC 310 Project

## To run locally
```
cd ./backend
```
Run the following commands inside the "backend/" folder
### Install Dependency in virtual environment and activate
1. Create virtual environment
```
python3 -m venv ".venv"
```
You can use other valid folder name besides ".venv", but here we use ".venv"

2. Activate the virtual environment

Mac
```
source "./.venv/bin/activate"
```
Windows
```
.\.venv\bin\Activate.ps1
```

If you want to deactivate the virtual environment later
```
deactivate
```

3. Install dependencies inside virtual environment
```
pip install -r "./requirements.txt"
```
### Run backend
```
fastapi dev app/main.py
```

### Run tests
```
python -m pytest testing-documents/
```

## To Run in Docker
The following command is at the project root folder.
### Build
```
docker compose up --build
```
### Run tests
```
docker compose exec backend python -m pytest testing-documents/
```