import pymysql
pymysql.install_as_MySQLdb()

from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)

# DB Config
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_PORT'] = 3307
app.config['MYSQL_USER'] = 'scheduler_user'
app.config['MYSQL_PASSWORD'] = 'aayush.new12'
app.config['MYSQL_DB'] = 'scheduler'

mysql = MySQL(app)

@app.route("/")
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT DATABASE();")
    data = cur.fetchone()
    return f"Connected to: {data}"

if __name__ == "__main__":
    app.run(debug=True)
