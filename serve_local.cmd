@echo off
REM Serve the built app with no AI Studio and no node: plain static files on port 8080.
cd /d "C:\Users\Gershon\Desktop\WORKSPACE\Ai-Brain-Map"
echo Hi5 Mechanical Knowledge Graph  ->  http://localhost:8080
"C:\Users\Gershon\Desktop\WORKSPACE\.venv\Scripts\python.exe" -m http.server 8080 --directory dist
