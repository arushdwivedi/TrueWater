# core/db.py
import sqlite3
import os

DB_PATH = os.path.join('data', 'truewater.db')


SQL_CREATE = '''
CREATE TABLE IF NOT EXISTS water_samples (
id TEXT PRIMARY KEY,
testId TEXT,
testNumber INTEGER,
dateOfTest TEXT,
sampleImagePath TEXT,
algaeContent TEXT
);
'''




def ensure_data_dir():
    d = os.path.dirname(DB_PATH)
    if not os.path.exists(d):
        os.makedirs(d, exist_ok=True)




def init_db():
    ensure_data_dir()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(SQL_CREATE)
    conn.commit()
    conn.close()




def insert_sample(record):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO water_samples (id, testId, testNumber, dateOfTest, sampleImagePath, algaeContent) VALUES (?, ?, ?, ?, ?, ?)",
        (record['id'], record['testId'], record['testNumber'], record['dateOfTest'], record['sampleImagePath'], record['algaeContent'])
    )
    conn.commit()
    conn.close()




def update_sample_content_by_path(sample_path, content_json):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT id FROM water_samples WHERE sampleImagePath = ? ORDER BY dateOfTest DESC LIMIT 1",
        (sample_path,)
    )
    row = c.fetchone()
    if row:
        id_ = row[0]
        c.execute("UPDATE water_samples SET algaeContent = ? WHERE id = ?", (content_json, id_))
        conn.commit()
    conn.close()




def get_all_samples():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, testId, testNumber, dateOfTest, sampleImagePath, algaeContent FROM water_samples ORDER BY dateOfTest DESC")
    rows = c.fetchall()
    conn.close()
    return rows




def get_samples_by_testId(testId):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, testId, testNumber, dateOfTest, sampleImagePath, algaeContent FROM water_samples WHERE testId = ? ORDER BY testNumber ASC", (testId,))
    rows = c.fetchall()
    conn.close()
    return rows




def get_latest_test_number(testId):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT MAX(testNumber) FROM water_samples WHERE testId = ?", (testId,))
    r = c.fetchone()
    conn.close()
    return r[0] if r and r[0] is not None else 0