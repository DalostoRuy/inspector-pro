"""
Selector Healing Engine
Version 1.0 - Automatic selector repair when AutomationIds change

This module orchestrates the healing process by combining pattern learning,
element discovery, relationship mapping, and intelligent selector regeneration.
"""

import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from dynamic_selector_cache import DynamicSelectorCache
from dynamic_selector_cache_schema import (
    CachedSelectorEntry, ElementFingerprint, SelectorVersion, 
    SelectorStrategy, PatternType, create_fingerprint_from_element_data
)
from automation_id_discovery import AutomationIdDiscoveryService, SearchContext, DiscoveryResult
from pattern_learning_engine import PatternLearningEngine, PatternAnalysisResult, PredictionResult
from element_relationship_mapper import ElementRelationshipMapper, NavigationResult
from element_fingerprinting import ElementFingerprintEngine
from xml_selector_generator import XMLSelectorGenerator
from utils import print_info, print_success, print_warning, print_error

class HealingStrategy(Enum):
    """Different healing strategies available"""
    PATTERN_PREDICTION = "pattern_prediction"
    DISCOVERY_SERVICE = "discovery_service"
    RELATIONSHIP_NAVIGATION = "relationship_navigation"
    REGENERATE_SELECTOR = "regenerate_selector"
    HYBRID_APPROACH = "hybrid_approach"

class HealingPriority(Enum):
    """Priority levels for healing operations"""
    CRITICAL = "critical"      # Essential selectors that must work
    HIGH = "high"             # Important selectors for main flows
    MEDIUM = "medium"         # Secondary selectors
    LOW = "low"               # Optional selectors

@dataclass
class HealingRequest:
    """Request for selector healing"""
    cache_id: str
    failed_selector: str
    element_fingerprint: ElementFingerprint
    failure_reason: str
    
    # Context information
    window_element: Optional[Any] = None
    last_known_automation_id: Optional[str] = None
    application_context: Dict[str, Any] = None
    
    # Healing preferences
    preferred_strategies: List[HealingStrategy] = None
    priority: HealingPriority = HealingPriority.MEDIUM
    timeout: float = 30.0
    
    # Metadata
    request_timestamp: str = ""
    user_id: Optional[str] = None

@dataclass
class HealingResult:
    """Result of healing operation"""
    success: bool
    healed_selector: Optional[str]
    new_automation_id: Optional[str]
    
    # Healing process information
    strategy_used: HealingStrategy
    healing_confidence: float  # 0.0-1.0
    execution_time: float
    
    # Validation results
    selector_validated: bool
    validation_confidence: float
    
    # Discovery details
    discovery_details: Dict[str, Any]
    pattern_analysis: Optional[PatternAnalysisResult] = None
    prediction_result: Optional[PredictionResult] = None
    navigation_result: Optional[NavigationResult] = None
    
    # Error information
    error_message: Optional[str] = None
    failed_strategies: List[str] = None
    
    # Metadata
    healing_timestamp: str = ""
    cache_updated: bool = False

class SelectorHealingEngine:
    """
    Orchestrates automatic selector healing using all available intelligence systems
    
    This engine combines pattern learning, element discovery, relationship mapping,
    and intelligent selector generation to automatically repair broken selectors.
    """
    
    def __init__(self, cache: DynamicSelectorCache):
        """
        Initialize the healing engine
        
        Args:
            cache: Dynamic selector cache instance
        """
        self.cache = cache
        self.discovery_service = AutomationIdDiscoveryService()
        self.pattern_engine = PatternLearningEngine()
        self.relationship_mapper = ElementRelationshipMapper()
        self.fingerprint_engine = ElementFingerprintEngine()
        self.selector_generator = XMLSelectorGenerator()
        
        # Healing configuration
        self.strategy_preferences = {
            HealingPriority.CRITICAL: [
                HealingStrategy.PATTERN_PREDICTION,
                HealingStrategy.DISCOVERY_SERVICE,
                HealingStrategy.RELATIONSHIP_NAVIGATION,
                HealingStrategy.REGENERATE_SELECTOR
            ],
            HealingPriority.HIGH: [
                HealingStrategy.DISCOVERY_SERVICE,
                HealingStrategy.PATTERN_PREDICTION,
                HealingStrategy.RELATIONSHIP_NAVIGATION,
                HealingStrategy.REGENERATE_SELECTOR
            ],
            HealingPriority.MEDIUM: [
                HealingStrategy.DISCOVERY_SERVICE,
                HealingStrategy.RELATIONSHIP_NAVIGATION,
                HealingStrategy.REGENERATE_SELECTOR
            ],
            HealingPriority.LOW: [
                HealingStrategy.DISCOVERY_SERVICE,
                HealingStrategy.REGENERATE_SELECTOR
            ]
        }
        
        # Performance tracking
        self.total_healing_requests = 0
        self.successful_healings = 0
        self.strategy_success_rates = {}
        
        print_info("Selector Healing Engine initialized")
    
    def heal_selector(self, request: HealingRequest) -> HealingResult:
        """
        Main healing method - orchestrates the complete healing process
        
        Args:
            request: Healing request with all necessary context
            
        Returns:
            HealingResult: Comprehensive healing result
        """
        start_time = time.time()
        self.total_healing_requests += 1
        
        print_info(f"Starting selector healing for cache_id: {request.cache_id}")
        
        # Set default timestamp
        if not request.request_timestamp:
            request.request_timestamp = datetime.now().isoformat()
        
        # Get cached entry for context
        cached_entry = None
        try:
            # Create a temporary fingerprint to find the cached entry
            temp_fingerprint = request.element_fingerprint
            cached_entry = self.cache.get(temp_fingerprint)
        except Exception as e:
            print_warning(f"Could not retrieve cached entry: {str(e)}")
        
        # Determine healing strategies to try
        strategies_to_try = request.preferred_strategies or self.strategy_preferences.get(
            request.priority, [HealingStrategy.DISCOVERY_SERVICE]
        )
        
        failed_strategies = []
        
        # Try each strategy in order
        for strategy in strategies_to_try:
            try:
                print_info(f"Attempting healing with strategy: {strategy.value}")
                
                healing_result = self._execute_healing_strategy(strategy, request, cached_entry)
                
                if healing_result.success:
                    # Update success metrics
                    self.successful_healings += 1
                    self._update_strategy_success_rate(strategy, True)
                    
                    # Update cache with healed selector
                    if cached_entry and healing_result.healed_selector:
                        self._update_cache_with_healing_result(cached_entry, healing_result, strategy)
                        healing_result.cache_updated = True
                    
                    healing_result.execution_time = time.time() - start_time
                    healing_result.healing_timestamp = datetime.now().isoformat()
                    
                    print_success(f"Selector healed successfully using {strategy.value} "
                                f"(confidence: {healing_result.healing_confidence:.2f})")
                    
                    return healing_result
                else:
                    failed_strategies.append(strategy.value)
                    self._update_strategy_success_rate(strategy, False)
                    print_warning(f"Strategy {strategy.value} failed: {healing_result.error_message}")
                    
            except Exception as e:
                failed_strategies.append(strategy.value)
                self._update_strategy_success_rate(strategy, False)
                print_error(f"Strategy {strategy.value} encountered error: {str(e)}")
                continue
        
        # All strategies failed
        execution_time = time.time() - start_time
        return HealingResult(
            success=False,
            healed_selector=None,
            new_automation_id=None,
            strategy_used=HealingStrategy.DISCOVERY_SERVICE,  # Default
            healing_confidence=0.0,
            execution_time=execution_time,
            selector_validated=False,
            validation_confidence=0.0,
            discovery_details={},
            error_message="All healing strategies failed",
            failed_strategies=failed_strategies,
            healing_timestamp=datetime.now().isoformat()
        )
    
    def _execute_healing_strategy(self, strategy: HealingStrategy, request: HealingRequest, 
                                cached_entry: Optional[CachedSelectorEntry]) -> HealingResult:
        """Execute a specific healing strategy"""
        
        if strategy == HealingStrategy.PATTERN_PREDICTION:
            return self._heal_using_pattern_prediction(request, cached_entry)
        elif strategy == HealingStrategy.DISCOVERY_SERVICE:
            return self._heal_using_discovery_service(request, cached_entry)
        elif strategy == HealingStrategy.RELATIONSHIP_NAVIGATION:
            return self._heal_using_relationship_navigation(request, cached_entry)
        elif strategy == HealingStrategy.REGENERATE_SELECTOR:
            return self._heal_by_regenerating_selector(request, cached_entry)
        elif strategy == HealingStrategy.HYBRID_APPROACH:
            return self._heal_using_hybrid_approach(request, cached_entry)
        else:
            return HealingResult(
                success=False,
                healed_selector=None,
                new_automation_id=None,
                strategy_used=strategy,
                healing_confidence=0.0,
                execution_time=0.0,
                selector_validated=False,
                validation_confidence=0.0,
                discovery_details={},
                error_message=f"Unknown healing strategy: {strategy.value}"
            )
    
    def _heal_using_pattern_prediction(self, request: HealingRequest, 
                                     cached_entry: Optional[CachedSelectorEntry]) -> HealingResult:
        """Heal selector using pattern prediction"""
        try:
            if not cached_entry or not cached_entry.automation_id_pattern:
                return HealingResult(
                    success=False,
                    healed_selector=None,
                    new_automation_id=None,
                    strategy_used=HealingStrategy.PATTERN_PREDICTION,
                    healing_confidence=0.0,
                    execution_time=0.0,
                    selector_validated=False,
                    validation_confidence=0.0,
                    discovery_details={},
                    error_message="No automation ID pattern available for prediction"
                )
            
            # Use pattern to predict next AutomationId
            prediction_result = self.pattern_engine.predict_next_automation_id(
                cached_entry.automation_id_pattern
            )
            
            if not prediction_result.success or not prediction_result.predicted_value:
                return HealingResult(
                    success=False,
                    healed_selector=None,
                    new_automation_id=None,
                    strategy_used=HealingStrategy.PATTERN_PREDICTION,
                    healing_confidence=0.0,
                    execution_time=0.0,
                    selector_validated=False,
                    validation_confidence=0.0,
                    discovery_details={},
                    prediction_result=prediction_result,
                    error_message="Pattern prediction failed or returned no value"
                )
            
            # Generate new selector with predicted AutomationId
            healed_selector = self._update_selector_automation_id(
                request.failed_selector, 
                prediction_result.predicted_value
            )
            
            if not healed_selector:
                return HealingResult(
                    success=False,
                    healed_selector=None,
                    new_automation_id=None,
                    strategy_used=HealingStrategy.PATTERN_PREDICTION,
                    healing_confidence=0.0,
                    execution_time=0.0,
                    selector_validated=False,
                    validation_confidence=0.0,
                    discovery_details={},
                    prediction_result=prediction_result,
                    error_message="Failed to update selector with predicted AutomationId"
                )
            
            # Validate the healed selector
            validation_result = self._validate_healed_selector(healed_selector, request)
            
            return HealingResult(
                success=validation_result['valid'],
                healed_selector=healed_selector if validation_result['valid'] else None,
                new_automation_id=prediction_result.predicted_value,
                strategy_used=HealingStrategy.PATTERN_PREDICTION,
                healing_confidence=prediction_result.confidence,
                execution_time=0.0,
                selector_validated=validation_result['valid'],
                validation_confidence=validation_result.get('confidence', 0.0),
                discovery_details={'predicted_automation_id': prediction_result.predicted_value},
                prediction_result=prediction_result,
                error_message=None if validation_result['valid'] else "Predicted selector validation failed"
            )
            
        except Exception as e:
            return HealingResult(
                success=False,
                healed_selector=None,
                new_automation_id=None,
                strategy_used=HealingStrategy.PATTERN_PREDICTION,
                healing_confidence=0.0,
                execution_time=0.0,
                selector_validated=False,
                validation_confidence=0.0,
                discovery_details={},
                error_message=f"Pattern prediction healing failed: {str(e)}"
            )
    
    def _heal_using_discovery_service(self, request: HealingRequest, 
                                    cached_entry: Optional[CachedSelectorEntry]) -> HealingResult:
        """Heal selector using element discovery service"""
        try:
            # Create search context
            search_context = SearchContext(
                target_fingerprint=request.element_fingerprint,
                window_element=request.window_element,
                search_timeout=min(request.timeout, 15.0),  # Limit discovery timeout
                confidence_threshold=0.6
            )
            
            # Attempt discovery
            discovery_result = self.discovery_service.discover_element(search_context)
            
            if not discovery_result.success or not discovery_result.new_automation_id:
                return HealingResult(
                    success=False,
                    healed_selector=None,
                    new_automation_id=None,
                    strategy_used=HealingStrategy.DISCOVERY_SERVICE,
                    healing_confidence=0.0,
                    execution_time=discovery_result.execution_time,
                    selector_validated=False,
                    validation_confidence=0.0,
                    discovery_details={
                        'discovery_strategy': discovery_result.strategy_used.value,
                        'attempts_made': discovery_result.attempts_made,
                        'similarity_score': discovery_result.similarity_score
                    },
                    error_message=discovery_result.error_message or "Element discovery failed"
                )
            
            # Generate new selector with discovered AutomationId
            healed_selector = self._update_selector_automation_id(
                request.failed_selector, 
                discovery_result.new_automation_id
            )
            
            if not healed_selector:
                return HealingResult(
                    success=False,
                    healed_selector=None,
                    new_automation_id=discovery_result.new_automation_id,
                    strategy_used=HealingStrategy.DISCOVERY_SERVICE,
                    healing_confidence=0.0,
                    execution_time=discovery_result.execution_time,
                    selector_validated=False,
                    validation_confidence=0.0,
                    discovery_details={
                        'discovery_strategy': discovery_result.strategy_used.value,
                        'new_automation_id': discovery_result.new_automation_id
                    },
                    error_message="Failed to update selector with discovered AutomationId"
                )
            
            # Validate the healed selector
            validation_result = self._validate_healed_selector(healed_selector, request)
            
            return HealingResult(
                success=validation_result['valid'],
                healed_selector=healed_selector if validation_result['valid'] else None,
                new_automation_id=discovery_result.new_automation_id,
                strategy_used=HealingStrategy.DISCOVERY_SERVICE,
                healing_confidence=discovery_result.confidence,
                execution_time=discovery_result.execution_time,
                selector_validated=validation_result['valid'],
                validation_confidence=validation_result.get('confidence', 0.0),
                discovery_details={
                    'discovery_strategy': discovery_result.strategy_used.value,
                    'matched_attributes': discovery_result.matched_attributes,
                    'similarity_score': discovery_result.similarity_score,
                    'attempts_made': discovery_result.attempts_made
                },
                error_message=None if validation_result['valid'] else "Discovered selector validation failed"
            )
            
        except Exception as e:
            return HealingResult(
                success=False,
                healed_selector=None,
                new_automation_id=None,
                strategy_used=HealingStrategy.DISCOVERY_SERVICE,
                healing_confidence=0.0,
                execution_time=0.0,
                selector_validated=False,
                validation_confidence=0.0,
                discovery_details={},
                error_message=f"Discovery service healing failed: {str(e)}"
            )
    
    def _heal_using_relationship_navigation(self, request: HealingRequest, 
                                          cached_entry: Optional[CachedSelectorEntry]) -> HealingResult:
        """Heal selector using relationship navigation"""
        try:
            if not request.window_element:
                return HealingResult(
                    success=False,
                    healed_selector=None,
                    new_automation_id=None,
                    strategy_used=HealingStrategy.RELATIONSHIP_NAVIGATION,
                    healing_confidence=0.0,
                    execution_time=0.0,
                    selector_validated=False,
                    validation_confidence=0.0,
                    discovery_details={},
                    error_message="No window element provided for relationship navigation"
                )
            
            # Try to find element using relationship mapping
            available_elements = [request.window_element]
            try:
                # Add other stable elements as potential starting points
                stable_children = request.window_element.GetChildren()[:5]  # First 5 children
                available_elements.extend(stable_children)
            except:
                pass
            
            found_element = self.relationship_mapper.find_element_using_relationships(
                request.element_fingerprint, 
                available_elements, 
                timeout=min(request.timeout, 20.0)
            )
            
            if not found_element:
                return HealingResult(
                    success=False,
                    healed_selector=None,
                    new_automation_id=None,
                    strategy_used=HealingStrategy.RELATIONSHIP_NAVIGATION,
                    healing_confidence=0.0,
                    execution_time=0.0,
                    selector_validated=False,
                    validation_confidence=0.0,
                    discovery_details={},
                    error_message="Element not found using relationship navigation"
                )
            
            # Extract new AutomationId from found element
            new_automation_id = getattr(found_element, 'AutomationId', '') or None
            
            if not new_automation_id:
                return HealingResult(
                    success=False,
                    healed_selector=None,
                    new_automation_id=None,
                    strategy_used=HealingStrategy.RELATIONSHIP_NAVIGATION,
                    healing_confidence=0.0,
                    execution_time=0.0,
                    selector_validated=False,
                    validation_confidence=0.0,
                    discovery_details={},
                    error_message="Found element has no AutomationId"
                )
            
            # Generate new selector with found AutomationId
            healed_selector = self._update_selector_automation_id(
                request.failed_selector, 
                new_automation_id
            )
            
            # Validate the healed selector
            validation_result = self._validate_healed_selector(healed_selector, request)
            
            return HealingResult(
                success=validation_result['valid'],
                healed_selector=healed_selector if validation_result['valid'] else None,
                new_automation_id=new_automation_id,
                strategy_used=HealingStrategy.RELATIONSHIP_NAVIGATION,
                healing_confidence=0.75,  # Medium confidence for relationship navigation
                execution_time=0.0,
                selector_validated=validation_result['valid'],
                validation_confidence=validation_result.get('confidence', 0.0),
                discovery_details={
                    'navigation_method': 'relationship_mapping',
                    'found_automation_id': new_automation_id
                },
                error_message=None if validation_result['valid'] else "Relationship-based selector validation failed"
            )
            
        except Exception as e:
            return HealingResult(
                success=False,
                healed_selector=None,
                new_automation_id=None,
                strategy_used=HealingStrategy.RELATIONSHIP_NAVIGATION,
                healing_confidence=0.0,
                execution_time=0.0,
                selector_validated=False,
                validation_confidence=0.0,
                discovery_details={},
                error_message=f"Relationship navigation healing failed: {str(e)}"
            )
    
    def _heal_by_regenerating_selector(self, request: HealingRequest, 
                                     cached_entry: Optional[CachedSelectorEntry]) -> HealingResult:
        """Heal selector by regenerating it completely"""
        try:
            # Convert fingerprint back to element data format for generator
            element_data = self._fingerprint_to_element_data(request.element_fingerprint)
            
            # Generate new ultra-robust selector
            generated_selectors = self.selector_generator.generate_ultra_robust_selectors(element_data)
            
            if not generated_selectors:
                return HealingResult(
                    success=False,
                    healed_selector=None,
                    new_automation_id=None,
                    strategy_used=HealingStrategy.REGENERATE_SELECTOR,
                    healing_confidence=0.0,
                    execution_time=0.0,
                    selector_validated=False,
                    validation_confidence=0.0,
                    discovery_details={},
                    error_message="No selectors generated during regeneration"
                )
            
            # Try each generated selector until one works
            for i, selector_info in enumerate(generated_selectors):
                selector_xml = selector_info.get('xml_selector', '')
                if not selector_xml:
                    continue
                
                validation_result = self._validate_healed_selector(selector_xml, request)
                
                if validation_result['valid']:
                    # Extract automation ID from the working selector
                    new_automation_id = self._extract_automation_id_from_selector(selector_xml)
                    
                    return HealingResult(
                        success=True,
                        healed_selector=selector_xml,
                        new_automation_id=new_automation_id,
                        strategy_used=HealingStrategy.REGENERATE_SELECTOR,
                        healing_confidence=selector_info.get('confidence', 0.5),
                        execution_time=0.0,
                        selector_validated=True,
                        validation_confidence=validation_result.get('confidence', 0.0),
                        discovery_details={
                            'generation_strategy': selector_info.get('strategy', 'unknown'),
                            'selector_index': i,
                            'total_generated': len(generated_selectors)
                        },
                        error_message=None
                    )
            
            # No generated selector worked
            return HealingResult(
                success=False,
                healed_selector=None,
                new_automation_id=None,
                strategy_used=HealingStrategy.REGENERATE_SELECTOR,
                healing_confidence=0.0,
                execution_time=0.0,
                selector_validated=False,
                validation_confidence=0.0,
                discovery_details={
                    'total_generated': len(generated_selectors),
                    'all_failed_validation': True
                },
                error_message="All regenerated selectors failed validation"
            )
            
        except Exception as e:
            return HealingResult(
                success=False,
                healed_selector=None,
                new_automation_id=None,
                strategy_used=HealingStrategy.REGENERATE_SELECTOR,
                healing_confidence=0.0,
                execution_time=0.0,
                selector_validated=False,
                validation_confidence=0.0,
                discovery_details={},
                error_message=f"Selector regeneration healing failed: {str(e)}"
            )
    
    def _heal_using_hybrid_approach(self, request: HealingRequest, 
                                  cached_entry: Optional[CachedSelectorEntry]) -> HealingResult:
        """Heal selector using multiple strategies combined"""
        try:
            # This would implement a sophisticated hybrid approach
            # For now, try strategies in order and combine results
            
            strategies = [
                HealingStrategy.PATTERN_PREDICTION,
                HealingStrategy.DISCOVERY_SERVICE,
                HealingStrategy.RELATIONSHIP_NAVIGATION
            ]
            
            best_result = None
            best_confidence = 0.0
            
            for strategy in strategies:
                try:
                    result = self._execute_healing_strategy(strategy, request, cached_entry)
                    
                    if result.success and result.healing_confidence > best_confidence:
                        best_result = result
                        best_confidence = result.healing_confidence
                        
                        # If we get excellent confidence, use it
                        if result.healing_confidence >= 0.9:
                            break
                            
                except Exception:
                    continue
            
            if best_result and best_result.success:
                best_result.strategy_used = HealingStrategy.HYBRID_APPROACH
                return best_result
            else:
                return HealingResult(
                    success=False,
                    healed_selector=None,
                    new_automation_id=None,
                    strategy_used=HealingStrategy.HYBRID_APPROACH,
                    healing_confidence=0.0,
                    execution_time=0.0,
                    selector_validated=False,
                    validation_confidence=0.0,
                    discovery_details={},
                    error_message="All hybrid strategies failed"
                )
                
        except Exception as e:
            return HealingResult(
                success=False,
                healed_selector=None,
                new_automation_id=None,
                strategy_used=HealingStrategy.HYBRID_APPROACH,
                healing_confidence=0.0,
                execution_time=0.0,
                selector_validated=False,
                validation_confidence=0.0,
                discovery_details={},
                error_message=f"Hybrid healing approach failed: {str(e)}"
            )
    
    def _update_selector_automation_id(self, original_selector: str, new_automation_id: str) -> Optional[str]:
        """Update AutomationId in XML selector"""
        try:
            import xml.etree.ElementTree as ET
            
            # Parse the XML
            root = ET.fromstring(original_selector)
            
            # Find Element tags and update automationId
            updated = False
            for element in root.iter():
                if element.tag == 'Element' and 'automationId' in element.attrib:
                    element.attrib['automationId'] = new_automation_id
                    updated = True
                    break
            
            if updated:
                # Convert back to string
                return ET.tostring(root, encoding='unicode')
            else:
                # If no automationId found, try to add it to the first Element
                for element in root.iter():
                    if element.tag == 'Element':
                        element.attrib['automationId'] = new_automation_id
                        return ET.tostring(root, encoding='unicode')
                
                return None
                
        except Exception as e:
            print_warning(f"Failed to update selector AutomationId: {str(e)}")
            return None
    
    def _extract_automation_id_from_selector(self, selector_xml: str) -> Optional[str]:
        """Extract AutomationId from XML selector"""
        try:
            import xml.etree.ElementTree as ET
            
            root = ET.fromstring(selector_xml)
            
            for element in root.iter():
                if element.tag == 'Element' and 'automationId' in element.attrib:
                    return element.attrib['automationId']
            
            return None
            
        except Exception:
            return None
    
    def _validate_healed_selector(self, healed_selector: str, request: HealingRequest) -> Dict[str, Any]:
        """Validate that the healed selector works"""
        try:
            # Import here to avoid circular imports
            from xml_selector_executor import XMLSelectorExecutor
            
            executor = XMLSelectorExecutor()
            
            # Try to execute the selector
            found_element = executor.execute_selector(healed_selector, timeout=5.0)
            
            if found_element:
                # Verify it matches the expected fingerprint
                element_properties = self._extract_element_properties(found_element)
                element_fingerprint = self._create_fingerprint_from_properties(element_properties)
                
                match_result = self.fingerprint_engine.calculate_fingerprint_similarity(
                    request.element_fingerprint, element_fingerprint
                )
                
                return {
                    'valid': match_result.confidence >= 0.6,
                    'confidence': match_result.confidence,
                    'element_found': True,
                    'fingerprint_match': match_result.confidence
                }
            else:
                return {
                    'valid': False,
                    'confidence': 0.0,
                    'element_found': False,
                    'error': 'Selector execution failed'
                }
                
        except Exception as e:
            return {
                'valid': False,
                'confidence': 0.0,
                'element_found': False,
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
            
        except Exception:
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
    
    def _fingerprint_to_element_data(self, fingerprint: ElementFingerprint) -> Dict[str, Any]:
        """Convert fingerprint back to element data format"""
        return {
            'automation_id': '',  # Will be discovered/generated
            'name': fingerprint.name or '',
            'class_name': fingerprint.class_name or '',
            'control_type': fingerprint.control_type or '',
            'localized_control_type': fingerprint.localized_control_type or '',
            'value': fingerprint.value or '',
            'bounding_rectangle': fingerprint.bounding_rect or {},
            'window_info': {
                'title': fingerprint.window_title or '',
                'class_name': fingerprint.window_class or ''
            }
        }
    
    def _update_cache_with_healing_result(self, cached_entry: CachedSelectorEntry, 
                                        healing_result: HealingResult, strategy: HealingStrategy):
        """Update cache with healing results"""
        try:
            if not healing_result.healed_selector:
                return
            
            # Create new selector version
            new_version = SelectorVersion(
                version=len(cached_entry.selector_versions) + 1,
                xml_content=healing_result.healed_selector,
                strategy=SelectorStrategy.PATTERN_PREDICTED if strategy == HealingStrategy.PATTERN_PREDICTION else SelectorStrategy.NAME_HIERARCHY,
                confidence_score=healing_result.healing_confidence,
                created_at=datetime.now().isoformat(),
                created_by="healing_engine",
                healing_source=strategy.value
            )
            
            # Add to cache entry
            cached_entry.selector_versions.insert(0, new_version)  # Add at beginning
            cached_entry.current_version = new_version.version
            cached_entry.last_updated = datetime.now().isoformat()
            
            # Update AutomationId if available
            if healing_result.new_automation_id:
                self.cache.update_automation_id(cached_entry.cache_id, healing_result.new_automation_id)
            
            print_info(f"Cache updated with healed selector (strategy: {strategy.value})")
            
        except Exception as e:
            print_warning(f"Failed to update cache with healing result: {str(e)}")
    
    def _update_strategy_success_rate(self, strategy: HealingStrategy, success: bool):
        """Update success rate tracking for healing strategies"""
        if strategy not in self.strategy_success_rates:
            self.strategy_success_rates[strategy] = {'successes': 0, 'attempts': 0}
        
        self.strategy_success_rates[strategy]['attempts'] += 1
        if success:
            self.strategy_success_rates[strategy]['successes'] += 1
    
    def get_healing_statistics(self) -> Dict[str, Any]:
        """Get comprehensive healing engine statistics"""
        overall_success_rate = (self.successful_healings / self.total_healing_requests * 100) if self.total_healing_requests > 0 else 0.0
        
        strategy_stats = {}
        for strategy, stats in self.strategy_success_rates.items():
            strategy_rate = (stats['successes'] / stats['attempts'] * 100) if stats['attempts'] > 0 else 0.0
            strategy_stats[strategy.value] = {
                'success_rate': strategy_rate,
                'total_attempts': stats['attempts'],
                'successful_attempts': stats['successes']
            }
        
        # Get statistics from component engines
        discovery_stats = self.discovery_service.get_statistics()
        pattern_stats = self.pattern_engine.get_learning_statistics()
        relationship_stats = self.relationship_mapper.get_relationship_statistics()
        
        return {
            'total_healing_requests': self.total_healing_requests,
            'successful_healings': self.successful_healings,
            'overall_success_rate': overall_success_rate,
            'strategy_statistics': strategy_stats,
            'component_statistics': {
                'discovery_service': discovery_stats,
                'pattern_engine': pattern_stats,
                'relationship_mapper': relationship_stats
            }
        }

# Export main classes
__all__ = [
    'SelectorHealingEngine',
    'HealingRequest',
    'HealingResult',
    'HealingStrategy',
    'HealingPriority'
]