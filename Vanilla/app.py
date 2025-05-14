from flask import Flask, request, jsonify
import  sqlite3
import subprocess
import base64

app = Flask(__name__)

# Global DB connection
db_connection = None
#generate tdx quote
def generate_tdx_quote():
    # Use the trustauthority-cli to collect TDX quote
    subprocess.run(["/usr/bin/trustauthority-cli", "collect-quote", "--tdx", "--out", "quote.bin"], check=True)
    with open("quote.bin", "rb") as f:
        quote = f.read()
    return base64.b64encode(quote).decode()

# Function to connect to the vanilla DB
def connect_to_db(db_path):
    conn = sqlite3.connect(db_path,check_same_thread = False)
    cursor = conn.cursor()
   # cursor.execute(f"PRAGMA key = '{encryption_key}';")
    return conn

# Insert a new health record
@app.route('/insert_record', methods=['POST'])
def insert_record():
    data = request.get_json()
    cursor = db_connection.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO records (user_id, timestamp, heart_rate, blood_pressure, notes) VALUES (?, ?, ?, ?, ?)",
        (data['user_id'], data['timestamp'], data['heart_rate'], data['blood_pressure'], data['notes'])
    )
    db_connection.commit()
    return jsonify({"message": "Record inserted successfully in vanilla db"})

# Get the latest health record for a user
@app.route('/get_latest', methods=['GET'])
def get_latest():
    user_id = request.args.get('user_id')
    cursor = db_connection.cursor()
    cursor.execute(
        "SELECT * FROM records WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1",
        (user_id,)
    )
    record = cursor.fetchone()
    if record:
        return jsonify({
            "user_id": record[0],
            "timestamp": record[1],
            "heart_rate": record[2],
            "blood_pressure": record[3],
            "notes": record[4]
        })
    else:
        return jsonify({"message": "No record found."}), 404

if __name__ == "__main__":
    # Hardcoded key for now (later replace this with attestation-based fetching)
    #encryption_key = 'your-strong-test-key-here'

    # Connect to the encrypted database
    db_connection = connect_to_db('fithealth.db')

    # Run HTTPS server
    app.run(host="0.0.0.0", port=5000, ssl_context=('cert.pem', 'key.pem'))

