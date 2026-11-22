TECH4LIFE - UPDATED PROJECT

LOCAL RUN
1. Install Python 3.10 or newer.
2. Open terminal in this folder.
3. Run: pip install -r requirements.txt
4. Run: python app.py
5. Open http://127.0.0.1:5000

RENDER
1. Upload this folder to a GitHub repository.
2. In Render, create a new Web Service and connect the repository.
3. Root Directory: Tech4Life (if repository contains this folder).
4. Build command: pip install -r requirements.txt
5. Start command: python app.py
6. Deploy.

NEW FEATURES
- /hospital-tracking uses browser location and OpenStreetMap / Overpass hospital listings.
- SOS asks for location permission, records coordinates in the SOS table and displays a map link.
- Admin can review recorded requests at /admin/sos after signing in.

IMPORTANT SOS LIMITATION
This version records SOS requests in the Tech4Life database and makes them visible in the admin SOS console. It DOES NOT automatically send notifications to nearby hospitals. Automatic delivery requires verified hospital contact details and an agreed channel/API (for example, a hospital dispatch endpoint, SMS gateway or email service), plus configuration credentials. Do not present this demo as a guaranteed emergency dispatch service. For immediate emergency assistance in India, call 112.

LOCATION / MAP NOTES
Browser geolocation generally requires HTTPS (Render provides HTTPS) and user permission. Hospital listings come from OpenStreetMap contributors and may be incomplete or outdated. Verify hospital details directly before relying on them.
