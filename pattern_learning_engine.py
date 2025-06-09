"""
Pattern Learning Engine Core
Version 1.0 - AutomationId pattern detection and prediction system

This module provides advanced pattern recognition and machine learning capabilities
to detect, analyze, and predict AutomationId change patterns for proactive selector healing.
"""

import re
import time
import math
import statistics
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import hashlib

from dynamic_selector_cache_schema import (
    AutomationIdPattern, PatternType, CachedSelectorEntry, 
    LearningData, SelectorStrategy
)
from utils import print_info, print_success, print_warning, print_error

class PredictionAccuracy(Enum):
    """Accuracy levels for pattern predictions"""
    EXCELLENT = "excellent"    # 95%+ accuracy
    GOOD = "good"             # 80-94% accuracy  
    MODERATE = "moderate"     # 60-79% accuracy
    POOR = "poor"             # 40-59% accuracy
    UNRELIABLE = "unreliable" # <40% accuracy

class LearningAlgorithm(Enum):
    """Types of learning algorithms available"""
    STATISTICAL_ANALYSIS = "statistical_analysis"
    PATTERN_MATCHING = "pattern_matching"
    SEQUENCE_PREDICTION = "sequence_prediction"
    BAYESIAN_INFERENCE = "bayesian_inference"
    SIMILARITY_CLUSTERING = "similarity_clustering"

@dataclass
class PatternAnalysisResult:
    """Result of pattern analysis operation"""
    pattern_detected: bool
    pattern_type: PatternType
    confidence: float  # 0.0-1.0
    sample_size: int
    
    # Pattern-specific data
    pattern_data: Dict[str, Any]
    
    # Prediction capabilities
    can_predict: bool = False
    next_predicted_value: Optional[str] = None
    prediction_confidence: float = 0.0
    
    # Analysis metadata
    analysis_method: LearningAlgorithm
    processing_time: float = 0.0
    error_message: Optional[str] = None

@dataclass
class PredictionResult:
    """Result of AutomationId prediction"""
    success: bool
    predicted_value: Optional[str]
    confidence: float
    pattern_type: PatternType
    
    # Supporting information
    pattern_strength: float  # How strong the detected pattern is
    sample_size: int
    prediction_window: int  # How many steps ahead
    
    # Accuracy tracking
    previous_predictions: List[Dict[str, Any]]
    historical_accuracy: float
    
    # Metadata
    prediction_timestamp: str
    expires_at: Optional[str] = None
    reasoning: str = ""

class PatternLearningEngine:
    """
    Advanced pattern learning and prediction engine for AutomationId changes
    
    This engine uses multiple algorithms to detect patterns in AutomationId changes
    and provides predictive capabilities for proactive selector maintenance.
    """
    
    def __init__(self):
        """Initialize the pattern learning engine"""
        self.pattern_analyzers = self._initialize_analyzers()
        self.prediction_cache = {}  # Cache for recent predictions
        self.learning_history = {}  # Track learning evolution
        self.accuracy_tracker = {}  # Track prediction accuracy per pattern type
        
        # Configuration
        self.min_samples_for_pattern = 3
        self.prediction_confidence_threshold = 0.7
        self.max_prediction_window = 5  # Maximum steps ahead to predict
        
        # Performance metrics
        self.total_analyses = 0
        self.successful_patterns = 0
        self.total_predictions = 0
        self.accurate_predictions = 0
        
        print_info("Pattern Learning Engine initialized with 5 analysis algorithms")
    
    def _initialize_analyzers(self) -> Dict[LearningAlgorithm, callable]:
        """Initialize pattern analysis algorithms"""
        return {
            LearningAlgorithm.STATISTICAL_ANALYSIS: self._analyze_statistical_patterns,
            LearningAlgorithm.PATTERN_MATCHING: self._analyze_regex_patterns,
            LearningAlgorithm.SEQUENCE_PREDICTION: self._analyze_sequence_patterns,
            LearningAlgorithm.BAYESIAN_INFERENCE: self._analyze_bayesian_patterns,
            LearningAlgorithm.SIMILARITY_CLUSTERING: self._analyze_similarity_patterns
        }
    
    def analyze_automation_id_pattern(self, automation_id_history: List[Dict[str, str]], 
                                    cache_entry: Optional[CachedSelectorEntry] = None) -> PatternAnalysisResult:
        """
        Analyze AutomationId history to detect patterns
        
        Args:
            automation_id_history: List of {value, timestamp} dictionaries
            cache_entry: Optional cache entry for additional context
            
        Returns:
            PatternAnalysisResult: Comprehensive analysis result
        """
        start_time = time.time()
        self.total_analyses += 1
        
        if len(automation_id_history) < self.min_samples_for_pattern:
            return PatternAnalysisResult(
                pattern_detected=False,
                pattern_type=PatternType.RANDOM,
                confidence=0.0,
                sample_size=len(automation_id_history),
                pattern_data={},
                analysis_method=LearningAlgorithm.STATISTICAL_ANALYSIS,
                processing_time=time.time() - start_time,
                error_message="Insufficient samples for pattern detection"
            )
        
        print_info(f"Analyzing pattern from {len(automation_id_history)} AutomationId samples")
        
        # Extract values and timestamps
        values = [entry['value'] for entry in automation_id_history]
        timestamps = [datetime.fromisoformat(entry['timestamp']) for entry in automation_id_history]
        
        # Try each analyzer in order of effectiveness
        best_result = None
        best_confidence = 0.0
        
        for algorithm, analyzer_func in self.pattern_analyzers.items():
            try:
                print_info(f"Trying {algorithm.value} analysis...")
                
                result = analyzer_func(values, timestamps, cache_entry)
                result.analysis_method = algorithm
                
                if result.pattern_detected and result.confidence > best_confidence:
                    best_result = result
                    best_confidence = result.confidence
                    
                    # If we found a high-confidence pattern, we can stop
                    if result.confidence >= 0.9:
                        break
                        
            except Exception as e:
                print_warning(f"Analysis {algorithm.value} failed: {str(e)}")
                continue
        
        # Use best result or create default
        if best_result:
            best_result.processing_time = time.time() - start_time
            if best_result.pattern_detected:
                self.successful_patterns += 1
                print_success(f"Pattern detected: {best_result.pattern_type.value} (confidence: {best_result.confidence:.2f})")
        else:
            best_result = PatternAnalysisResult(
                pattern_detected=False,
                pattern_type=PatternType.RANDOM,
                confidence=0.0,
                sample_size=len(values),
                pattern_data={},
                analysis_method=LearningAlgorithm.STATISTICAL_ANALYSIS,
                processing_time=time.time() - start_time,
                error_message="No patterns detected by any analyzer"
            )
        
        return best_result
    
    def _analyze_statistical_patterns(self, values: List[str], timestamps: List[datetime], 
                                    context: Optional[CachedSelectorEntry] = None) -> PatternAnalysisResult:
        """Analyze patterns using statistical methods"""
        try:
            # Check for pure numeric sequences
            if all(v.isdigit() for v in values):
                numbers = [int(v) for v in values]
                
                # Check for arithmetic progression
                if len(numbers) >= 3:
                    differences = [numbers[i+1] - numbers[i] for i in range(len(numbers)-1)]
                    
                    if len(set(differences)) == 1:  # All differences are the same
                        step = differences[0]
                        confidence = 0.95  # Very high confidence for arithmetic sequences
                        
                        # Predict next value
                        next_value = str(numbers[-1] + step)
                        
                        return PatternAnalysisResult(
                            pattern_detected=True,
                            pattern_type=PatternType.SEQUENTIAL_NUMERIC,
                            confidence=confidence,
                            sample_size=len(values),
                            pattern_data={
                                "sequence_type": "arithmetic",
                                "step": step,
                                "last_value": numbers[-1],
                                "growth_rate": step,
                                "variance": statistics.variance(differences) if len(differences) > 1 else 0
                            },
                            can_predict=True,
                            next_predicted_value=next_value,
                            prediction_confidence=confidence
                        )
                
                # Check for geometric progression
                if len(numbers) >= 3 and all(n > 0 for n in numbers):
                    ratios = [numbers[i+1] / numbers[i] for i in range(len(numbers)-1)]
                    avg_ratio = statistics.mean(ratios)
                    ratio_variance = statistics.variance(ratios) if len(ratios) > 1 else 0
                    
                    if ratio_variance < 0.1:  # Low variance in ratios
                        confidence = max(0.6, 0.9 - ratio_variance * 5)
                        next_value = str(int(numbers[-1] * avg_ratio))
                        
                        return PatternAnalysisResult(
                            pattern_detected=True,
                            pattern_type=PatternType.SEQUENTIAL_NUMERIC,
                            confidence=confidence,
                            sample_size=len(values),
                            pattern_data={
                                "sequence_type": "geometric",
                                "ratio": avg_ratio,
                                "last_value": numbers[-1],
                                "variance": ratio_variance
                            },
                            can_predict=True,
                            next_predicted_value=next_value,
                            prediction_confidence=confidence
                        )
            
            # Check for timestamp-based patterns
            if any(len(v) >= 10 and v.isdigit() for v in values):
                return self._analyze_timestamp_patterns(values, timestamps)
            
            # Check for hash-based patterns
            if all(len(v) >= 8 and all(c.isalnum() for c in v) for v in values):
                return self._analyze_hash_patterns(values, timestamps)
            
            # No clear statistical pattern
            return PatternAnalysisResult(
                pattern_detected=False,
                pattern_type=PatternType.RANDOM,
                confidence=0.0,
                sample_size=len(values),
                pattern_data={}
            )
            
        except Exception as e:
            return PatternAnalysisResult(
                pattern_detected=False,
                pattern_type=PatternType.RANDOM,
                confidence=0.0,
                sample_size=len(values),
                pattern_data={},
                error_message=str(e)
            )
    
    def _analyze_timestamp_patterns(self, values: List[str], timestamps: List[datetime]) -> PatternAnalysisResult:
        """Analyze timestamp-based patterns in AutomationIds"""
        try:
            # Extract potential timestamps from values
            potential_timestamps = []
            
            for value in values:
                # Look for Unix timestamps (10+ digits)
                timestamp_match = re.search(r'\d{10,}', value)
                if timestamp_match:
                    ts = int(timestamp_match.group())
                    # Check if it's a reasonable timestamp (between 2000 and 2050)
                    if 946684800 <= ts <= 2524608000:  # 2000-01-01 to 2050-01-01
                        potential_timestamps.append(ts)
            
            if len(potential_timestamps) >= 3:
                # Analyze timestamp intervals
                intervals = [potential_timestamps[i+1] - potential_timestamps[i] 
                           for i in range(len(potential_timestamps)-1)]
                
                avg_interval = statistics.mean(intervals)
                interval_variance = statistics.variance(intervals) if len(intervals) > 1 else 0
                
                # Check if intervals are consistent (low variance)
                if interval_variance < (avg_interval * 0.1):  # Variance < 10% of mean
                    confidence = max(0.7, 0.95 - (interval_variance / avg_interval))
                    
                    # Predict next timestamp
                    next_timestamp = potential_timestamps[-1] + int(avg_interval)
                    
                    # Find pattern in value and replace timestamp
                    last_value = values[-1]
                    last_ts_str = str(potential_timestamps[-1])
                    next_value = last_value.replace(last_ts_str, str(next_timestamp))
                    
                    return PatternAnalysisResult(
                        pattern_detected=True,
                        pattern_type=PatternType.TIMESTAMP_BASED,
                        confidence=confidence,
                        sample_size=len(values),
                        pattern_data={
                            "timestamp_format": "unix",
                            "avg_interval_seconds": avg_interval,
                            "interval_variance": interval_variance,
                            "timestamps": potential_timestamps,
                            "value_pattern": last_value.replace(last_ts_str, "{timestamp}")
                        },
                        can_predict=True,
                        next_predicted_value=next_value,
                        prediction_confidence=confidence
                    )
            
            return PatternAnalysisResult(
                pattern_detected=False,
                pattern_type=PatternType.RANDOM,
                confidence=0.0,
                sample_size=len(values),
                pattern_data={}
            )
            
        except Exception as e:
            return PatternAnalysisResult(
                pattern_detected=False,
                pattern_type=PatternType.RANDOM,
                confidence=0.0,
                sample_size=len(values),
                pattern_data={},
                error_message=str(e)
            )
    
    def _analyze_hash_patterns(self, values: List[str], timestamps: List[datetime]) -> PatternAnalysisResult:
        """Analyze hash-based patterns in AutomationIds"""
        try:
            # Check if values look like hashes (hex strings of consistent length)
            hash_lengths = [len(v) for v in values]
            
            if len(set(hash_lengths)) == 1:  # All same length
                hash_length = hash_lengths[0]
                
                # Check if all values are valid hex
                all_hex = all(all(c in '0123456789abcdefABCDEF' for c in v) for v in values)
                
                if all_hex and hash_length in [8, 16, 32, 40, 64]:  # Common hash lengths
                    # Check for time-based correlation
                    time_intervals = []
                    for i in range(len(timestamps) - 1):
                        interval = (timestamps[i+1] - timestamps[i]).total_seconds()
                        time_intervals.append(interval)
                    
                    if time_intervals:
                        avg_time_interval = statistics.mean(time_intervals)
                        time_variance = statistics.variance(time_intervals) if len(time_intervals) > 1 else 0
                        
                        # If hash changes correlate with time intervals
                        if time_variance < (avg_time_interval * 0.2):  # Consistent timing
                            confidence = 0.75  # Medium confidence for hash patterns
                            
                            # For hash patterns, we can't easily predict the exact value
                            # but we can predict when it might change
                            next_change_time = timestamps[-1] + timedelta(seconds=avg_time_interval)
                            
                            return PatternAnalysisResult(
                                pattern_detected=True,
                                pattern_type=PatternType.HASH_BASED,
                                confidence=confidence,
                                sample_size=len(values),
                                pattern_data={
                                    "hash_type": f"{hash_length}-char hex",
                                    "avg_change_interval": avg_time_interval,
                                    "time_variance": time_variance,
                                    "predicted_next_change": next_change_time.isoformat(),
                                    "hash_algorithm_hint": self._guess_hash_algorithm(hash_length)
                                },
                                can_predict=False,  # Can't predict exact hash value
                                prediction_confidence=0.0
                            )
            
            return PatternAnalysisResult(
                pattern_detected=False,
                pattern_type=PatternType.RANDOM,
                confidence=0.0,
                sample_size=len(values),
                pattern_data={}
            )
            
        except Exception as e:
            return PatternAnalysisResult(
                pattern_detected=False,
                pattern_type=PatternType.RANDOM,
                confidence=0.0,
                sample_size=len(values),
                pattern_data={},
                error_message=str(e)
            )
    
    def _guess_hash_algorithm(self, length: int) -> str:
        """Guess hash algorithm based on output length"""
        hash_types = {
            8: "CRC32 or custom",
            16: "MD5 (truncated)",
            32: "MD5",
            40: "SHA-1",
            64: "SHA-256"
        }
        return hash_types.get(length, "Unknown")
    
    def _analyze_regex_patterns(self, values: List[str], timestamps: List[datetime], 
                               context: Optional[CachedSelectorEntry] = None) -> PatternAnalysisResult:
        """Analyze patterns using regex pattern matching"""
        try:
            # Common AutomationId patterns
            patterns = [
                (r'^([a-zA-Z]+)_(\d+)$', "prefix_number"),
                (r'^(\d+)_([a-zA-Z]+)$', "number_suffix"),
                (r'^([a-zA-Z]+)(\d+)([a-zA-Z]+)$', "prefix_number_suffix"),
                (r'^session_(\d+)_(\d+)$', "session_based"),
                (r'^([a-zA-Z]+)_(\d{10,})$', "prefix_timestamp"),
                (r'^(\w+)_([0-9a-f]{8,})$', "prefix_hash"),
                (r'^(\d{4})(\d{2})(\d{2})_(\d+)$', "date_sequence"),
            ]
            
            best_pattern = None
            best_confidence = 0.0
            
            for pattern_regex, pattern_name in patterns:
                matches = []
                for value in values:
                    match = re.match(pattern_regex, value)
                    if match:
                        matches.append(match.groups())
                
                if len(matches) == len(values):  # All values match this pattern
                    confidence = 0.8  # High confidence for complete pattern match
                    
                    # Analyze the variable parts
                    if pattern_name == "prefix_number":
                        # Check if numbers are sequential
                        prefixes = [m[0] for m in matches]
                        numbers = [int(m[1]) for m in matches]
                        
                        if len(set(prefixes)) == 1:  # Same prefix
                            differences = [numbers[i+1] - numbers[i] for i in range(len(numbers)-1)]
                            if len(set(differences)) == 1 and differences[0] > 0:  # Sequential
                                step = differences[0]
                                next_value = f"{prefixes[0]}_{numbers[-1] + step}"
                                
                                return PatternAnalysisResult(
                                    pattern_detected=True,
                                    pattern_type=PatternType.SEQUENTIAL_NUMERIC,
                                    confidence=0.9,
                                    sample_size=len(values),
                                    pattern_data={
                                        "pattern_type": pattern_name,
                                        "prefix": prefixes[0],
                                        "sequence_step": step,
                                        "last_number": numbers[-1]
                                    },
                                    can_predict=True,
                                    next_predicted_value=next_value,
                                    prediction_confidence=0.85
                                )
                    
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_pattern = (pattern_name, matches)
            
            if best_pattern:
                return PatternAnalysisResult(
                    pattern_detected=True,
                    pattern_type=PatternType.SEQUENTIAL_NUMERIC,
                    confidence=best_confidence,
                    sample_size=len(values),
                    pattern_data={
                        "pattern_type": best_pattern[0],
                        "matches": best_pattern[1]
                    },
                    can_predict=False  # Generic patterns can't predict without specific analysis
                )
            
            return PatternAnalysisResult(
                pattern_detected=False,
                pattern_type=PatternType.RANDOM,
                confidence=0.0,
                sample_size=len(values),
                pattern_data={}
            )
            
        except Exception as e:
            return PatternAnalysisResult(
                pattern_detected=False,
                pattern_type=PatternType.RANDOM,
                confidence=0.0,
                sample_size=len(values),
                pattern_data={},
                error_message=str(e)
            )
    
    def _analyze_sequence_patterns(self, values: List[str], timestamps: List[datetime], 
                                 context: Optional[CachedSelectorEntry] = None) -> PatternAnalysisResult:
        """Analyze sequential patterns and cycles"""
        try:
            # Check for repeating cycles
            for cycle_length in range(2, min(len(values) // 2 + 1, 10)):
                is_cycle = True
                for i in range(cycle_length, len(values)):
                    if values[i] != values[i % cycle_length]:
                        is_cycle = False
                        break
                
                if is_cycle:
                    confidence = 0.8
                    next_index = len(values) % cycle_length
                    next_value = values[next_index]
                    
                    return PatternAnalysisResult(
                        pattern_detected=True,
                        pattern_type=PatternType.SEQUENTIAL_NUMERIC,
                        confidence=confidence,
                        sample_size=len(values),
                        pattern_data={
                            "pattern_type": "cyclic",
                            "cycle_length": cycle_length,
                            "cycle_values": values[:cycle_length],
                            "next_index": next_index
                        },
                        can_predict=True,
                        next_predicted_value=next_value,
                        prediction_confidence=confidence
                    )
            
            # Check for alternating patterns (A-B-A-B)
            if len(values) >= 4:
                alternating = True
                for i in range(2, len(values)):
                    if values[i] != values[i % 2]:
                        alternating = False
                        break
                
                if alternating:
                    confidence = 0.75
                    next_value = values[len(values) % 2]
                    
                    return PatternAnalysisResult(
                        pattern_detected=True,
                        pattern_type=PatternType.SEQUENTIAL_NUMERIC,
                        confidence=confidence,
                        sample_size=len(values),
                        pattern_data={
                            "pattern_type": "alternating",
                            "value_a": values[0],
                            "value_b": values[1]
                        },
                        can_predict=True,
                        next_predicted_value=next_value,
                        prediction_confidence=confidence
                    )
            
            return PatternAnalysisResult(
                pattern_detected=False,
                pattern_type=PatternType.RANDOM,
                confidence=0.0,
                sample_size=len(values),
                pattern_data={}
            )
            
        except Exception as e:
            return PatternAnalysisResult(
                pattern_detected=False,
                pattern_type=PatternType.RANDOM,
                confidence=0.0,
                sample_size=len(values),
                pattern_data={},
                error_message=str(e)
            )
    
    def _analyze_bayesian_patterns(self, values: List[str], timestamps: List[datetime], 
                                 context: Optional[CachedSelectorEntry] = None) -> PatternAnalysisResult:
        """Analyze patterns using Bayesian inference"""
        try:
            # Simple Bayesian analysis for session-based patterns
            # Check if AutomationIds reset at certain time intervals
            
            if len(timestamps) >= 3:
                # Calculate time intervals between changes
                intervals = []
                for i in range(len(timestamps) - 1):
                    interval = (timestamps[i+1] - timestamps[i]).total_seconds()
                    intervals.append(interval)
                
                # Check for session boundaries (large gaps)
                avg_interval = statistics.mean(intervals)
                large_gaps = [i for i in intervals if i > avg_interval * 3]
                
                if large_gaps:
                    # Potential session-based pattern
                    confidence = min(0.7, len(large_gaps) / len(intervals) + 0.3)
                    
                    return PatternAnalysisResult(
                        pattern_detected=True,
                        pattern_type=PatternType.SESSION_BASED,
                        confidence=confidence,
                        sample_size=len(values),
                        pattern_data={
                            "session_gaps": large_gaps,
                            "avg_interval": avg_interval,
                            "session_count": len(large_gaps) + 1
                        },
                        can_predict=False  # Session boundaries are hard to predict
                    )
            
            return PatternAnalysisResult(
                pattern_detected=False,
                pattern_type=PatternType.RANDOM,
                confidence=0.0,
                sample_size=len(values),
                pattern_data={}
            )
            
        except Exception as e:
            return PatternAnalysisResult(
                pattern_detected=False,
                pattern_type=PatternType.RANDOM,
                confidence=0.0,
                sample_size=len(values),
                pattern_data={},
                error_message=str(e)
            )
    
    def _analyze_similarity_patterns(self, values: List[str], timestamps: List[datetime], 
                                   context: Optional[CachedSelectorEntry] = None) -> PatternAnalysisResult:
        """Analyze patterns using string similarity clustering"""
        try:
            # Calculate similarity matrix
            similarities = []
            for i in range(len(values)):
                for j in range(i + 1, len(values)):
                    similarity = self._calculate_string_similarity(values[i], values[j])
                    similarities.append(similarity)
            
            if similarities:
                avg_similarity = statistics.mean(similarities)
                
                # If values are very similar, might be static with small variations
                if avg_similarity > 0.8:
                    confidence = avg_similarity
                    
                    return PatternAnalysisResult(
                        pattern_detected=True,
                        pattern_type=PatternType.STATIC,
                        confidence=confidence,
                        sample_size=len(values),
                        pattern_data={
                            "avg_similarity": avg_similarity,
                            "variation_type": "minor_variations",
                            "most_common_pattern": max(set(values), key=values.count)
                        },
                        can_predict=True,
                        next_predicted_value=max(set(values), key=values.count),
                        prediction_confidence=confidence * 0.8
                    )
            
            return PatternAnalysisResult(
                pattern_detected=False,
                pattern_type=PatternType.RANDOM,
                confidence=0.0,
                sample_size=len(values),
                pattern_data={}
            )
            
        except Exception as e:
            return PatternAnalysisResult(
                pattern_detected=False,
                pattern_type=PatternType.RANDOM,
                confidence=0.0,
                sample_size=len(values),
                pattern_data={},
                error_message=str(e)
            )
    
    def _calculate_string_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings using Levenshtein distance"""
        if not str1 or not str2:
            return 0.0
        
        if str1 == str2:
            return 1.0
        
        # Calculate Levenshtein distance
        distance = self._levenshtein_distance(str1, str2)
        max_len = max(len(str1), len(str2))
        
        return 1.0 - (distance / max_len) if max_len > 0 else 0.0
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def predict_next_automation_id(self, pattern: AutomationIdPattern, 
                                 steps_ahead: int = 1) -> PredictionResult:
        """
        Predict the next AutomationId value based on learned pattern
        
        Args:
            pattern: Learned AutomationId pattern
            steps_ahead: Number of steps ahead to predict
            
        Returns:
            PredictionResult: Prediction result with confidence
        """
        self.total_predictions += 1
        
        try:
            if not pattern.can_predict or steps_ahead > self.max_prediction_window:
                return PredictionResult(
                    success=False,
                    predicted_value=None,
                    confidence=0.0,
                    pattern_type=pattern.pattern_type,
                    pattern_strength=pattern.confidence,
                    sample_size=pattern.sample_size,
                    prediction_window=steps_ahead,
                    previous_predictions=[],
                    historical_accuracy=0.0,
                    prediction_timestamp=datetime.now().isoformat(),
                    reasoning="Pattern does not support prediction or window too large"
                )
            
            predicted_value = None
            prediction_confidence = pattern.confidence
            
            if pattern.pattern_type == PatternType.SEQUENTIAL_NUMERIC:
                predicted_value = self._predict_sequential_numeric(pattern, steps_ahead)
            elif pattern.pattern_type == PatternType.TIMESTAMP_BASED:
                predicted_value = self._predict_timestamp_based(pattern, steps_ahead)
            elif pattern.pattern_type == PatternType.STATIC:
                predicted_value = pattern.pattern_data.get("most_common_pattern")
            else:
                # For other patterns, use the stored prediction if available
                predicted_value = pattern.next_predicted_value
            
            if predicted_value:
                # Adjust confidence based on prediction window
                adjusted_confidence = prediction_confidence * (0.95 ** (steps_ahead - 1))
                
                # Get historical accuracy for this pattern type
                historical_accuracy = self.accuracy_tracker.get(pattern.pattern_type, 0.0)
                
                result = PredictionResult(
                    success=True,
                    predicted_value=predicted_value,
                    confidence=adjusted_confidence,
                    pattern_type=pattern.pattern_type,
                    pattern_strength=pattern.confidence,
                    sample_size=pattern.sample_size,
                    prediction_window=steps_ahead,
                    previous_predictions=self._get_previous_predictions(pattern.pattern_type),
                    historical_accuracy=historical_accuracy,
                    prediction_timestamp=datetime.now().isoformat(),
                    expires_at=(datetime.now() + timedelta(hours=1)).isoformat(),
                    reasoning=f"Predicted using {pattern.pattern_type.value} pattern analysis"
                )
                
                # Cache prediction for tracking
                self._cache_prediction(result)
                
                return result
            else:
                return PredictionResult(
                    success=False,
                    predicted_value=None,
                    confidence=0.0,
                    pattern_type=pattern.pattern_type,
                    pattern_strength=pattern.confidence,
                    sample_size=pattern.sample_size,
                    prediction_window=steps_ahead,
                    previous_predictions=[],
                    historical_accuracy=0.0,
                    prediction_timestamp=datetime.now().isoformat(),
                    reasoning="Unable to generate prediction from pattern data"
                )
                
        except Exception as e:
            return PredictionResult(
                success=False,
                predicted_value=None,
                confidence=0.0,
                pattern_type=pattern.pattern_type,
                pattern_strength=0.0,
                sample_size=0,
                prediction_window=steps_ahead,
                previous_predictions=[],
                historical_accuracy=0.0,
                prediction_timestamp=datetime.now().isoformat(),
                reasoning=f"Prediction failed: {str(e)}"
            )
    
    def _predict_sequential_numeric(self, pattern: AutomationIdPattern, steps_ahead: int) -> Optional[str]:
        """Predict next value for sequential numeric patterns"""
        try:
            pattern_data = pattern.pattern_data
            
            if pattern_data.get("sequence_type") == "arithmetic":
                step = pattern_data.get("step", 1)
                last_value = pattern_data.get("last_value", 0)
                next_value = last_value + (step * steps_ahead)
                return str(next_value)
                
            elif pattern_data.get("sequence_type") == "geometric":
                ratio = pattern_data.get("ratio", 1)
                last_value = pattern_data.get("last_value", 1)
                next_value = int(last_value * (ratio ** steps_ahead))
                return str(next_value)
                
            elif pattern_data.get("pattern_type") == "prefix_number":
                prefix = pattern_data.get("prefix", "")
                step = pattern_data.get("sequence_step", 1)
                last_number = pattern_data.get("last_number", 0)
                next_number = last_number + (step * steps_ahead)
                return f"{prefix}_{next_number}"
                
            elif pattern_data.get("pattern_type") == "cyclic":
                cycle_values = pattern_data.get("cycle_values", [])
                if cycle_values:
                    cycle_length = len(cycle_values)
                    current_index = pattern_data.get("next_index", 0)
                    next_index = (current_index + steps_ahead - 1) % cycle_length
                    return cycle_values[next_index]
                    
            elif pattern_data.get("pattern_type") == "alternating":
                value_a = pattern_data.get("value_a")
                value_b = pattern_data.get("value_b")
                if value_a and value_b:
                    # Determine which value comes next
                    return value_b if steps_ahead % 2 == 1 else value_a
            
            return None
            
        except Exception:
            return None
    
    def _predict_timestamp_based(self, pattern: AutomationIdPattern, steps_ahead: int) -> Optional[str]:
        """Predict next value for timestamp-based patterns"""
        try:
            pattern_data = pattern.pattern_data
            avg_interval = pattern_data.get("avg_interval_seconds", 0)
            value_pattern = pattern_data.get("value_pattern", "")
            timestamps = pattern_data.get("timestamps", [])
            
            if avg_interval > 0 and value_pattern and timestamps:
                last_timestamp = timestamps[-1]
                next_timestamp = last_timestamp + (avg_interval * steps_ahead)
                
                # Replace {timestamp} placeholder with predicted timestamp
                predicted_value = value_pattern.replace("{timestamp}", str(int(next_timestamp)))
                return predicted_value
            
            return None
            
        except Exception:
            return None
    
    def _cache_prediction(self, result: PredictionResult):
        """Cache prediction for accuracy tracking"""
        cache_key = f"{result.pattern_type.value}_{result.prediction_timestamp}"
        self.prediction_cache[cache_key] = {
            'prediction': result.predicted_value,
            'confidence': result.confidence,
            'timestamp': result.prediction_timestamp,
            'verified': False
        }
        
        # Keep only recent predictions (last 100)
        if len(self.prediction_cache) > 100:
            oldest_keys = sorted(self.prediction_cache.keys())[:50]
            for key in oldest_keys:
                del self.prediction_cache[key]
    
    def _get_previous_predictions(self, pattern_type: PatternType) -> List[Dict[str, Any]]:
        """Get previous predictions for the same pattern type"""
        predictions = []
        
        for cache_key, cache_data in self.prediction_cache.items():
            if pattern_type.value in cache_key:
                predictions.append({
                    'predicted_value': cache_data['prediction'],
                    'confidence': cache_data['confidence'],
                    'timestamp': cache_data['timestamp'],
                    'verified': cache_data['verified']
                })
        
        return sorted(predictions, key=lambda x: x['timestamp'], reverse=True)[:10]
    
    def verify_prediction(self, predicted_value: str, actual_value: str, 
                         pattern_type: PatternType) -> bool:
        """
        Verify a prediction and update accuracy metrics
        
        Args:
            predicted_value: What was predicted
            actual_value: What actually happened
            pattern_type: Type of pattern that made the prediction
            
        Returns:
            bool: True if prediction was accurate
        """
        accurate = predicted_value == actual_value
        
        if accurate:
            self.accurate_predictions += 1
        
        # Update accuracy tracking for this pattern type
        if pattern_type not in self.accuracy_tracker:
            self.accuracy_tracker[pattern_type] = 0.0
        
        # Simple moving average of accuracy
        current_accuracy = self.accuracy_tracker[pattern_type]
        weight = 0.1  # Weight for new observation
        new_accuracy = current_accuracy * (1 - weight) + (1.0 if accurate else 0.0) * weight
        self.accuracy_tracker[pattern_type] = new_accuracy
        
        print_info(f"Prediction verification: {'✓' if accurate else '✗'} "
                  f"({pattern_type.value} accuracy: {new_accuracy:.2f})")
        
        return accurate
    
    def get_learning_statistics(self) -> Dict[str, Any]:
        """Get comprehensive learning and prediction statistics"""
        overall_accuracy = (self.accurate_predictions / self.total_predictions * 100) if self.total_predictions > 0 else 0.0
        pattern_success_rate = (self.successful_patterns / self.total_analyses * 100) if self.total_analyses > 0 else 0.0
        
        return {
            'total_analyses': self.total_analyses,
            'successful_patterns': self.successful_patterns,
            'pattern_success_rate': pattern_success_rate,
            'total_predictions': self.total_predictions,
            'accurate_predictions': self.accurate_predictions,
            'overall_accuracy': overall_accuracy,
            'pattern_type_accuracies': {pt.value: acc for pt, acc in self.accuracy_tracker.items()},
            'cached_predictions': len(self.prediction_cache),
            'supported_algorithms': [alg.value for alg in self.pattern_analyzers.keys()],
            'accuracy_by_pattern': self.accuracy_tracker
        }
    
    def reset_learning_data(self):
        """Reset all learning data and statistics"""
        self.prediction_cache.clear()
        self.learning_history.clear()
        self.accuracy_tracker.clear()
        
        self.total_analyses = 0
        self.successful_patterns = 0
        self.total_predictions = 0
        self.accurate_predictions = 0
        
        print_info("Pattern learning data reset")

# Export main classes
__all__ = [
    'PatternLearningEngine',
    'PatternAnalysisResult',
    'PredictionResult',
    'PredictionAccuracy',
    'LearningAlgorithm'
]