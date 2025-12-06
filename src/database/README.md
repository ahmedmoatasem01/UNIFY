# Database Setup

This folder contains database schema and initialization scripts.

## Files

- `schema.sql` - SQL file containing all table creation statements
- `init_db.py` - Python script to initialize the database and create all tables

## Usage

1. Make sure MySQL is running
2. Update the database credentials in `init_db.py` if needed
3. Run the initialization script:
   ```bash
   python src/database/init_db.py
   ```

## Adding New Tables

Add your table creation statements to `schema.sql`. The `init_db.py` script will automatically execute all statements in that file.

