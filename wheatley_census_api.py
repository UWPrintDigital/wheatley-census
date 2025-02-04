from flask import Flask, jsonify, request
import psycopg2

app = Flask(__name__)

DB_SETTINGS = {
    "dbname": "wheatley_census",
    "user": "your_username",
    "password": "your_password",
    "host": "localhost",
    "port": "5432"
}

def connect_db():
    return psycopg2.connect(**DB_SETTINGS)

@app.route('/editions', methods=['GET'])
def get_editions():
    start_year = request.args.get('start_year', type=int)
    end_year = request.args.get('end_year', type=int)
    city = request.args.get('city', type=str)
    
    conn = connect_db()
    cursor = conn.cursor()
    
    sql = """
    SELECT e.id, e.publication_year, e.publisher, e.city, COUNT(c.id) AS copies_available, e.title
    FROM editions e
    LEFT JOIN copies c ON e.id = c.edition_id
    WHERE (%s IS NULL OR e.publication_year >= %s) 
    AND (%s IS NULL OR e.publication_year <= %s)
    AND (%s IS NULL OR e.city ILIKE %s)
    GROUP BY e.id, e.publication_year, e.publisher, e.city, e.title
    ORDER BY e.publication_year ASC;
    """
    
    cursor.execute(sql, (start_year, start_year, end_year, end_year, city, f'%{city}%' if city else None))
    editions = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify(editions)

if __name__ == '__main__':
    app.run(debug=True)
