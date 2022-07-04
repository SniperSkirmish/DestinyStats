from flask import Flask
from flask import g
from flask import render_template
from flask_apscheduler import APScheduler
from datetime import datetime
import logging
import sqlite3
import sys

import UpdateData

# logging.basicConfig(filename='app.log', encoding='utf-8', level=logging.info)
log_format = '%(name)s - %(levelname)s - %(message)s'
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Use FileHandler() to log to a file
file_handler = logging.FileHandler("app.log", mode='w', encoding=None, delay=False)
formatter = logging.Formatter(log_format)
file_handler.setFormatter(formatter)

# Don't forget to add the file handler
logger.addHandler(file_handler)

# guardians = ('SpacePirateKubli', 'DeathAngelx101', 'blacksun23')
# startDate = datetime.fromisoformat('2022-06-22T00:00:00')

print("Start Init")
logging.info("Start Init")

app = Flask(__name__)

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

print("Scheduler Started")

def get_db():
    """Connect to the application's configured database. The connection
    is unique for each request and will be reused if this is called
    again.
    """
    if "db" not in g:
        g.db = sqlite3.connect('eyetest.db')
        g.db.row_factory = sqlite3.Row

    return g.db

@scheduler.task('interval', id='do_job_1', seconds=30, misfire_grace_time=900)
def job1():
    try:
        UpdateData.updateStats()
    except Exception as e:
            print("Exception raised UpdateStats - " + str(e))
            logging.warning("Exception raised UpdateStats - " + str(e))

    print("Data Updated")
    logging.info("Data Updated")

@app.route("/")
def index():
    try:
        db = get_db()
        mostSnipes = db.execute("SELECT Name, max(SniperKills) FROM Leaderboard").fetchall()
        mostHeadshots = db.execute("SELECT Name, max(SniperHeadShots) FROM Leaderboard").fetchall()
        highestHsPercent = db.execute("SELECT Name, max(HeadshotPercentage) FROM Leaderboard").fetchall()
        playerStats = db.execute("SELECT Name, SniperKills, SniperHeadShots, HeadshotPercentage FROM Leaderboard").fetchall()
        return render_template("index.html", mostSnipes=mostSnipes, mostHeadshots=mostHeadshots, highestHsPercent=highestHsPercent, playerStats=playerStats)

    except Exception as e:
            print("Exception raised app route index - " + str(e))
            logging.warning("Exception raised app route index - " + str(e))

@app.route("/about")
def about():
    return render_template("aboutpage.html")
