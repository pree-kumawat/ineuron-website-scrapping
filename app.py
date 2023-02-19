from flask import Flask, render_template
import mysql.connector

app = Flask(__name__)

# Configure the MySQL connection
db = mysql.connector.connect(
    user='<USERNAME>', password='<PASSWORD>',
    host='<HOST>', database='<DB_NAME>'
)

# Define a route to display the course data
@app.route('/')
def index():
    # Retrieve the course data from the MySQL database
    cursor = db.cursor()
    query = "SELECT * FROM courses"
    cursor.execute(query)
    courses = cursor.fetchall()
    cursor.close()

    # Render the course data in a web page
    return render_template('index.html', courses=courses)

if __name__ == '__main__':
    app.run(debug=True)
