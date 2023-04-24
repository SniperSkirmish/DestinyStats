from flask import Flask
from flask import g
from flask import render_template
from flask_apscheduler import APScheduler
from datetime import datetime
import logging
import sqlite3
import sys

import UpdateData

# Log Setup
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
dateFormat='%Y-%m-%d,%H:%M:%S'
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Use FileHandler() to log to a file
file_handler = logging.FileHandler("app.log", mode='w', encoding=None, delay=False)
formatter = logging.Formatter(log_format, dateFormat)
file_handler.setFormatter(formatter)

# Don't forget to add the file handler
logger.addHandler(file_handler)

# guardians = ('SpacePirateKubli', 'DeathAngelx101', 'blacksun23')
# startDate = datetime.fromisoformat('2022-06-22T00:00:00')

print("Start Init")
logger.info("Start Init")

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

@scheduler.task('interval', id='do_job_1', seconds=120, misfire_grace_time=900)
def job1():
    try:
        UpdateData.updateStats()
    except Exception as e:
            print("Exception raised UpdateStats - " + str(e))
            logger.warning("Exception raised UpdateStats - " + str(e))

    print("Data Updated")
    logger.info("Data Updated")

@app.route("/")
def index():
    try:
        db = get_db()
        mostSnipes = db.execute("SELECT Name, SniperKills FROM Leaderboard ORDER BY SniperKills DESC LIMIT 3").fetchall()
        mostHeadshots = db.execute("SELECT Name, SniperHeadShots FROM Leaderboard ORDER BY SniperHeadShots DESC LIMIT 3").fetchall()
        highestHsPercent = db.execute("SELECT Name, HeadshotPercentage FROM Leaderboard ORDER BY HeadshotPercentage DESC LIMIT 3").fetchall()
        playerStats = db.execute("SELECT Name, SniperKills, SniperHeadShots, HeadshotPercentage FROM Leaderboard").fetchall()

        playerCard = []

        for player in playerStats:
            playerCard.append(dict(player))

        # for index, items in enumerate(playerCard):
        #     items.update({"bgColor": bgColor[index % 4]})
        #     items.update({"textColor": textColor[index % 4]})

        return render_template("index.html", mostSnipes=mostSnipes, mostHeadshots=mostHeadshots, highestHsPercent=highestHsPercent, playerCard=playerCard)

    except Exception as e:
            print("Exception raised app route index - " + str(e))
            # logging.warning("Exception raised app route index - " + str(e))

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == '__main__':
	app.run(debug=True)