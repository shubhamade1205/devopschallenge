from flask import Flask
import pymysql
import os
import logging
import sys

# Configure standard logging to output straight to stdout/stderr
# This ensures 'kubectl logs' can capture the output instantly
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route("/")
def home():
    logger.info("Received request on root '/' route.")
    try:
        host = os.getenv("MYSQL_HOST", "mysql")
        user = "root"
        database = "demo"
        
        logger.info(f"Attempting connection to MySQL at host: {host}, database: {database}")
        
        conn = pymysql.connect(
            host=host,
            user=user,
            password=os.getenv("MYSQL_PASSWORD", "mypass"), 
            database=database,
            connect_timeout=5 # Prevent the app from hanging indefinitely if DB is down
        )

        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            logger.info(f"Database query executed successfully. Result: {result}")

        conn.close()
        logger.info("MySQL connection closed cleanly.")
        return "Application + MySQL Working"

    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}", exc_info=True)
        return f"MySQL Error: {str(e)}", 500


@app.route("/health")
def health():
    # Using DEBUG level so health checks don't spam your main production logs,
    # but switching to INFO here will show you every single K8s probe hit.
    logger.debug("Readiness/Liveness probe hit '/health'")
    return "Healthy", 200


if __name__ == "__main__":
    logger.info("Starting Flask application server on port 5000...")
    app.run(host="0.0.0.0", port=5000)