"""Discovery tree tests."""

import json
from pathlib import Path

from dream_quant.discovery.tree import DiscoveryNode, DiscoveryTree
from dream_quant.strategies.base import StrategySpec


def _make_node(parent_id=None, sharpe=0.5):
    spec = StrategySpec(name="momentum", params={"lookback": 20, "threshold": 0.02})
    return DiscoveryNode(
        node_id=f"node_{sharpe}",
        parent_id=parent_id,
        spec=spec,
        metrics={"sharpe": sharpe, "total_return": 0.1},
    )


def test_tree_add_and_parent_child():
    tree = DiscoveryTree.empty()
    root = _make_node(sharpe=0.3)
    root.node_id = "root"
    tree.add_node(root)
    child = _make_node(parent_id="root", sharpe=0.8)
    child.node_id = "child"
    tree.add_node(child)

    assert tree.attempt_count() == 2
    assert "child" in tree.nodes["root"].children_ids
    assert tree.best_quality("sharpe") == 0.8


def test_tree_save_load(tmp_path: Path):
    tree = DiscoveryTree.empty(metadata={"round": 1})
    root = _make_node()
    root.node_id = "r1"
    tree.add_node(root)
    path = tmp_path / "tree.json"
    tree.save(path)
    loaded = DiscoveryTree.load(path)
    assert loaded.tree_id == tree.tree_id
    assert loaded.attempt_count() == 1
    assert loaded.metadata["round"] == 1
