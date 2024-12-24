from typing import Optional, Dict, Any
from pathlib import Path
import os
import json
import logging
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)

class Config:
    """Configuration management for HawkinsDB."""
    
    SENSITIVE_KEYS = {'OPENAI_API_KEY', 'CONCEPTNET_API_KEY'}
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration."""
        config_path_str = config_path or os.getenv("HAWKINSDB_CONFIG", "~/.hawkinsdb/config.json")
        self.config_path = Path(config_path_str).expanduser()
        self.config = self._load_config()
        self.config.setdefault('credentials', {})
        
        # Initialize with environment variables if available
        for key in self.SENSITIVE_KEYS:
            if os.getenv(key):
                self.config['credentials'][key] = os.getenv(key)
        
    def _setup_encryption(self):
        """Set up encryption for sensitive data with enhanced security."""
        try:
            # Use machine-specific salt
            machine_id = self._get_machine_id()
            salt_path = Path(self.config_path).parent / '.salt'
            
            # Generate or load salt
            if not salt_path.exists():
                self._salt = os.urandom(16)  # Use cryptographically secure random bytes
                salt_path.parent.mkdir(parents=True, exist_ok=True)
                with open(salt_path, 'wb') as f:
                    f.write(self._salt)
            else:
                with open(salt_path, 'rb') as f:
                    self._salt = f.read()

            # Use PBKDF2HMAC with stronger parameters
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=self._salt,
                iterations=200000,  # Increased iterations for better security
            )
            
            # Combine machine ID with additional system-specific data
            system_data = machine_id + self._get_additional_system_data()
            key = base64.urlsafe_b64encode(kdf.derive(system_data.encode()))
            self._fernet = Fernet(key)
            
        except Exception as e:
            logger.error(f"Failed to setup encryption: {str(e)}")
            raise ValueError("Could not initialize secure storage") from e
            
    def _get_additional_system_data(self) -> str:
        """Get additional system-specific data for key derivation."""
        try:
            # Try to get additional system-specific identifiers
            identifiers = []
            
            # Try reading system UUID
            try:
                with open('/sys/class/dmi/id/product_uuid', 'r') as f:
                    identifiers.append(f.read().strip())
            except:
                pass
                
            # Try reading CPU info
            try:
                with open('/proc/cpuinfo', 'r') as f:
                    for line in f:
                        if line.startswith('serial'):
                            identifiers.append(line.split(':')[1].strip())
                            break
            except:
                pass
                
            # If no system identifiers available, use a backup approach
            if not identifiers:
                identifiers.append(str(os.getpid()))
                identifiers.append(str(os.path.getmtime(__file__)))
                
            return '_'.join(identifiers)
            
        except Exception:
            # Fallback to basic identifiers if anything fails
            return str(os.getpid()) + '_' + str(os.path.getmtime(__file__))
        
    def _get_machine_id(self) -> str:
        """Get a unique machine identifier for key derivation."""
        try:
            with open('/etc/machine-id', 'r') as f:
                return f.read().strip()
        except FileNotFoundError:
            # Fallback to a development key if machine-id is not available
            return 'development_machine_id'
            
    def _encrypt_value(self, value: str) -> str:
        """
        Encrypt sensitive values with additional security measures.
        
        Args:
            value: The string value to encrypt
            
        Returns:
            str: The encrypted value encoded as base64
            
        Raises:
            ValueError: If encryption fails or value is invalid
        """
        if not value:
            return value
            
        try:
            # Add a random prefix to prevent identical values from producing identical ciphertexts
            random_prefix = os.urandom(8)
            data_to_encrypt = random_prefix + value.encode()
            
            # Encrypt with Fernet (already uses secure padding)
            encrypted_data = self._fernet.encrypt(data_to_encrypt)
            return base64.urlsafe_b64encode(encrypted_data).decode()
            
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise ValueError("Failed to encrypt sensitive data") from e
            
    def _decrypt_value(self, value: str) -> Optional[str]:
        """
        Decrypt sensitive values with enhanced error handling.
        
        Args:
            value: The encrypted value as base64 string
            
        Returns:
            Optional[str]: The decrypted value, or None if decryption fails
            
        Raises:
            ValueError: If the encrypted data appears to be tampered with
        """
        if not value:
            return None
            
        try:
            # Decode the base64 encrypted data
            encrypted_data = base64.urlsafe_b64decode(value.encode())
            
            # Decrypt the data
            decrypted_data = self._fernet.decrypt(encrypted_data)
            
            # Remove the random prefix (first 8 bytes)
            original_value = decrypted_data[8:].decode()
            return original_value
            
        except Exception as e:
            if "Token expired" in str(e):
                logger.error("Encrypted data has expired")
                raise ValueError("Secure storage data has expired")
            elif "Invalid token" in str(e):
                logger.error("Encrypted data appears to be tampered with")
                raise ValueError("Secure storage data integrity check failed")
            else:
                logger.error(f"Decryption failed: {str(e)}")
                return None
            
    def _load_config(self) -> Dict:
        """Load configuration from file with encrypted credentials."""
        default_config = {
            "features": {
                "auto_enrichment": False,
                "consensus_threshold": 0.6,
                "use_sqlite_storage": False  # Default to JSON storage
            },
            "storage": {
                "json_path": "./hawkins_db.json",
                "sqlite_path": "./hawkins_memory.db"
            },
            "credentials": {}
        }
        
        if not self.config_path.exists():
            return default_config
            
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            return config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return default_config
            
    def save(self):
        """Save configuration securely."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create a copy of config to avoid modifying the original
        config_to_save = self.config.copy()
        
        with open(self.config_path, 'w') as f:
            json.dump(config_to_save, f, indent=4)
            
    def get_feature(self, name: str) -> bool:
        """
        Get feature flag value.
        
        Args:
            name: Feature flag name (e.g., 'use_sqlite_storage')
            
        Returns:
            bool: True if feature is enabled, False otherwise
        """
        return self.config.get("features", {}).get(name, False)
        
    def set_feature(self, name: str, value: bool):
        """
        Set feature flag value.
        
        Args:
            name: Feature flag name (e.g., 'use_sqlite_storage')
            value: Boolean value to set
        """
        if "features" not in self.config:
            self.config["features"] = {}
        self.config["features"][name] = value
        self.save()
        
    def get_storage_backend(self) -> str:
        """
        Get configured storage backend.
        
        Returns:
            str: Storage backend type ('sqlite' or 'json')
        """
        return 'sqlite' if self.get_feature('use_sqlite_storage') else 'json'
        
    def set_storage_backend(self, backend_type: str):
        """
        Set storage backend type.
        
        Args:
            backend_type: Either 'sqlite' or 'json'
            
        Raises:
            ValueError: If backend_type is invalid
        """
        if backend_type not in ('sqlite', 'json'):
            raise ValueError("Storage backend must be either 'sqlite' or 'json'")
            
        self.set_feature('use_sqlite_storage', backend_type == 'sqlite')
        
    def get_credential(self, key: str) -> Optional[str]:
        """
        Get credential value, prioritizing environment variables.
        
        Args:
            key: Credential key (e.g., 'OPENAI_API_KEY')
            
        Returns:
            Optional[str]: Credential value if found, None otherwise
        """
        # First try environment variable
        env_value = os.getenv(key)
        if env_value:
            logger.debug(f"Using {key} from environment variables")
            return env_value
            
        # Fall back to stored credentials
        stored_value = self.config.get("credentials", {}).get(key)
        if stored_value:
            logger.debug(f"Using {key} from stored credentials")
            return stored_value
            
        logger.debug(f"No credential found for {key}")
        return None
        
    def set_credential(self, key: str, value: str):
        """
        Securely store a credential.
        
        Args:
            key: Credential key (e.g., 'OPENAI_API_KEY')
            value: Credential value to store
        """
        if not value:
            logger.warning(f"Attempted to store empty credential for {key}")
            return
            
        if "credentials" not in self.config:
            self.config["credentials"] = {}
            
        # Encrypt before storing
        self.config["credentials"][key] = self._encrypt_value(value)
        self.save()
        
    def _validate_and_migrate_credentials(self):
        """Validate and migrate existing credentials to encrypted storage."""
        if "credentials" not in self.config:
            self.config["credentials"] = {}
            return

        # Encrypt any unencrypted credentials
        for key in self.SENSITIVE_KEYS:
            value = self.config["credentials"].get(key)
            if value and not self._is_encrypted(value):
                try:
                    encrypted_value = self._encrypt_value(value)
                    self.config["credentials"][key] = encrypted_value
                    logger.info(f"Successfully migrated {key} to encrypted storage")
                except Exception as e:
                    logger.error(f"Failed to migrate {key}: {str(e)}")
                    
        self.save()
        
    def _is_encrypted(self, value: str) -> bool:
        """Check if a value is already encrypted."""
        try:
            self._decrypt_value(value)
            return True
        except Exception:
            return False
            
    def validate_credentials(self) -> Dict[str, Any]:
        """
        Validate all required credentials with enhanced security checks.
        
        Returns:
            Dict[str, Any]: Mapping of credential keys to their validation results
            
        Raises:
            ValueError: If credential storage appears to be compromised
        """
        validation_results = {}
        for key in self.SENSITIVE_KEYS:
            result = {
                'valid': False,
                'present': False,
                'error': None
            }
            
            try:
                value = self.get_credential(key)
                result['present'] = bool(value)
                
                if value:
                    if key == 'OPENAI_API_KEY':
                        # Enhanced OpenAI API key validation
                        if value.startswith(('sk-', 'org-')):
                            # Check length and character set
                            if len(value) >= 32 and all(c in '-_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789' for c in value):
                                result['valid'] = True
                            else:
                                result['error'] = "Invalid key format"
                        else:
                            result['error'] = "Invalid key prefix"
                    else:
                        # Generic credential validation
                        if len(value) >= 8:  # Minimum length check
                            result['valid'] = True
                        else:
                            result['error'] = "Credential too short"
                else:
                    result['error'] = "Missing credential"
                    
            except ValueError as ve:
                # Handle integrity check failures
                result['error'] = str(ve)
                logger.error(f"Security violation for {key}: {str(ve)}")
                raise
                
            except Exception as e:
                result['error'] = f"Validation error: {str(e)}"
                logger.error(f"Error validating {key}: {str(e)}")
                
            validation_results[key] = result
            
        return validation_results
        
    def clear_sensitive_data(self):
        """Securely clear all sensitive data from memory and storage."""
        try:
            # Clear encrypted storage
            if "credentials" in self.config:
                self.config["credentials"] = {}
                self.save()
                
            # Clear encryption key material
            if hasattr(self, '_fernet'):
                del self._fernet
            if hasattr(self, '_salt'):
                del self._salt
                
            # Trigger garbage collection to help remove sensitive data from memory
            import gc
            gc.collect()
            
            logger.info("Sensitive data cleared successfully")
            
        except Exception as e:
            logger.error(f"Error clearing sensitive data: {str(e)}")
            raise ValueError("Failed to securely clear sensitive data")
