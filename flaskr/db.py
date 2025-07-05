import sqlite3
from datetime import datetime
import csv, os
import click
from flask import current_app, g
from werkzeug.security import generate_password_hash

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):   
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))
    
    with open('data/passwords.csv', 'r', encoding='utf-8', newline='') as input_file:
        reader = csv.DictReader(input_file)

        with open('data/table_pass.csv','w', encoding='utf-8', newline='') as output_file:
            fieldnames = [field for field in reader.fieldnames if field!='pass'] + ['password']
            writer = csv.DictWriter(output_file, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                plain_pass = row['pass']
                hashed_pass = generate_password_hash(plain_pass)
                del row['pass']
                row['password'] = hashed_pass
                writer.writerow(row)
    print('Passowrds converted to password hashes successfully..')

    with open('data/table_user.csv', newline='', encoding='utf-8') as f:
        db = get_db()
        reader = csv.reader(f)
        columns = next(reader)
        placeholders = ','.join('?'*len(columns))
        for row in reader:
            db.execute(
                f'INSERT INTO user ({','.join(columns)}) VALUES ({placeholders})', row
            )
            db.commit()

    with open('data/table_pass.csv', newline='', encoding='utf-8') as f:
        db=get_db()
        reader = csv.reader(f)
        columns = next(reader)
        placeholders = ','.join('?'*len(columns))
        for row in reader:
            db.execute(
                f'INSERT INTO pass ({','.join(columns)}) VALUES ({placeholders})', row
            )
            db.commit()

    with open('data/table_comments.csv', newline='', encoding='utf-8') as csv_file:
        db=get_db()
        reader = csv.reader(csv_file)
        columns = next(reader)
        placeholders = ','.join('?'*len(columns))
        for row in reader:
            db.execute(
                f'INSERT INTO comments ({','.join(columns)}) VALUES ({placeholders})', row
            )
            db.commit()

    with open('data/MOCK_DATA.csv', newline='', encoding='utf-8') as csv_file:
        db=get_db()
        reader = csv.reader(csv_file)
        columns = next(reader)
        placeholders = ','.join('?'*len(columns))
        for row in reader:
            db.execute(
                f'INSERT INTO posts({','.join(columns)}) VALUES ({placeholders})', row
            )
            db.commit()
    print('Database populated successfully.')

@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Initialized the database.')

sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
