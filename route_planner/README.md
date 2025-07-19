# Route Planner

This project is a bus route planner for Rio de Janeiro. It allows users to find optimal routes between bus stops using a graph-based approach.

## Project Structure

- `app.py`: Main application file for running the route planner.
- `bus_graph.json`: JSON file containing the bus stop graph data.
- `convert_csv/`: Contains scripts and data for converting bus stop data from CSV to JSON.
- `insert_db/`: Contains scripts for inserting bus graph data into a database.

## Technologies Used

- **Python 3**: Main programming language.
- **Flask** (if used in `app.py`): For building the web API (check `app.py` for details).
- **JSON**: For storing bus graph data.
- **CSV**: For raw bus stop data.

## How to Run

1. **Install dependencies** (if any, e.g., Flask):
   ```sh
   pip install flask
   ```
2. **Dataset bus stop**
   [Kaggle](https://www.kaggle.com/datasets/igorbalteiro/bus-stops-in-rio-de-janeiro/data).
