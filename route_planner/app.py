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
    if route['distance'] == float('inf'):
        return {"error": "No route found between the selected points."}, 404

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

@app.route("/find_route", methods=["GET", "POST"])
def find_route():
    nodes, edge_weights = load_graph_from_db()
    all_stops = sorted(nodes)

    result = None
    error = None

    if request.method == "POST":
        start = request.form.get("start")
        end = request.form.get("end")

        if start and end:
            if start == end:
                error = "Start and end points cannot be the same."
            else:
                route = get_shortest_route(edge_weights, start, end)
                if route:
                    if route['distance'] == float('inf'):
                        error = "No route found between the selected points."
                    distance_km = round(route['distance'], 2)
                    duration = distance_km * 5  # 5 menit per km
                    duration_hours = round(minutes_to_hours(duration), 2)

                    result = {
                        "distance": f"{distance_km} km",
                        "duration": f"{duration_hours} hours" if duration_hours >= 1 else f"{round(duration, 2)} minutes",
                        "path": route['path']
                    }
                else:
                    error = "No route found between the selected points."
        else:
            error = "Please select both start and end points."

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Route Finder</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
                color: #333;
            }
            h2 {
                color: #2c3e50;
                text-align: center;
                margin-bottom: 30px;
            }
            .form-container {
                background-color: white;
                padding: 25px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }
            .form-row {
                display: flex;
                align-items: center;
                margin-bottom: 15px;
                flex-wrap: wrap;
            }
            label {
                width: 80px;
                font-weight: bold;
                margin-right: 10px;
            }
            select {
                flex: 1;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                margin-right: 15px;
                min-width: 200px;
            }
            button {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 4px;
                cursor: pointer;
                font-weight: bold;
                transition: background-color 0.3s;
            }
            button:hover {
                background-color: #2980b9;
            }
            .result-container {
                background-color: white;
                padding: 25px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin-top: 20px;
            }
            .result-title {
                color: #27ae60;
                margin-top: 0;
                border-bottom: 1px solid #eee;
                padding-bottom: 10px;
            }
            .error {
                color: #e74c3c;
                background-color: #fdecea;
                padding: 15px;
                border-radius: 4px;
                margin-top: 20px;
            }
            ol {
                padding-left: 20px;
            }
            li {
                margin-bottom: 8px;
                padding: 8px;
                background-color: #f8f9fa;
                border-radius: 4px;
            }
            .path-container {
                margin-top: 15px;
                padding: 15px;
                background-color: #f8f9fa;
                border-radius: 4px;
            }
            .stats {
                display: flex;
                gap: 20px;
                margin-bottom: 15px;
            }
            .stat-box {
                flex: 1;
                padding: 10px;
                background-color: #eaf2f8;
                border-radius: 4px;
                text-align: center;
            }
            .stat-value {
                font-size: 1.2em;
                font-weight: bold;
                color: #2c3e50;
            }
            .stepper-container {
                margin-top: 20px;
                background-color: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }

            .stepper {
                display: flex;
                flex-direction: column;
                gap: 8px;
            }

            .step {
                display: flex;
                flex-direction: column;
                position: relative;
            }

            .step-label {
                display: flex;
                align-items: center;
                margin-bottom: 8px;
            }

            .step-circle {
                width: 24px;
                height: 24px;
                border-radius: 50%;
                background-color: #e0e0e0;
                color: rgba(0, 0, 0, 0.6);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
                font-weight: bold;
                margin-right: 12px;
                flex-shrink: 0;
            }

            .step.active .step-circle {
                background-color: #1976d2 !important;
                color: white !important;
            }

            .step-title {
                font-weight: 500;
                color: rgba(0, 0, 0, 0.87);
            }

            .step.active .step-title {
                font-weight: 600 !important;
                color: #1976d2 !important;
            }

            .step-connector {
                position: relative;
                display: block;
                height: 24px;
                width: 2px;
                background-color: #e0e0e0;
                margin-left: 11px;
            }

            .step:last-child .step-connector {
                display: none;
            }

            .step.active ~ .step .step-circle {
                background-color: white;
                border: 2px solid #e0e0e0;
                color: rgba(0, 0, 0, 0.6);
            }

            .step.active ~ .step .step-title {
                color: rgba(0, 0, 0, 0.6);
                font-weight: 400;
            }
        </style>
    </head>
    <body>
        <h2>🚏 Public Transport Route Finder</h2>
        
        <div class="form-container">
            <form method="POST">
                <div class="form-row">
                    <label for="start">From:</label>
                    <select name="start" id="start" required>
                        <option value="" disabled selected>Select starting point</option>
                        {% for stop in stops %}
                        <option value="{{ stop }}" {% if request.method == 'POST' and start == stop %}selected{% endif %}>{{ stop }}</option>
                        {% endfor %}
                    </select>
                </div>
                
                <div class="form-row">
                    <label for="end">To:</label>
                    <select name="end" id="end" required>
                        <option value="" disabled selected>Select destination</option>
                        {% for stop in stops %}
                        <option value="{{ stop }}" {% if request.method == 'POST' and end == stop %}selected{% endif %}>{{ stop }}</option>
                        {% endfor %}
                    </select>
                </div>
                
                <div class="form-row">
                    <button type="submit">Find Best Route</button>
                </div>
            </form>
        </div>

        {% if error %}
            <div class="error">
                <strong>⚠️ Error:</strong> {{ error }}
            </div>
        {% endif %}

        {% if result %}
            <div class="result-container">
            <h3 class="result-title">📍 Route Details</h3>
            
            <div class="stats">
                <div class="stat-box">
                    <div>Distance</div>
                    <div class="stat-value">{{ result.distance }}</div>
                </div>
                <div class="stat-box">
                    <div>Duration</div>
                    <div class="stat-value">{{ result.duration }}</div>
                </div>
            </div>
            
            <p><strong>Route Path:</strong></p>
            <div class="stepper-container">
                <div class="stepper">
                    {% for stop in result.path %}
                    <div class="step {% if loop.first or loop.last %}active{% endif %}">
                        <div class="step-label">
                            <div class="step-circle">{{ loop.index }}</div>
                            <div class="step-title">{{ stop }}</div>
                        </div>
                        <div class="step-content">
                            {% if not loop.last %}
                            <div class="step-actions">
                                <span class="step-connector"></span>
                            </div>
                            {% endif %}
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
        {% endif %}
    </body>
    </html>
    """

    return render_template_string(html, stops=all_stops, result=result, error=error, request=request)

if __name__ == "__main__":
    app.run(debug=True)
