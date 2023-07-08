from math import floor
from typing import Tuple

import d20

from .type import Die


def _merge(d1: dict, d2: dict) -> dict:
    merged = {}
    for die, count in d1.items():
        existing = merged.get(die, 0)
        merged[die] = existing + count
    for die, count in d2.items():
        existing = merged.get(die, 0)
        merged[die] = existing + count
    return merged


def _visit_literal(node: d20.ast.Literal, multiplier=1) -> int:
    v = floor(node.value)
    if v != node.value:
        raise ValueError(f"Unsupported literal: {node.value}")
    return multiplier * v


def _visit_dice(node: d20.ast.Dice, multiplier=1) -> dict:
    die = Die.parse(f"d{node.size}")
    n = floor(node.num)
    if n != node.num:
        raise ValueError(f"Unsupport num: {node.num}")
    return {die: multiplier * n}


def _visit_node(node: d20.ast.Node, multiplier: int = 1) -> Tuple[dict, int]:
    mod = 0
    result = {}

    if isinstance(node, d20.ast.Literal):
        mod += _visit_literal(node, multiplier)
    elif isinstance(node, d20.ast.Dice):
        node_die = _visit_dice(node, multiplier)
        result = _merge(result, node_die)
    elif isinstance(node, d20.ast.BinOp):
        op_die, op_mod = _visit_bin_op(node)
        mod += op_mod
        result = _merge(result, op_die)
    elif isinstance(node, d20.ast.Expression):
        expression_die, expression_mod = _visit_expression(node)
        mod += expression_mod
        result = _merge(result, expression_die)
    else:
        raise ValueError(f"Unsupported node: {node}")

    return result, mod


def _visit_bin_op(node: d20.ast.BinOp) -> Tuple[dict, int]:
    left = node.left
    right = node.right
    if node.op == "+":
        right_multiplier = 1
    elif node.op == "-":
        right_multiplier = -1
    else:
        raise ValueError(f"Unsupported operator {node.op}")

    if left is not None:
        left_die, left_mod = _visit_node(left)
    else:
        left_die, left_mod = {}, 0

    if right is not None:
        right_die, right_mod = _visit_node(right, multiplier=right_multiplier)
    else:
        right_die, right_mod = {}, 0

    result = _merge(left_die, right_die)
    mod = left_mod + right_mod

    return result, mod


def _visit_expression(node: d20.ast.Expression) -> Tuple[dict, int]:
    return _visit_node(node.roll)
