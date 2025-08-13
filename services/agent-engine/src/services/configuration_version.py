"""
Configuration version tracking service.
Tracks versions of all specifications for rollback and auditing.
"""

import hashlib
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path


class ConfigurationVersionService:
    """Service to track configuration versions."""
    
    def __init__(self, storage_path: Optional[str] = None):
        """Initialize version tracking service."""
        self.storage_path = Path(storage_path) if storage_path else Path("versions")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.versions_index = self._load_index()
    
    def _load_index(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load version index from storage."""
        index_file = self.storage_path / "index.json"
        if index_file.exists():
            try:
                with open(index_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
    
    def _save_index(self):
        """Save version index to storage."""
        index_file = self.storage_path / "index.json"
        with open(index_file, 'w') as f:
            json.dump(self.versions_index, f, indent=2, default=str)
    
    def track_specification_version(self, spec: Dict[str, Any]) -> str:
        """Track a new version of a specification."""
        # Extract metadata
        kind = spec.get("kind", "unknown")
        metadata = spec.get("metadata", {})
        name = metadata.get("name", "unnamed")
        version = metadata.get("version", "1.0.0")
        
        # Calculate checksum
        checksum = self._calculate_checksum(spec)
        
        # Check if this exact version already exists
        spec_key = f"{kind}/{name}"
        if spec_key in self.versions_index:
            for existing in self.versions_index[spec_key]:
                if existing["checksum"] == checksum:
                    return checksum  # Already tracked
        
        # Create version record
        version_record = {
            "kind": kind,
            "name": name,
            "version": version,
            "checksum": checksum,
            "created_at": datetime.utcnow().isoformat(),
            "metadata": metadata
        }
        
        # Store the full specification
        self._store_specification(checksum, spec)
        
        # Update index
        if spec_key not in self.versions_index:
            self.versions_index[spec_key] = []
        
        self.versions_index[spec_key].append(version_record)
        self._save_index()
        
        return checksum
    
    def _calculate_checksum(self, spec: Dict[str, Any]) -> str:
        """Calculate SHA256 checksum for specification."""
        # Ensure consistent ordering for checksum calculation
        spec_string = json.dumps(spec, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(spec_string.encode()).hexdigest()
    
    def _store_specification(self, checksum: str, spec: Dict[str, Any]):
        """Store full specification content."""
        spec_file = self.storage_path / f"{checksum[:8]}.json"
        with open(spec_file, 'w') as f:
            json.dump(spec, f, indent=2)
    
    def get_specification_by_checksum(self, checksum: str) -> Optional[Dict[str, Any]]:
        """Retrieve specification by checksum."""
        spec_file = self.storage_path / f"{checksum[:8]}.json"
        if spec_file.exists():
            with open(spec_file, 'r') as f:
                return json.load(f)
        return None
    
    def get_specification_history(self, kind: str, name: str) -> List[Dict[str, Any]]:
        """Get version history for a specification."""
        spec_key = f"{kind}/{name}"
        return self.versions_index.get(spec_key, [])
    
    def get_latest_version(self, kind: str, name: str) -> Optional[Dict[str, Any]]:
        """Get the latest version of a specification."""
        history = self.get_specification_history(kind, name)
        if history:
            latest = history[-1]
            return self.get_specification_by_checksum(latest["checksum"])
        return None
    
    def rollback_to_version(self, kind: str, name: str, checksum: str) -> Optional[Dict[str, Any]]:
        """Rollback to a specific version of a specification."""
        # Verify the version exists
        spec_key = f"{kind}/{name}"
        if spec_key not in self.versions_index:
            return None
        
        for version in self.versions_index[spec_key]:
            if version["checksum"] == checksum:
                return self.get_specification_by_checksum(checksum)
        
        return None
    
    def compare_versions(self, checksum1: str, checksum2: str) -> Dict[str, Any]:
        """Compare two versions of a specification."""
        spec1 = self.get_specification_by_checksum(checksum1)
        spec2 = self.get_specification_by_checksum(checksum2)
        
        if not spec1 or not spec2:
            return {"error": "One or both specifications not found"}
        
        # Simple diff - in production, use a proper diff library
        differences = {
            "checksum1": checksum1,
            "checksum2": checksum2,
            "changes": []
        }
        
        # Compare top-level keys
        keys1 = set(spec1.keys())
        keys2 = set(spec2.keys())
        
        added_keys = keys2 - keys1
        removed_keys = keys1 - keys2
        common_keys = keys1 & keys2
        
        for key in added_keys:
            differences["changes"].append({
                "type": "added",
                "key": key,
                "value": spec2[key]
            })
        
        for key in removed_keys:
            differences["changes"].append({
                "type": "removed",
                "key": key,
                "value": spec1[key]
            })
        
        for key in common_keys:
            if spec1[key] != spec2[key]:
                differences["changes"].append({
                    "type": "modified",
                    "key": key,
                    "old_value": spec1[key],
                    "new_value": spec2[key]
                })
        
        return differences
    
    def clean_old_versions(self, keep_last: int = 10):
        """Clean old versions, keeping only the last N versions."""
        for spec_key in self.versions_index:
            versions = self.versions_index[spec_key]
            if len(versions) > keep_last:
                # Keep only the last N versions
                to_remove = versions[:-keep_last]
                self.versions_index[spec_key] = versions[-keep_last:]
                
                # Remove old specification files
                for version in to_remove:
                    spec_file = self.storage_path / f"{version['checksum'][:8]}.json"
                    if spec_file.exists():
                        spec_file.unlink()
        
        self._save_index()
    
    def export_version(self, checksum: str, export_path: str):
        """Export a specific version to a file."""
        spec = self.get_specification_by_checksum(checksum)
        if spec:
            export_file = Path(export_path)
            export_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(export_file, 'w') as f:
                json.dump(spec, f, indent=2)
            
            return True
        return False
    
    def import_version(self, import_path: str) -> Optional[str]:
        """Import a specification from a file."""
        import_file = Path(import_path)
        if not import_file.exists():
            return None
        
        try:
            with open(import_file, 'r') as f:
                spec = json.load(f)
            
            # Track the imported specification
            return self.track_specification_version(spec)
        except Exception:
            return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about tracked versions."""
        total_specs = len(self.versions_index)
        total_versions = sum(len(versions) for versions in self.versions_index.values())
        
        specs_by_kind = {}
        for spec_key in self.versions_index:
            kind = spec_key.split('/')[0]
            specs_by_kind[kind] = specs_by_kind.get(kind, 0) + 1
        
        return {
            "total_specifications": total_specs,
            "total_versions": total_versions,
            "specifications_by_kind": specs_by_kind,
            "storage_path": str(self.storage_path)
        }


def track_specification_version(spec: Dict[str, Any], service: Optional[ConfigurationVersionService] = None) -> str:
    """Convenience function to track a specification version."""
    if not service:
        service = ConfigurationVersionService()
    return service.track_specification_version(spec)