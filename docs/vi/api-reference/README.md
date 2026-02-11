# API Reference

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


Tài liệu tham khảo API đầy đủ cho Agentic SDLC v3.0.0.

## Cấu Trúc

### Core
Các module cốt lõi của hệ thống:
- [config.md](core/config.md) - Quản lý cấu hình
- [exceptions.md](core/exceptions.md) - Các exception types
- [logging.md](core/logging.md) - Hệ thống logging

### Infrastructure
Các module hạ tầng:
- [execution_engine.md](infrastructure/execution_engine.md) - Task execution engine
- [lifecycle.md](infrastructure/lifecycle.md) - Lifecycle management

### Intelligence
Các module trí tuệ nhân tạo:
- [learner.md](intelligence/learner.md) - Learning và knowledge management
- [monitor.md](intelligence/monitor.md) - Monitoring và metrics
- [reasoner.md](intelligence/reasoner.md) - Reasoning và decision making
- [collaborator.md](intelligence/collaborator.md) - Team collaboration

### Orchestration
Các module điều phối:
- [agent.md](orchestration/agent.md) - Agent management
- [workflow.md](orchestration/workflow.md) - Workflow definition
- [client.md](orchestration/client.md) - Model client integration

### Plugins
Hệ thống plugin:
- [base.md](plugins/base.md) - Plugin base class
- [registry.md](plugins/registry.md) - Plugin registry

## Quy Ước

### Type Hints
Tất cả các API đều có type hints đầy đủ để hỗ trợ IDE autocomplete và type checking.

### Docstrings
Mỗi class, method, và function đều có docstring mô tả chức năng, parameters, và return values.

### Examples
Mỗi API reference đều bao gồm ví dụ sử dụng cơ bản.

## Xem Thêm

- [Hướng dẫn cài đặt](../getting-started/installation.md)
- [Hướng dẫn cấu hình](../getting-started/configuration.md)
- [Use Cases](../use-cases/README.md)
- [Examples](../examples/README.md)
