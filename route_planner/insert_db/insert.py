import json
import psycopg2

# Koneksi ke database
conn = psycopg2.connect("dbname=route_planner user=sevima password=sevima host=localhost port=5433")
cur = conn.cursor()

# Baca file JSON
with open("bus_graph.json", "r", encoding="utf-8") as f:
    bus_graph = json.load(f)

nodes = bus_graph["nodes"]
# edges = bus_graph["edges"]
edge_weights = bus_graph["edge_weights"]

# # Buat tabel
# cur.execute("""
#     CREATE TABLE IF NOT EXISTS nodes (
#         id SERIAL PRIMARY KEY,
#         name TEXT UNIQUE NOT NULL
#     );
# """)

# cur.execute("""
#     CREATE TABLE IF NOT EXISTS edges (
#         source TEXT NOT NULL,
#         target TEXT NOT NULL,
#         weight DOUBLE PRECISION NOT NULL,
#         FOREIGN KEY (source) REFERENCES nodes(name),
#         FOREIGN KEY (target) REFERENCES nodes(name)
#     );
# """)

# conn.commit()
# Insert nodes
for name in nodes:
    print(f"Inserting node: {name}")
    cur.execute("INSERT INTO nodes (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (name,))

# Insert edges
for source, targets in edge_weights.items():
    for target, weight in targets.items():
        cur.execute(
            "INSERT INTO edges (source, target, weight) VALUES (%s, %s, %s)",
            (source, target, weight)
        )

conn.commit()
cur.close()
conn.close()
