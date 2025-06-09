"""
Element Fingerprinting System
Version 1.0 - Advanced UI element identification using stable attributes

This module provides sophisticated fingerprinting algorithms to identify
UI elements reliably even when AutomationIds change between sessions.
"""

import re
import math
import hashlib
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass
from enum import Enum

from dynamic_selector_cache_schema import ElementFingerprint
from utils import print_info, print_warning, print_error

class AttributeStability(Enum):
    """Stability levels for different attributes"""
    VERY_HIGH = "very_high"    # 0.9-1.0 - Almost never changes
    HIGH = "high"              # 0.7-0.89 - Rarely changes
    MEDIUM = "medium"          # 0.5-0.69 - Sometimes changes
    LOW = "low"                # 0.3-0.49 - Often changes
    VERY_LOW = "very_low"      # 0.0-0.29 - Frequently changes

class FingerprintMethod(Enum):
    """Different fingerprinting methods"""
    ATTRIBUTE_BASED = "attribute_based"
    HIERARCHY_BASED = "hierarchy_based"
    POSITION_BASED = "position_based"
    CONTENT_BASED = "content_based"
    RELATIONSHIP_BASED = "relationship_based"
    VISUAL_BASED = "visual_based"

@dataclass
class FingerprintMatchResult:
    """Result of fingerprint matching"""
    confidence: float  # 0.0-1.0
    method: FingerprintMethod
    matched_attributes: List[str]
    similarity_breakdown: Dict[str, float]
    total_score: float
    is_reliable_match: bool  # True if confidence >= 0.7

@dataclass
class AttributeWeight:
    """Weight and stability information for an attribute"""
    base_weight: float
    stability_score: float
    effective_weight: float  # base_weight * stability_score
    reason: str

class ElementFingerprintEngine:
    """
    Advanced fingerprinting engine for UI elements
    
    Creates multiple types of fingerprints and provides intelligent
    matching algorithms to identify elements across sessions.
    """
    
    def __init__(self):
        """Initialize the fingerprinting engine"""
        self.attribute_weights = self._initialize_attribute_weights()
        self.stability_patterns = self._initialize_stability_patterns()
        self.matching_thresholds = {
            'reliable_match': 0.75,
            'good_match': 0.60,
            'acceptable_match': 0.45,
            'poor_match': 0.30
        }
    
    def _initialize_attribute_weights(self) -> Dict[str, AttributeWeight]:
        """Initialize base weights for different attributes"""
        return {
            'name': AttributeWeight(
                base_weight=0.85,
                stability_score=0.9,
                effective_weight=0.85 * 0.9,
                reason="Name is usually stable and descriptive"
            ),
            'class_name': AttributeWeight(
                base_weight=0.75,
                stability_score=0.8,
                effective_weight=0.75 * 0.8,
                reason="ClassName is framework-dependent but often stable"
            ),
            'control_type': AttributeWeight(
                base_weight=0.95,
                stability_score=1.0,
                effective_weight=0.95 * 1.0,
                reason="ControlType almost never changes"
            ),
            'localized_control_type': AttributeWeight(
                base_weight=0.7,
                stability_score=0.85,
                effective_weight=0.7 * 0.85,
                reason="LocalizedControlType is language-dependent"
            ),
            'window_title': AttributeWeight(
                base_weight=0.8,
                stability_score=0.7,
                effective_weight=0.8 * 0.7,
                reason="Window title can change with document state"
            ),
            'window_class': AttributeWeight(
                base_weight=0.9,
                stability_score=0.9,
                effective_weight=0.9 * 0.9,
                reason="Window class is very stable"
            ),
            'parent_chain': AttributeWeight(
                base_weight=0.8,
                stability_score=0.75,
                effective_weight=0.8 * 0.75,
                reason="Hierarchy provides strong context"
            ),
            'sibling_index': AttributeWeight(
                base_weight=0.4,
                stability_score=0.6,
                effective_weight=0.4 * 0.6,
                reason="Index can change with dynamic content"
            ),
            'same_type_index': AttributeWeight(
                base_weight=0.5,
                stability_score=0.65,
                effective_weight=0.5 * 0.65,
                reason="Type-specific index is more stable"
            ),
            'relative_position': AttributeWeight(
                base_weight=0.6,
                stability_score=0.5,
                effective_weight=0.6 * 0.5,
                reason="Position can change with layout"
            ),
            'value': AttributeWeight(
                base_weight=0.3,
                stability_score=0.3,
                effective_weight=0.3 * 0.3,
                reason="Value often changes with user input"
            )
        }
    
    def _initialize_stability_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns that indicate stable vs unstable attributes"""
        return {
            'stable_name_patterns': [
                r'^(ok|cancel|yes|no|save|open|close|exit|help|about)$',
                r'^(button|btn)_\w+$',
                r'^(menu|mnv)_\w+$',
                r'^(tab|page)_\w+$',
                r'^\w+_(button|btn|menu|tab)$'
            ],
            'unstable_name_patterns': [
                r'\d{2}/\d{2}/\d{4}',  # Dates
                r'\d{2}:\d{2}:\d{2}',  # Times
                r'\$[\d,]+\.\d{2}',    # Currency
                r'\d+%',               # Percentages
                r'#\d+',               # Numbers/IDs
                r'^\d+$'               # Pure numbers
            ],
            'stable_class_patterns': [
                r'^(Button|TextBox|ComboBox|ListBox|CheckBox|RadioButton)$',
                r'^Wpf\w+$',
                r'^Windows\.UI\.\w+$',
                r'^\w+Control$'
            ],
            'unstable_class_patterns': [
                r'_\d+$',              # Class with numeric suffix
                r'^Temp\w+$',          # Temporary classes
                r'^Generated\w+$'      # Generated classes
            ]
        }
    
    def create_comprehensive_fingerprint(self, element_data: Dict[str, Any]) -> ElementFingerprint:
        """
        Create comprehensive fingerprint from element data
        
        Args:
            element_data: Raw element data from ElementInspector
            
        Returns:
            ElementFingerprint: Complete fingerprint with stability analysis
        """
        try:
            # Extract basic information
            fingerprint = self._extract_basic_fingerprint(element_data)
            
            # Analyze attribute stability
            fingerprint.attribute_stability = self._analyze_attribute_stability(fingerprint)
            
            # Enhance with hierarchy information
            self._enhance_hierarchy_information(fingerprint, element_data)
            
            # Add positional context
            self._add_positional_context(fingerprint, element_data)
            
            # Add content information
            self._add_content_information(fingerprint, element_data)
            
            print_info(f"Created fingerprint with {len([k for k, v in fingerprint.attribute_stability.items() if v > 0.7])} stable attributes")
            
            return fingerprint
            
        except Exception as e:
            print_error(f"Failed to create fingerprint: {str(e)}")
            return ElementFingerprint()
    
    def _extract_basic_fingerprint(self, element_data: Dict[str, Any]) -> ElementFingerprint:
        """Extract basic fingerprint information"""
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
            bounding_rect=bounding_rect if bounding_rect else None
        )
    
    def _analyze_attribute_stability(self, fingerprint: ElementFingerprint) -> Dict[str, float]:
        """Analyze stability of each attribute in the fingerprint"""
        stability = {}
        
        # Analyze name stability
        if fingerprint.name:
            stability['name'] = self._analyze_name_stability(fingerprint.name)
        else:
            stability['name'] = 0.0
        
        # Analyze class_name stability
        if fingerprint.class_name:
            stability['class_name'] = self._analyze_class_stability(fingerprint.class_name)
        else:
            stability['class_name'] = 0.0
        
        # Control type is always stable
        stability['control_type'] = 1.0 if fingerprint.control_type else 0.0
        
        # Localized control type
        stability['localized_control_type'] = 0.85 if fingerprint.localized_control_type else 0.0
        
        # Window information
        if fingerprint.window_title:
            stability['window_title'] = self._analyze_window_title_stability(fingerprint.window_title)
        else:
            stability['window_title'] = 0.0
        
        stability['window_class'] = 0.9 if fingerprint.window_class else 0.0
        
        # Positional information
        stability['sibling_index'] = 0.6 if fingerprint.sibling_index is not None else 0.0
        stability['same_type_index'] = 0.65 if fingerprint.same_type_index is not None else 0.0
        
        # Relative position
        stability['relative_position'] = 0.5 if fingerprint.relative_position else 0.0
        
        # Value stability
        if fingerprint.value:
            stability['value'] = self._analyze_value_stability(fingerprint.value)
        else:
            stability['value'] = 0.0
        
        return stability
    
    def _analyze_name_stability(self, name: str) -> float:
        """Analyze stability of element name"""
        if not name:
            return 0.0
        
        # Check against stable patterns
        for pattern in self.stability_patterns['stable_name_patterns']:
            if re.match(pattern, name, re.IGNORECASE):
                return 0.95
        
        # Check against unstable patterns
        for pattern in self.stability_patterns['unstable_name_patterns']:
            if re.search(pattern, name):
                return 0.2
        
        # Length-based heuristic
        if len(name) > 50:
            return 0.4  # Very long names often contain dynamic content
        
        # Character analysis
        digit_ratio = sum(1 for c in name if c.isdigit()) / len(name)
        if digit_ratio > 0.5:
            return 0.3  # Names with many digits are often dynamic
        
        # Default for normal names
        return 0.8
    
    def _analyze_class_stability(self, class_name: str) -> float:
        """Analyze stability of class name"""
        if not class_name:
            return 0.0
        
        # Check stable patterns
        for pattern in self.stability_patterns['stable_class_patterns']:
            if re.match(pattern, class_name):
                return 0.9
        
        # Check unstable patterns
        for pattern in self.stability_patterns['unstable_class_patterns']:
            if re.search(pattern, class_name):
                return 0.3
        
        # Framework-specific analysis
        if any(framework in class_name for framework in ['Wpf', 'WinForms', 'Windows.UI']):
            return 0.85
        
        return 0.7
    
    def _analyze_window_title_stability(self, title: str) -> float:
        """Analyze stability of window title"""
        if not title:
            return 0.0
        
        # Titles with dynamic content
        dynamic_patterns = [
            r'\d+%',                    # Progress percentages
            r'\(\d+/\d+\)',            # Counters
            r'- \d{2}/\d{2}/\d{4}',    # Dates
            r'v\d+\.\d+\.\d+',         # Version numbers
            r'\[\w+\]',                # Status indicators
        ]
        
        for pattern in dynamic_patterns:
            if re.search(pattern, title):
                return 0.5
        
        # Application names are usually stable
        return 0.8
    
    def _analyze_value_stability(self, value: str) -> float:
        """Analyze stability of element value"""
        if not value:
            return 0.0
        
        # Values are generally unstable as they change with user input
        # But some values might be stable (like button text)
        
        # Check if it looks like user input
        if len(value) > 20 or any(c.isdigit() for c in value):
            return 0.2
        
        # Short, text-only values might be stable
        return 0.4
    
    def _enhance_hierarchy_information(self, fingerprint: ElementFingerprint, element_data: Dict[str, Any]):
        """Enhance fingerprint with hierarchy information"""
        parent_info = element_data.get('parent_info', {})
        
        if parent_info:
            # Create simplified parent chain
            fingerprint.parent_chain = [{
                'name': parent_info.get('name', ''),
                'class_name': parent_info.get('class_name', ''),
                'control_type': parent_info.get('control_type', ''),
                'automation_id': parent_info.get('automation_id', '')
            }]
    
    def _add_positional_context(self, fingerprint: ElementFingerprint, element_data: Dict[str, Any]):
        """Add positional context to fingerprint"""
        # Add relative position if we have both element and window rectangles
        bounding_rect = element_data.get('bounding_rectangle', {})
        window_info = element_data.get('window_info', {})
        window_rect = window_info.get('window_rectangle', {})
        
        if bounding_rect and window_rect:
            try:
                rel_x = ((bounding_rect['left'] - window_rect['left']) / window_rect['width']) * 100
                rel_y = ((bounding_rect['top'] - window_rect['top']) / window_rect['height']) * 100
                
                fingerprint.relative_position = {
                    'x_percent': round(rel_x, 1),
                    'y_percent': round(rel_y, 1),
                    'width_percent': round((bounding_rect['width'] / window_rect['width']) * 100, 1),
                    'height_percent': round((bounding_rect['height'] / window_rect['height']) * 100, 1)
                }
            except (KeyError, ZeroDivisionError, TypeError):
                pass
    
    def _add_content_information(self, fingerprint: ElementFingerprint, element_data: Dict[str, Any]):
        """Add content-based information to fingerprint"""
        # Add text content if available
        if fingerprint.value and len(fingerprint.value) < 100:
            fingerprint.text_content = fingerprint.value
    
    def calculate_fingerprint_similarity(self, fp1: ElementFingerprint, fp2: ElementFingerprint) -> FingerprintMatchResult:
        """
        Calculate comprehensive similarity between two fingerprints
        
        Args:
            fp1: First fingerprint
            fp2: Second fingerprint
            
        Returns:
            FingerprintMatchResult: Detailed matching result
        """
        try:
            # Attribute-based matching
            attr_result = self._match_attributes(fp1, fp2)
            
            # Hierarchy-based matching
            hierarchy_result = self._match_hierarchy(fp1, fp2)
            
            # Position-based matching
            position_result = self._match_position(fp1, fp2)
            
            # Content-based matching
            content_result = self._match_content(fp1, fp2)
            
            # Combine results with weights
            total_score = (
                attr_result * 0.5 +
                hierarchy_result * 0.25 +
                position_result * 0.15 +
                content_result * 0.1
            )
            
            # Determine best matching method
            method_scores = {
                FingerprintMethod.ATTRIBUTE_BASED: attr_result,
                FingerprintMethod.HIERARCHY_BASED: hierarchy_result,
                FingerprintMethod.POSITION_BASED: position_result,
                FingerprintMethod.CONTENT_BASED: content_result
            }
            
            best_method = max(method_scores, key=method_scores.get)
            confidence = total_score
            
            # Gather matched attributes
            matched_attributes = self._get_matched_attributes(fp1, fp2)
            
            # Create similarity breakdown
            similarity_breakdown = {
                'attributes': attr_result,
                'hierarchy': hierarchy_result,
                'position': position_result,
                'content': content_result
            }
            
            result = FingerprintMatchResult(
                confidence=confidence,
                method=best_method,
                matched_attributes=matched_attributes,
                similarity_breakdown=similarity_breakdown,
                total_score=total_score,
                is_reliable_match=confidence >= self.matching_thresholds['reliable_match']
            )
            
            return result
            
        except Exception as e:
            print_error(f"Fingerprint similarity calculation failed: {str(e)}")
            return FingerprintMatchResult(
                confidence=0.0,
                method=FingerprintMethod.ATTRIBUTE_BASED,
                matched_attributes=[],
                similarity_breakdown={},
                total_score=0.0,
                is_reliable_match=False
            )
    
    def _match_attributes(self, fp1: ElementFingerprint, fp2: ElementFingerprint) -> float:
        """Match based on individual attributes"""
        total_weight = 0.0
        weighted_score = 0.0
        
        # Define attribute comparisons with weights
        comparisons = [
            ('name', self.attribute_weights['name'].effective_weight, fp1.name, fp2.name),
            ('class_name', self.attribute_weights['class_name'].effective_weight, fp1.class_name, fp2.class_name),
            ('control_type', self.attribute_weights['control_type'].effective_weight, fp1.control_type, fp2.control_type),
            ('window_title', self.attribute_weights['window_title'].effective_weight, fp1.window_title, fp2.window_title),
            ('window_class', self.attribute_weights['window_class'].effective_weight, fp1.window_class, fp2.window_class)
        ]
        
        for attr_name, weight, val1, val2 in comparisons:
            total_weight += weight
            
            if val1 is None and val2 is None:
                continue  # Both None - no information
            elif val1 is not None and val2 is not None:
                similarity = self._calculate_string_similarity(val1, val2)
                weighted_score += similarity * weight
            # If one is None and other isn't, no score added
        
        return weighted_score / total_weight if total_weight > 0 else 0.0
    
    def _match_hierarchy(self, fp1: ElementFingerprint, fp2: ElementFingerprint) -> float:
        """Match based on hierarchy information"""
        if not fp1.parent_chain or not fp2.parent_chain:
            return 0.0
        
        # Simple hierarchy matching (can be enhanced)
        parent1 = fp1.parent_chain[0] if fp1.parent_chain else {}
        parent2 = fp2.parent_chain[0] if fp2.parent_chain else {}
        
        if not parent1 or not parent2:
            return 0.0
        
        score = 0.0
        comparisons = 0
        
        for key in ['name', 'class_name', 'control_type']:
            val1 = parent1.get(key)
            val2 = parent2.get(key)
            
            if val1 and val2:
                similarity = self._calculate_string_similarity(val1, val2)
                score += similarity
                comparisons += 1
        
        return score / comparisons if comparisons > 0 else 0.0
    
    def _match_position(self, fp1: ElementFingerprint, fp2: ElementFingerprint) -> float:
        """Match based on position information"""
        if not fp1.relative_position or not fp2.relative_position:
            return 0.0
        
        pos1 = fp1.relative_position
        pos2 = fp2.relative_position
        
        # Calculate position similarity with tolerance
        tolerance = 10.0  # 10% tolerance for position changes
        
        x_diff = abs(pos1['x_percent'] - pos2['x_percent'])
        y_diff = abs(pos1['y_percent'] - pos2['y_percent'])
        
        x_similarity = max(0.0, 1.0 - (x_diff / tolerance))
        y_similarity = max(0.0, 1.0 - (y_diff / tolerance))
        
        # Position similarity is average of x and y
        return (x_similarity + y_similarity) / 2.0
    
    def _match_content(self, fp1: ElementFingerprint, fp2: ElementFingerprint) -> float:
        """Match based on content information"""
        if not fp1.text_content or not fp2.text_content:
            return 0.0
        
        return self._calculate_string_similarity(fp1.text_content, fp2.text_content)
    
    def _calculate_string_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings"""
        if not str1 or not str2:
            return 0.0
        
        if str1 == str2:
            return 1.0
        
        # Normalize strings
        s1 = str1.lower().strip()
        s2 = str2.lower().strip()
        
        if s1 == s2:
            return 1.0
        
        # Check if one contains the other
        if s1 in s2 or s2 in s1:
            return 0.8
        
        # Calculate Levenshtein distance similarity
        distance = self._levenshtein_distance(s1, s2)
        max_len = max(len(s1), len(s2))
        
        if max_len == 0:
            return 1.0
        
        similarity = 1.0 - (distance / max_len)
        return max(0.0, similarity)
    
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
    
    def _get_matched_attributes(self, fp1: ElementFingerprint, fp2: ElementFingerprint) -> List[str]:
        """Get list of attributes that match between fingerprints"""
        matched = []
        
        attribute_checks = [
            ('name', fp1.name, fp2.name),
            ('class_name', fp1.class_name, fp2.class_name),
            ('control_type', fp1.control_type, fp2.control_type),
            ('window_title', fp1.window_title, fp2.window_title),
            ('window_class', fp1.window_class, fp2.window_class)
        ]
        
        for attr_name, val1, val2 in attribute_checks:
            if val1 and val2:
                similarity = self._calculate_string_similarity(val1, val2)
                if similarity >= 0.8:  # High similarity threshold
                    matched.append(attr_name)
        
        return matched
    
    def find_best_matches(self, target_fingerprint: ElementFingerprint, 
                         candidate_fingerprints: List[Tuple[str, ElementFingerprint]], 
                         min_confidence: float = 0.5) -> List[Tuple[str, FingerprintMatchResult]]:
        """
        Find best matching fingerprints from a list of candidates
        
        Args:
            target_fingerprint: Fingerprint to match against
            candidate_fingerprints: List of (id, fingerprint) tuples
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of (id, match_result) tuples, sorted by confidence
        """
        matches = []
        
        for candidate_id, candidate_fp in candidate_fingerprints:
            try:
                match_result = self.calculate_fingerprint_similarity(target_fingerprint, candidate_fp)
                
                if match_result.confidence >= min_confidence:
                    matches.append((candidate_id, match_result))
                    
            except Exception as e:
                print_warning(f"Failed to match fingerprint {candidate_id}: {str(e)}")
                continue
        
        # Sort by confidence (highest first)
        matches.sort(key=lambda x: x[1].confidence, reverse=True)
        
        return matches
    
    def get_fingerprint_quality_score(self, fingerprint: ElementFingerprint) -> float:
        """
        Calculate quality score for a fingerprint
        
        Args:
            fingerprint: Fingerprint to evaluate
            
        Returns:
            float: Quality score (0.0-1.0)
        """
        try:
            if not fingerprint.attribute_stability:
                return 0.0
            
            # Calculate weighted average of stability scores
            total_weight = 0.0
            weighted_sum = 0.0
            
            for attr_name, stability_score in fingerprint.attribute_stability.items():
                if attr_name in self.attribute_weights:
                    weight = self.attribute_weights[attr_name].effective_weight
                    weighted_sum += stability_score * weight
                    total_weight += weight
            
            base_quality = weighted_sum / total_weight if total_weight > 0 else 0.0
            
            # Bonus for having multiple stable attributes
            stable_attributes = sum(1 for score in fingerprint.attribute_stability.values() if score >= 0.7)
            stability_bonus = min(stable_attributes * 0.1, 0.3)  # Max 30% bonus
            
            # Penalty for missing critical attributes
            critical_missing = 0
            if not fingerprint.name:
                critical_missing += 0.1
            if not fingerprint.control_type:
                critical_missing += 0.15
            if not fingerprint.class_name:
                critical_missing += 0.05
            
            final_quality = min(1.0, max(0.0, base_quality + stability_bonus - critical_missing))
            
            return final_quality
            
        except Exception as e:
            print_error(f"Failed to calculate fingerprint quality: {str(e)}")
            return 0.0
    
    def enhance_fingerprint_with_context(self, fingerprint: ElementFingerprint, 
                                       context_data: Dict[str, Any]) -> ElementFingerprint:
        """
        Enhance fingerprint with additional context information
        
        Args:
            fingerprint: Original fingerprint
            context_data: Additional context (siblings, application info, etc.)
            
        Returns:
            ElementFingerprint: Enhanced fingerprint
        """
        try:
            enhanced = fingerprint
            
            # Add sibling information if available
            siblings_info = context_data.get('siblings', [])
            if siblings_info:
                enhanced.sibling_count = len(siblings_info)
                
                # Calculate same-type index
                same_type_count = 0
                same_type_index = None
                element_control_type = fingerprint.control_type
                
                for i, sibling in enumerate(siblings_info):
                    if sibling.get('control_type') == element_control_type:
                        if sibling.get('is_target', False):
                            same_type_index = same_type_count
                        same_type_count += 1
                
                enhanced.same_type_index = same_type_index
            
            # Add application context
            app_info = context_data.get('application', {})
            if app_info:
                # Could enhance with app version, framework info, etc.
                pass
            
            # Recalculate stability with new information
            enhanced.attribute_stability = self._analyze_attribute_stability(enhanced)
            
            return enhanced
            
        except Exception as e:
            print_error(f"Failed to enhance fingerprint: {str(e)}")
            return fingerprint

# Export main classes and functions
__all__ = [
    'ElementFingerprintEngine',
    'FingerprintMatchResult',
    'FingerprintMethod',
    'AttributeStability',
    'AttributeWeight'
]