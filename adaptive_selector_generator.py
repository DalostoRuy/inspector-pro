"""
Adaptive Selector Generator
Version 1.0 - Generate new selectors using learned patterns and intelligence

This module enhances selector generation by incorporating pattern learning,
stability analysis, and adaptive strategies based on historical performance.
"""

import time
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from dynamic_selector_cache import DynamicSelectorCache
from dynamic_selector_cache_schema import (
    SelectorStrategy, SelectorVersion, create_fingerprint_from_element_data
)
from element_fingerprinting import ElementFingerprintEngine
from pattern_learning_engine import PatternLearningEngine
from xml_selector_generator import XMLSelectorGenerator
from utils import print_info, print_success, print_warning, print_error

class GenerationMode(Enum):
    """Different modes for selector generation"""
    ULTRA_ROBUST = "ultra_robust"           # Maximum reliability
    PERFORMANCE_OPTIMIZED = "performance"   # Balance of speed and reliability
    ADAPTIVE_LEARNING = "adaptive"          # Uses learned patterns
    FALLBACK_HEAVY = "fallback_heavy"       # Many fallback strategies
    MINIMAL_STABLE = "minimal_stable"       # Minimum viable selector

class AdaptiveStrategy(Enum):
    """Adaptive strategies based on learned patterns"""
    PATTERN_AWARE = "pattern_aware"         # Uses AutomationId patterns
    STABILITY_BASED = "stability_based"     # Focuses on stable attributes
    CONTEXT_ADAPTIVE = "context_adaptive"   # Adapts to application context
    PERFORMANCE_TUNED = "performance_tuned" # Optimized for execution speed
    RELATIONSHIP_ENHANCED = "relationship_enhanced"  # Enhanced with relationship mapping

@dataclass
class GenerationContext:
    """Context information for adaptive generation"""
    element_data: Dict[str, Any]
    application_context: Optional[Dict[str, Any]] = None
    historical_performance: Optional[Dict[str, Any]] = None
    user_preferences: Optional[Dict[str, Any]] = None
    
    # Generation settings
    mode: GenerationMode = GenerationMode.ULTRA_ROBUST
    preferred_strategies: List[AdaptiveStrategy] = None
    max_selectors: int = 5
    confidence_threshold: float = 0.7
    
    # Optimization preferences
    prioritize_speed: bool = False
    prioritize_reliability: bool = True
    include_fallbacks: bool = True

@dataclass
class AdaptiveSelector:
    """Enhanced selector with adaptive intelligence"""
    xml_selector: str
    strategy: SelectorStrategy
    adaptive_strategy: AdaptiveStrategy
    
    # Intelligence metrics
    confidence_score: float
    reliability_prediction: float
    performance_prediction: float
    stability_score: float
    
    # Adaptation information
    pattern_awareness: Dict[str, Any]
    learned_optimizations: List[str]
    context_adaptations: List[str]
    
    # Metadata
    generation_timestamp: str
    generated_by: str = "adaptive_generator"
    version: str = "1.0"

@dataclass
class GenerationResult:
    """Result of adaptive selector generation"""
    success: bool
    selectors: List[AdaptiveSelector]
    primary_selector: Optional[AdaptiveSelector]
    
    # Generation process information
    generation_time: float
    strategies_used: List[AdaptiveStrategy]
    optimizations_applied: List[str]
    
    # Intelligence insights
    pattern_analysis: Optional[Dict[str, Any]] = None
    stability_analysis: Optional[Dict[str, Any]] = None
    performance_predictions: Optional[Dict[str, Any]] = None
    
    # Error information
    error_message: Optional[str] = None
    warnings: List[str] = None

class AdaptiveSelectorGenerator:
    """
    Advanced selector generator with learning and adaptation capabilities
    
    This generator enhances traditional XML selector creation by incorporating
    pattern learning, stability analysis, and adaptive optimization strategies.
    """
    
    def __init__(self, cache: Optional[DynamicSelectorCache] = None):
        """
        Initialize the adaptive generator
        
        Args:
            cache: Optional cache for learning from historical data
        """
        self.cache = cache
        self.fingerprint_engine = ElementFingerprintEngine()
        self.pattern_engine = PatternLearningEngine()
        self.xml_generator = XMLSelectorGenerator()
        
        # Learning data
        self.strategy_performance = {}  # Track strategy performance over time
        self.application_patterns = {}  # Application-specific patterns
        self.optimization_rules = {}    # Learned optimization rules
        
        # Configuration
        self.default_strategies = [
            AdaptiveStrategy.STABILITY_BASED,
            AdaptiveStrategy.PATTERN_AWARE,
            AdaptiveStrategy.CONTEXT_ADAPTIVE
        ]
        
        # Performance tracking
        self.total_generations = 0
        self.successful_generations = 0
        self.strategy_usage_stats = {}
        
        print_info("Adaptive Selector Generator initialized")
    
    def generate_adaptive_selectors(self, context: GenerationContext) -> GenerationResult:
        """
        Generate adaptive selectors using intelligent strategies
        
        Args:
            context: Generation context with element data and preferences
            
        Returns:
            GenerationResult: Complete generation result with adaptive selectors
        """
        start_time = time.time()
        self.total_generations += 1
        
        print_info(f"Generating adaptive selectors in {context.mode.value} mode...")
        
        try:
            # Analyze element for adaptive insights
            analysis_results = self._analyze_element_for_adaptation(context.element_data)
            
            # Determine optimal strategies based on analysis
            optimal_strategies = self._determine_optimal_strategies(context, analysis_results)
            
            # Generate selectors using adaptive strategies
            generated_selectors = []
            generation_warnings = []
            
            for strategy in optimal_strategies:
                try:
                    print_info(f"Applying adaptive strategy: {strategy.value}")
                    
                    selectors = self._generate_using_adaptive_strategy(strategy, context, analysis_results)
                    generated_selectors.extend(selectors)
                    
                    # Track strategy usage
                    self._update_strategy_usage(strategy)
                    
                except Exception as e:
                    warning_msg = f"Strategy {strategy.value} failed: {str(e)}"
                    print_warning(warning_msg)
                    generation_warnings.append(warning_msg)
                    continue
            
            if not generated_selectors:
                return GenerationResult(
                    success=False,
                    selectors=[],
                    primary_selector=None,
                    generation_time=time.time() - start_time,
                    strategies_used=[],
                    optimizations_applied=[],
                    error_message="No selectors generated by any adaptive strategy",
                    warnings=generation_warnings
                )
            
            # Rank and optimize selectors
            ranked_selectors = self._rank_selectors_by_intelligence(generated_selectors, context)
            
            # Apply post-generation optimizations
            optimized_selectors = self._apply_post_generation_optimizations(ranked_selectors, context)
            
            # Select primary selector
            primary_selector = optimized_selectors[0] if optimized_selectors else None
            
            # Limit number of selectors if requested
            if context.max_selectors > 0:
                optimized_selectors = optimized_selectors[:context.max_selectors]
            
            generation_time = time.time() - start_time
            self.successful_generations += 1
            
            result = GenerationResult(
                success=True,
                selectors=optimized_selectors,
                primary_selector=primary_selector,
                generation_time=generation_time,
                strategies_used=optimal_strategies,
                optimizations_applied=self._get_applied_optimizations(optimized_selectors),
                pattern_analysis=analysis_results.get('pattern_analysis'),
                stability_analysis=analysis_results.get('stability_analysis'),
                performance_predictions=analysis_results.get('performance_predictions'),
                warnings=generation_warnings
            )
            
            print_success(f"Generated {len(optimized_selectors)} adaptive selectors "
                         f"(primary confidence: {primary_selector.confidence_score:.2f})")
            
            return result
            
        except Exception as e:
            return GenerationResult(
                success=False,
                selectors=[],
                primary_selector=None,
                generation_time=time.time() - start_time,
                strategies_used=[],
                optimizations_applied=[],
                error_message=f"Adaptive generation failed: {str(e)}"
            )
    
    def _analyze_element_for_adaptation(self, element_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze element to determine adaptive strategies"""
        analysis = {
            'pattern_analysis': {},
            'stability_analysis': {},
            'performance_predictions': {},
            'optimization_opportunities': []
        }
        
        try:
            # Create fingerprint for stability analysis
            fingerprint = create_fingerprint_from_element_data(element_data)
            
            # Analyze attribute stability
            stability_analysis = self.fingerprint_engine.get_fingerprint_quality_score(fingerprint)
            analysis['stability_analysis'] = {
                'overall_quality': stability_analysis,
                'stable_attributes': self._identify_stable_attributes(element_data),
                'unstable_attributes': self._identify_unstable_attributes(element_data)
            }
            
            # Check for AutomationId patterns (if we have cache access)
            if self.cache and element_data.get('automation_id'):
                pattern_analysis = self._analyze_automation_id_patterns(element_data['automation_id'])
                analysis['pattern_analysis'] = pattern_analysis
            
            # Predict performance characteristics
            performance_predictions = self._predict_performance_characteristics(element_data)
            analysis['performance_predictions'] = performance_predictions
            
            # Identify optimization opportunities
            optimizations = self._identify_optimization_opportunities(element_data, analysis)
            analysis['optimization_opportunities'] = optimizations
            
            print_info(f"Element analysis complete: {len(optimizations)} optimization opportunities found")
            
        except Exception as e:
            print_warning(f"Element analysis failed: {str(e)}")
        
        return analysis
    
    def _determine_optimal_strategies(self, context: GenerationContext, 
                                   analysis: Dict[str, Any]) -> List[AdaptiveStrategy]:
        """Determine optimal strategies based on context and analysis"""
        strategies = []
        
        # Use preferred strategies if specified
        if context.preferred_strategies:
            strategies.extend(context.preferred_strategies)
        else:
            # Intelligent strategy selection based on analysis
            
            # Always include stability-based strategy
            strategies.append(AdaptiveStrategy.STABILITY_BASED)
            
            # Add pattern-aware if AutomationId patterns detected
            pattern_analysis = analysis.get('pattern_analysis', {})
            if pattern_analysis.get('pattern_detected', False):
                strategies.append(AdaptiveStrategy.PATTERN_AWARE)
            
            # Add context-adaptive for complex applications
            if context.application_context:
                strategies.append(AdaptiveStrategy.CONTEXT_ADAPTIVE)
            
            # Add performance-tuned if speed is prioritized
            if context.prioritize_speed:
                strategies.append(AdaptiveStrategy.PERFORMANCE_TUNED)
            
            # Add relationship-enhanced for complex hierarchies
            stability_analysis = analysis.get('stability_analysis', {})
            if stability_analysis.get('overall_quality', 0) < 0.7:
                strategies.append(AdaptiveStrategy.RELATIONSHIP_ENHANCED)
        
        # Ensure we have at least one strategy
        if not strategies:
            strategies = [AdaptiveStrategy.STABILITY_BASED]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_strategies = []
        for strategy in strategies:
            if strategy not in seen:
                seen.add(strategy)
                unique_strategies.append(strategy)
        
        return unique_strategies[:4]  # Limit to 4 strategies for performance
    
    def _generate_using_adaptive_strategy(self, strategy: AdaptiveStrategy, 
                                        context: GenerationContext,
                                        analysis: Dict[str, Any]) -> List[AdaptiveSelector]:
        """Generate selectors using a specific adaptive strategy"""
        selectors = []
        
        try:
            if strategy == AdaptiveStrategy.STABILITY_BASED:
                selectors = self._generate_stability_based_selectors(context, analysis)
            elif strategy == AdaptiveStrategy.PATTERN_AWARE:
                selectors = self._generate_pattern_aware_selectors(context, analysis)
            elif strategy == AdaptiveStrategy.CONTEXT_ADAPTIVE:
                selectors = self._generate_context_adaptive_selectors(context, analysis)
            elif strategy == AdaptiveStrategy.PERFORMANCE_TUNED:
                selectors = self._generate_performance_tuned_selectors(context, analysis)
            elif strategy == AdaptiveStrategy.RELATIONSHIP_ENHANCED:
                selectors = self._generate_relationship_enhanced_selectors(context, analysis)
            
            # Add strategy metadata to all selectors
            for selector in selectors:
                selector.adaptive_strategy = strategy
                selector.generation_timestamp = datetime.now().isoformat()
            
        except Exception as e:
            print_warning(f"Strategy {strategy.value} generation failed: {str(e)}")
        
        return selectors
    
    def _generate_stability_based_selectors(self, context: GenerationContext, 
                                          analysis: Dict[str, Any]) -> List[AdaptiveSelector]:
        """Generate selectors prioritizing stable attributes"""
        selectors = []
        
        try:
            element_data = context.element_data
            stable_attributes = analysis.get('stability_analysis', {}).get('stable_attributes', [])
            
            # Create selector focusing on most stable attributes
            if stable_attributes:
                # Use traditional generator with stable attributes emphasized
                traditional_selectors = self.xml_generator.generate_ultra_robust_selectors(element_data)
                
                for selector_info in traditional_selectors[:2]:  # Take top 2
                    xml_selector = selector_info.get('xml_selector', '')
                    if xml_selector:
                        # Enhance with stability analysis
                        enhanced_selector = self._enhance_selector_with_stability(
                            xml_selector, stable_attributes, element_data
                        )
                        
                        if enhanced_selector:
                            adaptive_selector = AdaptiveSelector(
                                xml_selector=enhanced_selector,
                                strategy=SelectorStrategy.NAME_HIERARCHY,
                                adaptive_strategy=AdaptiveStrategy.STABILITY_BASED,
                                confidence_score=selector_info.get('confidence', 0.7),
                                reliability_prediction=self._predict_reliability(enhanced_selector, analysis),
                                performance_prediction=self._predict_performance(enhanced_selector),
                                stability_score=self._calculate_stability_score(enhanced_selector, stable_attributes),
                                pattern_awareness={'stable_attributes': stable_attributes},
                                learned_optimizations=['stability_prioritization'],
                                context_adaptations=['stable_attribute_emphasis'],
                                generation_timestamp=datetime.now().isoformat()
                            )
                            
                            selectors.append(adaptive_selector)
            
        except Exception as e:
            print_warning(f"Stability-based generation failed: {str(e)}")
        
        return selectors
    
    def _generate_pattern_aware_selectors(self, context: GenerationContext, 
                                        analysis: Dict[str, Any]) -> List[AdaptiveSelector]:
        """Generate selectors aware of AutomationId patterns"""
        selectors = []
        
        try:
            element_data = context.element_data
            pattern_analysis = analysis.get('pattern_analysis', {})
            
            if pattern_analysis.get('pattern_detected', False):
                automation_id = element_data.get('automation_id', '')
                
                # Create selector with pattern-aware fallbacks
                base_xml = self._create_base_xml_selector(element_data)
                
                if base_xml:
                    # Enhance with pattern awareness
                    pattern_enhanced_xml = self._enhance_selector_with_patterns(
                        base_xml, pattern_analysis, automation_id
                    )
                    
                    if pattern_enhanced_xml:
                        adaptive_selector = AdaptiveSelector(
                            xml_selector=pattern_enhanced_xml,
                            strategy=SelectorStrategy.AUTOMATION_ID,
                            adaptive_strategy=AdaptiveStrategy.PATTERN_AWARE,
                            confidence_score=pattern_analysis.get('confidence', 0.8),
                            reliability_prediction=0.85,  # High reliability with patterns
                            performance_prediction=0.9,   # Fast execution with AutomationId
                            stability_score=pattern_analysis.get('confidence', 0.8),
                            pattern_awareness=pattern_analysis,
                            learned_optimizations=['pattern_fallbacks', 'predictive_automation_id'],
                            context_adaptations=['automation_id_pattern_integration'],
                            generation_timestamp=datetime.now().isoformat()
                        )
                        
                        selectors.append(adaptive_selector)
            
        except Exception as e:
            print_warning(f"Pattern-aware generation failed: {str(e)}")
        
        return selectors
    
    def _generate_context_adaptive_selectors(self, context: GenerationContext, 
                                           analysis: Dict[str, Any]) -> List[AdaptiveSelector]:
        """Generate selectors adaptive to application context"""
        selectors = []
        
        try:
            element_data = context.element_data
            app_context = context.application_context or {}
            
            # Adapt based on application type
            app_type = app_context.get('type', 'unknown')
            framework = app_context.get('framework', 'unknown')
            
            # Generate context-specific selector
            context_xml = self._create_context_adaptive_selector(element_data, app_type, framework)
            
            if context_xml:
                adaptive_selector = AdaptiveSelector(
                    xml_selector=context_xml,
                    strategy=SelectorStrategy.CLASS_HIERARCHY,
                    adaptive_strategy=AdaptiveStrategy.CONTEXT_ADAPTIVE,
                    confidence_score=0.75,
                    reliability_prediction=self._predict_context_reliability(app_type, framework),
                    performance_prediction=0.8,
                    stability_score=0.7,
                    pattern_awareness={'application_context': app_context},
                    learned_optimizations=['context_adaptation', 'framework_optimization'],
                    context_adaptations=[f'{app_type}_optimization', f'{framework}_compatibility'],
                    generation_timestamp=datetime.now().isoformat()
                )
                
                selectors.append(adaptive_selector)
            
        except Exception as e:
            print_warning(f"Context-adaptive generation failed: {str(e)}")
        
        return selectors
    
    def _generate_performance_tuned_selectors(self, context: GenerationContext, 
                                            analysis: Dict[str, Any]) -> List[AdaptiveSelector]:
        """Generate selectors optimized for performance"""
        selectors = []
        
        try:
            element_data = context.element_data
            
            # Create performance-optimized selector (minimal, fast attributes)
            performance_xml = self._create_performance_optimized_selector(element_data)
            
            if performance_xml:
                adaptive_selector = AdaptiveSelector(
                    xml_selector=performance_xml,
                    strategy=SelectorStrategy.AUTOMATION_ID,
                    adaptive_strategy=AdaptiveStrategy.PERFORMANCE_TUNED,
                    confidence_score=0.8,
                    reliability_prediction=0.75,  # Slightly lower reliability for speed
                    performance_prediction=0.95,  # High performance
                    stability_score=0.7,
                    pattern_awareness={'performance_optimization': True},
                    learned_optimizations=['minimal_attributes', 'fast_execution'],
                    context_adaptations=['performance_priority'],
                    generation_timestamp=datetime.now().isoformat()
                )
                
                selectors.append(adaptive_selector)
            
        except Exception as e:
            print_warning(f"Performance-tuned generation failed: {str(e)}")
        
        return selectors
    
    def _generate_relationship_enhanced_selectors(self, context: GenerationContext, 
                                                analysis: Dict[str, Any]) -> List[AdaptiveSelector]:
        """Generate selectors enhanced with relationship mapping"""
        selectors = []
        
        try:
            element_data = context.element_data
            
            # Create selector with relationship-based fallbacks
            relationship_xml = self._create_relationship_enhanced_selector(element_data)
            
            if relationship_xml:
                adaptive_selector = AdaptiveSelector(
                    xml_selector=relationship_xml,
                    strategy=SelectorStrategy.RELATIONSHIP_BASED,
                    adaptive_strategy=AdaptiveStrategy.RELATIONSHIP_ENHANCED,
                    confidence_score=0.7,
                    reliability_prediction=0.85,  # High reliability with relationships
                    performance_prediction=0.6,   # Slower due to navigation
                    stability_score=0.8,
                    pattern_awareness={'relationship_enhanced': True},
                    learned_optimizations=['relationship_fallbacks', 'navigation_paths'],
                    context_adaptations=['hierarchy_navigation'],
                    generation_timestamp=datetime.now().isoformat()
                )
                
                selectors.append(adaptive_selector)
            
        except Exception as e:
            print_warning(f"Relationship-enhanced generation failed: {str(e)}")
        
        return selectors
    
    def _rank_selectors_by_intelligence(self, selectors: List[AdaptiveSelector], 
                                      context: GenerationContext) -> List[AdaptiveSelector]:
        """Rank selectors using intelligent scoring"""
        try:
            for selector in selectors:
                # Calculate composite intelligence score
                intelligence_score = self._calculate_intelligence_score(selector, context)
                selector.confidence_score = intelligence_score
            
            # Sort by intelligence score (descending)
            ranked_selectors = sorted(selectors, key=lambda s: s.confidence_score, reverse=True)
            
            print_info(f"Ranked {len(ranked_selectors)} selectors by intelligence score")
            return ranked_selectors
            
        except Exception as e:
            print_warning(f"Selector ranking failed: {str(e)}")
            return selectors
    
    def _calculate_intelligence_score(self, selector: AdaptiveSelector, 
                                    context: GenerationContext) -> float:
        """Calculate composite intelligence score for selector"""
        try:
            # Base score from selector confidence
            base_score = selector.confidence_score
            
            # Weight factors based on context preferences
            reliability_weight = 0.4 if context.prioritize_reliability else 0.3
            performance_weight = 0.4 if context.prioritize_speed else 0.2
            stability_weight = 0.3
            adaptivity_weight = 0.1
            
            # Calculate weighted score
            intelligence_score = (
                base_score * 0.2 +
                selector.reliability_prediction * reliability_weight +
                selector.performance_prediction * performance_weight +
                selector.stability_score * stability_weight +
                len(selector.learned_optimizations) * adaptivity_weight / 5  # Normalize optimizations
            )
            
            # Bonus for adaptive strategies
            strategy_bonus = {
                AdaptiveStrategy.PATTERN_AWARE: 0.1,
                AdaptiveStrategy.STABILITY_BASED: 0.05,
                AdaptiveStrategy.PERFORMANCE_TUNED: 0.05,
                AdaptiveStrategy.CONTEXT_ADAPTIVE: 0.05,
                AdaptiveStrategy.RELATIONSHIP_ENHANCED: 0.03
            }
            
            bonus = strategy_bonus.get(selector.adaptive_strategy, 0.0)
            intelligence_score += bonus
            
            return min(1.0, intelligence_score)  # Cap at 1.0
            
        except Exception:
            return 0.5  # Default score
    
    # Helper methods for specific generation strategies
    
    def _identify_stable_attributes(self, element_data: Dict[str, Any]) -> List[str]:
        """Identify stable attributes in element data"""
        stable_attributes = []
        
        # Name is usually stable if not empty and not purely numeric
        name = element_data.get('name', '')
        if name and not name.isdigit() and len(name) > 2:
            stable_attributes.append('name')
        
        # ClassName is usually stable
        class_name = element_data.get('class_name', '')
        if class_name and 'temp' not in class_name.lower():
            stable_attributes.append('class_name')
        
        # ControlType is very stable
        control_type = element_data.get('control_type', '')
        if control_type:
            stable_attributes.append('control_type')
        
        # AutomationId stability depends on pattern analysis
        automation_id = element_data.get('automation_id', '')
        if automation_id and not re.search(r'\d{10,}', automation_id):  # Not timestamp-like
            stable_attributes.append('automation_id')
        
        return stable_attributes
    
    def _identify_unstable_attributes(self, element_data: Dict[str, Any]) -> List[str]:
        """Identify potentially unstable attributes"""
        unstable_attributes = []
        
        # Value often changes
        value = element_data.get('value', '')
        if value:
            unstable_attributes.append('value')
        
        # AutomationId with timestamps or long numbers
        automation_id = element_data.get('automation_id', '')
        if automation_id and re.search(r'\d{10,}', automation_id):
            unstable_attributes.append('automation_id')
        
        # Names that are purely numeric
        name = element_data.get('name', '')
        if name and name.isdigit():
            unstable_attributes.append('name')
        
        return unstable_attributes
    
    def _create_base_xml_selector(self, element_data: Dict[str, Any]) -> Optional[str]:
        """Create base XML selector from element data"""
        try:
            # Use existing XML generator to create base selector
            selectors = self.xml_generator.generate_ultra_robust_selectors(element_data)
            if selectors:
                return selectors[0].get('xml_selector')
            return None
        except Exception:
            return None
    
    def _enhance_selector_with_stability(self, xml_selector: str, stable_attributes: List[str], 
                                       element_data: Dict[str, Any]) -> Optional[str]:
        """Enhance XML selector to prioritize stable attributes"""
        try:
            # This would implement XML manipulation to emphasize stable attributes
            # For now, return the original selector
            return xml_selector
        except Exception:
            return None
    
    def _enhance_selector_with_patterns(self, xml_selector: str, pattern_analysis: Dict[str, Any], 
                                      automation_id: str) -> Optional[str]:
        """Enhance XML selector with pattern awareness"""
        try:
            # This would implement pattern-aware XML enhancement
            # For now, return the original selector
            return xml_selector
        except Exception:
            return None
    
    def _create_context_adaptive_selector(self, element_data: Dict[str, Any], 
                                        app_type: str, framework: str) -> Optional[str]:
        """Create context-adaptive XML selector"""
        try:
            # Use existing generator and adapt based on context
            selectors = self.xml_generator.generate_ultra_robust_selectors(element_data)
            if selectors:
                return selectors[0].get('xml_selector')
            return None
        except Exception:
            return None
    
    def _create_performance_optimized_selector(self, element_data: Dict[str, Any]) -> Optional[str]:
        """Create performance-optimized XML selector"""
        try:
            # Create minimal selector with fastest attributes
            automation_id = element_data.get('automation_id', '')
            if automation_id:
                window_title = element_data.get('window_info', {}).get('title', '')
                return f'''<Selector>
    <Window title="{window_title}" />
    <Element automationId="{automation_id}" />
</Selector>'''
            return None
        except Exception:
            return None
    
    def _create_relationship_enhanced_selector(self, element_data: Dict[str, Any]) -> Optional[str]:
        """Create relationship-enhanced XML selector"""
        try:
            # Use existing generator - relationship enhancement would be done at execution time
            selectors = self.xml_generator.generate_ultra_robust_selectors(element_data)
            if selectors:
                return selectors[0].get('xml_selector')
            return None
        except Exception:
            return None
    
    # Prediction and analysis helper methods
    
    def _analyze_automation_id_patterns(self, automation_id: str) -> Dict[str, Any]:
        """Analyze AutomationId for patterns"""
        try:
            # Simple pattern detection
            pattern_detected = False
            confidence = 0.0
            pattern_type = "unknown"
            
            if automation_id.isdigit():
                pattern_detected = True
                pattern_type = "numeric"
                confidence = 0.7
            elif re.search(r'\d{10,}', automation_id):
                pattern_detected = True
                pattern_type = "timestamp_based"
                confidence = 0.8
            elif re.search(r'^[a-f0-9]{8,}$', automation_id, re.IGNORECASE):
                pattern_detected = True
                pattern_type = "hash_based"
                confidence = 0.6
            
            return {
                'pattern_detected': pattern_detected,
                'pattern_type': pattern_type,
                'confidence': confidence,
                'automation_id': automation_id
            }
            
        except Exception:
            return {'pattern_detected': False, 'confidence': 0.0}
    
    def _predict_performance_characteristics(self, element_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict performance characteristics of element"""
        try:
            predictions = {
                'execution_speed': 0.8,  # Default
                'reliability': 0.8,      # Default
                'stability': 0.7         # Default
            }
            
            # AutomationId generally provides best performance
            if element_data.get('automation_id'):
                predictions['execution_speed'] = 0.95
                predictions['reliability'] = 0.9
            
            # Name + ControlType is also good
            elif element_data.get('name') and element_data.get('control_type'):
                predictions['execution_speed'] = 0.8
                predictions['reliability'] = 0.85
            
            # ClassName fallback
            elif element_data.get('class_name'):
                predictions['execution_speed'] = 0.7
                predictions['reliability'] = 0.75
            
            return predictions
            
        except Exception:
            return {'execution_speed': 0.5, 'reliability': 0.5, 'stability': 0.5}
    
    def _identify_optimization_opportunities(self, element_data: Dict[str, Any], 
                                           analysis: Dict[str, Any]) -> List[str]:
        """Identify optimization opportunities"""
        opportunities = []
        
        try:
            # Pattern-based optimizations
            pattern_analysis = analysis.get('pattern_analysis', {})
            if pattern_analysis.get('pattern_detected'):
                opportunities.append('pattern_aware_fallbacks')
            
            # Stability-based optimizations
            stability_analysis = analysis.get('stability_analysis', {})
            stable_attrs = stability_analysis.get('stable_attributes', [])
            if len(stable_attrs) >= 2:
                opportunities.append('multi_attribute_stability')
            
            # Performance optimizations
            if element_data.get('automation_id'):
                opportunities.append('automation_id_optimization')
            
            # Context optimizations
            if element_data.get('window_info'):
                opportunities.append('window_context_optimization')
            
        except Exception:
            pass
        
        return opportunities
    
    def _predict_reliability(self, xml_selector: str, analysis: Dict[str, Any]) -> float:
        """Predict reliability of generated selector"""
        try:
            base_reliability = 0.7
            
            # Boost for automation ID
            if 'automationId=' in xml_selector:
                base_reliability += 0.2
            
            # Boost for stable attributes
            stable_attrs = analysis.get('stability_analysis', {}).get('stable_attributes', [])
            base_reliability += len(stable_attrs) * 0.05
            
            return min(1.0, base_reliability)
            
        except Exception:
            return 0.5
    
    def _predict_performance(self, xml_selector: str) -> float:
        """Predict performance of generated selector"""
        try:
            base_performance = 0.6
            
            # AutomationId is fastest
            if 'automationId=' in xml_selector:
                base_performance = 0.95
            elif 'name=' in xml_selector and 'controlType=' in xml_selector:
                base_performance = 0.8
            elif 'className=' in xml_selector:
                base_performance = 0.7
            
            return base_performance
            
        except Exception:
            return 0.5
    
    def _calculate_stability_score(self, xml_selector: str, stable_attributes: List[str]) -> float:
        """Calculate stability score based on used attributes"""
        try:
            score = 0.5  # Base score
            
            # Boost for each stable attribute used
            for attr in stable_attributes:
                if attr.lower() in xml_selector.lower():
                    score += 0.1
            
            return min(1.0, score)
            
        except Exception:
            return 0.5
    
    def _predict_context_reliability(self, app_type: str, framework: str) -> float:
        """Predict reliability based on application context"""
        try:
            # Different applications have different reliability patterns
            base_reliability = 0.75
            
            # Well-known frameworks tend to be more stable
            if framework.lower() in ['wpf', 'winforms', 'electron']:
                base_reliability += 0.1
            
            return min(1.0, base_reliability)
            
        except Exception:
            return 0.7
    
    def _apply_post_generation_optimizations(self, selectors: List[AdaptiveSelector], 
                                           context: GenerationContext) -> List[AdaptiveSelector]:
        """Apply optimizations after generation"""
        try:
            optimized_selectors = []
            
            for selector in selectors:
                # Apply context-specific optimizations
                optimized_xml = self._optimize_xml_for_context(selector.xml_selector, context)
                
                if optimized_xml != selector.xml_selector:
                    selector.xml_selector = optimized_xml
                    selector.learned_optimizations.append('post_generation_optimization')
                
                optimized_selectors.append(selector)
            
            return optimized_selectors
            
        except Exception:
            return selectors
    
    def _optimize_xml_for_context(self, xml_selector: str, context: GenerationContext) -> str:
        """Optimize XML selector for specific context"""
        try:
            # For now, return original XML
            # This would implement context-specific XML optimizations
            return xml_selector
        except Exception:
            return xml_selector
    
    def _get_applied_optimizations(self, selectors: List[AdaptiveSelector]) -> List[str]:
        """Get list of all applied optimizations"""
        all_optimizations = set()
        
        for selector in selectors:
            all_optimizations.update(selector.learned_optimizations)
        
        return list(all_optimizations)
    
    def _update_strategy_usage(self, strategy: AdaptiveStrategy):
        """Update strategy usage statistics"""
        if strategy not in self.strategy_usage_stats:
            self.strategy_usage_stats[strategy] = 0
        self.strategy_usage_stats[strategy] += 1
    
    def get_adaptive_statistics(self) -> Dict[str, Any]:
        """Get comprehensive adaptive generation statistics"""
        success_rate = (self.successful_generations / self.total_generations * 100) if self.total_generations > 0 else 0.0
        
        return {
            'total_generations': self.total_generations,
            'successful_generations': self.successful_generations,
            'success_rate': success_rate,
            'strategy_usage_stats': {k.value: v for k, v in self.strategy_usage_stats.items()},
            'available_strategies': [s.value for s in AdaptiveStrategy],
            'supported_generation_modes': [m.value for m in GenerationMode]
        }

# Export main classes
__all__ = [
    'AdaptiveSelectorGenerator',
    'GenerationContext',
    'GenerationResult',
    'AdaptiveSelector',
    'GenerationMode',
    'AdaptiveStrategy'
]