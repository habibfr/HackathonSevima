from flask import Flask, request, render_template_string
import csv
import json
from collections import defaultdict
import heapq
import psycopg2

def get_db_connection():
    return psycopg2.connect(
        dbname="route_planner",
        user="sevima",
        password="sevima",
        host="localhost",
        port="5433"
    )

def load_graph_from_db():
    conn = get_db_connection()
    cur = conn.cursor()
    # Ambil semua nodes
    cur.execute("SELECT name FROM nodes")
    nodes = [row[0] for row in cur.fetchall()]
    # Ambil semua edges
    cur.execute("SELECT source, target, weight FROM edges")
    edge_weights = {}
    for source, target, weight in cur.fetchall():
        if source not in edge_weights:
            edge_weights[source] = {}
        edge_weights[source][target] = float(weight)
    cur.close()
    conn.close()
    return nodes, edge_weights

def minutes_to_hours(minutes):
    return minutes / 60

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
        return {"error": "Please provide start and end parameters."}, 400

    _, edge_weights = load_graph_from_db()
    route = get_shortest_route(edge_weights, start, end)
    if not route:
        return {"error": "No route found."}, 404

    route['distance'] = round(route['distance'], 2)
    duration = route['distance'] * 5  # misal 5 menit per kilometer
    print(f"Duration in minutes: {duration}")
    route['duration_hours'] = round(minutes_to_hours(duration), 2)
    converted_route = {
        "distance": f"{route['distance']} km",
        "duration_hours": f"{route['duration_hours']} hours" if route['duration_hours'] > 1 else f"{round(duration, 2)} minutes",
        "path": route['path']
    }

    return converted_route

@app.route("/find_route")
def find_route():
    nodes, _ = load_graph_from_db()
    all_stops = sorted(nodes)

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
