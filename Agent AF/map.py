import folium

# Create a map centered at a coordinate
m = folium.Map(location=[23.249099, 72.579446], zoom_start=15)

# Add a marker
folium.Marker([23.235491, 72.579252]).add_to(m)
folium.Marker([23.253045, 72.584939]).add_to(m)

# Add a circle (radius in meters)
folium.Circle(
    location=[23.249099, 72.579446],
    radius=1000,
    color='blue',
    fill=True,
).add_to(m)

folium.Circle(
    location=[23.250344, 72.595505],
    radius=1000,
    color='purple',
    fill=True,
).add_to(m)

folium.Circle(
    location=[23.236352, 72.574773],
    radius=1000,
    color='pink',
    fill=True,
).add_to(m)

folium.Circle(
    location=[23.260947, 72.606442],
    radius=1000,
    color='green',
    fill=True,
).add_to(m)

folium.Circle(
    location=[23.241357, 72.593231],
    radius=1000,
    color='red',
    fill=True,
).add_to(m)

m.save("map.html")
