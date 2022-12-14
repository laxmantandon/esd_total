# SETUP ESD
# Start python
cd ./resources/backend/
1. py -m pip install -r requirements.txt

# Start test server
1. py .\app.py

# Start electron
1.  npm install
1.  npm run dev

## Build python
1. cd ./resources/backend/
2. Run py -m PyInstaller .\app.py

# Build Electron
1. Run npm run setup (In the root folder of the project)
2. Access executable in release folder
