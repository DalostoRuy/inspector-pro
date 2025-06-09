"""
Adaptive Integration Layer
Version 1.0 - Integration bridge for adaptive selector system

This module provides seamless integration between the adaptive selector evolution
system and the existing ElementInspector and XMLSelectorExecutor classes.
"""

import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from dynamic_selector_cache import DynamicSelectorCache
from dynamic_selector_cache_schema import (
    create_fingerprint_from_element_data, SelectorStrategy, CacheConfiguration
)
from selector_healing_engine import (
    SelectorHealingEngine, HealingRequest, HealingResult, HealingStrategy, HealingPriority
)
from adaptive_selector_generator import (
    AdaptiveSelectorGenerator, GenerationContext, GenerationMode, AdaptiveStrategy
)
from pattern_learning_engine import PatternLearningEngine
from automation_id_discovery import AutomationIdDiscoveryService
from element_relationship_mapper import ElementRelationshipMapper
from element_fingerprinting import ElementFingerprintEngine
from utils import print_info, print_success, print_warning, print_error

class AdaptiveIntegrationLayer:
    """
    Integration layer that bridges adaptive capabilities with existing systems
    
    This class provides a unified interface for adaptive selector functionality
    while maintaining backward compatibility with existing code.
    """
    
    def __init__(self, enable_adaptive_features: bool = True, 
                 cache_config: Optional[CacheConfiguration] = None):
        """
        Initialize the adaptive integration layer
        
        Args:
            enable_adaptive_features: Enable adaptive features (can be disabled for compatibility)
            cache_config: Custom cache configuration
        """
        self.enable_adaptive_features = enable_adaptive_features
        
        if self.enable_adaptive_features:
            # Initialize adaptive components
            self.cache = DynamicSelectorCache(cache_config)
            self.healing_engine = SelectorHealingEngine(self.cache)
            self.adaptive_generator = AdaptiveSelectorGenerator(self.cache)
            self.pattern_engine = PatternLearningEngine()
            self.discovery_service = AutomationIdDiscoveryService()
            self.relationship_mapper = ElementRelationshipMapper()
            self.fingerprint_engine = ElementFingerprintEngine()
            
            # Performance tracking
            self.adaptive_captures = 0
            self.healing_attempts = 0
            self.successful_healings = 0
            
            print_success("🚀 Adaptive Integration Layer initialized with full intelligence")
        else:
            print_info("Adaptive Integration Layer initialized in compatibility mode")
    
    def enhance_element_capture(self, element_data: Dict[str, Any], 
                              element_name: str) -> Dict[str, Any]:
        """
        Enhance element capture with adaptive intelligence
        
        Args:
            element_data: Original element data from ElementInspector
            element_name: Name of the captured element
            
        Returns:
            Enhanced element data with adaptive features
        """
        if not self.enable_adaptive_features:
            return element_data
        
        try:
            print_info("🧠 Enhancing element capture with adaptive intelligence...")
            
            enhanced_data = element_data.copy()
            self.adaptive_captures += 1
            
            # Create element fingerprint
            fingerprint = create_fingerprint_from_element_data(element_data)
            enhanced_data['adaptive_fingerprint'] = fingerprint.__dict__
            
            # Generate adaptive selectors
            adaptive_selectors = self._generate_adaptive_selectors(element_data, element_name)
            if adaptive_selectors:
                enhanced_data['adaptive_selectors'] = adaptive_selectors
                print_success(f"✅ Generated {len(adaptive_selectors)} adaptive selectors")
            
            # Analyze AutomationId patterns if available
            automation_id = element_data.get('automation_id')
            if automation_id:
                pattern_analysis = self._analyze_automation_id_patterns(automation_id)
                enhanced_data['pattern_analysis'] = pattern_analysis
            
            # Create relationship mapping
            relationship_map = self._create_relationship_context(element_data)
            if relationship_map:
                enhanced_data['relationship_context'] = relationship_map
            
            # Cache the element for future healing
            cache_id = self._cache_element_for_healing(element_data, enhanced_data, element_name)
            if cache_id:
                enhanced_data['adaptive_cache_id'] = cache_id
                print_info(f"📦 Element cached for adaptive healing: {cache_id}")
            
            # Add adaptive metadata
            enhanced_data['adaptive_metadata'] = {
                'enhanced_at': datetime.now().isoformat(),
                'adaptive_version': '1.0',
                'features_enabled': [
                    'pattern_learning',
                    'relationship_mapping',
                    'selector_healing',
                    'adaptive_generation'
                ],
                'enhancement_time': time.time()
            }
            
            return enhanced_data
            
        except Exception as e:
            print_warning(f"Adaptive enhancement failed: {str(e)}")
            return element_data
    
    def _generate_adaptive_selectors(self, element_data: Dict[str, Any], 
                                   element_name: str) -> List[Dict[str, Any]]:
        """Generate adaptive selectors for the element"""
        try:
            # Create generation context
            context = GenerationContext(
                element_data=element_data,
                mode=GenerationMode.ULTRA_ROBUST,
                max_selectors=3,
                confidence_threshold=0.7,
                prioritize_reliability=True,
                include_fallbacks=True
            )
            
            # Generate adaptive selectors
            generation_result = self.adaptive_generator.generate_adaptive_selectors(context)
            
            if generation_result.success:
                adaptive_selectors = []
                
                for selector in generation_result.selectors:
                    adaptive_selectors.append({
                        'xml_selector': selector.xml_selector,
                        'strategy': selector.strategy.value,
                        'adaptive_strategy': selector.adaptive_strategy.value,
                        'confidence_score': selector.confidence_score,
                        'reliability_prediction': selector.reliability_prediction,
                        'performance_prediction': selector.performance_prediction,
                        'stability_score': selector.stability_score,
                        'learned_optimizations': selector.learned_optimizations,
                        'context_adaptations': selector.context_adaptations,
                        'generation_timestamp': selector.generation_timestamp
                    })
                
                return adaptive_selectors
            
            return []
            
        except Exception as e:
            print_warning(f"Adaptive selector generation failed: {str(e)}")
            return []
    
    def _analyze_automation_id_patterns(self, automation_id: str) -> Dict[str, Any]:
        """Analyze AutomationId for patterns"""
        try:
            # Create mock history for pattern analysis
            history = [
                {'value': automation_id, 'timestamp': datetime.now().isoformat()}
            ]
            
            # Check if we have historical data in cache
            # In a real implementation, this would look up historical AutomationIds
            
            # For now, do basic pattern analysis
            pattern_analysis = {
                'current_automation_id': automation_id,
                'pattern_detected': False,
                'pattern_type': 'unknown',
                'confidence': 0.0,
                'predictive_capability': False,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            # Simple pattern detection
            if automation_id.isdigit():
                pattern_analysis.update({
                    'pattern_detected': True,
                    'pattern_type': 'numeric',
                    'confidence': 0.7,
                    'predictive_capability': True
                })
            elif len(automation_id) >= 10 and automation_id.replace('-', '').replace('_', '').isdigit():
                pattern_analysis.update({
                    'pattern_detected': True,
                    'pattern_type': 'timestamp_based',
                    'confidence': 0.8,
                    'predictive_capability': True
                })
            
            return pattern_analysis
            
        except Exception:
            return {'pattern_detected': False, 'error': 'Pattern analysis failed'}
    
    def _create_relationship_context(self, element_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create relationship context for the element"""
        try:
            # Extract relationship information from element data
            parent_info = element_data.get('parent_info', {})
            window_info = element_data.get('window_info', {})
            
            if not parent_info and not window_info:
                return None
            
            relationship_context = {
                'has_parent_info': bool(parent_info),
                'has_window_context': bool(window_info),
                'hierarchy_depth': 1 if parent_info else 0,
                'stable_anchors': [],
                'navigation_hints': []
            }
            
            # Add parent as potential navigation anchor
            if parent_info and parent_info.get('name'):
                relationship_context['stable_anchors'].append({
                    'type': 'parent',
                    'name': parent_info['name'],
                    'class_name': parent_info.get('class_name', ''),
                    'control_type': parent_info.get('control_type', '')
                })
                relationship_context['navigation_hints'].append('Can navigate via parent element')
            
            # Add window as navigation anchor
            if window_info and window_info.get('title'):
                relationship_context['stable_anchors'].append({
                    'type': 'window',
                    'title': window_info['title'],
                    'class_name': window_info.get('class_name', '')
                })
                relationship_context['navigation_hints'].append('Can navigate via window context')
            
            return relationship_context
            
        except Exception:
            return None
    
    def _cache_element_for_healing(self, element_data: Dict[str, Any], 
                                 enhanced_data: Dict[str, Any], element_name: str) -> Optional[str]:
        """Cache element data for future healing"""
        try:
            # Create fingerprint
            fingerprint = create_fingerprint_from_element_data(element_data)
            
            # Get the best selector (adaptive or traditional)
            xml_selector = None
            strategy = SelectorStrategy.AUTOMATION_ID
            confidence = 0.5
            
            # Prefer adaptive selectors
            adaptive_selectors = enhanced_data.get('adaptive_selectors', [])
            if adaptive_selectors:
                best_adaptive = adaptive_selectors[0]
                xml_selector = best_adaptive['xml_selector']
                strategy = SelectorStrategy(best_adaptive['strategy'])
                confidence = best_adaptive['confidence_score']
            
            # Fallback to ultra-robust selector
            elif 'xml_selector_ultra_robust' in element_data:
                xml_selector = element_data['xml_selector_ultra_robust']
                strategy = SelectorStrategy.AUTOMATION_ID
                metadata = element_data.get('ultra_robust_metadata', {})
                confidence = metadata.get('reliability_score', 50) / 100.0
            
            # Fallback to traditional selectors
            elif element_data.get('xml_selectors'):
                selectors = element_data['xml_selectors']
                if selectors:
                    xml_selector = selectors[0]
                    strategy = SelectorStrategy.NAME_HIERARCHY
                    confidence = 0.6
            
            if xml_selector:
                # Cache in the adaptive system
                cache_id = self.cache.put(
                    fingerprint=fingerprint,
                    xml_selector=xml_selector,
                    strategy=strategy,
                    automation_id=element_data.get('automation_id'),
                    confidence=confidence
                )
                
                return cache_id
            
            return None
            
        except Exception as e:
            print_warning(f"Failed to cache element for healing: {str(e)}")
            return None
    
    def enhance_xml_selector_execution(self, xml_selector: str, action_type: str = "click",
                                     timeout: float = 5.0, 
                                     enable_auto_healing: bool = True) -> Dict[str, Any]:
        """
        Enhance XML selector execution with adaptive capabilities
        
        Args:
            xml_selector: XML selector to execute
            action_type: Type of action to perform
            timeout: Execution timeout
            enable_auto_healing: Enable automatic healing if selector fails
            
        Returns:
            Enhanced execution result with adaptive features
        """
        if not self.enable_adaptive_features:
            # Return standard execution result format
            return {
                'success': False,
                'adaptive_features_disabled': True,
                'message': 'Adaptive features disabled - use standard XMLSelectorExecutor'
            }
        
        start_time = time.time()
        
        try:
            print_info(f"🎯 Executing selector with adaptive capabilities...")
            
            # Try standard execution first
            execution_result = self._execute_standard_selector(xml_selector, action_type, timeout)
            
            if execution_result['success']:
                # Successful execution - update cache with success metrics
                self._update_success_metrics(xml_selector, execution_result)
                
                execution_result.update({
                    'adaptive_enhancement': True,
                    'healing_required': False,
                    'execution_path': 'standard',
                    'total_execution_time': time.time() - start_time
                })
                
                return execution_result
            
            # Standard execution failed - try adaptive healing if enabled
            if enable_auto_healing:
                print_warning("Standard execution failed - attempting adaptive healing...")
                healing_result = self._attempt_selector_healing(xml_selector, action_type, timeout)
                
                if healing_result['success']:
                    return healing_result
                else:
                    # Healing also failed - return comprehensive failure result
                    return {
                        'success': False,
                        'adaptive_enhancement': True,
                        'healing_attempted': True,
                        'healing_result': healing_result,
                        'original_failure': execution_result,
                        'execution_path': 'healing_failed',
                        'total_execution_time': time.time() - start_time,
                        'error_message': f"Both standard execution and adaptive healing failed"
                    }
            else:
                # Return standard failure with adaptive metadata
                execution_result.update({
                    'adaptive_enhancement': True,
                    'healing_available': True,
                    'healing_attempted': False,
                    'execution_path': 'standard_failed',
                    'total_execution_time': time.time() - start_time,
                    'suggestion': 'Enable auto-healing for automatic recovery'
                })
                
                return execution_result
            
        except Exception as e:
            return {
                'success': False,
                'adaptive_enhancement': True,
                'error': str(e),
                'execution_path': 'exception',
                'total_execution_time': time.time() - start_time,
                'error_message': f"Adaptive execution failed: {str(e)}"
            }
    
    def _execute_standard_selector(self, xml_selector: str, action_type: str, timeout: float) -> Dict[str, Any]:
        """Execute selector using standard XMLSelectorExecutor"""
        try:
            # Import here to avoid circular dependencies
            from xml_selector_executor import XMLSelectorExecutor
            
            executor = XMLSelectorExecutor()
            result = executor.execute_click_action(xml_selector, action_type, timeout)
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'execution_method': 'standard_executor'
            }
    
    def _attempt_selector_healing(self, xml_selector: str, action_type: str, timeout: float) -> Dict[str, Any]:
        """Attempt to heal a failed selector and execute the healed version"""
        self.healing_attempts += 1
        
        try:
            print_info("🔧 Initiating adaptive selector healing...")
            
            # Extract element fingerprint from failed selector (simplified approach)
            fingerprint = self._extract_fingerprint_from_selector(xml_selector)
            
            if not fingerprint:
                return {
                    'success': False,
                    'healing_attempted': True,
                    'error': 'Could not extract element fingerprint from selector',
                    'healing_stage': 'fingerprint_extraction'
                }
            
            # Create healing request
            healing_request = HealingRequest(
                cache_id="", # Will be determined by healing engine
                failed_selector=xml_selector,
                element_fingerprint=fingerprint,
                failure_reason="Standard execution failed",
                priority=HealingPriority.HIGH,
                timeout=timeout,
                preferred_strategies=[
                    HealingStrategy.DISCOVERY_SERVICE,
                    HealingStrategy.PATTERN_PREDICTION,
                    HealingStrategy.RELATIONSHIP_NAVIGATION
                ]
            )
            
            # Attempt healing
            healing_result = self.healing_engine.heal_selector(healing_request)
            
            if healing_result.success and healing_result.healed_selector:
                print_success("🎉 Selector healing successful!")
                
                # Execute healed selector
                execution_result = self._execute_standard_selector(
                    healing_result.healed_selector, 
                    action_type, 
                    timeout
                )
                
                if execution_result['success']:
                    self.successful_healings += 1
                    
                    return {
                        'success': True,
                        'adaptive_enhancement': True,
                        'healing_attempted': True,
                        'healing_successful': True,
                        'healed_selector': healing_result.healed_selector,
                        'healing_strategy': healing_result.strategy_used.value,
                        'healing_confidence': healing_result.healing_confidence,
                        'original_selector': xml_selector,
                        'execution_result': execution_result,
                        'execution_path': 'healed_success',
                        'new_automation_id': healing_result.new_automation_id
                    }
                else:
                    return {
                        'success': False,
                        'adaptive_enhancement': True,
                        'healing_attempted': True,
                        'healing_successful': True,
                        'execution_failed': True,
                        'healed_selector': healing_result.healed_selector,
                        'healing_result': healing_result,
                        'execution_result': execution_result,
                        'execution_path': 'healed_execution_failed'
                    }
            else:
                return {
                    'success': False,
                    'adaptive_enhancement': True,
                    'healing_attempted': True,
                    'healing_successful': False,
                    'healing_result': healing_result,
                    'execution_path': 'healing_failed',
                    'error_message': healing_result.error_message or "Healing failed for unknown reason"
                }
                
        except Exception as e:
            return {
                'success': False,
                'adaptive_enhancement': True,
                'healing_attempted': True,
                'healing_error': str(e),
                'execution_path': 'healing_exception',
                'error_message': f"Healing attempt failed: {str(e)}"
            }
    
    def _extract_fingerprint_from_selector(self, xml_selector: str) -> Optional[Any]:
        """Extract element fingerprint from XML selector (simplified approach)"""
        try:
            import xml.etree.ElementTree as ET
            from dynamic_selector_cache_schema import ElementFingerprint
            
            root = ET.fromstring(xml_selector)
            
            # Extract information from XML
            name = None
            class_name = None
            control_type = None
            automation_id = None
            window_title = None
            
            # Look for Window element
            for window in root.iter('Window'):
                window_title = window.get('title')
            
            # Look for Element
            for element in root.iter('Element'):
                automation_id = element.get('automationId')
                name = element.get('name')
                class_name = element.get('className')
                control_type = element.get('controlType')
            
            # Create fingerprint
            fingerprint = ElementFingerprint(
                name=name,
                class_name=class_name,
                control_type=control_type,
                window_title=window_title
            )
            
            return fingerprint
            
        except Exception:
            return None
    
    def _update_success_metrics(self, xml_selector: str, execution_result: Dict[str, Any]):
        """Update success metrics for selector execution"""
        try:
            # This would update cache with execution success
            # For now, just track basic metrics
            execution_time = execution_result.get('execution_time', 0.0)
            print_info(f"✅ Selector executed successfully in {execution_time:.2f}s")
            
        except Exception:
            pass
    
    def get_adaptive_statistics(self) -> Dict[str, Any]:
        """Get comprehensive adaptive system statistics"""
        if not self.enable_adaptive_features:
            return {'adaptive_features_enabled': False}
        
        try:
            # Get statistics from all components
            cache_stats = self.cache.get_statistics()
            healing_stats = self.healing_engine.get_healing_statistics()
            generator_stats = self.adaptive_generator.get_adaptive_statistics()
            discovery_stats = self.discovery_service.get_statistics()
            pattern_stats = self.pattern_engine.get_learning_statistics()
            relationship_stats = self.relationship_mapper.get_relationship_statistics()
            
            # Calculate integration layer metrics
            healing_success_rate = (self.successful_healings / self.healing_attempts * 100) if self.healing_attempts > 0 else 0.0
            
            return {
                'adaptive_features_enabled': True,
                'integration_layer': {
                    'adaptive_captures': self.adaptive_captures,
                    'healing_attempts': self.healing_attempts,
                    'successful_healings': self.successful_healings,
                    'healing_success_rate': healing_success_rate
                },
                'component_statistics': {
                    'cache': cache_stats,
                    'healing_engine': healing_stats,
                    'adaptive_generator': generator_stats,
                    'discovery_service': discovery_stats,
                    'pattern_engine': pattern_stats,
                    'relationship_mapper': relationship_stats
                },
                'system_health': {
                    'cache_size': cache_stats.get('cache_size', 0),
                    'cache_hit_rate': cache_stats.get('hit_rate', 0.0),
                    'overall_healing_success': healing_stats.get('overall_success_rate', 0.0),
                    'pattern_detection_rate': pattern_stats.get('pattern_success_rate', 0.0)
                }
            }
            
        except Exception as e:
            return {
                'adaptive_features_enabled': True,
                'error': str(e),
                'statistics_available': False
            }
    
    def enable_adaptive_mode(self):
        """Enable adaptive features if they were disabled"""
        if not self.enable_adaptive_features:
            self.__init__(enable_adaptive_features=True)
            print_success("🚀 Adaptive features enabled")
    
    def disable_adaptive_mode(self):
        """Disable adaptive features for compatibility mode"""
        self.enable_adaptive_features = False
        print_info("Adaptive features disabled - running in compatibility mode")
    
    def save_adaptive_data(self) -> bool:
        """Save all adaptive data to disk"""
        if not self.enable_adaptive_features:
            return False
        
        try:
            # Save cache data
            cache_saved = self.cache.save_cache()
            
            if cache_saved:
                print_success("💾 Adaptive data saved successfully")
                return True
            else:
                print_warning("Failed to save adaptive data")
                return False
                
        except Exception as e:
            print_error(f"Error saving adaptive data: {str(e)}")
            return False

# Enhanced ElementInspector integration
class AdaptiveElementInspector:
    """
    Enhanced ElementInspector with adaptive capabilities
    
    This class wraps the original ElementInspector and adds adaptive features
    while maintaining full backward compatibility.
    """
    
    def __init__(self, enable_adaptive_features: bool = True):
        """Initialize enhanced ElementInspector"""
        # Import the original ElementInspector
        from element_inspector import ElementInspector
        
        self.original_inspector = ElementInspector()
        self.adaptive_layer = AdaptiveIntegrationLayer(enable_adaptive_features)
        self.enable_adaptive_features = enable_adaptive_features
    
    def start_capture_mode(self, element_name: str, capture_type: str = "element") -> Optional[Dict[str, Any]]:
        """Enhanced capture mode with adaptive features"""
        # Use original capture logic
        capture_result = self.original_inspector.start_capture_mode(element_name, capture_type)
        
        if capture_result and self.enable_adaptive_features:
            # Enhance with adaptive capabilities
            element_data = capture_result.get('element_data', {})
            enhanced_data = self.adaptive_layer.enhance_element_capture(element_data, element_name)
            
            # Update result with enhanced data
            capture_result['element_data'] = enhanced_data
            capture_result['adaptive_enhanced'] = True
        
        return capture_result
    
    def execute_xml_selector_action(self, xml_selector: str, action_type: str = "click") -> Dict[str, Any]:
        """Enhanced XML selector execution with adaptive capabilities"""
        if self.enable_adaptive_features:
            return self.adaptive_layer.enhance_xml_selector_execution(xml_selector, action_type)
        else:
            # Use original execution
            return self.original_inspector.execute_xml_selector_action(xml_selector, action_type)
    
    def test_xml_selector(self, xml_selector: str) -> Dict[str, Any]:
        """Enhanced XML selector testing"""
        # Use original testing logic
        result = self.original_inspector.test_xml_selector(xml_selector)
        
        if self.enable_adaptive_features and not result.get('success', False):
            # Add healing suggestion
            result['adaptive_healing_available'] = True
            result['suggestion'] = 'Consider using adaptive healing to repair this selector'
        
        return result
    
    def get_adaptive_statistics(self) -> Dict[str, Any]:
        """Get adaptive system statistics"""
        return self.adaptive_layer.get_adaptive_statistics()
    
    # Delegate all other methods to original inspector
    def __getattr__(self, name):
        return getattr(self.original_inspector, name)

# Enhanced XMLSelectorExecutor integration
class AdaptiveXMLSelectorExecutor:
    """
    Enhanced XMLSelectorExecutor with adaptive capabilities
    
    This class wraps the original XMLSelectorExecutor and adds adaptive features.
    """
    
    def __init__(self, enable_adaptive_features: bool = True):
        """Initialize enhanced XMLSelectorExecutor"""
        from xml_selector_executor import XMLSelectorExecutor
        
        self.original_executor = XMLSelectorExecutor()
        self.adaptive_layer = AdaptiveIntegrationLayer(enable_adaptive_features)
        self.enable_adaptive_features = enable_adaptive_features
    
    def execute_click_action(self, xml_selector: str, action_type: str = "click", 
                           timeout: Optional[int] = None) -> Dict[str, Any]:
        """Enhanced click action execution with adaptive capabilities"""
        if self.enable_adaptive_features:
            return self.adaptive_layer.enhance_xml_selector_execution(
                xml_selector, action_type, timeout or 5.0
            )
        else:
            # Use original execution
            return self.original_executor.execute_click_action(xml_selector, action_type, timeout)
    
    def execute_selector(self, xml_selector: str, timeout: Optional[int] = None):
        """Enhanced selector execution"""
        if self.enable_adaptive_features:
            # Try original execution first
            result = self.original_executor.execute_selector(xml_selector, timeout)
            
            if not result:
                # Attempt healing
                print_info("🔧 Original execution failed - attempting adaptive healing...")
                healing_result = self.adaptive_layer._attempt_selector_healing(
                    xml_selector, "find", timeout or 5.0
                )
                
                if healing_result.get('success') and healing_result.get('healed_selector'):
                    # Try healed selector
                    return self.original_executor.execute_selector(
                        healing_result['healed_selector'], timeout
                    )
            
            return result
        else:
            # Use original execution
            return self.original_executor.execute_selector(xml_selector, timeout)
    
    # Delegate all other methods to original executor
    def __getattr__(self, name):
        return getattr(self.original_executor, name)

# Export main classes
__all__ = [
    'AdaptiveIntegrationLayer',
    'AdaptiveElementInspector', 
    'AdaptiveXMLSelectorExecutor'
]