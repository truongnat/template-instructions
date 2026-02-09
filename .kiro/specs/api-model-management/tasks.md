# Implementation Plan: API-Based Model Selection & Rate Limit Management

## Overview

This implementation plan breaks down the API-Based Model Selection & Rate Limit Management system into discrete, incremental coding tasks. The plan follows a bottom-up approach, building foundational components first, then integrating them into higher-level systems.

The implementation will be done in Python 3.10+ using async/await patterns, with SQLite for persistence, and integration with the existing ModelOptimizer in `agentic_sdlc/orchestration/engine/`.

## Tasks

- [x] 1. Set up project structure and core data models
  - Create directory structure: `agentic_sdlc/orchestration/api_model_management/`
  - Create `__init__.py`, `models.py`, `exceptions.py`
  - Implement all data models from design (ModelMetadata, ModelRequest, ModelResponse, etc.)
  - Implement custom exceptions (APIModelError, RateLimitError, FailoverError, etc.)
  - _Requirements: 1.1, 2.1, 7.1, 8.1, 9.1, 10.1, 11.1_

- [x] 1.1 Write property tests for data models
  - **Property 1**: Model metadata persistence round-trip
  - **Validates: Requirements 1.1, 1.5**

- [x] 2. Implement Model Registry
  - [x] 2.1 Create `registry.py` with ModelRegistry class
    - Implement `__init__`, `load_config`, `get_model`, `get_models_by_provider`
    - Implement `get_models_by_capability`, `get_models_by_cost_range`
    - Implement `update_model`, `add_model`
    - Add JSON schema validation for model configurations
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_
  
  - [x] 2.2 Write property tests for Model Registry
    - **Property 2**: Invalid model configuration rejection
    - **Property 3**: Model query filtering
    - **Validates: Requirements 1.3, 1.4**
  
  - [x] 2.3 Write unit tests for Model Registry
    - Test configuration loading from JSON file
    - Test invalid configuration handling
    - Test query methods with edge cases
    - _Requirements: 1.2, 1.3_

- [x] 3. Implement API Key Manager
  - [x] 3.1 Create `api_key_manager.py` with APIKeyManager class
    - Implement `__init__`, `load_keys`, `get_key`, `validate_keys`
    - Implement `add_key` and round-robin rotation logic
    - Support environment variable naming convention
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
  
  - [x] 3.2 Write property tests for API Key Manager
    - **Property 23**: API key loading from environment
    - **Property 24**: Missing key handling
    - **Property 25**: Multiple key support
    - **Property 26**: Round-robin key rotation
    - **Validates: Requirements 6.1, 6.3, 6.4, 6.5**
  
  - [x] 3.3 Write unit tests for API Key Manager
    - Test startup validation
    - Test missing key warnings
    - Test environment variable loading
    - _Requirements: 6.2_

- [x] 4. Implement database schema and utilities
  - [x] 4.1 Create database initialization script
    - Create SQL schema for cost_records, performance_records, cached_responses
    - Create SQL schema for health_checks, rate_limit_events, failover_events
    - Implement database migration utilities
    - _Requirements: 9.3, 10.4, 11.5_
  
  - [x] 4.2 Write unit tests for database initialization
    - Test schema creation
    - Test table existence and structure
    - _Requirements: 10.4, 11.5_

- [x] 5. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Implement Cache Manager
  - [x] 6.1 Create `cache_manager.py` with CacheManager class
    - Implement `__init__`, `get`, `set`, `generate_cache_key`
    - Implement `evict_expired`, `evict_lru`
    - Use SQLite for cache storage with aiosqlite
    - Implement TTL and LRU eviction logic
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_
  
  - [x] 6.2 Write property tests for Cache Manager
    - **Property 37**: Cache hit serves without API call
    - **Property 38**: Response caching with TTL
    - **Property 39**: Cache key uniqueness
    - **Property 40**: LRU cache eviction
    - **Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5**
  
  - [x] 6.3 Write unit tests for Cache Manager
    - Test cache hit/miss scenarios
    - Test TTL expiration
    - Test LRU eviction edge cases
    - _Requirements: 9.3, 9.5_

- [x] 7. Implement Cost Tracker
  - [x] 7.1 Create `cost_tracker.py` with CostTracker class
    - Implement `__init__`, `record_cost`, `get_daily_cost`
    - Implement `get_cost_by_model`, `check_budget`
    - Use SQLite with aiosqlite for persistence
    - Implement cost aggregation queries
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_
  
  - [x] 7.2 Write property tests for Cost Tracker
    - **Property 41**: Cost calculation accuracy
    - **Property 42**: Cost aggregation correctness
    - **Property 43**: Budget threshold alerting
    - **Property 44**: Cost data persistence
    - **Property 45**: Cost query filtering
    - **Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5**
  
  - [x] 7.3 Write unit tests for Cost Tracker
    - Test budget threshold detection
    - Test cost aggregation edge cases
    - Test query filtering
    - _Requirements: 10.3, 10.5_

- [x] 8. Implement Performance Monitor
  - [x] 8.1 Create `performance_monitor.py` with PerformanceMonitor class
    - Implement `__init__`, `record_performance`, `get_model_performance`
    - Implement `detect_degradation`
    - Use SQLite with aiosqlite for persistence
    - Implement rolling average calculations
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_
  
  - [x] 8.2 Write property tests for Performance Monitor
    - **Property 46**: Performance metric tracking
    - **Property 47**: Performance metric updates
    - **Property 48**: Rolling average calculation
    - **Property 49**: Performance degradation alerting
    - **Property 50**: Performance data persistence
    - **Validates: Requirements 11.1, 11.2, 11.3, 11.4, 11.5**
  
  - [x] 8.3 Write unit tests for Performance Monitor
    - Test rolling average edge cases
    - Test degradation detection thresholds
    - Test metric persistence
    - _Requirements: 11.3, 11.4, 11.5_

- [x] 9. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Implement Provider Adapters
  - [x] 10.1 Create base adapter interface
    - Create `adapters/base.py` with ProviderAdapter abstract class
    - Define abstract methods: `send_request`, `parse_response`, `extract_token_usage`, `is_rate_limit_error`
    - _Requirements: 16.1, 16.2, 16.3, 16.4_
  
  - [x] 10.2 Implement OpenAI Adapter
    - Create `adapters/openai_adapter.py` with OpenAIAdapter class
    - Implement request formatting for OpenAI API
    - Implement response parsing and normalization
    - Implement token usage extraction
    - _Requirements: 7.1, 7.4, 7.5, 16.2, 16.3, 16.4_
  
  - [x] 10.3 Implement Anthropic Adapter
    - Create `adapters/anthropic_adapter.py` with AnthropicAdapter class
    - Implement request formatting for Anthropic API
    - Implement response parsing and normalization
    - Implement token usage extraction
    - _Requirements: 7.1, 7.4, 7.5, 16.2, 16.3, 16.4_
  
  - [x] 10.4 Implement Google Adapter
    - Create `adapters/google_adapter.py` with GoogleAdapter class
    - Implement request formatting for Google AI API
    - Implement response parsing and normalization
    - Implement token usage extraction
    - _Requirements: 7.1, 7.4, 7.5, 16.2, 16.3, 16.4_
  
  - [x] 10.5 Implement Ollama Adapter
    - Create `adapters/ollama_adapter.py` with OllamaAdapter class
    - Implement request formatting for Ollama API
    - Implement response parsing and normalization
    - Implement token usage extraction (estimated for local models)
    - _Requirements: 7.1, 7.4, 7.5, 16.2, 16.3, 16.4_
  
  - [x] 10.6 Write property tests for Provider Adapters
    - **Property 27**: Request authentication and formatting
    - **Property 30**: Provider adapter request/response normalization
    - **Property 31**: Token usage and cost extraction
    - **Validates: Requirements 7.1, 7.5, 16.2, 16.3, 16.4**
  
  - [x] 10.7 Write unit tests for Provider Adapters
    - Test each adapter with sample responses
    - Test error handling for each provider
    - Test rate limit error detection
    - _Requirements: 16.1, 16.2, 16.3_

- [x] 11. Implement API Client Manager
  - [x] 11.1 Create `api_client.py` with APIClientManager class
    - Implement `__init__`, `send_request`, `send_request_with_retry`
    - Implement connection pooling with httpx
    - Implement retry logic with exponential backoff
    - Implement error categorization (transient vs permanent)
    - Route requests to appropriate provider adapters
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 15.2_
  
  - [x] 11.2 Write property tests for API Client Manager
    - **Property 28**: Transient error retry with backoff
    - **Property 29**: Final failure error details
    - **Property 62**: Error categorization
    - **Validates: Requirements 7.2, 7.3, 15.2**
  
  - [x] 11.3 Write unit tests for API Client Manager
    - Test retry logic with mock failures
    - Test error categorization
    - Test adapter routing
    - _Requirements: 7.2, 7.3, 15.2_

- [x] 12. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [-] 13. Implement Health Checker
  - [x] 13.1 Create `health_checker.py` with HealthChecker class
    - Implement `__init__`, `start`, `stop`, `check_model_health`
    - Implement `get_model_status`, `is_model_available`
    - Implement periodic health checking with asyncio
    - Implement consecutive failure tracking
    - Implement exponential backoff for failed checks
    - Persist health check history to SQLite
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [x] 13.2 Write property tests for Health Checker
    - **Property 9**: Periodic health checks
    - **Property 10**: Health check data recording
    - **Property 11**: Consecutive failure marking
    - **Property 12**: Recovery from unavailability
    - **Property 13**: Availability status visibility
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**
  
  - [x] 13.3 Write unit tests for Health Checker
    - Test periodic execution timing
    - Test consecutive failure threshold
    - Test recovery behavior
    - _Requirements: 3.1, 3.3, 3.4_

- [x] 14. Implement Rate Limiter
  - [x] 14.1 Create `rate_limiter.py` with RateLimiter class
    - Implement `__init__`, `check_rate_limit`, `record_request`
    - Implement `is_rate_limited`, `get_time_until_reset`
    - Implement sliding window algorithm for request counting
    - Implement 90% threshold detection
    - Persist rate limit events to SQLite
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  
  - [x] 14.2 Write property tests for Rate Limiter
    - **Property 14**: Rate limit tracking with threshold detection
    - **Property 15**: Rate limit event recording
    - **Property 16**: Rate limit window reset
    - **Property 17**: Rate-limited model request blocking
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**
  
  - [x] 14.3 Write unit tests for Rate Limiter
    - Test sliding window algorithm
    - Test threshold detection edge cases
    - Test window reset timing
    - _Requirements: 4.1, 4.3, 4.4_

- [x] 15. Implement Response Evaluator
  - [x] 15.1 Create `evaluator.py` with ResponseEvaluator class
    - Implement `__init__`, `evaluate_response`, `should_switch_model`
    - Implement `calculate_completeness`, `calculate_relevance`, `calculate_coherence`
    - Implement quality score calculation (weighted average)
    - Implement low-quality detection and model switch recommendation
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_
  
  - [x] 15.2 Write property tests for Response Evaluator
    - **Property 32**: Quality assessment calculation
    - **Property 33**: Low-quality response flagging
    - **Property 34**: Consistent low-quality model switch
    - **Property 35**: Quality score persistence
    - **Property 36**: Quality evaluation skip when disabled
    - **Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5**
  
  - [x] 15.3 Write unit tests for Response Evaluator
    - Test quality metric calculations
    - Test threshold detection
    - Test model switch recommendation logic
    - _Requirements: 8.1, 8.2, 8.3_

- [x] 16. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 17. Implement Model Selector
  - [x] 17.1 Create `selector.py` with ModelSelector class
    - Implement `__init__`, `select_model`, `calculate_suitability_score`, `rank_models`
    - Implement selection algorithm (filter by capabilities, availability, rate limits)
    - Implement suitability scoring (capability: 30%, cost: 25%, performance: 25%, availability: 20%)
    - Implement priority-based adjustments (CRITICAL/HIGH prioritize quality)
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [x] 17.2 Write property tests for Model Selector
    - **Property 4**: Model selection considers all factors
    - **Property 5**: Cost-efficiency prioritization
    - **Property 6**: Fallback selection on unavailability
    - **Property 7**: Performance data influences ranking
    - **Property 8**: High-priority tasks prioritize quality
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**
  
  - [x] 17.3 Write unit tests for Model Selector
    - Test suitability score calculation
    - Test ranking algorithm
    - Test priority adjustments
    - _Requirements: 2.1, 2.2, 2.5_

- [-] 18. Implement Failover Manager
  - [x] 18.1 Create `failover_manager.py` with FailoverManager class
    - Implement `__init__`, `execute_with_failover`, `select_alternative`
    - Implement `record_failover`
    - Implement exponential backoff retry logic
    - Implement excessive failover detection and alerting
    - Persist failover events to SQLite
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [x] 18.2 Write property tests for Failover Manager
    - **Property 18**: Automatic failover on unavailability
    - **Property 19**: Failover event logging completeness
    - **Property 20**: Exponential backoff retry
    - **Property 21**: Original model retry after recovery
    - **Property 22**: Excessive failover alerting
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5**
  
  - [x] 18.3 Write unit tests for Failover Manager
    - Test failover triggering conditions
    - Test alternative selection
    - Test excessive failover detection
    - _Requirements: 5.1, 5.2, 5.5_

- [x] 19. Implement configuration management
  - [x] 19.1 Create configuration schema and validation
    - Create `config/schema.json` with JSON schema for configuration
    - Implement configuration loading and validation
    - Implement environment-specific configuration support
    - Implement hot reload functionality
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_
  
  - [x] 19.2 Write property tests for configuration management
    - **Property 51**: Invalid configuration error handling
    - **Property 52**: Configuration hot reload
    - **Property 53**: Configuration schema validation
    - **Validates: Requirements 12.2, 12.4, 12.5**
  
  - [x] 19.3 Write unit tests for configuration management
    - Test configuration loading from file
    - Test environment-specific configs
    - Test schema validation errors
    - _Requirements: 12.1, 12.3, 12.5_

- [x] 20. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 21. Implement error handling and logging
  - [x] 21.1 Create comprehensive error handling
    - Implement error categorization logic
    - Implement detailed error logging
    - Implement event logging (rate limits, failover, alerts)
    - Configure log levels
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5_
  
  - [x] 21.2 Write property tests for error handling
    - **Property 61**: Error logging completeness
    - **Property 63**: Permanent error detail reporting
    - **Property 64**: Event logging coverage
    - **Validates: Requirements 15.1, 15.3, 15.4**
  
  - [x] 21.3 Write unit tests for error handling
    - Test error categorization
    - Test log level configuration
    - Test event logging
    - _Requirements: 15.2, 15.4, 15.5_

- [-] 22. Implement concurrency and async handling
  - [x] 22.1 Add concurrency controls
    - Implement concurrent request processing with asyncio
    - Implement concurrency limits per provider
    - Implement non-blocking request handling
    - _Requirements: 14.2, 14.4, 14.5_
  
  - [x] 22.2 Write property tests for concurrency
    - **Property 58**: Concurrent request processing
    - **Property 59**: Non-blocking request handling
    - **Property 60**: Concurrency limit enforcement
    - **Validates: Requirements 14.2, 14.4, 14.5**
  
  - [x] 22.3 Write unit tests for concurrency
    - Test concurrent request handling
    - Test concurrency limit enforcement
    - Test non-blocking behavior
    - _Requirements: 14.2, 14.5_

- [x] 23. Implement metrics export
  - [x] 23.1 Create metrics export interface
    - Implement metrics query interface
    - Implement JSON formatting for metrics
    - Implement metric filtering (time range, model, provider, agent type)
    - Implement derived metrics calculation
    - Implement real-time metric updates
    - _Requirements: 17.1, 17.2, 17.3, 17.4, 17.5_
  
  - [x] 23.2 Write property tests for metrics export
    - **Property 65**: Metrics export format
    - **Property 66**: Metrics completeness
    - **Property 67**: Metrics filtering
    - **Property 68**: Derived metrics calculation
    - **Property 69**: Real-time metrics updates
    - **Validates: Requirements 17.1, 17.2, 17.3, 17.4, 17.5**
  
  - [x] 23.3 Write unit tests for metrics export
    - Test JSON formatting
    - Test metric filtering
    - Test derived metric calculations
    - _Requirements: 17.1, 17.3, 17.4_

- [x] 24. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 25. Implement graceful degradation
  - [x] 25.1 Add graceful degradation handling
    - Implement provider failure isolation
    - Implement request queuing on total unavailability
    - Implement cache failure fallback
    - Implement monitoring failure fallback
    - Implement degraded mode logging
    - _Requirements: 18.1, 18.2, 18.3, 18.4, 18.5_
  
  - [x] 25.2 Write property tests for graceful degradation
    - **Property 70**: Provider failure isolation
    - **Property 71**: Request queuing on total unavailability
    - **Property 72**: Cache failure fallback
    - **Property 73**: Monitoring failure fallback
    - **Property 74**: Degraded mode logging
    - **Validates: Requirements 18.1, 18.2, 18.3, 18.4, 18.5**
  
  - [x] 25.3 Write unit tests for graceful degradation
    - Test provider failure scenarios
    - Test cache failure handling
    - Test monitoring failure handling
    - _Requirements: 18.1, 18.3, 18.4_

- [-] 26. Integrate with ModelOptimizer
  - [x] 26.1 Create ModelOptimizer integration layer
    - Extend ModelAssignment with API details
    - Implement performance feedback to ModelOptimizer
    - Implement failover coordination with ModelOptimizer
    - Implement model selection coordination
    - Ensure backward compatibility with existing interfaces
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_
  
  - [x] 26.2 Write property tests for ModelOptimizer integration
    - **Property 54**: ModelOptimizer integration
    - **Property 55**: Failover event reporting
    - **Property 56**: Performance data sharing
    - **Property 57**: ModelOptimizer interface compatibility
    - **Validates: Requirements 13.1, 13.2, 13.3, 13.4, 13.5**
  
  - [x] 26.3 Write integration tests for ModelOptimizer
    - Test end-to-end integration with ModelOptimizer
    - Test backward compatibility
    - Test performance data flow
    - _Requirements: 13.1, 13.5_

- [x] 27. Create configuration files and documentation
  - [x] 27.1 Create default configuration files
    - Create `config/model_registry.json` with sample models
    - Create `.env.template` with required environment variables
    - Create configuration schema documentation
    - _Requirements: 1.2, 6.1, 12.1_
  
  - [x] 27.2 Create API documentation
    - Document all public interfaces
    - Document configuration options
    - Document integration with ModelOptimizer
    - Create usage examples
    - _Requirements: 13.5_

- [x] 28. Final integration testing
  - [ ] 28.1 Write end-to-end integration tests
    - Test complete request flow: Task → Selection → API → Evaluation → Caching
    - Test failover scenario: Unavailable → Alternative → Success
    - Test rate limit scenario: Approach limit → Failover → Reset → Recovery
    - Test cost tracking: Multiple requests → Aggregation → Budget alert
    - Test performance monitoring: Multiple requests → Metrics → Degradation detection
    - _Requirements: 2.1, 5.1, 4.3, 10.3, 11.4_

- [x] 29. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional property-based and unit tests that can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation throughout implementation
- Property tests validate universal correctness properties with minimum 100 iterations
- Unit tests validate specific examples, edge cases, and integration points
- The implementation follows a bottom-up approach: data models → storage → components → integration
- All async operations use Python's asyncio and aiohttp/httpx libraries
- SQLite with aiosqlite is used for all persistence needs
- Configuration uses JSON with jsonschema validation
- Environment variables are managed with python-dotenv
