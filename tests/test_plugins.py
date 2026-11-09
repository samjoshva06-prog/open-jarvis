from app.assistant_manager import AssistantManager
from app.plugins.calculator import CalculatorPlugin


def test_assistants_have_separate_plugin_permissions():
    manager = AssistantManager()
    assert manager.respond("general", "What is 12 * (3 + 4)?")[1] == "calculator"
    assert manager.respond("developer", "What time is it?")[1] is None
    assert manager.respond("planner", "What time is it?")[1] == "clock"


def test_calculator_supports_basic_arithmetic():
    plugin = CalculatorPlugin()
    assert plugin.run("What is 12 * (3 + 4)?") == "12 * (3 + 4) = 84"


def test_calculator_rejects_python_expressions():
    plugin = CalculatorPlugin()
    assert "couldn't safely evaluate" in plugin.run("calculate __import__('os')")
