@echo off
set /p GOOGLE_MAPS_API_KEY=Enter your Google Maps API Key: 
setx GOOGLE_MAPS_API_KEY %GOOGLE_MAPS_API_KEY%
echo API Key set successfully!
