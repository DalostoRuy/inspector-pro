# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Inspector Pro v3.0 is a Windows desktop UI automation tool for RPA development. It captures detailed UI element information using UIA3 (UI Automation) technology and generates **ULTRA-ROBUST XML selectors** for automation scripts that work even when AutomationId changes between executions.

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run the main application (Windows only)
python main.py

# Run tests for XML executor
python test_xml_executor.py
```

The application requires Windows and uses Win32 APIs extensively. It will exit with an error on other platforms.

## Core Architecture

The codebase follows a modular architecture with clear separation of concerns:

### Main Application Flow
- `main.py` → `ElementInspector` → `UltraRobustSelectorGenerator` → `XMLSelectorValidator` → `XMLSelectorGenerator` + `XMLSelectorExecutor`

### Key Components

**UIInspectorApp (main.py)**
- CLI interface and menu system (v3.0 with ultra-robust features)
- Coordinates user workflows (capture, list, test with action execution)
- Integrates all components through ElementInspector

**ElementInspector (element_inspector.py)**
- Core capture engine using Win32 APIs and uiautomation
- **NEW v3.0**: Automatic ultra-robust selector generation during capture
- Supports two capture modes: single element and anchor+relative click
- Integrates automatic selector validation during capture
- Uses CTRL+Click and CTRL+SHIFT+Click for different capture modes

**Ultra-Robust XML Selector System (NEW v3.0)**
- `UltraRobustSelectorGenerator`: **Main innovation** - analyzes attribute stability and generates multiple fallback strategies
- `XMLSelectorValidator`: Validates and ranks selector strategies by reliability
- `XMLSelectorExecutor`: Executes XML selectors with multiple click methods (InvokePattern, direct, coordinates)
- `XMLSelectorGenerator`: Legacy generator (kept for compatibility)

**NEW Ultra-Robust Features:**
- **Attribute Stability Analysis**: Detects if AutomationId is dynamic vs stable
- **Multiple Strategy Generation**: Name+Hierarchy, ClassName+Index, Visual Anchors, Coordinate fallbacks
- **Automatic Validation**: Tests each strategy immediately during capture
- **Reliability Scoring**: Rates selectors 0-100% with detailed classification
- **Fallback Cascading**: Multiple strategies embedded in generated XML

### Data Flow

1. **Capture**: User triggers capture → ElementInspector extracts UI properties
2. **Generation**: XMLSelectorValidator generates multiple XML selectors
3. **Validation**: Each selector is tested against the live UI element
4. **Storage**: Only validated selectors are saved to JSON files
5. **Testing**: Users can test custom selectors through CLI interface

### XML Selector Format

Selectors use a UiPath-inspired XML format:
```xml
<Selector><Window title="AppName" /><Element automationId="buttonId" controlType="ButtonControl" /></Selector>
```

Supports hierarchical selection with Window→Element chains and multiple fallback strategies.

## Development Guidelines

### File Organization
- `utils.py` contains shared utilities (colored output, file operations, process info)
- All classes use dependency injection (ElementInspector receives validator/generator)
- Captured elements are stored in `captured_elements/` with timestamped folders

### Testing Approach
- Use `test_xml_executor.py` for basic XML functionality testing
- The app includes built-in testing via menu option 4 "Testar Seletor XML"
- Validation includes reliability testing (multiple executions) and performance metrics

### Error Handling
- All capture operations use retry logic (max 3 attempts)
- XML parsing includes comprehensive error reporting
- Validation failures fall back to traditional selector generation

### Platform Requirements
- Windows-only (uses win32gui, win32api, uiautomation)
- Depends on Windows UI Automation framework
- Requires elevated permissions for some applications

## Key Technical Details

### Capture Mechanisms
- Uses `auto.ControlFromPoint()` and `auto.GetCursorControl()` for element detection
- Implements 300ms debounce to prevent double-captures
- Extracts comprehensive element properties (automation IDs, patterns, hierarchy)

### Selector Reliability
- Selectors are scored 0-100 based on reliability (40%), speed (20%), and robustness (40%)
- Classification: EXCELENTE (≥90%), BOA (≥75%), MODERADA (≥50%), BAIXA/PÉSSIMA (<50%)
- AutomationId-based selectors receive highest robustness scores

### Data Persistence
- Elements saved as JSON with complex object serialization
- Includes both validated (`xml_selectors`) and legacy (`xml_selectors_legacy`) selectors
- Validation reports include timing and success metrics