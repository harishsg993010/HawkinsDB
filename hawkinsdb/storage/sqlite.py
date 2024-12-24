"""SQLite storage backend implementation."""
import os
import json
import logging
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class SQLiteStorage:
    """Simple SQLite storage implementation."""
    
    def __init__(self, db_path: str = "hawkins_memory.db"):
        """Initialize SQLite storage."""
        try:
            # Convert to absolute path
            self.db_path = str(Path(db_path).absolute())
            
            # Ensure directory exists
            directory = os.path.dirname(self.db_path)
            if directory:
                os.makedirs(directory, exist_ok=True)
            
            self._initialized = False
            
            # Remove existing database if it's corrupted
            try:
                if os.path.exists(self.db_path):
                    with sqlite3.connect(self.db_path) as test_conn:
                        test_conn.execute("SELECT 1")
            except sqlite3.DatabaseError:
                logger.warning(f"Removing corrupted database file: {self.db_path}")
                os.remove(self.db_path)
            
            # Create a new database connection
            with sqlite3.connect(self.db_path) as conn:
                # Set pragmas for better performance and reliability
                conn.execute("PRAGMA foreign_keys = ON")
                conn.execute("PRAGMA journal_mode = WAL")
                conn.execute("PRAGMA synchronous = NORMAL")
                conn.execute("PRAGMA busy_timeout = 5000")
                
                # Initialize schema in a transaction
                self.initialize()
                self._initialized = True
                
                # Verify tables after initialization
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = {row[0] for row in cursor.fetchall()}
                
                required_tables = {'columns', 'frames'}
                if not required_tables.issubset(tables):
                    missing = required_tables - tables
                    raise RuntimeError(f"Failed to create tables: {missing}")
            
            logger.info(f"SQLite storage initialized successfully at {self.db_path}")
            
        except sqlite3.Error as e:
            logger.error(f"SQLite error during initialization: {str(e)}")
            self._initialized = False
            if os.path.exists(self.db_path):
                try:
                    os.remove(self.db_path)
                except OSError:
                    pass
            raise
        except Exception as e:
            logger.error(f"Failed to initialize SQLite storage: {str(e)}")
            self._initialized = False
            if os.path.exists(self.db_path):
                try:
                    os.remove(self.db_path)
                except OSError:
                    pass
            raise RuntimeError(f"SQLite storage initialization failed: {str(e)}")
    
    def get_connection(self):
        """Get a database connection with row factory."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=60)
            conn.row_factory = sqlite3.Row
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys = ON")
            return conn
        except sqlite3.Error as e:
            logger.error(f"Failed to establish database connection: {e}")
            raise

    def initialize(self):
        """Initialize database schema with proper error handling."""
        if not os.path.exists(self.db_path):
            # Create new database file if it doesn't exist
            open(self.db_path, 'a').close()
            
        try:
            with self.get_connection() as conn:
                conn.execute("BEGIN IMMEDIATE TRANSACTION")
                
                try:
                    # Create tables with proper constraints
                    conn.executescript('''
                        CREATE TABLE IF NOT EXISTS columns (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT UNIQUE NOT NULL,
                            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                        );
                        
                        CREATE TABLE IF NOT EXISTS frames (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            column_id INTEGER NOT NULL,
                            properties TEXT NOT NULL DEFAULT '{}',
                            relationships TEXT NOT NULL DEFAULT '{}',
                            location TEXT DEFAULT '{}',
                            history TEXT DEFAULT '[]',
                            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (column_id) REFERENCES columns(id)
                                ON DELETE CASCADE
                                ON UPDATE CASCADE
                        );
                        
                        CREATE INDEX IF NOT EXISTS idx_frames_name ON frames(name);
                        CREATE INDEX IF NOT EXISTS idx_frames_column_id ON frames(column_id);
                    ''')
                    
                    # Verify tables were created
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name IN ('columns', 'frames')
                    """)
                    tables = {row[0] for row in cursor.fetchall()}
                    
                    required_tables = {'columns', 'frames'}
                    if not required_tables.issubset(tables):
                        missing = required_tables - tables
                        raise RuntimeError(f"Failed to create required tables: {missing}")
                    
                    conn.commit()
                    self._initialized = True
                    logger.info("SQLite storage schema initialized successfully")
                    
                except Exception as e:
                    conn.rollback()
                    logger.error(f"Error during schema initialization: {str(e)}")
                    raise
                    
        except sqlite3.Error as e:
            logger.error(f"SQLite error during schema initialization: {str(e)}")
            self._initialized = False
            raise
        except Exception as e:
            logger.error(f"Failed to initialize SQLite storage schema: {str(e)}")
            self._initialized = False
            raise

    def load_columns(self) -> List[Dict[str, Any]]:
        """Load all columns from storage."""
        if not self._initialized:
            raise RuntimeError("Storage not initialized")
            
        try:
            columns = []
            with self.get_connection() as conn:
                # Get all columns
                cursor = conn.cursor()
                for col_row in cursor.execute('SELECT * FROM columns').fetchall():
                    frames = []
                    
                    # Get frames for this column
                    frame_rows = cursor.execute(
                        'SELECT * FROM frames WHERE column_id = ?', 
                        (col_row['id'],)
                    ).fetchall()
                    
                    for frame_row in frame_rows:
                        frame = {
                            'name': frame_row['name'],
                            'properties': json.loads(frame_row['properties']),
                            'relationships': json.loads(frame_row['relationships']),
                            'location': json.loads(frame_row['location']) if frame_row['location'] else {},
                            'history': json.loads(frame_row['history']) if frame_row['history'] else [],
                            'created_at': frame_row['created_at'],
                            'updated_at': frame_row['updated_at']
                        }
                        frames.append(frame)
                        
                    column = {
                        'name': col_row['name'],
                        'frames': frames,
                        'created_at': col_row['created_at'],
                        'updated_at': col_row['updated_at']
                    }
                    columns.append(column)
                    
            return columns
            
        except Exception as e:
            logger.error("Error loading columns: %s", str(e))
            raise

    def save_columns(self, columns: List[Dict[str, Any]]) -> None:
        """Save columns to storage."""
        if not self._initialized:
            raise RuntimeError("Storage not initialized")
            
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Clear existing data
                cursor.execute('DELETE FROM frames')
                cursor.execute('DELETE FROM columns')
                
                # Save new data
                for column in columns:
                    now = datetime.now().isoformat()
                    
                    # Insert column
                    cursor.execute(
                        'INSERT INTO columns (name, created_at, updated_at) VALUES (?, ?, ?)',
                        (column['name'], 
                         column.get('created_at', now), 
                         column.get('updated_at', now))
                    )
                    column_id = cursor.lastrowid
                    
                    # Insert frames
                    for frame in column.get('frames', []):
                        cursor.execute('''
                            INSERT INTO frames (
                                name, column_id, properties, relationships, 
                                location, history, created_at, updated_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            frame['name'],
                            column_id,
                            json.dumps(frame.get('properties', {})),
                            json.dumps(frame.get('relationships', {})),
                            json.dumps(frame.get('location', {})),
                            json.dumps(frame.get('history', [])),
                            frame.get('created_at', now),
                            frame.get('updated_at', now)
                        ))
                        
            logger.info("Successfully saved %d columns", len(columns))
            
        except Exception as e:
            logger.error("Error saving columns: %s", str(e))
            raise

    def cleanup(self) -> None:
        """Clean up resources."""
        logger.info("SQLite storage cleaned up successfully")
