"""
Database Viewer - Displays all tables from PostgreSQL database
Reads configuration from backend/.env file
"""

import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import webbrowser
from pathlib import Path

# Load environment variables from backend/.env
def load_env():
    env_path = Path(__file__).parent / 'backend' / '.env'
    if not env_path.exists():
        print(f"Error: .env file not found at {env_path}")
        print("Please create backend/.env file based on backend/env.example")
        sys.exit(1)
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

load_env()

import psycopg2
from psycopg2 import extras

def get_connection():
    """Create database connection using environment variables"""
    return psycopg2.connect(
        host=os.environ.get('POSTGRES_HOST', 'localhost'),
        port=int(os.environ.get('POSTGRES_PORT', 5432)),
        dbname=os.environ.get('POSTGRES_DB', 'ZedReq'),
        user=os.environ.get('POSTGRES_USER', 'postgres'),
        password=os.environ.get('POSTGRES_PASSWORD', 'database')
    )

def get_all_tables():
    """Get list of all tables in the database"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
    """)
    tables = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return tables

def get_table_data(table_name):
    """Get all data from a specific table"""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
    
    # Get column info
    cursor.execute(f"""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name = %s
        ORDER BY ordinal_position
    """, (table_name,))
    columns = cursor.fetchall()
    
    # Get row count
    cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
    row_count = cursor.fetchone()['count']
    
    # Get data (limit to 100 rows for display)
    cursor.execute(f'SELECT * FROM "{table_name}" LIMIT 100')
    rows = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return {
        'columns': [dict(col) for col in columns],
        'rows': [dict(row) for row in rows],
        'total_count': row_count
    }

def generate_html():
    """Generate HTML page with all tables and data"""
    try:
        tables = get_all_tables()
        table_data = {}
        
        for table in tables:
            try:
                table_data[table] = get_table_data(table)
            except Exception as e:
                table_data[table] = {'error': str(e)}
        
        db_info = {
            'host': os.environ.get('POSTGRES_HOST', 'localhost'),
            'port': os.environ.get('POSTGRES_PORT', 5432),
            'database': os.environ.get('POSTGRES_DB', 'ZedReq'),
            'user': os.environ.get('POSTGRES_USER', 'postgres')
        }
        
        return generate_html_content(tables, table_data, db_info)
        
    except Exception as e:
        return f"""
        <!DOCTYPE html>
        <html><head><title>Database Error</title></head>
        <body style="font-family: sans-serif; padding: 40px; background: #1a1a2e; color: #fff;">
            <h1 style="color: #ff6b6b;">Database Connection Error</h1>
            <p>{str(e)}</p>
            <p>Please check your backend/.env file configuration.</p>
        </body></html>
        """

def generate_html_content(tables, table_data, db_info):
    """Generate the complete HTML content"""
    
    # Build table cards HTML
    table_cards = ""
    for table in tables:
        data = table_data.get(table, {})
        
        if 'error' in data:
            table_cards += f'''
            <div class="table-card error">
                <h3>{table}</h3>
                <p class="error-msg">Error: {data['error']}</p>
            </div>
            '''
            continue
        
        columns = data.get('columns', [])
        rows = data.get('rows', [])
        total_count = data.get('total_count', 0)
        
        # Column headers
        col_headers = "".join([f'<th>{col["column_name"]}<span class="col-type">{col["data_type"]}</span></th>' for col in columns])
        
        # Table rows
        row_html = ""
        for row in rows[:50]:  # Limit display to 50 rows
            cells = ""
            for col in columns:
                value = row.get(col['column_name'], '')
                if value is None:
                    cells += '<td class="null">NULL</td>'
                elif isinstance(value, (dict, list)):
                    cells += f'<td class="json">{json.dumps(value, default=str)[:100]}</td>'
                else:
                    str_val = str(value)
                    if len(str_val) > 100:
                        str_val = str_val[:100] + '...'
                    cells += f'<td>{str_val}</td>'
            row_html += f'<tr>{cells}</tr>'
        
        if not rows:
            row_html = f'<tr><td colspan="{len(columns)}" class="empty">No data</td></tr>'
        
        table_cards += f'''
        <div class="table-card" id="table-{table}">
            <div class="table-header">
                <h3>{table}</h3>
                <span class="row-count">{total_count} rows • {len(columns)} columns</span>
            </div>
            <div class="table-wrapper">
                <table>
                    <thead><tr>{col_headers}</tr></thead>
                    <tbody>{row_html}</tbody>
                </table>
            </div>
            {f'<p class="more-rows">Showing 50 of {total_count} rows</p>' if total_count > 50 else ''}
        </div>
        '''
    
    # Build sidebar navigation
    nav_items = "".join([f'<a href="#table-{table}" class="nav-item">{table}</a>' for table in tables])
    
    # Calculate total rows (compute outside f-string to avoid issues)
    total_rows = 0
    for t in tables:
        data = table_data.get(t, {})
        if 'error' not in data:
            total_rows += data.get('total_count', 0)
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZedReq Database Viewer</title>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        :root {{
            --bg-primary: #0d0d14;
            --bg-secondary: #13131f;
            --bg-card: #1a1a2e;
            --bg-hover: #252540;
            --accent: #6366f1;
            --accent-glow: rgba(99, 102, 241, 0.3);
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --border: #2d2d44;
            --success: #10b981;
            --warning: #f59e0b;
            --error: #ef4444;
        }}
        
        body {{
            font-family: 'Outfit', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
        }}
        
        /* Sidebar */
        .sidebar {{
            width: 280px;
            background: var(--bg-secondary);
            border-right: 1px solid var(--border);
            padding: 24px 16px;
            position: fixed;
            height: 100vh;
            overflow-y: auto;
        }}
        
        .logo {{
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--accent);
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .logo::before {{
            content: '⚡';
            font-size: 1.2rem;
        }}
        
        .db-info {{
            background: var(--bg-card);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 24px;
            border: 1px solid var(--border);
        }}
        
        .db-info p {{
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-bottom: 6px;
            font-family: 'JetBrains Mono', monospace;
        }}
        
        .db-info p:last-child {{
            margin-bottom: 0;
        }}
        
        .db-info strong {{
            color: var(--text-primary);
        }}
        
        .nav-title {{
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-muted);
            margin-bottom: 12px;
            padding-left: 8px;
        }}
        
        .nav-item {{
            display: block;
            padding: 10px 12px;
            color: var(--text-secondary);
            text-decoration: none;
            border-radius: 8px;
            font-size: 0.9rem;
            transition: all 0.2s;
            margin-bottom: 4px;
        }}
        
        .nav-item:hover {{
            background: var(--bg-hover);
            color: var(--text-primary);
        }}
        
        .nav-item:active {{
            background: var(--accent);
            color: white;
        }}
        
        /* Main Content */
        .main {{
            margin-left: 280px;
            flex: 1;
            padding: 32px 40px;
            max-width: calc(100vw - 280px);
        }}
        
        .header {{
            margin-bottom: 32px;
        }}
        
        .header h1 {{
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 8px;
            background: linear-gradient(135deg, var(--text-primary), var(--accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .header p {{
            color: var(--text-secondary);
            font-size: 1rem;
        }}
        
        .stats {{
            display: flex;
            gap: 16px;
            margin-bottom: 32px;
        }}
        
        .stat-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px 24px;
            flex: 1;
        }}
        
        .stat-card .value {{
            font-size: 2rem;
            font-weight: 700;
            color: var(--accent);
        }}
        
        .stat-card .label {{
            color: var(--text-muted);
            font-size: 0.85rem;
            margin-top: 4px;
        }}
        
        /* Table Cards */
        .table-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            margin-bottom: 24px;
            overflow: hidden;
            scroll-margin-top: 20px;
        }}
        
        .table-card.error {{
            border-color: var(--error);
        }}
        
        .table-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 24px;
            border-bottom: 1px solid var(--border);
            background: var(--bg-secondary);
        }}
        
        .table-header h3 {{
            font-size: 1.1rem;
            font-weight: 600;
            font-family: 'JetBrains Mono', monospace;
            color: var(--accent);
        }}
        
        .row-count {{
            font-size: 0.85rem;
            color: var(--text-muted);
            background: var(--bg-hover);
            padding: 6px 12px;
            border-radius: 6px;
        }}
        
        .table-wrapper {{
            overflow-x: auto;
            max-height: 400px;
            overflow-y: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.875rem;
        }}
        
        thead {{
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        
        th {{
            background: var(--bg-secondary);
            color: var(--text-primary);
            font-weight: 600;
            padding: 14px 16px;
            text-align: left;
            border-bottom: 1px solid var(--border);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            white-space: nowrap;
        }}
        
        .col-type {{
            display: block;
            font-size: 0.7rem;
            color: var(--text-muted);
            font-weight: 400;
            margin-top: 2px;
        }}
        
        td {{
            padding: 12px 16px;
            border-bottom: 1px solid var(--border);
            color: var(--text-secondary);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            max-width: 300px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        
        tr:hover td {{
            background: var(--bg-hover);
        }}
        
        td.null {{
            color: var(--text-muted);
            font-style: italic;
        }}
        
        td.json {{
            color: var(--warning);
        }}
        
        td.empty {{
            text-align: center;
            color: var(--text-muted);
            padding: 40px;
            font-style: italic;
        }}
        
        .more-rows {{
            text-align: center;
            padding: 12px;
            color: var(--text-muted);
            font-size: 0.85rem;
            border-top: 1px solid var(--border);
            background: var(--bg-secondary);
        }}
        
        .error-msg {{
            color: var(--error);
            padding: 20px;
        }}
        
        /* Scrollbar */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: var(--bg-secondary);
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: var(--border);
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: var(--text-muted);
        }}
        
        /* Responsive */
        @media (max-width: 1024px) {{
            .sidebar {{
                width: 220px;
            }}
            .main {{
                margin-left: 220px;
                padding: 24px;
            }}
        }}
    </style>
</head>
<body>
    <aside class="sidebar">
        <div class="logo">ZedReq DB</div>
        <div class="db-info">
            <p><strong>Host:</strong> {db_info['host']}</p>
            <p><strong>Port:</strong> {db_info['port']}</p>
            <p><strong>Database:</strong> {db_info['database']}</p>
            <p><strong>User:</strong> {db_info['user']}</p>
        </div>
        <div class="nav-title">Tables ({len(tables)})</div>
        <nav>
            {nav_items}
        </nav>
    </aside>
    
    <main class="main">
        <header class="header">
            <h1>Database Tables</h1>
            <p>Viewing all tables from the ZedReq PostgreSQL database</p>
        </header>
        
        <div class="stats">
            <div class="stat-card">
                <div class="value">{len(tables)}</div>
                <div class="label">Total Tables</div>
            </div>
            <div class="stat-card">
                <div class="value">{total_rows}</div>
                <div class="label">Total Rows</div>
            </div>
        </div>
        
        {table_cards}
    </main>
    
    <script>
        // Smooth scroll for navigation
        document.querySelectorAll('.nav-item').forEach(link => {{
            link.addEventListener('click', (e) => {{
                e.preventDefault();
                const target = document.querySelector(link.getAttribute('href'));
                if (target) {{
                    target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                }}
            }});
        }});
    </script>
</body>
</html>'''
    
    return html

def main():
    # Generate HTML content
    print("[*] Connecting to database...")
    html_content = generate_html()
    
    # Write to HTML file
    html_path = Path(__file__).parent / 'db_viewer.html'
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"[+] Generated {html_path}")
    print(f"[*] Opening in browser...")
    
    # Open in default browser
    webbrowser.open(f'file:///{html_path}')

if __name__ == '__main__':
    main()

