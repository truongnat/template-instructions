#!/bin/bash
# Test execution script for SDLC Kit
# Supports running different test types with coverage reporting

set -e  # Exit on error

# Default values
TEST_TYPE="all"
COVERAGE=false
VERBOSE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            TEST_TYPE="$2"
            shift 2
            ;;
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            echo "Usage: ./scripts/run-tests.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -t, --type TYPE      Test type to run: all, unit, integration, e2e, property"
            echo "  -c, --coverage       Generate coverage report"
            echo "  -v, --verbose        Verbose output"
            echo "  -h, --help           Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./scripts/run-tests.sh                    # Run all tests"
            echo "  ./scripts/run-tests.sh -t unit            # Run only unit tests"
            echo "  ./scripts/run-tests.sh -t unit -c         # Run unit tests with coverage"
            echo "  ./scripts/run-tests.sh -c -v              # Run all tests with coverage and verbose output"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

echo "=========================================="
echo "Running SDLC Kit Tests"
echo "=========================================="
echo "Test type: $TEST_TYPE"
echo "Coverage: $COVERAGE"
echo "Verbose: $VERBOSE"
echo ""

# Build pytest command
PYTEST_CMD="pytest"

# Add test directory based on type
case $TEST_TYPE in
    all)
        PYTEST_CMD="$PYTEST_CMD tests/"
        ;;
    unit)
        PYTEST_CMD="$PYTEST_CMD tests/unit/"
        ;;
    integration)
        PYTEST_CMD="$PYTEST_CMD tests/integration/"
        ;;
    e2e)
        PYTEST_CMD="$PYTEST_CMD tests/e2e/"
        ;;
    property)
        PYTEST_CMD="$PYTEST_CMD tests/property/"
        ;;
    *)
        echo "Error: Invalid test type '$TEST_TYPE'"
        echo "Valid types: all, unit, integration, e2e, property"
        exit 1
        ;;
esac

# Add coverage options
if [ "$COVERAGE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=agentic_sdlc --cov-report=term --cov-report=html --cov-report=xml"
fi

# Add verbose option
if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -v"
fi

# Run tests
echo "Executing: $PYTEST_CMD"
echo ""

if $PYTEST_CMD; then
    echo ""
    echo "=========================================="
    echo "✓ All tests passed!"
    echo "=========================================="
    
    if [ "$COVERAGE" = true ]; then
        echo ""
        echo "Coverage report generated:"
        echo "  - Terminal: (shown above)"
        echo "  - HTML: htmlcov/index.html"
        echo "  - XML: coverage.xml"
    fi
    
    exit 0
else
    echo ""
    echo "=========================================="
    echo "✗ Some tests failed"
    echo "=========================================="
    exit 1
fi
