import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = 'crm.db'

def get_connection():
    # Added timeout to prevent database lock errors when reading/writing simultaneously
    return sqlite3.connect(DB_NAME, timeout=10)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            pg_location TEXT NOT NULL,
            move_in_date DATE NOT NULL,
            status TEXT NOT NULL DEFAULT 'New' CHECK(status IN ('New', 'Contacted', 'Visit Scheduled', 'Won', 'Lost')),
            agent_id INTEGER,
            visit_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (agent_id) REFERENCES agents(id)
        )
    ''')
    
    cursor.execute('SELECT COUNT(*) FROM agents')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('INSERT INTO agents (name) VALUES (?)', [('Rahul',), ('Priya',), ('Amit',)])
        
    conn.commit()
    conn.close()

def add_lead(name, phone, pg_location, move_in_date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO leads (name, phone, pg_location, move_in_date, status)
        VALUES (?, ?, ?, ?, 'New')
    ''', (name, phone, pg_location, move_in_date))
    conn.commit()
    conn.close()

def get_agents():
    conn = get_connection()
    df = pd.read_sql_query('SELECT * FROM agents', conn)
    conn.close()
    return df

def get_leads():
    conn = get_connection()
    query = '''
        SELECT l.id, l.name, l.phone, l.pg_location, l.move_in_date, l.status, 
               l.agent_id, a.name as agent_name, l.visit_date, l.created_at
        FROM leads l
        LEFT JOIN agents a ON l.agent_id = a.id
        ORDER BY l.created_at DESC
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def update_lead(lead_id, status, agent_id, visit_date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE leads
        SET status = ?, agent_id = ?, visit_date = ?
        WHERE id = ?
    ''', (status, agent_id, visit_date, lead_id))
    conn.commit()
    conn.close()

def get_dashboard_stats():
    """Returns aggregated stats and data suitable for dashboard charting."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM leads')
    total_leads = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM leads WHERE status = 'New'")
    new_leads = cursor.fetchone()[0]
    
    today_str = datetime.now().strftime('%Y-%m-%d')
    cursor.execute("SELECT COUNT(*) FROM leads WHERE visit_date >= ? AND status != 'Lost'", (today_str,))
    upcoming_visits = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM leads WHERE status = 'Won'")
    conversions = cursor.fetchone()[0]
    
    # Location Donut Chart Data
    cursor.execute("SELECT pg_location, COUNT(*) as count FROM leads GROUP BY pg_location")
    location_data = cursor.fetchall()
    
    # Funnel Chart Data (Status Counts)
    cursor.execute("SELECT status, COUNT(*) as count FROM leads GROUP BY status")
    status_counts = dict(cursor.fetchall())
    
    conn.close()
    
    funnel_data = {
        'New': status_counts.get('New', 0),
        'Contacted': status_counts.get('Contacted', 0),
        'Visit Scheduled': status_counts.get('Visit Scheduled', 0),
        'Won': status_counts.get('Won', 0)
    }
    
    return {
        'metrics': {
            'Total Leads': total_leads,
            'New Leads': new_leads,
            'Upcoming Visits': upcoming_visits,
            'Conversions (Won)': conversions
        },
        'funnel_data': funnel_data,
        'location_data': location_data
    }
