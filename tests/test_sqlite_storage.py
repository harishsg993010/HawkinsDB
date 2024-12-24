"""Test suite for SQLite storage backend."""
import os
import unittest
import tempfile
from datetime import datetime
from typing import Optional, Sequence, cast, Type, TypeVar

from hawkinsdb.storage.sqlite import SQLiteStorage
from hawkinsdb.types import CorticalColumn, ReferenceFrame, PropertyCandidate
from hawkinsdb.base import BaseCorticalColumn

# Type variable for CorticalColumn
T_CorticalColumn = TypeVar('T_CorticalColumn', bound=BaseCorticalColumn)

class TestSQLiteStorage(unittest.TestCase):
    """Test cases for SQLite storage backend."""
    
    def setUp(self):
        """Set up test environment with temporary database."""
        # Use temporary file for testing
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_hawkins.db")
        self.storage = SQLiteStorage(db_path=self.db_path)
        self.storage.initialize()
        
    def tearDown(self):
        """Clean up test environment."""
        self.storage.cleanup()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)
        
    def test_initialize_and_cleanup(self):
        """Test database initialization and cleanup."""
        self.assertTrue(os.path.exists(self.db_path))
        self.storage.cleanup()
        
    def test_save_and_load_columns(self):
        """Test saving and loading columns with various data types."""
        # Create test data
        test_time = datetime.now().isoformat()
        test_columns: Sequence[T_CorticalColumn] = cast(
            Sequence[T_CorticalColumn],
            [
                CorticalColumn(
                    name="test_column",
                    frames=[
                        ReferenceFrame(
                            name="test_frame",
                            properties={
                                "color": [PropertyCandidate(value="red", confidence=0.9)],
                                "size": [PropertyCandidate(value=42, confidence=1.0)]
                            },
                            relationships={
                                "contains": [PropertyCandidate(value="item", confidence=0.8)]
                            },
                            location={"x": 0, "y": 0},
                            history=[(test_time, "created"), (test_time, "updated")]
                        )
                    ]
                )
            ]
        )
        
        # Save columns
        self.storage.save_columns(test_columns)
        
        # Load columns
        loaded_columns = self.storage.load_columns()
        
        # Verify data
        self.assertEqual(len(loaded_columns), 1)
        self.assertEqual(loaded_columns[0].name, "test_column")
        self.assertEqual(len(loaded_columns[0].frames), 1)
        
        loaded_frame = loaded_columns[0].frames[0]
        self.assertEqual(loaded_frame.name, "test_frame")
        self.assertEqual(loaded_frame.properties["color"][0].value, "red")
        self.assertEqual(loaded_frame.properties["size"][0].value, 42)
        self.assertEqual(loaded_frame.relationships["contains"][0].value, "item")
        self.assertEqual(loaded_frame.location, {"x": 0, "y": 0})
        self.assertEqual(loaded_frame.history, [(test_time, "created"), (test_time, "updated")])
        
    def test_error_handling(self):
        """Test error handling for invalid operations."""
        # Test saving invalid data (empty column name)
        with self.assertRaises(ValueError):
            invalid_columns: Sequence[T_CorticalColumn] = cast(
                Sequence[T_CorticalColumn], 
                [CorticalColumn(name="", frames=[])]
            )
            self.storage.save_columns(invalid_columns)
            
        # Test empty database path
        with self.assertRaises(ValueError) as cm:
            SQLiteStorage(db_path="")
        self.assertIn("Invalid database path", str(cm.exception))
            
        # Test non-existent directory creation
        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = os.path.join(temp_dir, "newdir")
            db_path = os.path.join(new_dir, "test.db")
            storage = SQLiteStorage(db_path=db_path)
            self.assertTrue(os.path.exists(new_dir))
            storage.cleanup()
            
        # Test invalid directory permissions
        if os.name != 'nt':  # Skip on Windows
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create a read-only directory
                read_only_dir = os.path.join(temp_dir, "readonly")
                os.makedirs(read_only_dir)
                os.chmod(read_only_dir, 0o555)  # Read + execute only
                
                db_path = os.path.join(read_only_dir, "test.db")
                with self.assertRaises(ValueError) as cm:
                    SQLiteStorage(db_path=db_path)
                self.assertIn("write", str(cm.exception).lower())

if __name__ == '__main__':
    unittest.main()