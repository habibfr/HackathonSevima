import csv
from collections import defaultdict
from math import radians, sin, cos, sqrt, atan2

# from haversine import haversine, Unit

def haversine(coord1, coord2):
    """
    Calculate the great-circle distance between two points on the Earth specified in decimal degrees.
    
    Args:
        coord1 (tuple): Latitude and longitude of the first point (lat, lon).
        coord2 (tuple): Latitude and longitude of the second point (lat, lon).
        
    Returns:
        float: Distance in kilometers.
    """
    # Convert latitude and longitude from degrees to radians
    lat1, lon1 = map(radians, coord1)
    lat2, lon2 = map(radians, coord2)

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    # Radius of Earth in kilometers (mean radius)
    r = 6371.0
    return r * c

def convert_csv_to_graph(csv_file_path):
    """
    Convert CSV data of bus stops into a graph structure.
    
    Args:
        csv_file_path (str): Path to the CSV file containing bus stop data.
        
    Returns:
        dict: A dictionary representing the graph with nodes and edges.
    """
    # Ganti dengan path file CSV-mu
    # 1. Load CSV
    bus_data = []
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
      reader = csv.DictReader(csvfile, delimiter='|')
      # print("CSV columns:", reader.fieldnames)
      for row in reader:
          if row['stop_latitude'] and row['stop_longitude']:  # pastikan data lokasi tidak null
              bus_data.append(row)

    # 2. Sort data per line_number, direction, dan urutan kemunculan stop (sementara pakai stop_name)
    bus_data = sorted(bus_data, key=lambda x: (x['line_number'], x['direction'], x['stop_name']))

    # 3. Bangun graph
    graph = defaultdict(dict)
    nodes = set()
    edges = []

    for i in range(len(bus_data) - 1):
        current = bus_data[i]
        nxt = bus_data[i + 1]

        # Cek apakah dalam jalur dan arah yang sama
        if current['line_number'] == nxt['line_number'] and current['direction'] == nxt['direction']:
            a_stop = current['stop_name']
            b_stop = nxt['stop_name']
            a_coord = (float(current['stop_latitude']), float(current['stop_longitude']))
            b_coord = (float(nxt['stop_latitude']), float(nxt['stop_longitude']))
            distance = round(haversine(a_coord, b_coord), 4)  # dibulatkan 4 desimal

            graph[a_stop][b_stop] = distance
            edges.append((a_stop, b_stop))
            nodes.update([a_stop, b_stop])

        # 4. Buat output final
        output = {
            "nodes": sorted(list(nodes)),
            "edges": edges,
            "edge_weights": dict(graph)
        }

        # 5. Simpan ke file JSON (opsional)
        import json
        with open("bus_graph.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        # 6. (Opsional) Print sebagian isi
        print(json.dumps(output, indent=2, ensure_ascii=False))

# run the function to convert CSV to graph
# convert_csv_to_graph(CSV_FILE_PATH)
CSV_FILE_PATH = 'bus_stops_rio_de_janeiro.csv'
convert_csv_to_graph(CSV_FILE_PATH)
