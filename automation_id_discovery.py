"""
AutomationId Discovery Service
Version 1.0 - Intelligent element location when AutomationIds change

This service acts as a "scout" system that finds UI elements using stable attributes
when their AutomationIds have changed between application sessions.
"""

import time
import uiautomation as auto
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass
from enum import Enum

from dynamic_selector_cache_schema import ElementFingerprint, SelectorStrategy
from element_fingerprinting import ElementFingerprintEngine, FingerprintMatchResult
from utils import print_info, print_success, print_warning, print_error

class DiscoveryStrategy(Enum):
    """Different strategies for element discovery"""
    NAME_AND_TYPE = "name_and_type"
    CLASS_AND_HIERARCHY = "class_and_hierarchy"
    VISUAL_POSITION = "visual_position"
    SIBLING_RELATIONSHIPS = "sibling_relationships"
    CONTENT_MATCHING = "content_matching"
    FUZZY_ATTRIBUTES = "fuzzy_attributes"
    COORDINATE_PROXIMITY = "coordinate_proximity"

class DiscoveryMethod(Enum):
    """Methods used for element search"""
    DIRECT_SEARCH = "direct_search"
    HIERARCHY_NAVIGATION = "hierarchy_navigation"
    SIBLING_ENUMERATION = "sibling_enumeration"
    WINDOW_SCANNING = "window_scanning"
    COORDINATE_SEARCH = "coordinate_search"

@dataclass
class DiscoveryResult:
    """Result of element discovery operation"""
    success: bool
    element: Optional[Any]  # UI Automation element
    new_automation_id: Optional[str]
    strategy_used: DiscoveryStrategy
    method_used: DiscoveryMethod
    confidence: float  # 0.0-1.0
    execution_time: float
    attempts_made: int
    
    # Detailed information
    matched_attributes: List[str]
    similarity_score: float
    validation_passed: bool
    error_message: Optional[str] = None
    
    # Element properties for verification
    discovered_properties: Optional[Dict[str, Any]] = None

@dataclass
class SearchContext:
    """Context information for element search"""
    target_fingerprint: ElementFingerprint
    window_element: Optional[Any] = None
    search_timeout: float = 5.0
    max_attempts: int = 3
    confidence_threshold: float = 0.7
    
    # Strategy preferences
    preferred_strategies: List[DiscoveryStrategy] = None
    excluded_strategies: Set[DiscoveryStrategy] = None
    
    # Search constraints
    search_area: Optional[Dict[str, int]] = None  # Bounding rectangle to search within
    max_depth: int = 10  # Maximum hierarchy depth to search
    
    def __post_init__(self):
        if self.preferred_strategies is None:
            self.preferred_strategies = [
                DiscoveryStrategy.NAME_AND_TYPE,
                DiscoveryStrategy.CLASS_AND_HIERARCHY,
                DiscoveryStrategy.VISUAL_POSITION,
                DiscoveryStrategy.SIBLING_RELATIONSHIPS,
                DiscoveryStrategy.FUZZY_ATTRIBUTES
            ]
        if self.excluded_strategies is None:
            self.excluded_strategies = set()

class AutomationIdDiscoveryService:
    """
    Service for discovering UI elements when AutomationIds change
    
    Uses multiple intelligent strategies to relocate elements and extract
    their new AutomationIds for selector healing.
    """
    
    def __init__(self):
        """Initialize the discovery service"""
        self.fingerprint_engine = ElementFingerprintEngine()
        self.strategy_success_rates = {}  # Track success rates per strategy
        self.discovery_cache = {}  # Cache recent discoveries for performance
        self.total_discoveries = 0
        self.successful_discoveries = 0
        
        # Strategy configuration
        self.strategy_timeouts = {
            DiscoveryStrategy.NAME_AND_TYPE: 2.0,
            DiscoveryStrategy.CLASS_AND_HIERARCHY: 3.0,
            DiscoveryStrategy.VISUAL_POSITION: 2.5,
            DiscoveryStrategy.SIBLING_RELATIONSHIPS: 4.0,
            DiscoveryStrategy.CONTENT_MATCHING: 1.5,
            DiscoveryStrategy.FUZZY_ATTRIBUTES: 3.5,
            DiscoveryStrategy.COORDINATE_PROXIMITY: 1.0
        }
    
    def discover_element(self, context: SearchContext) -> DiscoveryResult:
        """
        Main discovery method - tries multiple strategies to find element
        
        Args:
            context: Search context with target fingerprint and constraints
            
        Returns:
            DiscoveryResult: Complete discovery result
        """
        start_time = time.time()
        self.total_discoveries += 1
        
        print_info(f"Starting element discovery using {len(context.preferred_strategies)} strategies")
        
        # Try each strategy in order of preference
        best_result = None
        all_attempts = []
        
        for strategy in context.preferred_strategies:
            if strategy in context.excluded_strategies:
                continue
            
            print_info(f"Trying discovery strategy: {strategy.value}")
            
            try:
                # Execute strategy with timeout
                strategy_timeout = min(
                    self.strategy_timeouts.get(strategy, 3.0),
                    context.search_timeout
                )
                
                result = self._execute_strategy(strategy, context, strategy_timeout)
                all_attempts.append(result)
                
                # Check if this result is good enough
                if result.success and result.confidence >= context.confidence_threshold:
                    print_success(f"Element found using {strategy.value} (confidence: {result.confidence:.2f})")
                    self.successful_discoveries += 1
                    self._update_strategy_success_rate(strategy, True)
                    return result
                
                # Keep track of best result so far
                if not best_result or (result.confidence > best_result.confidence):
                    best_result = result
                    
            except Exception as e:
                print_warning(f"Strategy {strategy.value} failed: {str(e)}")
                self._update_strategy_success_rate(strategy, False)
                continue
        
        # If no strategy succeeded completely, return the best partial result
        if best_result and best_result.confidence > 0.3:  # Minimum acceptable confidence
            print_warning(f"Best discovery result: {best_result.strategy_used.value} (confidence: {best_result.confidence:.2f})")
            if best_result.confidence >= 0.5:
                self.successful_discoveries += 1
            return best_result
        
        # Complete failure
        execution_time = time.time() - start_time
        print_error(f"Element discovery failed after {len(all_attempts)} attempts")
        
        return DiscoveryResult(
            success=False,
            element=None,
            new_automation_id=None,
            strategy_used=DiscoveryStrategy.NAME_AND_TYPE,
            method_used=DiscoveryMethod.DIRECT_SEARCH,
            confidence=0.0,
            execution_time=execution_time,
            attempts_made=len(all_attempts),
            matched_attributes=[],
            similarity_score=0.0,
            validation_passed=False,
            error_message="All discovery strategies failed"
        )
    
    def _execute_strategy(self, strategy: DiscoveryStrategy, context: SearchContext, timeout: float) -> DiscoveryResult:
        """Execute a specific discovery strategy"""
        start_time = time.time()
        
        try:
            if strategy == DiscoveryStrategy.NAME_AND_TYPE:
                return self._discover_by_name_and_type(context, timeout)
            elif strategy == DiscoveryStrategy.CLASS_AND_HIERARCHY:
                return self._discover_by_class_and_hierarchy(context, timeout)
            elif strategy == DiscoveryStrategy.VISUAL_POSITION:
                return self._discover_by_visual_position(context, timeout)
            elif strategy == DiscoveryStrategy.SIBLING_RELATIONSHIPS:
                return self._discover_by_sibling_relationships(context, timeout)
            elif strategy == DiscoveryStrategy.CONTENT_MATCHING:
                return self._discover_by_content_matching(context, timeout)
            elif strategy == DiscoveryStrategy.FUZZY_ATTRIBUTES:
                return self._discover_by_fuzzy_attributes(context, timeout)
            elif strategy == DiscoveryStrategy.COORDINATE_PROXIMITY:
                return self._discover_by_coordinate_proximity(context, timeout)
            else:
                raise ValueError(f"Unknown strategy: {strategy}")
                
        except Exception as e:
            execution_time = time.time() - start_time
            return DiscoveryResult(
                success=False,
                element=None,
                new_automation_id=None,
                strategy_used=strategy,
                method_used=DiscoveryMethod.DIRECT_SEARCH,
                confidence=0.0,
                execution_time=execution_time,
                attempts_made=1,
                matched_attributes=[],
                similarity_score=0.0,
                validation_passed=False,
                error_message=str(e)
            )
    
    def _discover_by_name_and_type(self, context: SearchContext, timeout: float) -> DiscoveryResult:
        """Discover element by Name + ControlType combination"""
        start_time = time.time()
        fingerprint = context.target_fingerprint
        
        if not fingerprint.name or not fingerprint.control_type:
            return self._create_failed_result(DiscoveryStrategy.NAME_AND_TYPE, start_time, "Missing name or control_type")
        
        try:
            # Start from window or desktop
            search_root = context.window_element or auto.GetRootControl()
            
            # Try direct search by name and control type
            control_type_attr = getattr(auto.ControlType, fingerprint.control_type, None)
            if not control_type_attr:
                return self._create_failed_result(DiscoveryStrategy.NAME_AND_TYPE, start_time, "Invalid control type")
            
            # Search with timeout
            end_time = time.time() + timeout
            attempts = 0
            
            while time.time() < end_time and attempts < context.max_attempts:
                attempts += 1
                
                try:
                    # Direct search
                    element = search_root.Control(Name=fingerprint.name, ControlType=control_type_attr)
                    
                    if element and element.Exists(0):
                        # Validate the found element
                        validation_result = self._validate_discovered_element(element, fingerprint)
                        
                        if validation_result['valid']:
                            new_automation_id = getattr(element, 'AutomationId', '') or None
                            
                            return DiscoveryResult(
                                success=True,
                                element=element,
                                new_automation_id=new_automation_id,
                                strategy_used=DiscoveryStrategy.NAME_AND_TYPE,
                                method_used=DiscoveryMethod.DIRECT_SEARCH,
                                confidence=validation_result['confidence'],
                                execution_time=time.time() - start_time,
                                attempts_made=attempts,
                                matched_attributes=validation_result['matched_attributes'],
                                similarity_score=validation_result['similarity'],
                                validation_passed=True,
                                discovered_properties=self._extract_element_properties(element)
                            )
                        
                except Exception:
                    pass  # Continue trying
                
                time.sleep(0.1)  # Brief pause between attempts
            
            return self._create_failed_result(DiscoveryStrategy.NAME_AND_TYPE, start_time, f"Element not found after {attempts} attempts")
            
        except Exception as e:
            return self._create_failed_result(DiscoveryStrategy.NAME_AND_TYPE, start_time, str(e))
    
    def _discover_by_class_and_hierarchy(self, context: SearchContext, timeout: float) -> DiscoveryResult:
        """Discover element by ClassName + hierarchy navigation"""
        start_time = time.time()
        fingerprint = context.target_fingerprint
        
        if not fingerprint.class_name:
            return self._create_failed_result(DiscoveryStrategy.CLASS_AND_HIERARCHY, start_time, "Missing class_name")
        
        try:
            search_root = context.window_element or auto.GetRootControl()
            end_time = time.time() + timeout
            attempts = 0
            
            while time.time() < end_time and attempts < context.max_attempts:
                attempts += 1
                
                try:
                    # Find elements by class name
                    elements = self._find_elements_by_class(search_root, fingerprint.class_name, context.max_depth)
                    
                    # Score each element based on fingerprint similarity
                    best_element = None
                    best_score = 0.0
                    
                    for element in elements:
                        validation_result = self._validate_discovered_element(element, fingerprint)
                        
                        if validation_result['similarity'] > best_score:
                            best_score = validation_result['similarity']
                            best_element = element
                    
                    # If we found a good match
                    if best_element and best_score >= 0.6:
                        new_automation_id = getattr(best_element, 'AutomationId', '') or None
                        
                        return DiscoveryResult(
                            success=True,
                            element=best_element,
                            new_automation_id=new_automation_id,
                            strategy_used=DiscoveryStrategy.CLASS_AND_HIERARCHY,
                            method_used=DiscoveryMethod.HIERARCHY_NAVIGATION,
                            confidence=best_score,
                            execution_time=time.time() - start_time,
                            attempts_made=attempts,
                            matched_attributes=['class_name'],
                            similarity_score=best_score,
                            validation_passed=True,
                            discovered_properties=self._extract_element_properties(best_element)
                        )
                
                except Exception:
                    pass
                
                time.sleep(0.1)
            
            return self._create_failed_result(DiscoveryStrategy.CLASS_AND_HIERARCHY, start_time, "No suitable element found")
            
        except Exception as e:
            return self._create_failed_result(DiscoveryStrategy.CLASS_AND_HIERARCHY, start_time, str(e))
    
    def _discover_by_visual_position(self, context: SearchContext, timeout: float) -> DiscoveryResult:
        """Discover element by visual position within window"""
        start_time = time.time()
        fingerprint = context.target_fingerprint
        
        if not fingerprint.relative_position:
            return self._create_failed_result(DiscoveryStrategy.VISUAL_POSITION, start_time, "Missing relative position")
        
        try:
            window_element = context.window_element
            if not window_element:
                return self._create_failed_result(DiscoveryStrategy.VISUAL_POSITION, start_time, "No window context")
            
            # Calculate target coordinates
            window_rect = window_element.BoundingRectangle
            target_x = window_rect.left + (window_rect.right - window_rect.left) * (fingerprint.relative_position['x_percent'] / 100)
            target_y = window_rect.top + (window_rect.bottom - window_rect.top) * (fingerprint.relative_position['y_percent'] / 100)
            
            # Search for elements near the target position
            tolerance = 50  # 50 pixel tolerance
            candidates = []
            
            try:
                # Get all children of the window
                all_elements = self._get_all_child_elements(window_element, context.max_depth)
                
                for element in all_elements:
                    try:
                        elem_rect = element.BoundingRectangle
                        if not elem_rect:
                            continue
                        
                        # Calculate distance from target position
                        elem_center_x = elem_rect.left + (elem_rect.right - elem_rect.left) / 2
                        elem_center_y = elem_rect.top + (elem_rect.bottom - elem_rect.top) / 2
                        
                        distance = ((elem_center_x - target_x) ** 2 + (elem_center_y - target_y) ** 2) ** 0.5
                        
                        if distance <= tolerance:
                            # Validate against fingerprint
                            validation_result = self._validate_discovered_element(element, fingerprint)
                            
                            if validation_result['similarity'] > 0.3:  # Minimum similarity for position-based search
                                candidates.append((element, validation_result['similarity'], distance))
                    
                    except Exception:
                        continue
                
                # Sort candidates by similarity then by distance
                candidates.sort(key=lambda x: (-x[1], x[2]))
                
                if candidates:
                    best_element, similarity, distance = candidates[0]
                    new_automation_id = getattr(best_element, 'AutomationId', '') or None
                    
                    # Confidence based on similarity and position accuracy
                    position_accuracy = max(0.0, 1.0 - (distance / tolerance))
                    confidence = (similarity * 0.7) + (position_accuracy * 0.3)
                    
                    return DiscoveryResult(
                        success=True,
                        element=best_element,
                        new_automation_id=new_automation_id,
                        strategy_used=DiscoveryStrategy.VISUAL_POSITION,
                        method_used=DiscoveryMethod.COORDINATE_SEARCH,
                        confidence=confidence,
                        execution_time=time.time() - start_time,
                        attempts_made=1,
                        matched_attributes=['relative_position'],
                        similarity_score=similarity,
                        validation_passed=True,
                        discovered_properties=self._extract_element_properties(best_element)
                    )
            
            except Exception as e:
                print_warning(f"Visual position search failed: {str(e)}")
            
            return self._create_failed_result(DiscoveryStrategy.VISUAL_POSITION, start_time, "No elements found at target position")
            
        except Exception as e:
            return self._create_failed_result(DiscoveryStrategy.VISUAL_POSITION, start_time, str(e))
    
    def _discover_by_sibling_relationships(self, context: SearchContext, timeout: float) -> DiscoveryResult:
        """Discover element by sibling index and relationships"""
        start_time = time.time()
        fingerprint = context.target_fingerprint
        
        if fingerprint.sibling_index is None and fingerprint.same_type_index is None:
            return self._create_failed_result(DiscoveryStrategy.SIBLING_RELATIONSHIPS, start_time, "Missing sibling index information")
        
        try:
            # Find parent container first
            parent_element = self._find_parent_container(context, fingerprint)
            
            if not parent_element:
                return self._create_failed_result(DiscoveryStrategy.SIBLING_RELATIONSHIPS, start_time, "Parent container not found")
            
            # Get siblings
            siblings = parent_element.GetChildren()
            if not siblings:
                return self._create_failed_result(DiscoveryStrategy.SIBLING_RELATIONSHIPS, start_time, "No siblings found")
            
            candidates = []
            
            # Try by same-type index first (more reliable)
            if fingerprint.same_type_index is not None and fingerprint.control_type:
                same_type_elements = [s for s in siblings if getattr(s, 'ControlTypeName', '') == fingerprint.control_type]
                
                if 0 <= fingerprint.same_type_index < len(same_type_elements):
                    candidate = same_type_elements[fingerprint.same_type_index]
                    validation_result = self._validate_discovered_element(candidate, fingerprint)
                    candidates.append((candidate, validation_result['similarity'], 'same_type_index'))
            
            # Try by general sibling index
            if fingerprint.sibling_index is not None:
                if 0 <= fingerprint.sibling_index < len(siblings):
                    candidate = siblings[fingerprint.sibling_index]
                    validation_result = self._validate_discovered_element(candidate, fingerprint)
                    candidates.append((candidate, validation_result['similarity'], 'sibling_index'))
            
            # Check nearby indices if exact index fails
            if fingerprint.sibling_index is not None and not candidates:
                for offset in [-1, 1, -2, 2]:  # Check adjacent positions
                    idx = fingerprint.sibling_index + offset
                    if 0 <= idx < len(siblings):
                        candidate = siblings[idx]
                        validation_result = self._validate_discovered_element(candidate, fingerprint)
                        if validation_result['similarity'] > 0.5:
                            candidates.append((candidate, validation_result['similarity'], f'sibling_index_offset_{offset}'))
            
            # Return best candidate
            if candidates:
                candidates.sort(key=lambda x: x[1], reverse=True)
                best_element, similarity, method = candidates[0]
                
                if similarity >= 0.4:  # Minimum threshold for sibling-based discovery
                    new_automation_id = getattr(best_element, 'AutomationId', '') or None
                    
                    return DiscoveryResult(
                        success=True,
                        element=best_element,
                        new_automation_id=new_automation_id,
                        strategy_used=DiscoveryStrategy.SIBLING_RELATIONSHIPS,
                        method_used=DiscoveryMethod.SIBLING_ENUMERATION,
                        confidence=similarity,
                        execution_time=time.time() - start_time,
                        attempts_made=1,
                        matched_attributes=[method],
                        similarity_score=similarity,
                        validation_passed=True,
                        discovered_properties=self._extract_element_properties(best_element)
                    )
            
            return self._create_failed_result(DiscoveryStrategy.SIBLING_RELATIONSHIPS, start_time, "No matching siblings found")
            
        except Exception as e:
            return self._create_failed_result(DiscoveryStrategy.SIBLING_RELATIONSHIPS, start_time, str(e))
    
    def _discover_by_content_matching(self, context: SearchContext, timeout: float) -> DiscoveryResult:
        """Discover element by content/value matching"""
        start_time = time.time()
        fingerprint = context.target_fingerprint
        
        if not fingerprint.value and not fingerprint.text_content:
            return self._create_failed_result(DiscoveryStrategy.CONTENT_MATCHING, start_time, "No content to match")
        
        try:
            search_root = context.window_element or auto.GetRootControl()
            target_text = fingerprint.value or fingerprint.text_content
            
            # Get all elements and check their text content
            all_elements = self._get_all_child_elements(search_root, context.max_depth)
            candidates = []
            
            for element in all_elements:
                try:
                    element_text = getattr(element, 'Name', '') or getattr(element, 'Value', '')
                    
                    if element_text and target_text:
                        # Calculate text similarity
                        similarity = self.fingerprint_engine._calculate_string_similarity(element_text, target_text)
                        
                        if similarity >= 0.7:  # High text similarity threshold
                            validation_result = self._validate_discovered_element(element, fingerprint)
                            combined_score = (similarity * 0.6) + (validation_result['similarity'] * 0.4)
                            candidates.append((element, combined_score, similarity))
                
                except Exception:
                    continue
            
            if candidates:
                candidates.sort(key=lambda x: x[1], reverse=True)
                best_element, combined_score, text_similarity = candidates[0]
                
                new_automation_id = getattr(best_element, 'AutomationId', '') or None
                
                return DiscoveryResult(
                    success=True,
                    element=best_element,
                    new_automation_id=new_automation_id,
                    strategy_used=DiscoveryStrategy.CONTENT_MATCHING,
                    method_used=DiscoveryMethod.WINDOW_SCANNING,
                    confidence=combined_score,
                    execution_time=time.time() - start_time,
                    attempts_made=1,
                    matched_attributes=['content'],
                    similarity_score=combined_score,
                    validation_passed=True,
                    discovered_properties=self._extract_element_properties(best_element)
                )
            
            return self._create_failed_result(DiscoveryStrategy.CONTENT_MATCHING, start_time, "No content matches found")
            
        except Exception as e:
            return self._create_failed_result(DiscoveryStrategy.CONTENT_MATCHING, start_time, str(e))
    
    def _discover_by_fuzzy_attributes(self, context: SearchContext, timeout: float) -> DiscoveryResult:
        """Discover element using fuzzy matching on multiple attributes"""
        start_time = time.time()
        fingerprint = context.target_fingerprint
        
        try:
            search_root = context.window_element or auto.GetRootControl()
            
            # Get all elements within reasonable scope
            all_elements = self._get_all_child_elements(search_root, context.max_depth)
            candidates = []
            
            for element in all_elements:
                try:
                    # Create fingerprint for this element
                    element_props = self._extract_element_properties(element)
                    element_fingerprint = self._create_fingerprint_from_properties(element_props)
                    
                    # Calculate similarity using fingerprint engine
                    match_result = self.fingerprint_engine.calculate_fingerprint_similarity(fingerprint, element_fingerprint)
                    
                    if match_result.confidence >= 0.4:  # Minimum threshold for fuzzy matching
                        candidates.append((element, match_result))
                
                except Exception:
                    continue
            
            if candidates:
                # Sort by confidence
                candidates.sort(key=lambda x: x[1].confidence, reverse=True)
                best_element, best_match = candidates[0]
                
                new_automation_id = getattr(best_element, 'AutomationId', '') or None
                
                return DiscoveryResult(
                    success=True,
                    element=best_element,
                    new_automation_id=new_automation_id,
                    strategy_used=DiscoveryStrategy.FUZZY_ATTRIBUTES,
                    method_used=DiscoveryMethod.WINDOW_SCANNING,
                    confidence=best_match.confidence,
                    execution_time=time.time() - start_time,
                    attempts_made=1,
                    matched_attributes=best_match.matched_attributes,
                    similarity_score=best_match.confidence,
                    validation_passed=True,
                    discovered_properties=self._extract_element_properties(best_element)
                )
            
            return self._create_failed_result(DiscoveryStrategy.FUZZY_ATTRIBUTES, start_time, "No fuzzy matches found")
            
        except Exception as e:
            return self._create_failed_result(DiscoveryStrategy.FUZZY_ATTRIBUTES, start_time, str(e))
    
    def _discover_by_coordinate_proximity(self, context: SearchContext, timeout: float) -> DiscoveryResult:
        """Discover element by coordinate proximity (last resort)"""
        start_time = time.time()
        fingerprint = context.target_fingerprint
        
        if not fingerprint.bounding_rect:
            return self._create_failed_result(DiscoveryStrategy.COORDINATE_PROXIMITY, start_time, "No bounding rectangle")
        
        try:
            # Use exact coordinates as last resort
            target_rect = fingerprint.bounding_rect
            center_x = target_rect['left'] + target_rect['width'] // 2
            center_y = target_rect['top'] + target_rect['height'] // 2
            
            # Try to find element at exact coordinates
            try:
                element = auto.ControlFromPoint(center_x, center_y)
                
                if element and element.BoundingRectangle:
                    validation_result = self._validate_discovered_element(element, fingerprint)
                    
                    if validation_result['similarity'] >= 0.3:  # Very low threshold for coordinate search
                        new_automation_id = getattr(element, 'AutomationId', '') or None
                        
                        return DiscoveryResult(
                            success=True,
                            element=element,
                            new_automation_id=new_automation_id,
                            strategy_used=DiscoveryStrategy.COORDINATE_PROXIMITY,
                            method_used=DiscoveryMethod.COORDINATE_SEARCH,
                            confidence=validation_result['similarity'],
                            execution_time=time.time() - start_time,
                            attempts_made=1,
                            matched_attributes=['coordinates'],
                            similarity_score=validation_result['similarity'],
                            validation_passed=True,
                            discovered_properties=self._extract_element_properties(element)
                        )
            
            except Exception:
                pass
            
            return self._create_failed_result(DiscoveryStrategy.COORDINATE_PROXIMITY, start_time, "No element at target coordinates")
            
        except Exception as e:
            return self._create_failed_result(DiscoveryStrategy.COORDINATE_PROXIMITY, start_time, str(e))
    
    # Helper methods
    
    def _validate_discovered_element(self, element: Any, target_fingerprint: ElementFingerprint) -> Dict[str, Any]:
        """Validate that discovered element matches target fingerprint"""
        try:
            element_props = self._extract_element_properties(element)
            element_fingerprint = self._create_fingerprint_from_properties(element_props)
            
            match_result = self.fingerprint_engine.calculate_fingerprint_similarity(target_fingerprint, element_fingerprint)
            
            return {
                'valid': match_result.confidence >= 0.3,
                'confidence': match_result.confidence,
                'similarity': match_result.confidence,
                'matched_attributes': match_result.matched_attributes
            }
            
        except Exception as e:
            return {
                'valid': False,
                'confidence': 0.0,
                'similarity': 0.0,
                'matched_attributes': [],
                'error': str(e)
            }
    
    def _extract_element_properties(self, element: Any) -> Dict[str, Any]:
        """Extract properties from UI element"""
        try:
            props = {
                'automation_id': getattr(element, 'AutomationId', ''),
                'name': getattr(element, 'Name', ''),
                'class_name': getattr(element, 'ClassName', ''),
                'control_type': getattr(element, 'ControlTypeName', ''),
                'localized_control_type': getattr(element, 'LocalizedControlType', ''),
                'value': getattr(element, 'Value', ''),
                'is_enabled': getattr(element, 'IsEnabled', True),
                'is_visible': not getattr(element, 'IsOffscreen', False)
            }
            
            # Add bounding rectangle
            try:
                rect = element.BoundingRectangle
                if rect:
                    props['bounding_rectangle'] = {
                        'left': rect.left,
                        'top': rect.top,
                        'right': rect.right,
                        'bottom': rect.bottom,
                        'width': rect.right - rect.left,
                        'height': rect.bottom - rect.top
                    }
            except:
                pass
            
            return props
            
        except Exception as e:
            print_warning(f"Failed to extract element properties: {str(e)}")
            return {}
    
    def _create_fingerprint_from_properties(self, props: Dict[str, Any]) -> ElementFingerprint:
        """Create fingerprint from element properties"""
        return ElementFingerprint(
            name=props.get('name'),
            class_name=props.get('class_name'),
            control_type=props.get('control_type'),
            localized_control_type=props.get('localized_control_type'),
            value=props.get('value'),
            bounding_rect=props.get('bounding_rectangle')
        )
    
    def _find_elements_by_class(self, root_element: Any, class_name: str, max_depth: int) -> List[Any]:
        """Find all elements with specific class name"""
        elements = []
        
        def search_recursive(element, depth):
            if depth > max_depth:
                return
            
            try:
                if getattr(element, 'ClassName', '') == class_name:
                    elements.append(element)
                
                children = element.GetChildren()
                for child in children:
                    search_recursive(child, depth + 1)
            except:
                pass
        
        search_recursive(root_element, 0)
        return elements
    
    def _get_all_child_elements(self, root_element: Any, max_depth: int) -> List[Any]:
        """Get all child elements up to max_depth"""
        elements = []
        
        def collect_recursive(element, depth):
            if depth > max_depth:
                return
            
            try:
                elements.append(element)
                children = element.GetChildren()
                for child in children:
                    collect_recursive(child, depth + 1)
            except:
                pass
        
        collect_recursive(root_element, 0)
        return elements
    
    def _find_parent_container(self, context: SearchContext, fingerprint: ElementFingerprint) -> Optional[Any]:
        """Find parent container for sibling-based search"""
        if not fingerprint.parent_chain:
            return context.window_element
        
        # Try to find parent by its attributes
        parent_info = fingerprint.parent_chain[0]
        search_root = context.window_element or auto.GetRootControl()
        
        # Simple parent search by name or class
        if parent_info.get('name'):
            try:
                parent = search_root.Control(Name=parent_info['name'])
                if parent and parent.Exists(0):
                    return parent
            except:
                pass
        
        if parent_info.get('class_name'):
            try:
                parent = search_root.Control(ClassName=parent_info['class_name'])
                if parent and parent.Exists(0):
                    return parent
            except:
                pass
        
        return context.window_element
    
    def _create_failed_result(self, strategy: DiscoveryStrategy, start_time: float, error_message: str) -> DiscoveryResult:
        """Create a failed discovery result"""
        return DiscoveryResult(
            success=False,
            element=None,
            new_automation_id=None,
            strategy_used=strategy,
            method_used=DiscoveryMethod.DIRECT_SEARCH,
            confidence=0.0,
            execution_time=time.time() - start_time,
            attempts_made=1,
            matched_attributes=[],
            similarity_score=0.0,
            validation_passed=False,
            error_message=error_message
        )
    
    def _update_strategy_success_rate(self, strategy: DiscoveryStrategy, success: bool):
        """Update success rate tracking for strategies"""
        if strategy not in self.strategy_success_rates:
            self.strategy_success_rates[strategy] = {'successes': 0, 'attempts': 0}
        
        self.strategy_success_rates[strategy]['attempts'] += 1
        if success:
            self.strategy_success_rates[strategy]['successes'] += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get discovery service statistics"""
        success_rate = (self.successful_discoveries / self.total_discoveries * 100) if self.total_discoveries > 0 else 0.0
        
        strategy_stats = {}
        for strategy, stats in self.strategy_success_rates.items():
            strategy_rate = (stats['successes'] / stats['attempts'] * 100) if stats['attempts'] > 0 else 0.0
            strategy_stats[strategy.value] = {
                'success_rate': strategy_rate,
                'total_attempts': stats['attempts'],
                'successful_attempts': stats['successes']
            }
        
        return {
            'total_discoveries': self.total_discoveries,
            'successful_discoveries': self.successful_discoveries,
            'overall_success_rate': success_rate,
            'strategy_statistics': strategy_stats
        }

# Export main classes
__all__ = [
    'AutomationIdDiscoveryService',
    'DiscoveryResult',
    'SearchContext',
    'DiscoveryStrategy',
    'DiscoveryMethod'
]