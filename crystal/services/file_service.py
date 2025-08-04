"""
File Service - File System Integration

Implements file system integration as outlined in PROJECT_OVERVIEW.md core components.
Handles file organization, duplicate detection, and file operations for Ruby assistant.
"""

import asyncio
import shutil
from typing import Dict, Any, List, Optional, Set
from pathlib import Path
import hashlib
import mimetypes
from datetime import datetime
import os

from crystal.utils.logging import CrystalLogger
from config.settings import settings

class FileService:
    """
    File system integration service.
    
    Implements Ruby assistant's file organization capabilities from PROJECT_OVERVIEW.md:
    - Automated file sorting
    - Duplicate detection and cleanup  
    - Folder structure optimization
    - File search and retrieval
    """
    
    def __init__(self):
        self.logger = CrystalLogger("file_service")
        self.allowed_directories = [Path(d) for d in settings.allowed_directories]
        
        # File type categories for organization
        self.file_categories = {
            'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.tiff'],
            'videos': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm'],
            'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma'],
            'archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
            'code': ['.py', '.js', '.html', '.css', '.cpp', '.java', '.cs', '.php'],
            'spreadsheets': ['.xls', '.xlsx', '.csv', '.ods'],
            'presentations': ['.ppt', '.pptx', '.odp']
        }
    
    async def organize_directory(self, directory_path: str, create_subdirs: bool = True) -> Dict[str, Any]:
        """
        Organize files in a directory by type.
        
        Args:
            directory_path: Path to directory to organize
            create_subdirs: Whether to create category subdirectories
            
        Returns:
            Organization result summary
        """
        dir_path = Path(directory_path)
        
        # Security check - ensure directory is allowed
        if not self._is_directory_allowed(dir_path):
            return {
                "success": False,
                "error": f"Directory {directory_path} is not in the allowed directories list"
            }
        
        if not dir_path.exists() or not dir_path.is_dir():
            return {
                "success": False,
                "error": f"Directory {directory_path} does not exist or is not a directory"
            }
        
        self.logger.assistant_action(
            assistant="file_service",
            action="directory_organization_started",
            directory=str(dir_path)
        )
        
        organized_files = {category: [] for category in self.file_categories}
        organized_files['other'] = []
        errors = []
        
        try:
            # Create backup if enabled
            if settings.backup_before_organize:
                await self._create_backup(dir_path)
            
            # Process files
            for file_path in dir_path.iterdir():
                if file_path.is_file():
                    try:
                        category = self._get_file_category(file_path)
                        
                        if create_subdirs:
                            target_dir = dir_path / category
                            target_dir.mkdir(exist_ok=True)
                            target_path = target_dir / file_path.name
                        else:
                            target_path = dir_path / f"{category}_{file_path.name}"
                        
                        # Move file if target doesn't exist
                        if not target_path.exists():
                            shutil.move(str(file_path), str(target_path))
                            organized_files[category].append(str(target_path))
                        else:
                            # Handle duplicates
                            if settings.duplicate_check_enabled:
                                if await self._are_files_identical(file_path, target_path):
                                    file_path.unlink()  # Remove duplicate
                                    organized_files[category].append(f"Removed duplicate: {file_path.name}")
                                else:
                                    # Rename and move
                                    counter = 1
                                    while target_path.exists():
                                        stem = target_path.stem
                                        suffix = target_path.suffix
                                        target_path = target_path.parent / f"{stem}_{counter}{suffix}"
                                        counter += 1
                                    
                                    shutil.move(str(file_path), str(target_path))
                                    organized_files[category].append(str(target_path))
                        
                    except Exception as e:
                        errors.append(f"Error processing {file_path.name}: {str(e)}")
            
            result = {
                "success": True,
                "organized_files": organized_files,
                "total_files": sum(len(files) for files in organized_files.values()),
                "errors": errors,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.logger.assistant_action(
                assistant="file_service",
                action="directory_organization_completed",
                directory=str(dir_path),
                files_organized=result["total_files"]
            )
            
            return result
            
        except Exception as e:
            self.logger.error("directory_organization_failed", directory=str(dir_path), error=str(e))
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def find_duplicates(self, directory_path: str) -> Dict[str, Any]:
        """
        Find duplicate files in a directory.
        
        Args:
            directory_path: Path to directory to scan
            
        Returns:
            Dictionary of duplicate file groups
        """
        dir_path = Path(directory_path)
        
        if not self._is_directory_allowed(dir_path):
            return {"success": False, "error": "Directory not allowed"}
        
        if not dir_path.exists():
            return {"success": False, "error": "Directory does not exist"}
        
        self.logger.assistant_action(
            assistant="file_service",
            action="duplicate_scan_started",
            directory=str(dir_path)
        )
        
        file_hashes: Dict[str, List[str]] = {}
        
        try:
            for file_path in dir_path.rglob('*'):
                if file_path.is_file():
                    file_hash = await self._calculate_file_hash(file_path)
                    if file_hash:
                        if file_hash not in file_hashes:
                            file_hashes[file_hash] = []
                        file_hashes[file_hash].append(str(file_path))
            
            # Find duplicates (groups with more than one file)
            duplicates = {hash_val: files for hash_val, files in file_hashes.items() if len(files) > 1}
            
            result = {
                "success": True,
                "duplicate_groups": len(duplicates),
                "total_duplicates": sum(len(files) - 1 for files in duplicates.values()),
                "duplicates": duplicates,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.logger.assistant_action(
                assistant="file_service",
                action="duplicate_scan_completed",
                directory=str(dir_path),
                duplicate_groups=result["duplicate_groups"]
            )
            
            return result
            
        except Exception as e:
            self.logger.error("duplicate_scan_failed", directory=str(dir_path), error=str(e))
            return {"success": False, "error": str(e)}
    
    async def search_files(self, directory_path: str, pattern: str, include_content: bool = False) -> Dict[str, Any]:
        """
        Search for files by name pattern and optionally content.
        
        Args:
            directory_path: Path to directory to search
            pattern: Search pattern (filename or content)
            include_content: Whether to search file contents
            
        Returns:
            Search results
        """
        dir_path = Path(directory_path)
        
        if not self._is_directory_allowed(dir_path):
            return {"success": False, "error": "Directory not allowed"}
        
        matches = []
        
        try:
            for file_path in dir_path.rglob('*'):
                if file_path.is_file():
                    # Search filename
                    if pattern.lower() in file_path.name.lower():
                        matches.append({
                            "path": str(file_path),
                            "name": file_path.name,
                            "size": file_path.stat().st_size,
                            "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                            "match_type": "filename"
                        })
                    
                    # Search content for text files
                    elif include_content and self._is_text_file(file_path):
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                if pattern.lower() in content.lower():
                                    matches.append({
                                        "path": str(file_path),
                                        "name": file_path.name,
                                        "size": file_path.stat().st_size,
                                        "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                                        "match_type": "content"
                                    })
                        except Exception:
                            continue  # Skip files that can't be read
            
            return {
                "success": True,
                "matches": matches,
                "count": len(matches),
                "pattern": pattern,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error("file_search_failed", directory=str(dir_path), error=str(e))
            return {"success": False, "error": str(e)}
    
    def _is_directory_allowed(self, directory: Path) -> bool:
        """Check if directory is in allowed directories list."""
        if not settings.allow_file_operations:
            return False
        
        directory = directory.resolve()
        return any(directory.is_relative_to(allowed) for allowed in self.allowed_directories)
    
    def _get_file_category(self, file_path: Path) -> str:
        """Determine file category based on extension."""
        extension = file_path.suffix.lower()
        
        for category, extensions in self.file_categories.items():
            if extension in extensions:
                return category
        
        return 'other'
    
    async def _calculate_file_hash(self, file_path: Path) -> Optional[str]:
        """Calculate SHA-256 hash of file."""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return None
    
    async def _are_files_identical(self, file1: Path, file2: Path) -> bool:
        """Check if two files are identical."""
        if file1.stat().st_size != file2.stat().st_size:
            return False
        
        hash1 = await self._calculate_file_hash(file1)
        hash2 = await self._calculate_file_hash(file2)
        
        return hash1 == hash2 if hash1 and hash2 else False
    
    def _is_text_file(self, file_path: Path) -> bool:
        """Check if file is a text file."""
        mime_type, _ = mimetypes.guess_type(str(file_path))
        return bool(mime_type and mime_type.startswith('text/'))
    
    async def _create_backup(self, directory: Path) -> None:
        """Create backup of directory before organization."""
        backup_dir = directory.parent / f"{directory.name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copytree(directory, backup_dir)
        self.logger.info("backup_created", backup_path=str(backup_dir))
