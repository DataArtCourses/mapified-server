from app.profiles.urls import routes as profile_routes
from app.pins.urls import routes as pins_routes


routes = [
    * profile_routes,
    * pins_routes
]
