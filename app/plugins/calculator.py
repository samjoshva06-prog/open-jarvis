from __future__ import annotations

import ast
import operator
import re

from app.plugin_base import Plugin, PluginManifest


class CalculatorPlugin(Plugin):
    manifest = PluginManifest(
        id="calculator",
        name="Calculator",
        description="Safely evaluates basic arithmetic expressions.",
    )
    _expression = re.compile(r"(?<![\w.])[0-9][0-9\s()+\-*/%.]*")
    _operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    def matches(self, message: str) -> bool:
        lowered = message.lower()
        return "calculate" in lowered or "what is" in lowered or bool(
            re.search(r"\d\s*[+*/%\-]\s*\d", message)
        )

    def run(self, message: str) -> str:
        match = self._expression.search(message)
        if not match:
            return "I couldn't find an arithmetic expression to calculate."
        expression = match.group(0).strip().rstrip(".")
        if len(expression) > 100:
            return "That expression is too long to calculate."
        try:
            tree = ast.parse(expression, mode="eval")
            if sum(1 for _ in ast.walk(tree)) > 40:
                return "That expression is too complex to calculate."
            result = self._evaluate(tree.body)
            if isinstance(result, (int, float)) and abs(result) > 1e100:
                return "The result is too large to display."
            return f"{expression} = {result}"
        except (SyntaxError, ValueError, TypeError, ZeroDivisionError, OverflowError):
            return "I couldn't safely evaluate that expression. Try basic arithmetic such as 12 * (3 + 4)."

    def _evaluate(self, node: ast.expr) -> int | float:
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in self._operators:
            left = self._evaluate(node.left)
            right = self._evaluate(node.right)
            if isinstance(node.op, ast.Mult) and abs(left) > 1e100 / max(abs(right), 1):
                raise ValueError("result too large")
            return self._operators[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and type(node.op) in self._operators:
            return self._operators[type(node.op)](self._evaluate(node.operand))
        raise ValueError("unsupported expression")
