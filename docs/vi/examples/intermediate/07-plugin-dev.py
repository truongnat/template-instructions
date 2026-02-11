"""
Ví Dụ 7: Plugin Development (Phát Triển Plugin)

Setup Instructions:
1. Cài đặt: pip install agentic-sdlc
2. Chạy: python 07-plugin-dev.py

Dependencies:
- agentic-sdlc>=3.0.0

Expected Output:
- Custom plugin được tạo và đăng ký
- Plugin lifecycle hoạt động
- Plugin được sử dụng trong workflow
"""

from agentic_sdlc.plugins.base import Plugin, PluginRegistry


class CustomAnalyzerPlugin(Plugin):
    """Custom plugin để phân tích code."""
    
    @property
    def name(self) -> str:
        return "custom-analyzer"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def initialize(self) -> None:
        """Initialize plugin."""
        print(f"  ✓ Initializing {self.name} v{self.version}")
        self.analysis_count = 0
    
    def shutdown(self) -> None:
        """Shutdown plugin."""
        print(f"  ✓ Shutting down {self.name}")
        print(f"    Total analyses: {self.analysis_count}")
    
    def analyze_code(self, code: str) -> dict:
        """Phân tích code."""
        self.analysis_count += 1
        
        # Simple analysis
        lines = code.split('\n')
        functions = [l for l in lines if 'def ' in l]
        classes = [l for l in lines if 'class ' in l]
        
        return {
            "lines": len(lines),
            "functions": len(functions),
            "classes": len(classes),
            "complexity": "low" if len(lines) < 50 else "high"
        }


class DataTransformPlugin(Plugin):
    """Plugin để transform data."""
    
    @property
    def name(self) -> str:
        return "data-transform"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def initialize(self) -> None:
        print(f"  ✓ Initializing {self.name}")
        self.transformers = {
            "uppercase": str.upper,
            "lowercase": str.lower,
            "reverse": lambda x: x[::-1]
        }
    
    def shutdown(self) -> None:
        print(f"  ✓ Shutting down {self.name}")
    
    def transform(self, data: str, transform_type: str) -> str:
        """Transform data."""
        transformer = self.transformers.get(transform_type)
        if transformer:
            return transformer(data)
        return data


def create_and_register_plugins():
    """Tạo và đăng ký plugins."""
    registry = PluginRegistry()
    
    # Tạo plugins
    analyzer = CustomAnalyzerPlugin()
    transformer = DataTransformPlugin()
    
    # Đăng ký plugins
    registry.register(analyzer)
    registry.register(transformer)
    
    print("✓ Plugins đã được đăng ký")
    print(f"  Total plugins: {len(registry.list_plugins())}")
    for plugin_name in registry.list_plugins():
        plugin = registry.get(plugin_name)
        print(f"    - {plugin.name} v{plugin.version}")
    
    return registry


def use_plugins(registry):
    """Sử dụng plugins."""
    # Get analyzer plugin
    analyzer = registry.get("custom-analyzer")
    
    # Analyze code
    code = """
def hello():
    print("Hello")

class MyClass:
    pass
"""
    
    result = analyzer.analyze_code(code)
    
    print("\n✓ Code analysis result:")
    for key, value in result.items():
        print(f"    {key}: {value}")
    
    # Get transformer plugin
    transformer = registry.get("data-transform")
    
    # Transform data
    data = "Hello World"
    transformed = transformer.transform(data, "uppercase")
    
    print(f"\n✓ Data transformation:")
    print(f"    Original: {data}")
    print(f"    Transformed: {transformed}")


if __name__ == "__main__":
    print("=" * 60)
    print("VÍ DỤ: PLUGIN DEVELOPMENT")
    print("=" * 60)
    
    registry = create_and_register_plugins()
    use_plugins(registry)
    
    print("\n" + "=" * 60)
    print("✓ Hoàn thành!")
    print("=" * 60)
