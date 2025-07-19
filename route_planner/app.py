from flask import Flask, request, render_template_string
import csv
import json
from collections import defaultdict
import heapq

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, World!"

def get_shortest_route(edge_weights, start, end):
    queue = [(0, start, [start])]
    
    # Dictionary untuk menyimpan jarak minimum ke tiap node
    visited = {}

    while queue:
        current_dist, current_node, path = heapq.heappop(queue)

        # Jika node sudah dikunjungi dengan jarak lebih kecil, skip
        if current_node in visited and visited[current_node] <= current_dist:
            continue

        # Tandai node sudah dikunjungi
        visited[current_node] = current_dist

        # Kalau sudah sampai tujuan, return hasil
        if current_node == end:
            return {
                'distance': round(current_dist, 4),
                'path': path
            }

        # Tetangga node sekarang
        neighbors = edge_weights.get(current_node, {})
        for neighbor, weight in neighbors.items():
            if neighbor not in visited:
                heapq.heappush(queue, (
                    current_dist + weight,
                    neighbor,
                    path + [neighbor]
                ))
    return {
        'distance': float('inf'),
        'path': []
    }


@app.route("/route")
def route():
    start = request.args.get("start")
    end = request.args.get("end")
    if not start or not end:
        return "Please provide start and end parameters.", 400
    with open("bus_graph.json", "r", encoding="utf-8") as f:
        bus_graph = json.load(f)

    route = get_shortest_route(bus_graph['edge_weights'], start, end)
    if not route:
        return "No route found.", 404

    # a float with 2 decimal places
    route['distance'] = round(route['distance'], 2)
    duration = route['distance'] * 5  # misal 5 menit per kilometer
    route['duration_minutes'] = duration
    converted_route = {
        "distance": f"{route['distance']} km",
        "duration_minutes": f"{route['duration_minutes']} minutes",
        "path": route['path']
    }

    return converted_route


@app.route("/find_route")
def find_route():
    with open("bus_graph.json", "r", encoding="utf-8") as f:
        bus_graph = json.load(f)

    all_stops = sorted({stop for stop in bus_graph["nodes"]})

    html = """
    <form action="/route" method="get">
        <label>Start:</label>
        <select name="start">
            {% for stop in stops %}
            <option value="{{ stop }}">{{ stop }}</option>
            {% endfor %}
        </select>
        <label>End:</label>
        <select name="end">
            {% for stop in stops %}
            <option value="{{ stop }}">{{ stop }}</option>
            {% endfor %}
        </select>
        <button type="submit">Get Shortest Route</button>
    </form>
    """
    return render_template_string(html, stops=all_stops)

if __name__ == "__main__":
    app.run(debug=True)
