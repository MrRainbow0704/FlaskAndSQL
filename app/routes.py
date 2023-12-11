from flask import render_template, request
import config
from . import app, functions


SQLITE_CONN = functions.SQLite.db_connect(config.SQLITE_PATH)
MYSQL_CONN = functions.MySQL.create_db(
    config.MYSQL_HOST,
    config.MYSQL_PORT,
    config.MYSQL_USERNAME,
    config.MYSQL_PASSWORD,
    config.MYSQL_DBNAME,
)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    elif request.method == "POST":
        try:
            query = request.form.get("query-input")
            db = request.form.get("db-input")
            if request.form.get("params-input"):
                _params = map(
                    lambda x: x.strip(), request.form.get("params-input").split(", ")
                )
            else:
                _params = []

            params = []
            for p in _params:
                if p.isdigit() and not p[0] in ('"', "'") and not p[-1] in ('"', "'"):
                    params.append(int(p))
                else:
                    params.append(p.strip('"'))
            params = tuple(params)

            if db == "SQLITE":
                query = query.replace("%s", "?")
                res = functions.SQLite.SQL_query(SQLITE_CONN, query, params)
            elif db == "MYSQL":
                res = functions.MySQL.SQL_query(MYSQL_CONN, query, params)

            return render_template("index.html", result=res, status="OK")
        except Exception as err:
            print(f"Error: '{err}'")
            return render_template("index.html", result=err, status="ERROR")
