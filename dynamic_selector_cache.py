"""
Dynamic Selector Cache Implementation
Version 1.0 - High-performance caching system for adaptive selectors

This module provides intelligent caching, learning, and performance optimization
for the Adaptive Selector Evolution System.
"""

import json
import os
import time
import uuid
import threading
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import hashlib

from dynamic_selector_cache_schema import (
    CachedSelectorEntry, ElementFingerprint, SelectorVersion, ExecutionMetrics,
    LearningData, AutomationIdPattern, CacheConfiguration, CacheMetrics,
    SelectorStrategy, PatternType, dataclass_to_dict, validate_cache_entry,
    CACHE_SCHEMA_VERSION, DEFAULT_CACHE_CONFIG
)
from utils import print_info, print_success, print_warning, print_error

class DynamicSelectorCache:
    """
    High-performance cache for adaptive UI selectors
    
    Features:
    - Thread-safe operations
    - Automatic backup and recovery
    - Performance metrics tracking
    - Intelligent cleanup and expiration
    - Pattern learning and prediction
    - Confidence-based selection
    """
    
    def __init__(self, config: Optional[CacheConfiguration] = None):
        """
        Initialize the cache with configuration
        
        Args:
            config: Cache configuration (uses default if None)
        """
        self.config = config or DEFAULT_CACHE_CONFIG
        self.cache: Dict[str, CachedSelectorEntry] = {}
        self.metrics = CacheMetrics()
        self._lock = threading.RLock()
        self._last_cleanup = time.time()
        self._last_backup = time.time()
        
        # Performance tracking
        self._lookup_times: List[float] = []
        self._max_lookup_history = 1000
        
        # Initialize cache
        self._initialize_cache()
    
    def _initialize_cache(self):
        """Initialize cache from disk and perform setup"""
        try:
            # Create cache directory if needed
            cache_dir = Path(self.config.cache_file_path).parent
            cache_dir.mkdir(parents=True, exist_ok=True)
            
            # Load existing cache
            if self._load_cache_from_disk():
                print_success(f"Cache loaded: {len(self.cache)} entries")
            else:
                print_info("Starting with empty cache")
            
            # Perform initial cleanup
            self._cleanup_expired_entries()
            
            print_info(f"Cache initialized with {len(self.cache)} entries")
            
        except Exception as e:
            print_error(f"Cache initialization failed: {str(e)}")
            # Continue with empty cache
            self.cache = {}
    
    def _load_cache_from_disk(self) -> bool:
        """
        Load cache from disk file
        
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        if not os.path.exists(self.config.cache_file_path):
            return False
        
        try:
            with open(self.config.cache_file_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Validate schema version
            schema_version = cache_data.get('schema_version', '0.0')
            if schema_version != CACHE_SCHEMA_VERSION:
                print_warning(f"Cache schema version mismatch: {schema_version} vs {CACHE_SCHEMA_VERSION}")
                # TODO: Implement migration logic here
                return False
            
            # Load entries
            entries_data = cache_data.get('entries', {})
            for cache_id, entry_data in entries_data.items():
                try:
                    entry = self._deserialize_cache_entry(entry_data)
                    self.cache[cache_id] = entry
                except Exception as e:
                    print_warning(f"Failed to load cache entry {cache_id}: {str(e)}")
                    continue
            
            # Load metrics if available
            if 'metrics' in cache_data:
                self._load_metrics(cache_data['metrics'])
            
            return True
            
        except Exception as e:
            print_error(f"Failed to load cache from disk: {str(e)}")
            return False
    
    def _save_cache_to_disk(self) -> bool:
        """
        Save cache to disk file
        
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            # Prepare data for serialization
            cache_data = {
                'schema_version': CACHE_SCHEMA_VERSION,
                'saved_at': datetime.now().isoformat(),
                'entries': {},
                'metrics': self._serialize_metrics(),
                'config': dataclass_to_dict(self.config)
            }
            
            # Serialize cache entries
            for cache_id, entry in self.cache.items():
                try:
                    cache_data['entries'][cache_id] = self._serialize_cache_entry(entry)
                except Exception as e:
                    print_warning(f"Failed to serialize cache entry {cache_id}: {str(e)}")
                    continue
            
            # Create backup of existing file
            if os.path.exists(self.config.cache_file_path) and self.config.backup_enabled:
                backup_path = f"{self.config.cache_file_path}.backup"
                shutil.copy2(self.config.cache_file_path, backup_path)
            
            # Write to temporary file first, then rename (atomic operation)
            temp_path = f"{self.config.cache_file_path}.tmp"
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            # Atomic rename
            os.replace(temp_path, self.config.cache_file_path)
            
            return True
            
        except Exception as e:
            print_error(f"Failed to save cache to disk: {str(e)}")
            return False
    
    def _serialize_cache_entry(self, entry: CachedSelectorEntry) -> Dict[str, Any]:
        """Serialize cache entry to dictionary"""
        return dataclass_to_dict(entry)
    
    def _deserialize_cache_entry(self, data: Dict[str, Any]) -> CachedSelectorEntry:
        """Deserialize dictionary to cache entry"""
        # This is a simplified version - in production, you'd want more robust deserialization
        # with proper type checking and validation
        
        # Convert nested dictionaries back to dataclass objects
        fingerprint_data = data.get('element_fingerprint', {})
        fingerprint = ElementFingerprint(**fingerprint_data)
        
        # Deserialize selector versions
        versions = []
        for version_data in data.get('selector_versions', []):
            version = SelectorVersion(
                version=version_data.get('version', 1),
                xml_content=version_data.get('xml_content', ''),
                strategy=SelectorStrategy(version_data.get('strategy', 'automation_id')),
                success_count=version_data.get('success_count', 0),
                failure_count=version_data.get('failure_count', 0),
                avg_execution_time=version_data.get('avg_execution_time', 0.0),
                confidence_score=version_data.get('confidence_score', 0.0),
                reliability_percentage=version_data.get('reliability_percentage', 0.0),
                created_at=version_data.get('created_at', ''),
                created_by=version_data.get('created_by', 'user')
            )
            versions.append(version)
        
        # Create entry
        entry = CachedSelectorEntry(
            cache_id=data.get('cache_id', str(uuid.uuid4())),
            element_fingerprint=fingerprint,
            selector_versions=versions,
            current_version=data.get('current_version', 1),
            current_automation_id=data.get('current_automation_id'),
            overall_confidence=data.get('overall_confidence', 0.0),
            created_at=data.get('created_at', datetime.now().isoformat()),
            last_accessed=data.get('last_accessed', datetime.now().isoformat()),
            last_updated=data.get('last_updated', datetime.now().isoformat()),
            access_count=data.get('access_count', 0)
        )
        
        return entry
    
    def _serialize_metrics(self) -> Dict[str, Any]:
        """Serialize metrics to dictionary"""
        return {
            'hit_count': self.metrics.hit_count,
            'miss_count': self.metrics.miss_count,
            'total_requests': self.metrics.total_requests,
            'avg_lookup_time': self.metrics.avg_lookup_time,
            'cache_size': len(self.cache),
            'patterns_discovered': self.metrics.patterns_discovered,
            'successful_predictions': self.metrics.successful_predictions,
            'healing_success_rate': self.metrics.healing_success_rate,
            'performance_improvement': self.metrics.performance_improvement,
            'last_reset': self.metrics.last_reset
        }
    
    def _load_metrics(self, metrics_data: Dict[str, Any]):
        """Load metrics from dictionary"""
        self.metrics.hit_count = metrics_data.get('hit_count', 0)
        self.metrics.miss_count = metrics_data.get('miss_count', 0)
        self.metrics.total_requests = metrics_data.get('total_requests', 0)
        self.metrics.avg_lookup_time = metrics_data.get('avg_lookup_time', 0.0)
        self.metrics.patterns_discovered = metrics_data.get('patterns_discovered', 0)
        self.metrics.successful_predictions = metrics_data.get('successful_predictions', 0)
        self.metrics.healing_success_rate = metrics_data.get('healing_success_rate', 0.0)
        self.metrics.performance_improvement = metrics_data.get('performance_improvement', 0.0)
        self.metrics.last_reset = metrics_data.get('last_reset', datetime.now().isoformat())
    
    def create_cache_id(self, fingerprint: ElementFingerprint) -> str:
        """
        Create unique cache ID from element fingerprint
        
        Args:
            fingerprint: Element fingerprint
            
        Returns:
            str: Unique cache ID
        """
        # Create deterministic ID based on stable attributes
        id_components = [
            fingerprint.name or '',
            fingerprint.class_name or '',
            fingerprint.control_type or '',
            fingerprint.window_title or '',
            fingerprint.window_class or '',
            str(fingerprint.sibling_index or 0),
            str(fingerprint.same_type_index or 0)
        ]
        
        # Create hash of components
        id_string = '|'.join(id_components)
        cache_id = hashlib.md5(id_string.encode('utf-8')).hexdigest()
        
        return f"cache_{cache_id[:16]}"
    
    def put(self, fingerprint: ElementFingerprint, xml_selector: str, 
            strategy: SelectorStrategy, automation_id: Optional[str] = None,
            confidence: float = 0.5) -> str:
        """
        Store selector in cache
        
        Args:
            fingerprint: Element fingerprint for identification
            xml_selector: XML selector content
            strategy: Strategy used to create selector
            automation_id: Current AutomationId (if any)
            confidence: Initial confidence score
            
        Returns:
            str: Cache ID of stored entry
        """
        start_time = time.time()
        
        with self._lock:
            try:
                cache_id = self.create_cache_id(fingerprint)
                
                # Check if entry already exists
                if cache_id in self.cache:
                    # Add new version to existing entry
                    entry = self.cache[cache_id]
                    new_version = len(entry.selector_versions) + 1
                    
                    # Create new selector version
                    selector_version = SelectorVersion(
                        version=new_version,
                        xml_content=xml_selector,
                        strategy=strategy,
                        confidence_score=confidence,
                        created_at=datetime.now().isoformat(),
                        created_by="adaptive_system"
                    )
                    
                    # Add to entry
                    entry.selector_versions.insert(0, selector_version)  # Insert at beginning (newest first)
                    entry.current_version = new_version
                    entry.last_updated = datetime.now().isoformat()
                    
                    # Update AutomationId if provided
                    if automation_id:
                        self._update_automation_id(entry, automation_id)
                    
                    # Trim old versions if too many
                    max_versions = self.config.max_versions_per_entry
                    if len(entry.selector_versions) > max_versions:
                        entry.selector_versions = entry.selector_versions[:max_versions]
                    
                    # Recalculate overall confidence
                    entry.overall_confidence = self._calculate_overall_confidence(entry)
                    
                else:
                    # Create new entry
                    selector_version = SelectorVersion(
                        version=1,
                        xml_content=xml_selector,
                        strategy=strategy,
                        confidence_score=confidence,
                        created_at=datetime.now().isoformat(),
                        created_by="adaptive_system"
                    )
                    
                    entry = CachedSelectorEntry(
                        cache_id=cache_id,
                        element_fingerprint=fingerprint,
                        selector_versions=[selector_version],
                        current_version=1,
                        current_automation_id=automation_id,
                        overall_confidence=confidence,
                        created_at=datetime.now().isoformat(),
                        last_accessed=datetime.now().isoformat(),
                        last_updated=datetime.now().isoformat(),
                        access_count=0
                    )
                    
                    # Initialize AutomationId history
                    if automation_id:
                        entry.automation_id_history = [{
                            'value': automation_id,
                            'timestamp': datetime.now().isoformat()
                        }]
                    
                    self.cache[cache_id] = entry
                
                # Validate entry
                validation_errors = validate_cache_entry(entry)
                if validation_errors:
                    print_warning(f"Cache entry validation warnings: {validation_errors}")
                
                # Update metrics
                lookup_time = time.time() - start_time
                self._update_lookup_metrics(lookup_time)
                
                # Trigger maintenance if needed
                self._maybe_trigger_maintenance()
                
                print_info(f"Cached selector for {cache_id} (strategy: {strategy.value})")
                return cache_id
                
            except Exception as e:
                print_error(f"Failed to cache selector: {str(e)}")
                return ""
    
    def get(self, fingerprint: ElementFingerprint, 
            preferred_strategies: Optional[List[SelectorStrategy]] = None) -> Optional[CachedSelectorEntry]:
        """
        Retrieve best matching selector from cache
        
        Args:
            fingerprint: Element fingerprint to search for
            preferred_strategies: Preferred strategies in order of preference
            
        Returns:
            CachedSelectorEntry: Best matching entry or None
        """
        start_time = time.time()
        
        with self._lock:
            try:
                self.metrics.total_requests += 1
                
                cache_id = self.create_cache_id(fingerprint)
                
                # Direct cache hit
                if cache_id in self.cache:
                    entry = self.cache[cache_id]
                    
                    # Update access tracking
                    entry.last_accessed = datetime.now().isoformat()
                    entry.access_count += 1
                    
                    # Filter by preferred strategies if specified
                    if preferred_strategies:
                        best_version = self._find_best_version_by_strategy(entry, preferred_strategies)
                        if best_version:
                            # Create a copy with only the best version for this request
                            filtered_entry = self._create_filtered_entry(entry, best_version)
                            self.metrics.hit_count += 1
                            lookup_time = time.time() - start_time
                            self._update_lookup_metrics(lookup_time)
                            return filtered_entry
                    else:
                        # Return entry with current version
                        self.metrics.hit_count += 1
                        lookup_time = time.time() - start_time
                        self._update_lookup_metrics(lookup_time)
                        return entry
                
                # Cache miss - try fuzzy matching
                fuzzy_match = self._find_fuzzy_match(fingerprint, preferred_strategies)
                if fuzzy_match:
                    self.metrics.hit_count += 1  # Count as hit since we found something useful
                    lookup_time = time.time() - start_time
                    self._update_lookup_metrics(lookup_time)
                    return fuzzy_match
                
                # Complete miss
                self.metrics.miss_count += 1
                lookup_time = time.time() - start_time
                self._update_lookup_metrics(lookup_time)
                return None
                
            except Exception as e:
                print_error(f"Cache lookup failed: {str(e)}")
                self.metrics.miss_count += 1
                return None
    
    def update_execution_result(self, cache_id: str, success: bool, 
                              execution_time: float, version: Optional[int] = None) -> bool:
        """
        Update execution metrics for a cached selector
        
        Args:
            cache_id: Cache ID of the entry
            success: Whether execution was successful
            execution_time: Time taken for execution
            version: Specific version to update (current if None)
            
        Returns:
            bool: True if updated successfully
        """
        with self._lock:
            try:
                if cache_id not in self.cache:
                    return False
                
                entry = self.cache[cache_id]
                
                # Find the version to update
                target_version = version or entry.current_version
                selector_version = None
                
                for sv in entry.selector_versions:
                    if sv.version == target_version:
                        selector_version = sv
                        break
                
                if not selector_version:
                    return False
                
                # Update version metrics
                if success:
                    selector_version.success_count += 1
                    selector_version.last_success = datetime.now().isoformat()
                else:
                    selector_version.failure_count += 1
                    selector_version.last_failure = datetime.now().isoformat()
                
                # Update average execution time
                total_executions = selector_version.success_count + selector_version.failure_count
                current_avg = selector_version.avg_execution_time
                selector_version.avg_execution_time = (
                    (current_avg * (total_executions - 1) + execution_time) / total_executions
                )
                
                # Update reliability percentage
                if total_executions > 0:
                    selector_version.reliability_percentage = (
                        selector_version.success_count / total_executions
                    ) * 100
                
                # Update overall entry metrics
                entry.execution_metrics.total_executions += 1
                if success:
                    entry.execution_metrics.successful_executions += 1
                else:
                    entry.execution_metrics.failed_executions += 1
                
                # Update overall confidence
                entry.overall_confidence = self._calculate_overall_confidence(entry)
                entry.last_updated = datetime.now().isoformat()
                
                return True
                
            except Exception as e:
                print_error(f"Failed to update execution result: {str(e)}")
                return False
    
    def update_automation_id(self, cache_id: str, new_automation_id: str) -> bool:
        """
        Update AutomationId for a cached entry
        
        Args:
            cache_id: Cache ID of the entry
            new_automation_id: New AutomationId value
            
        Returns:
            bool: True if updated successfully
        """
        with self._lock:
            try:
                if cache_id not in self.cache:
                    return False
                
                entry = self.cache[cache_id]
                return self._update_automation_id(entry, new_automation_id)
                
            except Exception as e:
                print_error(f"Failed to update AutomationId: {str(e)}")
                return False
    
    def _update_automation_id(self, entry: CachedSelectorEntry, new_automation_id: str) -> bool:
        """Internal method to update AutomationId"""
        try:
            # Don't update if it's the same
            if entry.current_automation_id == new_automation_id:
                return True
            
            # Add to history
            history_entry = {
                'value': new_automation_id,
                'timestamp': datetime.now().isoformat()
            }
            entry.automation_id_history.append(history_entry)
            
            # Keep only recent history (last 20 entries)
            if len(entry.automation_id_history) > 20:
                entry.automation_id_history = entry.automation_id_history[-20:]
            
            # Update current value
            old_automation_id = entry.current_automation_id
            entry.current_automation_id = new_automation_id
            entry.last_updated = datetime.now().isoformat()
            
            # Analyze pattern if we have enough data
            if len(entry.automation_id_history) >= 3:
                self._analyze_automation_id_pattern(entry)
            
            print_info(f"AutomationId updated: {old_automation_id} → {new_automation_id}")
            return True
            
        except Exception as e:
            print_error(f"AutomationId update failed: {str(e)}")
            return False
    
    def _analyze_automation_id_pattern(self, entry: CachedSelectorEntry):
        """Analyze AutomationId change patterns for prediction"""
        try:
            history = entry.automation_id_history
            if len(history) < 3:
                return
            
            values = [h['value'] for h in history[-10:]]  # Last 10 values
            
            # Simple pattern detection (could be much more sophisticated)
            pattern_detected = False
            pattern_type = PatternType.RANDOM
            
            # Check for numeric sequence
            if all(v.isdigit() for v in values):
                numbers = [int(v) for v in values]
                if self._is_arithmetic_sequence(numbers):
                    pattern_type = PatternType.SEQUENTIAL_NUMERIC
                    pattern_detected = True
            
            # Check for timestamp patterns
            elif any(len(v) >= 10 and v.isdigit() for v in values):
                pattern_type = PatternType.TIMESTAMP_BASED
                pattern_detected = True
            
            # Check for hash patterns
            elif all(len(v) >= 8 and all(c.isalnum() for c in v) for v in values):
                pattern_type = PatternType.HASH_BASED
                pattern_detected = True
            
            if pattern_detected:
                # Create or update pattern
                if not entry.automation_id_pattern:
                    entry.automation_id_pattern = AutomationIdPattern(
                        pattern_type=pattern_type,
                        confidence=0.7,
                        pattern_data={},
                        observed_values=values,
                        change_timestamps=[h['timestamp'] for h in history[-10:]],
                        discovered_at=datetime.now().isoformat(),
                        sample_size=len(values)
                    )
                    self.metrics.patterns_discovered += 1
                else:
                    # Update existing pattern
                    entry.automation_id_pattern.observed_values = values
                    entry.automation_id_pattern.change_timestamps = [h['timestamp'] for h in history[-10:]]
                    entry.automation_id_pattern.last_updated = datetime.now().isoformat()
                    entry.automation_id_pattern.sample_size = len(values)
                
                print_info(f"AutomationId pattern detected: {pattern_type.value}")
        
        except Exception as e:
            print_warning(f"Pattern analysis failed: {str(e)}")
    
    def _is_arithmetic_sequence(self, numbers: List[int]) -> bool:
        """Check if numbers form an arithmetic sequence"""
        if len(numbers) < 3:
            return False
        
        diff = numbers[1] - numbers[0]
        for i in range(2, len(numbers)):
            if numbers[i] - numbers[i-1] != diff:
                return False
        return True
    
    def _find_best_version_by_strategy(self, entry: CachedSelectorEntry, 
                                     preferred_strategies: List[SelectorStrategy]) -> Optional[SelectorVersion]:
        """Find best version matching preferred strategies"""
        for strategy in preferred_strategies:
            for version in entry.selector_versions:
                if version.strategy == strategy and version.confidence_score > 0.3:
                    return version
        
        # If no preferred strategy found, return highest confidence version
        if entry.selector_versions:
            return max(entry.selector_versions, key=lambda v: v.confidence_score)
        
        return None
    
    def _create_filtered_entry(self, original_entry: CachedSelectorEntry, 
                             target_version: SelectorVersion) -> CachedSelectorEntry:
        """Create a copy of entry with only the target version"""
        filtered_entry = CachedSelectorEntry(
            cache_id=original_entry.cache_id,
            element_fingerprint=original_entry.element_fingerprint,
            selector_versions=[target_version],
            current_version=target_version.version,
            current_automation_id=original_entry.current_automation_id,
            automation_id_pattern=original_entry.automation_id_pattern,
            automation_id_history=original_entry.automation_id_history,
            execution_metrics=original_entry.execution_metrics,
            overall_confidence=target_version.confidence_score,
            learning_data=original_entry.learning_data,
            created_at=original_entry.created_at,
            last_accessed=original_entry.last_accessed,
            last_updated=original_entry.last_updated,
            access_count=original_entry.access_count
        )
        return filtered_entry
    
    def _find_fuzzy_match(self, fingerprint: ElementFingerprint, 
                         preferred_strategies: Optional[List[SelectorStrategy]] = None) -> Optional[CachedSelectorEntry]:
        """Find fuzzy matches based on similarity scoring"""
        best_match = None
        best_score = 0.0
        min_threshold = 0.6  # Minimum similarity threshold
        
        for entry in self.cache.values():
            similarity = self._calculate_fingerprint_similarity(fingerprint, entry.element_fingerprint)
            
            if similarity >= min_threshold and similarity > best_score:
                # Check if entry has suitable strategies
                if preferred_strategies:
                    has_preferred = any(v.strategy in preferred_strategies for v in entry.selector_versions)
                    if not has_preferred:
                        continue
                
                best_match = entry
                best_score = similarity
        
        if best_match:
            print_info(f"Fuzzy match found with {best_score:.2f} similarity")
        
        return best_match
    
    def _calculate_fingerprint_similarity(self, fp1: ElementFingerprint, fp2: ElementFingerprint) -> float:
        """Calculate similarity score between two fingerprints"""
        score = 0.0
        total_weight = 0.0
        
        # Weighted comparison of attributes
        comparisons = [
            ('name', 0.25, fp1.name, fp2.name),
            ('class_name', 0.20, fp1.class_name, fp2.class_name),
            ('control_type', 0.30, fp1.control_type, fp2.control_type),
            ('window_title', 0.15, fp1.window_title, fp2.window_title),
            ('sibling_index', 0.10, fp1.sibling_index, fp2.sibling_index)
        ]
        
        for attr_name, weight, val1, val2 in comparisons:
            total_weight += weight
            
            if val1 is None and val2 is None:
                score += weight  # Both None counts as match
            elif val1 is not None and val2 is not None:
                if val1 == val2:
                    score += weight  # Exact match
                elif isinstance(val1, str) and isinstance(val2, str):
                    # Partial string match
                    if val1.lower() in val2.lower() or val2.lower() in val1.lower():
                        score += weight * 0.5
            # Different values or one None = no score
        
        return score / total_weight if total_weight > 0 else 0.0
    
    def _calculate_overall_confidence(self, entry: CachedSelectorEntry) -> float:
        """Calculate overall confidence based on all versions"""
        if not entry.selector_versions:
            return 0.0
        
        # Weighted average based on reliability and recency
        total_weight = 0.0
        weighted_sum = 0.0
        
        for version in entry.selector_versions:
            # Weight based on reliability and execution count
            execution_count = version.success_count + version.failure_count
            reliability_weight = (version.reliability_percentage / 100.0) if execution_count > 0 else version.confidence_score
            recency_weight = 1.0 / version.version  # Newer versions get higher weight
            
            weight = reliability_weight * recency_weight * max(execution_count, 1)
            weighted_sum += version.confidence_score * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _update_lookup_metrics(self, lookup_time: float):
        """Update lookup performance metrics"""
        self._lookup_times.append(lookup_time)
        
        # Keep only recent lookup times
        if len(self._lookup_times) > self._max_lookup_history:
            self._lookup_times = self._lookup_times[-self._max_lookup_history:]
        
        # Update average
        if self._lookup_times:
            self.metrics.avg_lookup_time = sum(self._lookup_times) / len(self._lookup_times)
    
    def _maybe_trigger_maintenance(self):
        """Trigger maintenance tasks if needed"""
        current_time = time.time()
        
        # Cleanup check
        cleanup_interval = self.config.cleanup_interval_hours * 3600
        if current_time - self._last_cleanup > cleanup_interval:
            self._cleanup_expired_entries()
            self._last_cleanup = current_time
        
        # Backup check
        backup_interval = self.config.backup_interval_hours * 3600
        if current_time - self._last_backup > backup_interval:
            self._backup_cache()
            self._last_backup = current_time
        
        # Size check
        if len(self.cache) > self.config.max_cache_entries:
            self._evict_least_useful_entries()
    
    def _cleanup_expired_entries(self):
        """Remove expired and low-confidence entries"""
        current_time = datetime.now()
        expired_keys = []
        
        for cache_id, entry in self.cache.items():
            # Check expiration
            if entry.expires_at:
                expires_at = datetime.fromisoformat(entry.expires_at)
                if current_time > expires_at:
                    expired_keys.append(cache_id)
                    continue
            
            # Check confidence threshold
            if entry.auto_cleanup and entry.overall_confidence < entry.cleanup_threshold:
                # Check if unused for a while
                last_accessed = datetime.fromisoformat(entry.last_accessed)
                days_unused = (current_time - last_accessed).days
                
                if days_unused > self.config.unused_expire_days:
                    expired_keys.append(cache_id)
        
        # Remove expired entries
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            print_info(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def _evict_least_useful_entries(self):
        """Evict least useful entries when cache is full"""
        if len(self.cache) <= self.config.max_cache_entries:
            return
        
        # Sort entries by usefulness score
        entries_with_scores = []
        for cache_id, entry in self.cache.items():
            score = self._calculate_usefulness_score(entry)
            entries_with_scores.append((cache_id, score))
        
        # Sort by score (ascending - least useful first)
        entries_with_scores.sort(key=lambda x: x[1])
        
        # Remove least useful entries
        entries_to_remove = len(self.cache) - self.config.max_cache_entries + 100  # Remove extra to avoid frequent evictions
        for i in range(min(entries_to_remove, len(entries_with_scores))):
            cache_id = entries_with_scores[i][0]
            del self.cache[cache_id]
        
        print_info(f"Evicted {entries_to_remove} least useful cache entries")
    
    def _calculate_usefulness_score(self, entry: CachedSelectorEntry) -> float:
        """Calculate usefulness score for cache eviction"""
        score = 0.0
        
        # Confidence factor (40%)
        score += entry.overall_confidence * 0.4
        
        # Access frequency factor (30%)
        access_factor = min(entry.access_count / 100.0, 1.0)  # Normalize to 0-1
        score += access_factor * 0.3
        
        # Recency factor (20%)
        last_accessed = datetime.fromisoformat(entry.last_accessed)
        days_since_access = (datetime.now() - last_accessed).days
        recency_factor = max(0.0, 1.0 - (days_since_access / 30.0))  # Decay over 30 days
        score += recency_factor * 0.2
        
        # Success rate factor (10%)
        if entry.execution_metrics.total_executions > 0:
            success_rate = entry.execution_metrics.successful_executions / entry.execution_metrics.total_executions
            score += success_rate * 0.1
        
        return score
    
    def _backup_cache(self):
        """Create backup of cache file"""
        if not self.config.backup_enabled:
            return
        
        try:
            # Save current cache
            if self._save_cache_to_disk():
                # Create timestamped backup
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_filename = f"{self.config.cache_file_path}.backup_{timestamp}"
                shutil.copy2(self.config.cache_file_path, backup_filename)
                
                # Clean old backups
                self._cleanup_old_backups()
                
                print_info(f"Cache backup created: {backup_filename}")
        
        except Exception as e:
            print_error(f"Backup failed: {str(e)}")
    
    def _cleanup_old_backups(self):
        """Remove old backup files"""
        try:
            cache_dir = Path(self.config.cache_file_path).parent
            pattern = f"{Path(self.config.cache_file_path).name}.backup_*"
            
            backup_files = list(cache_dir.glob(pattern))
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Keep only the most recent backups
            for backup_file in backup_files[self.config.max_backup_files:]:
                backup_file.unlink()
        
        except Exception as e:
            print_warning(f"Backup cleanup failed: {str(e)}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        with self._lock:
            stats = {
                'cache_size': len(self.cache),
                'hit_rate': self.metrics.hit_rate(),
                'miss_rate': self.metrics.miss_rate(),
                'avg_lookup_time': self.metrics.avg_lookup_time,
                'total_requests': self.metrics.total_requests,
                'patterns_discovered': self.metrics.patterns_discovered,
                'successful_predictions': self.metrics.successful_predictions,
                'healing_success_rate': self.metrics.healing_success_rate,
                'performance_improvement': self.metrics.performance_improvement,
                
                # Entry statistics
                'entries_with_patterns': sum(1 for e in self.cache.values() if e.automation_id_pattern),
                'avg_confidence': sum(e.overall_confidence for e in self.cache.values()) / len(self.cache) if self.cache else 0.0,
                'high_confidence_entries': sum(1 for e in self.cache.values() if e.overall_confidence >= 0.8),
                'low_confidence_entries': sum(1 for e in self.cache.values() if e.overall_confidence < 0.5),
                
                # Strategy distribution
                'strategy_distribution': self._get_strategy_distribution(),
                
                # Recent performance
                'recent_lookup_times': self._lookup_times[-10:] if self._lookup_times else []
            }
            
            return stats
    
    def _get_strategy_distribution(self) -> Dict[str, int]:
        """Get distribution of strategies across all cached versions"""
        distribution = {}
        
        for entry in self.cache.values():
            for version in entry.selector_versions:
                strategy_name = version.strategy.value
                distribution[strategy_name] = distribution.get(strategy_name, 0) + 1
        
        return distribution
    
    def save_cache(self) -> bool:
        """Manually save cache to disk"""
        with self._lock:
            return self._save_cache_to_disk()
    
    def clear_cache(self) -> bool:
        """Clear all cache entries"""
        with self._lock:
            self.cache.clear()
            self.metrics = CacheMetrics()
            print_info("Cache cleared")
            return True
    
    def remove_entry(self, cache_id: str) -> bool:
        """Remove specific cache entry"""
        with self._lock:
            if cache_id in self.cache:
                del self.cache[cache_id]
                print_info(f"Removed cache entry: {cache_id}")
                return True
            return False
    
    def get_entry_count(self) -> int:
        """Get total number of cached entries"""
        return len(self.cache)
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - save cache"""
        self.save_cache()