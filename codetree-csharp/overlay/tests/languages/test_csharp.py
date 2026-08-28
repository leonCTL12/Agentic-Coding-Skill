from codetree.languages.csharp import CSharpPlugin

PLUGIN = CSharpPlugin()

SAMPLE = b"""\
using System;

namespace Demo;

public class Calculator {
    public int Add(int a, int b) {
        return a + b;
    }
    public int Divide(int a, int b) {
        if (b == 0) throw new ArgumentException("div by zero");
        return a / b;
    }
}

public class Helper {
    public int Run() {
        Calculator calc = new Calculator();
        return calc.Add(1, 2);
    }
}

public interface IAlertRepository {
    Task AddAsync(Alert alert, CancellationToken cancellationToken);
}
"""

CONSTRUCTOR_SAMPLE = b"""\
public class Service {
    private string name;
    public Service(string name) {
        this.name = name;
        Init();
    }
    public void Init() {}
}
"""


def test_skeleton_finds_classes():
    result = PLUGIN.extract_skeleton(SAMPLE)
    names = [item["name"] for item in result]
    assert "Calculator" in names
    assert "Helper" in names


def test_skeleton_finds_interface():
    result = PLUGIN.extract_skeleton(SAMPLE)
    iface = next(item for item in result if item["name"] == "IAlertRepository")
    assert iface["type"] == "interface"


def test_skeleton_finds_methods():
    result = PLUGIN.extract_skeleton(SAMPLE)
    names = [item["name"] for item in result]
    assert "Add" in names and "Divide" in names


def test_skeleton_method_has_parent():
    result = PLUGIN.extract_skeleton(SAMPLE)
    add = next(item for item in result if item["name"] == "Add")
    assert add["parent"] == "Calculator"


def test_extract_symbol_finds_class():
    result = PLUGIN.extract_symbol_source(SAMPLE, "Calculator")
    assert result is not None
    source, _ = result
    assert "class Calculator" in source


def test_extract_symbol_finds_method():
    result = PLUGIN.extract_symbol_source(SAMPLE, "Add")
    assert result is not None
    source, _ = result
    assert "Add" in source


def test_extract_symbol_returns_none_for_missing():
    assert PLUGIN.extract_symbol_source(SAMPLE, "nonexistent") is None


def test_extract_calls_in_function():
    calls = PLUGIN.extract_calls_in_function(SAMPLE, "Run")
    assert "Add" in calls or "Calculator" in calls


def test_extract_symbol_usages():
    usages = PLUGIN.extract_symbol_usages(SAMPLE, "Calculator")
    assert len(usages) >= 1


def test_extract_imports():
    imports = PLUGIN.extract_imports(SAMPLE)
    assert any("System" in item["text"] for item in imports)


def test_skeleton_finds_constructor():
    result = PLUGIN.extract_skeleton(CONSTRUCTOR_SAMPLE)
    names = [item["name"] for item in result]
    assert "Service" in names
    ctors = [item for item in result if item["name"] == "Service" and item["parent"] == "Service"]
    assert len(ctors) == 1


def test_extract_calls_in_constructor():
    calls = PLUGIN.extract_calls_in_function(CONSTRUCTOR_SAMPLE, "Service")
    assert "Init" in calls


def test_complexity_counts_if():
    result = PLUGIN.compute_complexity(SAMPLE, "Divide")
    assert result is not None
    assert result["total"] >= 2
    assert result["breakdown"].get("if", 0) >= 1
