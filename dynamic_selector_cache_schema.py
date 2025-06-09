"""
Dynamic Selector Cache Schema Design
Version 1.0 - Foundation for Adaptive Selector Evolution System

This module defines the complete data schema for storing and managing
intelligent selector metadata, learning patterns, and adaptive improvements.
"""

from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

class SelectorStrategy(Enum):
    """Types of selector strategies available"""
    AUTOMATION_ID = "automation_id"
    NAME_HIERARCHY = "name_hierarchy"
    CLASS_HIERARCHY = "class_hierarchy"
    VISUAL_ANCHOR = "visual_anchor"
    SIBLING_INDEX = "sibling_index"
    COORDINATE_FALLBACK = "coordinate_fallback"
    RELATIONSHIP_BASED = "relationship_based"
    PATTERN_PREDICTED = "pattern_predicted"

class PatternType(Enum):
    """Types of AutomationId change patterns"""
    TIMESTAMP_BASED = "timestamp_based"
    SEQUENTIAL_NUMERIC = "sequential_numeric"
    HASH_BASED = "hash_based"
    SESSION_BASED = "session_based"
    RANDOM = "random"
    STATIC = "static"

class ConfidenceLevel(Enum):
    """Confidence level classifications"""
    EXCELLENT = "excellent"    # 0.9-1.0
    GOOD = "good"             # 0.75-0.89
    MODERATE = "moderate"     # 0.5-0.74
    LOW = "low"               # 0.25-0.49
    POOR = "poor"             # 0.0-0.24

@dataclass
class ElementFingerprint:
    """Unique fingerprint for identifying UI elements"""
    
    # Primary identification attributes
    name: Optional[str] = None
    class_name: Optional[str] = None
    control_type: Optional[str] = None
    localized_control_type: Optional[str] = None
    
    # Hierarchical context
    window_title: Optional[str] = None
    window_class: Optional[str] = None
    parent_chain: List[Dict[str, str]] = None  # Chain of parent elements
    
    # Positional context
    sibling_index: Optional[int] = None
    sibling_count: Optional[int] = None
    same_type_index: Optional[int] = None
    
    # Visual properties
    bounding_rect: Optional[Dict[str, int]] = None
    relative_position: Optional[Dict[str, float]] = None  # Percentage in window
    
    # Content properties
    value: Optional[str] = None
    text_content: Optional[str] = None
    
    # Stability scores for each attribute (0.0-1.0)
    attribute_stability: Dict[str, float] = None
    
    def __post_init__(self):
        if self.parent_chain is None:
            self.parent_chain = []
        if self.attribute_stability is None:
            self.attribute_stability = {}

@dataclass
class AutomationIdPattern:
    """Pattern analysis for AutomationId changes"""
    
    pattern_type: PatternType
    confidence: float  # 0.0-1.0
    
    # Pattern-specific data
    pattern_data: Dict[str, Any]  # Flexible storage for different patterns
    
    # Historical data
    observed_values: List[str]  # Recent AutomationId values
    change_timestamps: List[str]  # When changes were observed
    
    # Prediction capabilities
    can_predict: bool = False
    prediction_accuracy: float = 0.0  # Historical accuracy
    next_predicted_value: Optional[str] = None
    
    # Pattern metadata
    discovered_at: str = ""
    last_updated: str = ""
    sample_size: int = 0

@dataclass
class SelectorVersion:
    """Version of a selector with metadata"""
    
    version: int
    xml_content: str
    strategy: SelectorStrategy
    
    # Performance metrics
    success_count: int = 0
    failure_count: int = 0
    avg_execution_time: float = 0.0
    last_success: Optional[str] = None
    last_failure: Optional[str] = None
    
    # Confidence and reliability
    confidence_score: float = 0.0  # 0.0-1.0
    reliability_percentage: float = 0.0  # Based on success/failure ratio
    
    # Creation metadata
    created_at: str = ""
    created_by: str = "user"  # "user", "adaptive_system", "healing_engine"
    healing_source: Optional[str] = None  # If healed, what was the source strategy
    
    # Validation status
    last_validated: Optional[str] = None
    validation_confidence: float = 0.0

@dataclass
class ExecutionMetrics:
    """Detailed execution performance metrics"""
    
    # Overall statistics
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    
    # Timing metrics
    avg_execution_time: float = 0.0
    min_execution_time: float = 0.0
    max_execution_time: float = 0.0
    
    # Strategy performance
    strategy_success_rates: Dict[SelectorStrategy, float] = None
    strategy_avg_times: Dict[SelectorStrategy, float] = None
    
    # Recent performance (sliding window)
    recent_success_rate: float = 0.0  # Last 10 executions
    performance_trend: str = "stable"  # "improving", "degrading", "stable"
    
    # Failure analysis
    common_failure_reasons: List[str] = None
    failure_patterns: Dict[str, int] = None
    
    def __post_init__(self):
        if self.strategy_success_rates is None:
            self.strategy_success_rates = {}
        if self.strategy_avg_times is None:
            self.strategy_avg_times = {}
        if self.common_failure_reasons is None:
            self.common_failure_reasons = []
        if self.failure_patterns is None:
            self.failure_patterns = {}

@dataclass
class LearningData:
    """Machine learning and pattern recognition data"""
    
    # Element behavior patterns
    stability_patterns: Dict[str, Any] = None
    change_frequency: float = 0.0  # How often element properties change
    
    # Optimal strategies learned
    preferred_strategies: List[SelectorStrategy] = None
    strategy_confidence_map: Dict[SelectorStrategy, float] = None
    
    # Environmental factors
    application_context: Dict[str, str] = None  # App version, framework, etc.
    system_context: Dict[str, str] = None  # OS, resolution, etc.
    
    # Learning metadata
    learning_start_date: str = ""
    last_learning_update: str = ""
    learning_iterations: int = 0
    
    # Prediction models
    automation_id_predictor: Optional[Dict[str, Any]] = None
    stability_predictor: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.stability_patterns is None:
            self.stability_patterns = {}
        if self.preferred_strategies is None:
            self.preferred_strategies = []
        if self.strategy_confidence_map is None:
            self.strategy_confidence_map = {}
        if self.application_context is None:
            self.application_context = {}
        if self.system_context is None:
            self.system_context = {}

@dataclass
class CachedSelectorEntry:
    """Complete cached entry for a UI element"""
    
    # Unique identification
    cache_id: str  # UUID for this cache entry
    element_fingerprint: ElementFingerprint
    
    # Selector versions (ordered by creation time, newest first)
    selector_versions: List[SelectorVersion] = None
    current_version: int = 1
    
    # AutomationId intelligence
    current_automation_id: Optional[str] = None
    automation_id_pattern: Optional[AutomationIdPattern] = None
    automation_id_history: List[Dict[str, str]] = None  # {value, timestamp}
    
    # Performance and reliability
    execution_metrics: ExecutionMetrics = None
    overall_confidence: float = 0.0  # Weighted average of all versions
    
    # Learning and adaptation
    learning_data: LearningData = None
    
    # Cache management
    created_at: str = ""
    last_accessed: str = ""
    last_updated: str = ""
    access_count: int = 0
    
    # Expiration and cleanup
    expires_at: Optional[str] = None
    auto_cleanup: bool = True
    cleanup_threshold: float = 0.1  # Cleanup if confidence below this
    
    # Metadata
    tags: List[str] = None  # For categorization and search
    notes: Optional[str] = None
    
    def __post_init__(self):
        if self.selector_versions is None:
            self.selector_versions = []
        if self.automation_id_history is None:
            self.automation_id_history = []
        if self.execution_metrics is None:
            self.execution_metrics = ExecutionMetrics()
        if self.learning_data is None:
            self.learning_data = LearningData()
        if self.tags is None:
            self.tags = []

@dataclass
class CacheConfiguration:
    """Configuration for cache behavior and policies"""
    
    # Storage settings
    cache_file_path: str = "adaptive_selector_cache.json"
    backup_enabled: bool = True
    backup_interval_hours: int = 24
    max_backup_files: int = 7
    
    # Performance settings
    max_cache_entries: int = 10000
    max_versions_per_entry: int = 5
    cleanup_interval_hours: int = 6
    
    # Confidence and expiration policies
    min_confidence_threshold: float = 0.1
    auto_expire_days: int = 30
    unused_expire_days: int = 7
    
    # Learning settings
    learning_enabled: bool = True
    pattern_detection_min_samples: int = 3
    prediction_confidence_threshold: float = 0.7
    
    # Monitoring settings
    metrics_enabled: bool = True
    detailed_logging: bool = False
    performance_tracking: bool = True
    
    # Advanced settings
    parallel_execution_enabled: bool = True
    cache_warming_enabled: bool = True
    predictive_updates_enabled: bool = True

class CacheMetrics:
    """Runtime metrics for cache performance"""
    
    def __init__(self):
        self.hit_count: int = 0
        self.miss_count: int = 0
        self.total_requests: int = 0
        self.avg_lookup_time: float = 0.0
        self.cache_size: int = 0
        self.memory_usage_mb: float = 0.0
        
        # Learning metrics
        self.patterns_discovered: int = 0
        self.successful_predictions: int = 0
        self.healing_success_rate: float = 0.0
        
        # Performance trends
        self.performance_improvement: float = 0.0  # vs non-adaptive baseline
        
        # Timestamps
        self.metrics_start_time: str = datetime.now().isoformat()
        self.last_reset: str = datetime.now().isoformat()
    
    def hit_rate(self) -> float:
        """Calculate cache hit rate"""
        if self.total_requests == 0:
            return 0.0
        return (self.hit_count / self.total_requests) * 100
    
    def miss_rate(self) -> float:
        """Calculate cache miss rate"""
        return 100.0 - self.hit_rate()

# Schema version for migration purposes
CACHE_SCHEMA_VERSION = "1.0"

# Default configuration instance
DEFAULT_CACHE_CONFIG = CacheConfiguration()

def create_fingerprint_from_element_data(element_data: Dict[str, Any]) -> ElementFingerprint:
    """
    Helper function to create ElementFingerprint from captured element data
    
    Args:
        element_data: Dictionary containing element information from ElementInspector
        
    Returns:
        ElementFingerprint: Structured fingerprint object
    """
    window_info = element_data.get('window_info', {})
    bounding_rect = element_data.get('bounding_rectangle', {})
    
    return ElementFingerprint(
        name=element_data.get('name'),
        class_name=element_data.get('class_name'),
        control_type=element_data.get('control_type'),
        localized_control_type=element_data.get('localized_control_type'),
        window_title=window_info.get('title'),
        window_class=window_info.get('class_name'),
        value=element_data.get('value'),
        bounding_rect=bounding_rect if bounding_rect else None,
        # Calculate relative position if we have both element and window rectangles
        relative_position=_calculate_relative_position(bounding_rect, window_info.get('window_rectangle', {}))
    )

def _calculate_relative_position(element_rect: Dict[str, int], window_rect: Dict[str, int]) -> Optional[Dict[str, float]]:
    """Calculate element position relative to window (as percentages)"""
    if not element_rect or not window_rect:
        return None
    
    try:
        rel_x = ((element_rect['left'] - window_rect['left']) / window_rect['width']) * 100
        rel_y = ((element_rect['top'] - window_rect['top']) / window_rect['height']) * 100
        
        return {
            'x_percent': round(rel_x, 2),
            'y_percent': round(rel_y, 2),
            'width_percent': round((element_rect['width'] / window_rect['width']) * 100, 2),
            'height_percent': round((element_rect['height'] / window_rect['height']) * 100, 2)
        }
    except (KeyError, ZeroDivisionError, TypeError):
        return None

def dataclass_to_dict(obj) -> Dict[str, Any]:
    """Convert dataclass to dictionary for JSON serialization"""
    if hasattr(obj, '__dataclass_fields__'):
        return asdict(obj)
    return obj

def validate_cache_entry(entry: CachedSelectorEntry) -> List[str]:
    """
    Validate cache entry for consistency and completeness
    
    Args:
        entry: Cache entry to validate
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    # Required fields validation
    if not entry.cache_id:
        errors.append("cache_id is required")
    
    if not entry.element_fingerprint:
        errors.append("element_fingerprint is required")
    
    if not entry.selector_versions:
        errors.append("at least one selector_version is required")
    
    # Version consistency
    if entry.current_version > len(entry.selector_versions):
        errors.append("current_version exceeds available versions")
    
    # Confidence bounds validation
    if not 0.0 <= entry.overall_confidence <= 1.0:
        errors.append("overall_confidence must be between 0.0 and 1.0")
    
    # Timestamp validation
    try:
        datetime.fromisoformat(entry.created_at)
    except ValueError:
        errors.append("invalid created_at timestamp format")
    
    return errors

# Export main schema components
__all__ = [
    'SelectorStrategy',
    'PatternType', 
    'ConfidenceLevel',
    'ElementFingerprint',
    'AutomationIdPattern',
    'SelectorVersion',
    'ExecutionMetrics',
    'LearningData',
    'CachedSelectorEntry',
    'CacheConfiguration',
    'CacheMetrics',
    'CACHE_SCHEMA_VERSION',
    'DEFAULT_CACHE_CONFIG',
    'create_fingerprint_from_element_data',
    'dataclass_to_dict',
    'validate_cache_entry'
]