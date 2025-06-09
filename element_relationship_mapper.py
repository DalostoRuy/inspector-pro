"""
Element Relationship Mapper
Version 1.0 - Parent-child navigation and relationship stability scoring

This module provides intelligent mapping of UI element relationships,
enabling navigation through element hierarchies when direct identification fails.
"""

import time
import uiautomation as auto
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from dynamic_selector_cache_schema import ElementFingerprint, SelectorStrategy
from element_fingerprinting import ElementFingerprintEngine, FingerprintMatchResult
from utils import print_info, print_success, print_warning, print_error

class RelationshipType(Enum):
    """Types of element relationships"""
    PARENT = "parent"
    CHILD = "child"
    SIBLING = "sibling"
    ANCESTOR = "ancestor"
    DESCENDANT = "descendant"
    NEXT_SIBLING = "next_sibling"
    PREVIOUS_SIBLING = "previous_sibling"

class NavigationStrategy(Enum):
    """Navigation strategies for relationship traversal"""
    DIRECT_PARENT = "direct_parent"
    ANCESTOR_SEARCH = "ancestor_search"
    SIBLING_ENUMERATION = "sibling_enumeration"
    CHILD_TRAVERSAL = "child_traversal"
    BREADTH_FIRST_SEARCH = "breadth_first_search"
    DEPTH_FIRST_SEARCH = "depth_first_search"
    LANDMARK_NAVIGATION = "landmark_navigation"

@dataclass
class ElementRelationship:
    """Represents a relationship between two UI elements"""
    source_fingerprint: ElementFingerprint
    target_fingerprint: ElementFingerprint
    relationship_type: RelationshipType
    
    # Navigation path
    navigation_steps: List[Dict[str, Any]]
    navigation_strategy: NavigationStrategy
    
    # Stability metrics
    stability_score: float  # 0.0-1.0
    confidence: float  # 0.0-1.0
    success_count: int = 0
    failure_count: int = 0
    
    # Performance metrics
    avg_navigation_time: float = 0.0
    last_verified: Optional[str] = None
    
    # Metadata
    discovered_at: str = ""
    last_updated: str = ""
    verification_count: int = 0

@dataclass
class NavigationResult:
    """Result of relationship-based navigation"""
    success: bool
    target_element: Optional[Any]  # UI Automation element
    navigation_path: List[Dict[str, Any]]
    
    # Performance metrics
    steps_taken: int
    execution_time: float
    strategy_used: NavigationStrategy
    
    # Verification data
    relationship_verified: bool
    target_matches_fingerprint: bool
    confidence_score: float
    
    # Error information
    error_message: Optional[str] = None
    failed_at_step: Optional[int] = None

@dataclass
class RelationshipMap:
    """Complete relationship map for an element"""
    center_fingerprint: ElementFingerprint
    relationships: List[ElementRelationship]
    
    # Map metadata
    created_at: str
    last_updated: str
    verification_count: int = 0
    overall_confidence: float = 0.0
    
    # Navigation statistics
    successful_navigations: int = 0
    failed_navigations: int = 0
    avg_navigation_time: float = 0.0

class ElementRelationshipMapper:
    """
    Advanced element relationship mapper for UI navigation
    
    This class creates and maintains maps of UI element relationships,
    enabling intelligent navigation when direct element identification fails.
    """
    
    def __init__(self):
        """Initialize the relationship mapper"""
        self.fingerprint_engine = ElementFingerprintEngine()
        self.relationship_maps: Dict[str, RelationshipMap] = {}
        self.navigation_cache: Dict[str, NavigationResult] = {}
        
        # Configuration
        self.max_search_depth = 5
        self.max_sibling_search = 20
        self.relationship_confidence_threshold = 0.6
        self.cache_size_limit = 1000
        
        # Performance tracking
        self.total_mappings = 0
        self.successful_mappings = 0
        self.total_navigations = 0
        self.successful_navigations = 0
        
        print_info("Element Relationship Mapper initialized")
    
    def create_relationship_map(self, center_element: Any, 
                              context_data: Optional[Dict[str, Any]] = None) -> RelationshipMap:
        """
        Create comprehensive relationship map for an element
        
        Args:
            center_element: Central UI element to map relationships from
            context_data: Optional context information
            
        Returns:
            RelationshipMap: Complete relationship map
        """
        start_time = time.time()
        self.total_mappings += 1
        
        try:
            print_info("Creating relationship map...")
            
            # Create fingerprint for center element
            center_properties = self._extract_element_properties(center_element)
            center_fingerprint = self._create_fingerprint_from_properties(center_properties)
            
            relationships = []
            
            # Map parent relationships
            parent_relationships = self._map_parent_relationships(center_element, center_fingerprint)
            relationships.extend(parent_relationships)
            
            # Map sibling relationships
            sibling_relationships = self._map_sibling_relationships(center_element, center_fingerprint)
            relationships.extend(sibling_relationships)
            
            # Map child relationships
            child_relationships = self._map_child_relationships(center_element, center_fingerprint)
            relationships.extend(child_relationships)
            
            # Map landmark relationships (stable reference points)
            landmark_relationships = self._map_landmark_relationships(center_element, center_fingerprint)
            relationships.extend(landmark_relationships)
            
            # Calculate overall confidence
            overall_confidence = self._calculate_map_confidence(relationships)
            
            # Create relationship map
            relationship_map = RelationshipMap(
                center_fingerprint=center_fingerprint,
                relationships=relationships,
                created_at=datetime.now().isoformat(),
                last_updated=datetime.now().isoformat(),
                overall_confidence=overall_confidence
            )
            
            # Cache the map
            map_id = self._create_map_id(center_fingerprint)
            self.relationship_maps[map_id] = relationship_map
            
            processing_time = time.time() - start_time
            self.successful_mappings += 1
            
            print_success(f"Relationship map created: {len(relationships)} relationships "
                         f"(confidence: {overall_confidence:.2f}, time: {processing_time:.2f}s)")
            
            return relationship_map
            
        except Exception as e:
            print_error(f"Failed to create relationship map: {str(e)}")
            return RelationshipMap(
                center_fingerprint=ElementFingerprint(),
                relationships=[],
                created_at=datetime.now().isoformat(),
                last_updated=datetime.now().isoformat()
            )
    
    def _map_parent_relationships(self, center_element: Any, 
                                center_fingerprint: ElementFingerprint) -> List[ElementRelationship]:
        """Map parent and ancestor relationships"""
        relationships = []
        
        try:
            current_element = center_element
            depth = 0
            
            while current_element and depth < self.max_search_depth:
                try:
                    parent_element = current_element.GetParentControl()
                    if not parent_element or parent_element == current_element:
                        break
                    
                    # Create fingerprint for parent
                    parent_properties = self._extract_element_properties(parent_element)
                    parent_fingerprint = self._create_fingerprint_from_properties(parent_properties)
                    
                    # Determine relationship type
                    relationship_type = RelationshipType.PARENT if depth == 0 else RelationshipType.ANCESTOR
                    
                    # Create navigation steps
                    navigation_steps = [
                        {
                            "action": "get_parent",
                            "depth": depth + 1,
                            "target_fingerprint": parent_fingerprint.__dict__
                        }
                    ]
                    
                    # Calculate stability score
                    stability_score = self._calculate_parent_stability(parent_element, parent_fingerprint)
                    
                    relationship = ElementRelationship(
                        source_fingerprint=center_fingerprint,
                        target_fingerprint=parent_fingerprint,
                        relationship_type=relationship_type,
                        navigation_steps=navigation_steps,
                        navigation_strategy=NavigationStrategy.DIRECT_PARENT if depth == 0 else NavigationStrategy.ANCESTOR_SEARCH,
                        stability_score=stability_score,
                        confidence=min(0.9 - (depth * 0.1), stability_score),  # Confidence decreases with depth
                        discovered_at=datetime.now().isoformat(),
                        last_updated=datetime.now().isoformat()
                    )
                    
                    relationships.append(relationship)
                    
                    current_element = parent_element
                    depth += 1
                    
                except Exception:
                    break
            
            print_info(f"Mapped {len(relationships)} parent/ancestor relationships")
            
        except Exception as e:
            print_warning(f"Parent relationship mapping failed: {str(e)}")
        
        return relationships
    
    def _map_sibling_relationships(self, center_element: Any, 
                                 center_fingerprint: ElementFingerprint) -> List[ElementRelationship]:
        """Map sibling relationships"""
        relationships = []
        
        try:
            parent_element = center_element.GetParentControl()
            if not parent_element:
                return relationships
            
            siblings = parent_element.GetChildren()
            if not siblings:
                return relationships
            
            # Find center element index
            center_index = -1
            for i, sibling in enumerate(siblings):
                if sibling == center_element:
                    center_index = i
                    break
            
            if center_index == -1:
                return relationships
            
            # Map interesting siblings (not all of them to avoid noise)
            interesting_indices = []
            
            # Always include immediate neighbors
            if center_index > 0:
                interesting_indices.append(center_index - 1)  # Previous sibling
            if center_index < len(siblings) - 1:
                interesting_indices.append(center_index + 1)  # Next sibling
            
            # Include first and last siblings if different
            if 0 not in interesting_indices and len(siblings) > 2:
                interesting_indices.append(0)
            if (len(siblings) - 1) not in interesting_indices and len(siblings) > 2:
                interesting_indices.append(len(siblings) - 1)
            
            # Include siblings with same control type
            center_control_type = getattr(center_element, 'ControlTypeName', '')
            for i, sibling in enumerate(siblings):
                if (i != center_index and 
                    getattr(sibling, 'ControlTypeName', '') == center_control_type and
                    len(interesting_indices) < 8):  # Limit to prevent too many relationships
                    interesting_indices.append(i)
            
            # Create relationships for interesting siblings
            for sibling_index in interesting_indices:
                try:
                    sibling_element = siblings[sibling_index]
                    
                    # Create fingerprint for sibling
                    sibling_properties = self._extract_element_properties(sibling_element)
                    sibling_fingerprint = self._create_fingerprint_from_properties(sibling_properties)
                    
                    # Determine relationship type
                    if sibling_index == center_index - 1:
                        relationship_type = RelationshipType.PREVIOUS_SIBLING
                    elif sibling_index == center_index + 1:
                        relationship_type = RelationshipType.NEXT_SIBLING
                    else:
                        relationship_type = RelationshipType.SIBLING
                    
                    # Create navigation steps
                    navigation_steps = [
                        {
                            "action": "get_parent",
                            "depth": 1
                        },
                        {
                            "action": "get_child_by_index",
                            "index": sibling_index,
                            "total_siblings": len(siblings),
                            "target_fingerprint": sibling_fingerprint.__dict__
                        }
                    ]
                    
                    # Calculate stability score
                    stability_score = self._calculate_sibling_stability(sibling_index, len(siblings), sibling_fingerprint)
                    
                    relationship = ElementRelationship(
                        source_fingerprint=center_fingerprint,
                        target_fingerprint=sibling_fingerprint,
                        relationship_type=relationship_type,
                        navigation_steps=navigation_steps,
                        navigation_strategy=NavigationStrategy.SIBLING_ENUMERATION,
                        stability_score=stability_score,
                        confidence=stability_score,
                        discovered_at=datetime.now().isoformat(),
                        last_updated=datetime.now().isoformat()
                    )
                    
                    relationships.append(relationship)
                    
                except Exception:
                    continue
            
            print_info(f"Mapped {len(relationships)} sibling relationships")
            
        except Exception as e:
            print_warning(f"Sibling relationship mapping failed: {str(e)}")
        
        return relationships
    
    def _map_child_relationships(self, center_element: Any, 
                               center_fingerprint: ElementFingerprint) -> List[ElementRelationship]:
        """Map child relationships"""
        relationships = []
        
        try:
            children = center_element.GetChildren()
            if not children:
                return relationships
            
            # Limit children to avoid too many relationships
            max_children = min(len(children), 10)
            
            for i in range(max_children):
                try:
                    child_element = children[i]
                    
                    # Create fingerprint for child
                    child_properties = self._extract_element_properties(child_element)
                    child_fingerprint = self._create_fingerprint_from_properties(child_properties)
                    
                    # Create navigation steps
                    navigation_steps = [
                        {
                            "action": "get_child_by_index",
                            "index": i,
                            "total_children": len(children),
                            "target_fingerprint": child_fingerprint.__dict__
                        }
                    ]
                    
                    # Calculate stability score
                    stability_score = self._calculate_child_stability(i, len(children), child_fingerprint)
                    
                    relationship = ElementRelationship(
                        source_fingerprint=center_fingerprint,
                        target_fingerprint=child_fingerprint,
                        relationship_type=RelationshipType.CHILD,
                        navigation_steps=navigation_steps,
                        navigation_strategy=NavigationStrategy.CHILD_TRAVERSAL,
                        stability_score=stability_score,
                        confidence=stability_score,
                        discovered_at=datetime.now().isoformat(),
                        last_updated=datetime.now().isoformat()
                    )
                    
                    relationships.append(relationship)
                    
                except Exception:
                    continue
            
            print_info(f"Mapped {len(relationships)} child relationships")
            
        except Exception as e:
            print_warning(f"Child relationship mapping failed: {str(e)}")
        
        return relationships
    
    def _map_landmark_relationships(self, center_element: Any, 
                                  center_fingerprint: ElementFingerprint) -> List[ElementRelationship]:
        """Map relationships to stable landmark elements"""
        relationships = []
        
        try:
            # Find window element (primary landmark)
            window_element = self._find_window_element(center_element)
            if window_element:
                window_properties = self._extract_element_properties(window_element)
                window_fingerprint = self._create_fingerprint_from_properties(window_properties)
                
                # Create navigation path from window to center element
                navigation_path = self._create_navigation_path_from_window(window_element, center_element)
                
                if navigation_path:
                    relationship = ElementRelationship(
                        source_fingerprint=window_fingerprint,  # Source is window
                        target_fingerprint=center_fingerprint,  # Target is center element
                        relationship_type=RelationshipType.DESCENDANT,
                        navigation_steps=navigation_path,
                        navigation_strategy=NavigationStrategy.LANDMARK_NAVIGATION,
                        stability_score=0.9,  # Windows are usually stable
                        confidence=0.8,
                        discovered_at=datetime.now().isoformat(),
                        last_updated=datetime.now().isoformat()
                    )
                    
                    relationships.append(relationship)
            
            # Find other stable landmarks (menus, toolbars, etc.)
            stable_landmarks = self._find_stable_landmarks(center_element)
            for landmark_element in stable_landmarks:
                try:
                    landmark_properties = self._extract_element_properties(landmark_element)
                    landmark_fingerprint = self._create_fingerprint_from_properties(landmark_properties)
                    
                    # Create navigation path from landmark to center element
                    navigation_path = self._create_navigation_path_between_elements(landmark_element, center_element)
                    
                    if navigation_path:
                        relationship = ElementRelationship(
                            source_fingerprint=landmark_fingerprint,
                            target_fingerprint=center_fingerprint,
                            relationship_type=RelationshipType.DESCENDANT,
                            navigation_steps=navigation_path,
                            navigation_strategy=NavigationStrategy.LANDMARK_NAVIGATION,
                            stability_score=0.75,
                            confidence=0.7,
                            discovered_at=datetime.now().isoformat(),
                            last_updated=datetime.now().isoformat()
                        )
                        
                        relationships.append(relationship)
                        
                except Exception:
                    continue
            
            print_info(f"Mapped {len(relationships)} landmark relationships")
            
        except Exception as e:
            print_warning(f"Landmark relationship mapping failed: {str(e)}")
        
        return relationships
    
    def navigate_using_relationship(self, relationship: ElementRelationship, 
                                  source_element: Any, timeout: float = 5.0) -> NavigationResult:
        """
        Navigate to target element using relationship mapping
        
        Args:
            relationship: Relationship to follow for navigation
            source_element: Starting element for navigation
            timeout: Maximum time for navigation
            
        Returns:
            NavigationResult: Result of navigation attempt
        """
        start_time = time.time()
        self.total_navigations += 1
        
        try:
            print_info(f"Navigating using {relationship.relationship_type.value} relationship...")
            
            current_element = source_element
            executed_steps = []
            
            # Execute navigation steps
            for step_index, step in enumerate(relationship.navigation_steps):
                try:
                    action = step.get("action")
                    
                    if action == "get_parent":
                        current_element = current_element.GetParentControl()
                        executed_steps.append({"step": step_index, "action": action, "success": True})
                        
                    elif action == "get_child_by_index":
                        index = step.get("index", 0)
                        children = current_element.GetChildren()
                        if 0 <= index < len(children):
                            current_element = children[index]
                            executed_steps.append({"step": step_index, "action": action, "index": index, "success": True})
                        else:
                            raise IndexError(f"Child index {index} out of range (max: {len(children)})")
                    
                    elif action == "search_by_fingerprint":
                        target_fingerprint_data = step.get("target_fingerprint", {})
                        target_fingerprint = ElementFingerprint(**target_fingerprint_data)
                        found_element = self._search_element_by_fingerprint(current_element, target_fingerprint)
                        if found_element:
                            current_element = found_element
                            executed_steps.append({"step": step_index, "action": action, "success": True})
                        else:
                            raise ValueError("Element not found by fingerprint")
                    
                    else:
                        raise ValueError(f"Unknown navigation action: {action}")
                    
                    # Check if we have a valid element
                    if not current_element:
                        raise ValueError(f"Navigation failed at step {step_index}: element is None")
                    
                    # Check timeout
                    if time.time() - start_time > timeout:
                        raise TimeoutError(f"Navigation timed out at step {step_index}")
                        
                except Exception as e:
                    execution_time = time.time() - start_time
                    executed_steps.append({"step": step_index, "action": step.get("action"), "success": False, "error": str(e)})
                    
                    return NavigationResult(
                        success=False,
                        target_element=None,
                        navigation_path=executed_steps,
                        steps_taken=step_index + 1,
                        execution_time=execution_time,
                        strategy_used=relationship.navigation_strategy,
                        relationship_verified=False,
                        target_matches_fingerprint=False,
                        confidence_score=0.0,
                        error_message=str(e),
                        failed_at_step=step_index
                    )
            
            # Verify that we reached the correct target
            execution_time = time.time() - start_time
            target_matches = self._verify_element_matches_fingerprint(current_element, relationship.target_fingerprint)
            
            if target_matches:
                # Update relationship success metrics
                relationship.success_count += 1
                relationship.avg_navigation_time = self._update_average_time(
                    relationship.avg_navigation_time, execution_time, relationship.success_count
                )
                relationship.last_verified = datetime.now().isoformat()
                relationship.verification_count += 1
                
                self.successful_navigations += 1
                
                result = NavigationResult(
                    success=True,
                    target_element=current_element,
                    navigation_path=executed_steps,
                    steps_taken=len(relationship.navigation_steps),
                    execution_time=execution_time,
                    strategy_used=relationship.navigation_strategy,
                    relationship_verified=True,
                    target_matches_fingerprint=True,
                    confidence_score=relationship.confidence
                )
                
                print_success(f"Navigation successful: {len(executed_steps)} steps, {execution_time:.2f}s")
                return result
            else:
                # Update failure metrics
                relationship.failure_count += 1
                
                return NavigationResult(
                    success=False,
                    target_element=current_element,
                    navigation_path=executed_steps,
                    steps_taken=len(relationship.navigation_steps),
                    execution_time=execution_time,
                    strategy_used=relationship.navigation_strategy,
                    relationship_verified=False,
                    target_matches_fingerprint=False,
                    confidence_score=0.0,
                    error_message="Target element does not match expected fingerprint"
                )
                
        except Exception as e:
            execution_time = time.time() - start_time
            return NavigationResult(
                success=False,
                target_element=None,
                navigation_path=[],
                steps_taken=0,
                execution_time=execution_time,
                strategy_used=relationship.navigation_strategy,
                relationship_verified=False,
                target_matches_fingerprint=False,
                confidence_score=0.0,
                error_message=str(e)
            )
    
    def find_element_using_relationships(self, target_fingerprint: ElementFingerprint, 
                                       available_elements: List[Any], 
                                       timeout: float = 10.0) -> Optional[Any]:
        """
        Find target element using relationship mapping from available source elements
        
        Args:
            target_fingerprint: Fingerprint of element to find
            available_elements: List of available source elements
            timeout: Maximum search time
            
        Returns:
            UI element if found, None otherwise
        """
        start_time = time.time()
        
        print_info(f"Searching for element using relationship mapping...")
        
        # Look for cached relationship maps that can reach the target
        for map_id, relationship_map in self.relationship_maps.items():
            # Check if any relationship in this map leads to our target
            for relationship in relationship_map.relationships:
                if self._fingerprints_match(relationship.target_fingerprint, target_fingerprint):
                    # Try to navigate using this relationship
                    for source_element in available_elements:
                        try:
                            # Check if source element matches the relationship source
                            if self._verify_element_matches_fingerprint(source_element, relationship.source_fingerprint):
                                navigation_result = self.navigate_using_relationship(relationship, source_element, timeout)
                                
                                if navigation_result.success:
                                    print_success("Element found using cached relationship mapping")
                                    return navigation_result.target_element
                                    
                        except Exception:
                            continue
                        
                        # Check timeout
                        if time.time() - start_time > timeout:
                            break
                
                # Check timeout
                if time.time() - start_time > timeout:
                    break
        
        # If no cached relationships work, try creating new relationship maps
        for source_element in available_elements:
            try:
                # Create new relationship map for this source element
                relationship_map = self.create_relationship_map(source_element)
                
                # Check if any relationship leads to our target
                for relationship in relationship_map.relationships:
                    if self._fingerprints_match(relationship.target_fingerprint, target_fingerprint):
                        navigation_result = self.navigate_using_relationship(relationship, source_element, timeout)
                        
                        if navigation_result.success:
                            print_success("Element found using new relationship mapping")
                            return navigation_result.target_element
                
                # Check timeout
                if time.time() - start_time > timeout:
                    break
                    
            except Exception:
                continue
        
        print_warning("Element not found using relationship mapping")
        return None
    
    # Helper methods
    
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
    
    def _calculate_parent_stability(self, parent_element: Any, parent_fingerprint: ElementFingerprint) -> float:
        """Calculate stability score for parent relationship"""
        base_score = 0.7
        
        # Boost score for stable parent types
        stable_types = ['Window', 'Pane', 'Document', 'Tab', 'Group']
        control_type = parent_fingerprint.control_type or ''
        if any(stable_type in control_type for stable_type in stable_types):
            base_score += 0.2
        
        # Boost score if parent has stable identifying attributes
        if parent_fingerprint.name and len(parent_fingerprint.name) > 3:
            base_score += 0.1
        
        return min(1.0, base_score)
    
    def _calculate_sibling_stability(self, sibling_index: int, total_siblings: int, 
                                   sibling_fingerprint: ElementFingerprint) -> float:
        """Calculate stability score for sibling relationship"""
        base_score = 0.5
        
        # Index-based stability (edges are more stable)
        if sibling_index == 0 or sibling_index == total_siblings - 1:
            base_score += 0.2  # First or last sibling
        elif sibling_index == 1 or sibling_index == total_siblings - 2:
            base_score += 0.1  # Second or second-to-last
        
        # Boost for stable identifying attributes
        if sibling_fingerprint.name and len(sibling_fingerprint.name) > 3:
            base_score += 0.15
        if sibling_fingerprint.class_name:
            base_score += 0.1
        
        return min(1.0, base_score)
    
    def _calculate_child_stability(self, child_index: int, total_children: int, 
                                 child_fingerprint: ElementFingerprint) -> float:
        """Calculate stability score for child relationship"""
        base_score = 0.4
        
        # First child is usually more stable
        if child_index == 0:
            base_score += 0.3
        elif child_index < 3:  # Early children
            base_score += 0.2
        
        # Boost for stable attributes
        if child_fingerprint.name:
            base_score += 0.2
        if child_fingerprint.class_name:
            base_score += 0.1
        
        return min(1.0, base_score)
    
    def _calculate_map_confidence(self, relationships: List[ElementRelationship]) -> float:
        """Calculate overall confidence for relationship map"""
        if not relationships:
            return 0.0
        
        # Weighted average of relationship confidences
        total_weight = 0.0
        weighted_sum = 0.0
        
        for relationship in relationships:
            # Weight based on relationship type importance
            weight = self._get_relationship_weight(relationship.relationship_type)
            weighted_sum += relationship.confidence * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _get_relationship_weight(self, relationship_type: RelationshipType) -> float:
        """Get importance weight for relationship type"""
        weights = {
            RelationshipType.PARENT: 0.9,
            RelationshipType.ANCESTOR: 0.7,
            RelationshipType.NEXT_SIBLING: 0.8,
            RelationshipType.PREVIOUS_SIBLING: 0.8,
            RelationshipType.SIBLING: 0.6,
            RelationshipType.CHILD: 0.5,
            RelationshipType.DESCENDANT: 0.4
        }
        return weights.get(relationship_type, 0.5)
    
    def _create_map_id(self, fingerprint: ElementFingerprint) -> str:
        """Create unique ID for relationship map"""
        import hashlib
        
        # Create hash from stable attributes
        id_components = [
            fingerprint.name or '',
            fingerprint.class_name or '',
            fingerprint.control_type or '',
            str(fingerprint.sibling_index or 0)
        ]
        
        id_string = '|'.join(id_components)
        return hashlib.md5(id_string.encode('utf-8')).hexdigest()[:16]
    
    def _find_window_element(self, element: Any) -> Optional[Any]:
        """Find the window element containing the given element"""
        try:
            current = element
            while current:
                control_type = getattr(current, 'ControlTypeName', '')
                if 'Window' in control_type:
                    return current
                current = current.GetParentControl()
            return None
        except:
            return None
    
    def _find_stable_landmarks(self, element: Any) -> List[Any]:
        """Find stable landmark elements in the same window"""
        landmarks = []
        
        try:
            window_element = self._find_window_element(element)
            if not window_element:
                return landmarks
            
            # Look for common stable elements
            stable_patterns = [
                ('Menu', 'MenuBar'),
                ('ToolBar', 'Tool'),
                ('StatusBar', 'Status'),
                ('Tab', 'TabItem')
            ]
            
            all_descendants = self._get_all_descendants(window_element, max_depth=3)
            
            for descendant in all_descendants:
                try:
                    control_type = getattr(descendant, 'ControlTypeName', '')
                    name = getattr(descendant, 'Name', '')
                    
                    # Check if it matches stable patterns
                    for pattern1, pattern2 in stable_patterns:
                        if (pattern1 in control_type or pattern2 in control_type or 
                            pattern1.lower() in name.lower() or pattern2.lower() in name.lower()):
                            if descendant not in landmarks and descendant != element:
                                landmarks.append(descendant)
                                break
                
                except:
                    continue
            
            return landmarks[:5]  # Limit to top 5 landmarks
            
        except:
            return landmarks
    
    def _get_all_descendants(self, element: Any, max_depth: int = 3) -> List[Any]:
        """Get all descendant elements up to max_depth"""
        descendants = []
        
        def collect_recursive(elem, depth):
            if depth > max_depth:
                return
            
            try:
                descendants.append(elem)
                children = elem.GetChildren()
                for child in children:
                    collect_recursive(child, depth + 1)
            except:
                pass
        
        collect_recursive(element, 0)
        return descendants
    
    def _create_navigation_path_from_window(self, window_element: Any, target_element: Any) -> List[Dict[str, Any]]:
        """Create navigation path from window to target element"""
        try:
            # This is a simplified implementation
            # In practice, you'd implement a more sophisticated pathfinding algorithm
            
            path = []
            
            # For now, create a basic breadth-first search path
            # This should be enhanced with more intelligent pathfinding
            
            return path
            
        except:
            return []
    
    def _create_navigation_path_between_elements(self, source_element: Any, target_element: Any) -> List[Dict[str, Any]]:
        """Create navigation path between two elements"""
        try:
            # Simplified implementation
            # Should implement intelligent pathfinding between arbitrary elements
            
            return []
            
        except:
            return []
    
    def _search_element_by_fingerprint(self, parent_element: Any, target_fingerprint: ElementFingerprint) -> Optional[Any]:
        """Search for element matching fingerprint within parent"""
        try:
            children = parent_element.GetChildren()
            
            for child in children:
                child_properties = self._extract_element_properties(child)
                child_fingerprint = self._create_fingerprint_from_properties(child_properties)
                
                if self._fingerprints_match(child_fingerprint, target_fingerprint):
                    return child
            
            return None
            
        except:
            return None
    
    def _verify_element_matches_fingerprint(self, element: Any, fingerprint: ElementFingerprint) -> bool:
        """Verify that element matches the given fingerprint"""
        try:
            element_properties = self._extract_element_properties(element)
            element_fingerprint = self._create_fingerprint_from_properties(element_properties)
            
            return self._fingerprints_match(element_fingerprint, fingerprint)
            
        except:
            return False
    
    def _fingerprints_match(self, fp1: ElementFingerprint, fp2: ElementFingerprint) -> bool:
        """Check if two fingerprints match sufficiently"""
        match_result = self.fingerprint_engine.calculate_fingerprint_similarity(fp1, fp2)
        return match_result.confidence >= self.relationship_confidence_threshold
    
    def _update_average_time(self, current_avg: float, new_time: float, count: int) -> float:
        """Update running average of execution time"""
        if count <= 1:
            return new_time
        return ((current_avg * (count - 1)) + new_time) / count
    
    def get_relationship_statistics(self) -> Dict[str, Any]:
        """Get comprehensive relationship mapping statistics"""
        total_relationships = sum(len(rmap.relationships) for rmap in self.relationship_maps.values())
        
        # Calculate success rates
        mapping_success_rate = (self.successful_mappings / self.total_mappings * 100) if self.total_mappings > 0 else 0.0
        navigation_success_rate = (self.successful_navigations / self.total_navigations * 100) if self.total_navigations > 0 else 0.0
        
        # Relationship type distribution
        relationship_types = {}
        for rmap in self.relationship_maps.values():
            for relationship in rmap.relationships:
                rel_type = relationship.relationship_type.value
                relationship_types[rel_type] = relationship_types.get(rel_type, 0) + 1
        
        return {
            'total_mappings': self.total_mappings,
            'successful_mappings': self.successful_mappings,
            'mapping_success_rate': mapping_success_rate,
            'total_navigations': self.total_navigations,
            'successful_navigations': self.successful_navigations,
            'navigation_success_rate': navigation_success_rate,
            'cached_relationship_maps': len(self.relationship_maps),
            'total_relationships': total_relationships,
            'relationship_type_distribution': relationship_types,
            'cache_size': len(self.navigation_cache)
        }

# Export main classes
__all__ = [
    'ElementRelationshipMapper',
    'RelationshipMap',
    'ElementRelationship',
    'NavigationResult',
    'RelationshipType',
    'NavigationStrategy'
]