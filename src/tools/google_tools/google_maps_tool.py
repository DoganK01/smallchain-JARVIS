import requests
from pydantic import Field, ConfigDict
from typing import ClassVar
import geocoder

from src.tools.base import AsyncBaseTool
from src.settings import settings

import sys
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton
from PyQt6.QtWebEngineWidgets import QWebEngineView



class GoogleMapsTool(AsyncBaseTool):
    """
    Get the roadmap, route for destination point from Google Maps. Inform the user by showing the route
    """
    model_config = ConfigDict(json_schema_extra={"name": "google_maps"})

    GOOGLE_MAPS_API_KEY: ClassVar[str] = settings.GOOGLE_MAPS_API_KEY
    GOOGLE_MAPS_API_URL: ClassVar[str] = 'https://maps.googleapis.com/maps/api/directions/json'
    GOOGLE_GEOCODING_API_URL: ClassVar[str] = 'https://maps.googleapis.com/maps/api/geocode/json'
    destination: str = Field(description="The location which the weather information will be gathered about")

    def get_location(self):
        """Get the current location using geocoder (simulated here)."""
        g = geocoder.ip('me')  # This uses IP-based geolocation
        return g.latlng

    def get_coordinates(self, address: str):
        """Convert the address to coordinates using Google Geocoding API."""
        params = {
            'address': address,
            'key': self.GOOGLE_MAPS_API_KEY
        }
        response = requests.get(self.GOOGLE_GEOCODING_API_URL, params=params)
        data = response.json()
        if data['status'] == 'OK':
            lat = data['results'][0]['geometry']['location']['lat']
            lng = data['results'][0]['geometry']['location']['lng']
            return lat, lng
        return None, None

    def get_route(self, origin_lat: float, origin_lng: float, destination_lat: float, destination_lng: float):
        """Get the route from current location to the destination."""
        route_params = {
            'origin': f'{origin_lat},{origin_lng}',
            'destination': f'{destination_lat},{destination_lng}',
            'key': self.GOOGLE_MAPS_API_KEY
        }
        route_response = requests.get(self.GOOGLE_MAPS_API_URL, params=route_params)
        route_data = route_response.json()

        if route_data['status'] == 'OK':
            route_polyline = route_data['routes'][0]['overview_polyline']['points']
            return route_polyline
        return None

    async def _arun(self):
        app = QApplication(sys.argv)
        google_tool = GoogleMapsTool(name="Google Tool", destination=self.destination)
        pyqt_tool = PyQt6UI(google_tool)
        pyqt_tool.show()
        app.exec()
        return




class PyQt6UI:
    def __init__(self, google_tool: GoogleMapsTool):
        self.google_tool = google_tool
        self.current_location = None

        # Set up the main window
        self.window = QMainWindow()
        self.window.setWindowTitle("Bus Driver Navigation Tool")
        self.window.setGeometry(100, 100, 1000, 700)

        # Set up the layout
        self.layout = QVBoxLayout()

        # Input field for destination
        self.destination_input = QLineEdit(self.window)
        self.destination_input.setPlaceholderText("Enter your destination")
        self.layout.addWidget(self.destination_input)

        # Button to get the route
        self.get_route_button = QPushButton("Get Route", self.window)
        self.get_route_button.clicked.connect(self.get_route)
        self.layout.addWidget(self.get_route_button)

        # Web view to display the map
        self.map_view = QWebEngineView(self.window)
        self.layout.addWidget(self.map_view)

        # Create a central widget
        central_widget = QWidget(self.window)
        central_widget.setLayout(self.layout)
        self.window.setCentralWidget(central_widget)

        # Timer to update user location (simulating real-time location change)
        self.timer = QTimer(self.window)
        self.timer.timeout.connect(self.update_location)
        self.timer.start(5000)  # Update every 5 seconds

    def get_route(self):
        """Get the route from current location to the destination."""
        destination = self.google_tool.destination
        if not destination:
            return

        # Get the coordinates of the destination
        target_lat, target_lng = self.google_tool.get_coordinates(destination)
        if not target_lat or not target_lng:
            print("Error: Could not find destination.")
            return

        # Get the current location of the user
        
        self.current_location = self.google_tool.get_location()

        if not self.current_location:
            print("Error: Could not get current location.")
            return

        current_lat, current_lng = self.current_location

        # Get the route data
        route_polyline = self.google_tool.get_route(current_lat, current_lng, target_lat, target_lng)
        if route_polyline:
            self.display_map(route_polyline, current_lat, current_lng, target_lat, target_lng)

    def display_map(self, polyline, start_lat, start_lng, end_lat, end_lng):
        """Display the route on a map using Google Maps UI in a WebView."""
        map_url = f"https://www.google.com/maps/embed/v1/directions?key={self.google_tool.GOOGLE_MAPS_API_KEY}&origin={start_lat},{start_lng}&destination={end_lat},{end_lng}&mode=driving"

        html = f"""
        <html>
            <head>
                <title>Google Maps Route</title>
                <style>
                    body, html {{ margin: 0; padding: 0; height: 100%; }}
                    iframe {{ border: 0; width: 100%; height: 100%; }}
                </style>
            </head>
            <body>
                <iframe src="{map_url}"></iframe>
            </body>
        </html>
        """
        self.map_view.setHtml(html)

    def update_location(self):
        """Simulate location updates for the user (e.g., from GPS)."""
        self.current_location = self.google_tool.get_location()
        if self.current_location:
            print(f"Current Location Updated: {self.current_location}")

    def show(self):
        self.window.show()


# Main execution
if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Create the Google-related tool instance
    google_tool = GoogleMapsTool(name="Google Tool")

    # Create and show the PyQt6-related window
    pyqt_tool = PyQt6UI(google_tool)
    pyqt_tool.show()

    #sys.exit(app.exec())
    app.exec()
