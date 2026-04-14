const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

const db = new sqlite3.Database(':memory:', (err) => {
    if (err) return console.error(err.message);
    console.log('Connected to the in-memory SQLite analytics database.');
});

// Seed Analytics Database
db.serialize(() => {
    db.run("CREATE TABLE IF NOT EXISTS analytics (id INTEGER PRIMARY KEY, metric_name TEXT, count INTEGER, date TEXT)");
    const stmt = db.prepare("INSERT INTO analytics (metric_name, count, date) VALUES (?, ?, ?)");
    
    // Seed dummy data matching our chart array lengths
    stmt.run("inbound_intake", 12, "Mon");
    stmt.run("inbound_intake", 19, "Tue");
    stmt.run("inbound_intake", 15, "Wed");
    stmt.run("inbound_intake", 25, "Thu");
    stmt.run("inbound_intake", 22, "Fri");
    stmt.run("inbound_intake", 10, "Sat");
    stmt.run("inbound_intake", 8, "Sun");
    stmt.finalize();
});

// ── Legal Intake Table ──
db.run(`CREATE TABLE IF NOT EXISTS intake (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    matter TEXT,
    created_at TEXT DEFAULT (datetime('now'))
)`);

app.post('/api/v1/intake', (req, res) => {
    const { name, email, matter } = req.body;
    if (!name) {
        return res.status(400).json({ error: 'Name is required.' });
    }
    db.run(
        `INSERT INTO intake (name, email, matter) VALUES (?, ?, ?)`,
        [name, email || null, matter || null],
        function (err) {
            if (err) {
                return res.status(500).json({ error: err.message });
            }
            res.status(201).json({ id: this.lastID, status: 'intake_received' });
        }
    );
});

app.get('/api/v1/intake', (req, res) => {
    db.all('SELECT * FROM intake ORDER BY id DESC', [], (err, rows) => {
        if (err) return res.status(500).json({ error: err.message });
        res.json({ data: rows });
    });
});

app.get('/api/v1/analytics', (req, res) => {
    db.all("SELECT * FROM analytics ORDER BY id ASC", [], (err, rows) => {
        if (err) {
            res.status(500).json({ error: err.message });
            return;
        }
        res.json({ data: rows });
    });
});

const PORT = 3001;
app.listen(PORT, () => {
    console.log(`SQLite Analytics Wrapper running on port ${PORT}`);
});
