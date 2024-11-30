from flask import Flask, request, jsonify, render_template_string
import sqlite3
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# SQLite database setup
DB_FILE = 'text_data.db'


def init_db():
    """Initialize the database and create the texts table if it doesn't exist."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS texts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT
            )
        ''')
        conn.commit()


@app.route('/')
def index():
    """Serve the main HTML page."""
    try:
        # Open index.html with UTF-8 encoding
        with open('index.html', 'r', encoding='utf-8') as file:
            html_content = file.read()  # Read the content of index.html

        return render_template_string(html_content)  # Use render_template_string to render the HTML

    except UnicodeDecodeError:
        return "Error: Unable to decode the HTML file. Please check the file's encoding.", 500


@app.route('/api/send', methods=['POST'])
def send_message():
    """Save a message to the database."""
    try:
        data = request.get_json()
        content = data.get('content')

        if not content:
            return jsonify({'error': 'Message content is required'}), 400

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO texts (content) VALUES (?)', (content,))
            conn.commit()

        return jsonify({'message': 'Message sent successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/delete/<int:message_id>', methods=['DELETE'])
def delete_message(message_id):
    """Delete a specific message by ID."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM texts WHERE id = ?', (message_id,))
            conn.commit()

        return jsonify({'message': 'Message deleted successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/clear', methods=['DELETE'])
def clear_messages():
    """Clear all messages from the database."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM texts')
            conn.commit()

        return jsonify({'message': 'All messages cleared successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/messages', methods=['GET'])
def get_messages():
    """Retrieve all messages from the database."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, content FROM texts')
            messages = [{'id': row[0], 'content': row[1]} for row in cursor.fetchall()]

        return jsonify({'messages': messages}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    if not os.path.exists(DB_FILE):
        init_db()

    app.run(debug=True)
