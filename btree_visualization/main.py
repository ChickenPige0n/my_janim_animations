from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from janim.imports import *


WHITE_HEX = '#F8FAFC'
INK_HEX = '#0F172A'
PANEL_FILL_HEX = '#101826'
PANEL_STROKE_HEX = '#37517A'
MUTED_TEXT_HEX = '#B8C7DC'
SOFT_TEXT_HEX = '#8FA1BA'
BASE_STROKE_HEX = '#5B82C9'
BASE_FILL_HEX = '#1D2A44'
EDGE_HEX = '#6D7B91'
ACTIVE_HEX = '#F8D75B'
SPLIT_HEX = '#FF6B6B'
SUCCESS_HEX = '#64D59B'
FAIL_HEX = '#FF7C70'
INSERT_TOKEN_HEX = '#FFD166'
PROMOTE_TOKEN_HEX = '#F28482'
QUERY_TOKEN_HEX = '#70E1F5'
EMPTY_SLOT_HEX = '#5C6778'


@dataclass(slots=True)
class BTreeNode:
    id: int
    keys: list[int] = field(default_factory=list)
    children: list['BTreeNode'] = field(default_factory=list)
    leaf: bool = True


@dataclass(frozen=True, slots=True)
class SnapshotNode:
    id: int
    keys: tuple[int, ...]
    children: tuple['SnapshotNode', ...]
    leaf: bool = True


@dataclass(slots=True)
class StepRecord:
    kind: str
    key: int
    snapshot: SnapshotNode
    note: str
    source_node: int | None = None
    target_node: int | None = None
    promoted_key: int | None = None


@dataclass(slots=True)
class SearchTrace:
    path: tuple[int, ...]
    compare_slots: dict[int, tuple[int, ...]]
    chosen_edges: tuple[int, ...]
    found: bool
    found_node: int | None = None
    found_slot: int | None = None
    insertion_slot: int | None = None


@dataclass(slots=True)
class HighlightState:
    active_nodes: set[int] = field(default_factory=set)
    split_nodes: set[int] = field(default_factory=set)
    fail_nodes: set[int] = field(default_factory=set)
    compare_slots: dict[int, tuple[int, ...]] = field(default_factory=dict)
    edge_focus: set[int] = field(default_factory=set)
    success_slot: tuple[int, int] | None = None
    fail_slot: tuple[int, int] | None = None


def freeze_tree(node: BTreeNode) -> SnapshotNode:
    return SnapshotNode(
        id=node.id,
        keys=tuple(node.keys),
        children=tuple(freeze_tree(child) for child in node.children),
        leaf=node.leaf,
    )


def walk_snapshot(node: SnapshotNode):
    yield node
    for child in node.children:
        yield from walk_snapshot(child)


def find_node(node: SnapshotNode, target_id: int) -> SnapshotNode:
    if node.id == target_id:
        return node
    for child in node.children:
        try:
            return find_node(child, target_id)
        except LookupError:
            continue
    raise LookupError(f'Node {target_id} not found')


def path_to_node(node: SnapshotNode, target_id: int) -> list[int]:
    if node.id == target_id:
        return [node.id]
    for child in node.children:
        path = path_to_node(child, target_id)
        if path:
            return [node.id, *path]
    return []


def find_key_slot(node: SnapshotNode, node_id: int, key: int) -> int | None:
    target = find_node(node, node_id)
    for idx, value in enumerate(target.keys):
        if value == key:
            return idx
    return None


def trace_search(node: SnapshotNode, key: int) -> SearchTrace:
    path: list[int] = []
    compare_slots: dict[int, tuple[int, ...]] = {}
    chosen_edges: list[int] = []
    current = node

    while True:
        path.append(current.id)
        compared: list[int] = []
        idx = 0
        while idx < len(current.keys) and key > current.keys[idx]:
            compared.append(idx)
            idx += 1
        if idx < len(current.keys):
            compared.append(idx)
        compare_slots[current.id] = tuple(compared)

        if idx < len(current.keys) and key == current.keys[idx]:
            return SearchTrace(
                path=tuple(path),
                compare_slots=compare_slots,
                chosen_edges=tuple(chosen_edges),
                found=True,
                found_node=current.id,
                found_slot=idx,
                insertion_slot=idx,
            )

        if current.leaf:
            return SearchTrace(
                path=tuple(path),
                compare_slots=compare_slots,
                chosen_edges=tuple(chosen_edges),
                found=False,
                insertion_slot=idx,
            )

        child = current.children[idx]
        chosen_edges.append(child.id)
        current = child


class BTreeRecorder:
    def __init__(self, t: int = 2) -> None:
        self.t = t
        self.max_keys = 2 * t - 1
        self.next_id = 0
        self.root: BTreeNode | None = None
        self.steps: list[StepRecord] = []

    def new_node(self, leaf: bool = True) -> BTreeNode:
        self.next_id += 1
        return BTreeNode(id=self.next_id, leaf=leaf)

    def record_build(self, values: list[int]) -> tuple[list[StepRecord], SnapshotNode]:
        for value in values:
            self.insert(value)
        assert self.root is not None
        return self.steps, freeze_tree(self.root)

    def insert(self, key: int) -> None:
        if self.root is None:
            self.root = self.new_node(leaf=True)
            self.root.keys.append(key)
            self.steps.append(
                StepRecord(
                    kind='insert',
                    key=key,
                    snapshot=freeze_tree(self.root),
                    note=f'根节点为空，直接插入 {key}。',
                    target_node=self.root.id,
                )
            )
            return

        if len(self.root.keys) == self.max_keys:
            old_root = self.root
            new_root = self.new_node(leaf=False)
            new_root.children.append(old_root)
            self.root = new_root
            promoted = self._split_child(new_root, 0)
            self.steps.append(
                StepRecord(
                    kind='split',
                    key=key,
                    snapshot=freeze_tree(self.root),
                    note=f'根节点已满，提升中位键 {promoted}。',
                    source_node=old_root.id,
                    target_node=new_root.id,
                    promoted_key=promoted,
                )
            )

        self._insert_non_full(self.root, key)

    def _insert_non_full(self, node: BTreeNode, key: int) -> None:
        idx = len(node.keys) - 1

        if node.leaf:
            while idx >= 0 and key < node.keys[idx]:
                idx -= 1
            node.keys.insert(idx + 1, key)
            assert self.root is not None
            self.steps.append(
                StepRecord(
                    kind='insert',
                    key=key,
                    snapshot=freeze_tree(self.root),
                    note=f'在叶节点中插入 {key}。',
                    target_node=node.id,
                )
            )
            return

        while idx >= 0 and key < node.keys[idx]:
            idx -= 1
        idx += 1

        child = node.children[idx]
        if len(child.keys) == self.max_keys:
            source_id = child.id
            promoted = self._split_child(node, idx)
            assert self.root is not None
            self.steps.append(
                StepRecord(
                    kind='split',
                    key=key,
                    snapshot=freeze_tree(self.root),
                    note=f'目标子节点已满，先提升中位键 {promoted}。',
                    source_node=source_id,
                    target_node=node.id,
                    promoted_key=promoted,
                )
            )
            if key > node.keys[idx]:
                idx += 1

        self._insert_non_full(node.children[idx], key)

    def _split_child(self, parent: BTreeNode, idx: int) -> int:
        full_child = parent.children[idx]
        sibling = self.new_node(leaf=full_child.leaf)
        mid_idx = self.t - 1
        promoted = full_child.keys[mid_idx]

        sibling.keys = full_child.keys[mid_idx + 1:]
        full_child.keys = full_child.keys[:mid_idx]

        if not full_child.leaf:
            sibling.children = full_child.children[self.t:]
            full_child.children = full_child.children[:self.t]

        parent.children.insert(idx + 1, sibling)
        parent.keys.insert(idx, promoted)
        return promoted


class BTreeBuildAndSearch(Timeline):
    CONFIG = Config(font=['Microsoft YaHei', 'Consolas', 'LXGW WenKai GB'])

    MIN_DEGREE = 2
    MAX_KEYS = 2 * MIN_DEGREE - 1
    INSERT_SEQUENCE = [10, 20, 5, 6, 12, 30, 7, 17]
    QUERY_SEQUENCE = [17, 8]

    CELL_WIDTH = 0.86
    CELL_GAP = 0.06
    NODE_HEIGHT = 0.72
    NODE_WIDTH = MAX_KEYS * CELL_WIDTH + (MAX_KEYS - 1) * CELL_GAP
    SIBLING_GAP = 0.45
    LEVEL_GAP = 1.62
    ROOT_Y = 1.2
    TREE_CENTER_X = -2.4

    PANEL_CENTER = np.array([4.2, 0.1, 0.0])
    PANEL_SIZE = (4.85, 4.8)
    TOKEN_HOME = np.array([4.2, -1.7, 0.0])

    def construct(self) -> None:
        self.current_snapshot: SnapshotNode | None = None
        self.node_views: dict[int, Group] = {}
        self.edge_views: dict[int, Line] = {}
        self.node_positions: dict[int, np.ndarray] = {}
        self.parent_map: dict[int, int] = {}

        self.setup_hud()

        recorder = BTreeRecorder(self.MIN_DEGREE)
        steps, final_snapshot = recorder.record_build(self.INSERT_SEQUENCE)

        self.forward(0.35)
        for step in steps:
            if step.kind == 'split':
                self.animate_split(step)
            else:
                self.animate_insert(step)

        self.sync_scene_to_snapshot(
            final_snapshot,
            headline='构建完成',
            detail='结构已经稳定，接着演示查询路径。',
            duration=0.65,
        )
        self.forward(0.35)

        for key in self.QUERY_SEQUENCE:
            self.animate_query(final_snapshot, key)

        self.sync_scene_to_snapshot(
            final_snapshot,
            headline='演示完成',
            detail='已经展示了构建、分裂和查询过程。',
            duration=0.6,
        )
        self.forward(1.1)

    def setup_hud(self) -> None:
        title = Title('B 树构建与查询', match_underline_width_to_text=True, color=WHITE_HEX)
        title.points.to_border(UP, buff=0.24)

        panel = RoundedRect(
            self.PANEL_SIZE[0],
            self.PANEL_SIZE[1],
            corner_radius=0.18,
            color=PANEL_STROKE_HEX,
            fill_color=PANEL_FILL_HEX,
            fill_alpha=0.08,
        )
        panel.points.move_to(self.PANEL_CENTER)

        static_header = self.make_text(
            '阶数 t = 2\n每个节点最多容纳 3 个键',  
            font_size=21,
            color=MUTED_TEXT_HEX,
            center=self.PANEL_CENTER + np.array([0.0, 1.58, 0.0]),
        )
        insert_text = self.make_text(
            '插入：10 → 20 → 5 → 6\n      12 → 30 → 7 → 17',
            font_size=20,
            color=SOFT_TEXT_HEX,
            center=self.PANEL_CENTER + np.array([0.0, 0.62, 0.0]),
        )
        query_text = self.make_text(
            '查询：17 命中，8 失败',
            font_size=20,
            color=SOFT_TEXT_HEX,
            center=self.PANEL_CENTER + np.array([0.0, -0.02, 0.0]),
        )

        self.status_center = self.PANEL_CENTER + np.array([0.0, -0.92, 0.0])
        self.detail_center = self.PANEL_CENTER + np.array([0.0, -1.58, 0.0])

        self.status_text = self.make_text(
            '准备开始',
            font_size=28,
            color=WHITE_HEX,
            center=self.status_center,
        )
        self.detail_text = self.make_text(
            '先看一棵 B 树怎样逐步长大。',
            font_size=20,
            color=MUTED_TEXT_HEX,
            center=self.detail_center,
        )

        hud = Group(
            panel,
            static_header,
            insert_text,
            query_text,
            self.status_text,
            self.detail_text,
        )
        self.play(FadeIn(title), FadeIn(hud), duration=2.0)

    def make_text(self, text: str, *, font_size: float, color: str, center: np.ndarray) -> Text:
        item = Text(text, font_size=font_size, color=color, stroke_alpha=0)
        item.points.move_to(center)
        return item

    def make_key_token(self, value: int, color: str, position: np.ndarray | None = None) -> Group:
        box = RoundedRect(
            self.CELL_WIDTH,
            self.NODE_HEIGHT,
            corner_radius=0.12,
            color=color,
            fill_color=color,
            fill_alpha=0.32,
        )
        label = Text(str(value), font_size=30, color=INK_HEX, stroke_alpha=0)
        label.points.move_to(box.points.box.center)
        token = Group(box, label)
        token.points.move_to(self.TOKEN_HOME if position is None else position)
        return token

    def format_keys(self, values: tuple[int, ...]) -> str:
        return '[' + ', '.join(str(v) for v in values) + ']'

    def update_info_anims(self, headline: str | None, detail: str | None) -> list:
        anims = []
        if headline is not None:
            old_status = self.status_text
            new_status = self.make_text(
                headline,
                font_size=28,
                color=WHITE_HEX,
                center=self.status_center,
            )
            anims.append(Transform(old_status, new_status, rate_func = ease_out_expo))
            self.status_text = new_status
        if detail is not None:
            old_detail = self.detail_text
            new_detail = self.make_text(
                detail,
                font_size=20,
                color=MUTED_TEXT_HEX,
                center=self.detail_center,
            )
            anims.append(Transform(old_detail, new_detail, rate_func = ease_out_expo))
            self.detail_text = new_detail
        return anims

    def layout_snapshot(self, root: SnapshotNode) -> tuple[dict[int, np.ndarray], dict[int, int]]:
        widths: dict[int, float] = {}
        parents: dict[int, int] = {}

        def measure(node: SnapshotNode) -> float:
            if not node.children:
                widths[node.id] = self.NODE_WIDTH
                return self.NODE_WIDTH
            children_width = sum(measure(child) for child in node.children)
            children_width += self.SIBLING_GAP * (len(node.children) - 1)
            widths[node.id] = max(self.NODE_WIDTH, children_width)
            return widths[node.id]

        def assign(node: SnapshotNode, left: float, depth: int, positions: dict[int, np.ndarray]) -> None:
            width = widths[node.id]
            center_x = left + width / 2
            positions[node.id] = np.array([center_x, self.ROOT_Y - depth * self.LEVEL_GAP, 0.0])

            if not node.children:
                return

            child_width = sum(widths[child.id] for child in node.children)
            child_width += self.SIBLING_GAP * (len(node.children) - 1)
            child_left = left + (width - child_width) / 2

            for child in node.children:
                parents[child.id] = node.id
                assign(child, child_left, depth + 1, positions)
                child_left += widths[child.id] + self.SIBLING_GAP

        measure(root)
        positions: dict[int, np.ndarray] = {}
        assign(root, 0.0, 0, positions)

        delta_x = self.TREE_CENTER_X - positions[root.id][0]
        for position in positions.values():
            position[0] += delta_x

        return positions, parents

    def slot_visuals(
        self,
        node_id: int,
        slot: int,
        occupied: bool,
        highlight: HighlightState,
    ) -> tuple[str, str, float, str, float]:
        stroke = BASE_STROKE_HEX
        fill = BASE_FILL_HEX
        fill_alpha = 0.20 if occupied else 0.06
        text_color = WHITE_HEX if occupied else EMPTY_SLOT_HEX
        text_alpha = 1.0 if occupied else 0.35

        if node_id in highlight.active_nodes:
            stroke = ACTIVE_HEX
            fill_alpha = max(fill_alpha, 0.26)

        if node_id in highlight.split_nodes:
            stroke = SPLIT_HEX
            fill = SPLIT_HEX
            fill_alpha = 0.22 if occupied else 0.10

        if node_id in highlight.fail_nodes:
            stroke = FAIL_HEX

        if slot in highlight.compare_slots.get(node_id, ()): 
            stroke = ACTIVE_HEX
            fill = ACTIVE_HEX
            fill_alpha = 0.48
            text_color = INK_HEX
            text_alpha = 1.0

        if highlight.success_slot == (node_id, slot):
            stroke = SUCCESS_HEX
            fill = SUCCESS_HEX
            fill_alpha = 0.52
            text_color = INK_HEX
            text_alpha = 1.0

        if highlight.fail_slot == (node_id, slot):
            stroke = FAIL_HEX
            fill = FAIL_HEX
            fill_alpha = 0.48
            text_color = WHITE_HEX
            text_alpha = 0.92 if occupied else 0.65

        return stroke, fill, fill_alpha, text_color, text_alpha

    def build_node_group(self, node: SnapshotNode, center: np.ndarray, highlight: HighlightState) -> Group:
        items = []
        slots = list(node.keys) + [None] * (self.MAX_KEYS - len(node.keys))

        for idx, value in enumerate(slots):
            x_offset = (idx - (self.MAX_KEYS - 1) / 2) * (self.CELL_WIDTH + self.CELL_GAP)
            stroke, fill, fill_alpha, text_color, text_alpha = self.slot_visuals(
                node.id,
                idx,
                value is not None,
                highlight,
            )

            cell = RoundedRect(
                self.CELL_WIDTH,
                self.NODE_HEIGHT,
                corner_radius=0.12,
                color=stroke,
                fill_color=fill,
                fill_alpha=fill_alpha,
            )
            cell.points.shift(RIGHT * x_offset)

            label = Text(
                str(value) if value is not None else '·',
                font_size=30,
                color=text_color,
                fill_alpha=text_alpha,
                stroke_alpha=0,
            )
            label.points.move_to(cell.points.box.center)
            items.extend([cell, label])

        group = Group(*items)
        group.points.move_to(center)
        return group

    def build_edge(
        self,
        parent_center: np.ndarray,
        child_center: np.ndarray,
        child_id: int,
        highlight: HighlightState,
    ) -> Line:
        start = parent_center + np.array([0.0, -self.NODE_HEIGHT / 2 - 0.03, 0.0])
        end = child_center + np.array([0.0, self.NODE_HEIGHT / 2 + 0.03, 0.0])
        color = ACTIVE_HEX if child_id in highlight.edge_focus else EDGE_HEX
        alpha = 1.0 if child_id in highlight.edge_focus else 0.82
        return Line(start, end, buff=0, color=color, stroke_alpha=alpha)

    def build_targets(
        self,
        snapshot: SnapshotNode,
        highlight: HighlightState,
    ) -> tuple[dict[int, Group], dict[int, Line], dict[int, np.ndarray], dict[int, int]]:
        positions, parents = self.layout_snapshot(snapshot)
        nodes = {
            node.id: self.build_node_group(node, positions[node.id], highlight)
            for node in walk_snapshot(snapshot)
        }
        edges = {
            child_id: self.build_edge(positions[parent_id], positions[child_id], child_id, highlight)
            for child_id, parent_id in parents.items()
        }
        return nodes, edges, positions, parents

    def sync_scene_to_snapshot(
        self,
        snapshot: SnapshotNode,
        *,
        highlight: HighlightState | None = None,
        headline: str | None = None,
        detail: str | None = None,
        duration: float = 0.8,
        extra_anims: list | None = None,
    ) -> None:
        state = highlight or HighlightState()
        target_nodes, target_edges, positions, parents = self.build_targets(snapshot, state)
        anims = self.update_info_anims(headline, detail)

        if self.current_snapshot is None:
            for edge_id in sorted(target_edges):
                self.edge_views[edge_id] = target_edges[edge_id]
                anims.append(Create(target_edges[edge_id], rate_func = ease_out_quint))
            for node_id in sorted(target_nodes):
                self.node_views[node_id] = target_nodes[node_id]
                anims.append(Create(target_nodes[node_id], rate_func = ease_out_quint))
        else:
            for edge_id in [edge_id for edge_id in list(self.edge_views) if edge_id not in target_edges]:
                anims.append(Uncreate(self.edge_views[edge_id], rate_func = ease_out_quint))
                del self.edge_views[edge_id]
            for node_id in [node_id for node_id in list(self.node_views) if node_id not in target_nodes]:
                anims.append(Uncreate(self.node_views[node_id], rate_func = ease_out_quint))
                del self.node_views[node_id]

            for edge_id, target in target_edges.items():
                if edge_id in self.edge_views:
                    current = self.edge_views[edge_id]
                    anims.append(Transform(current, target, rate_func = ease_out_quint))
                else:
                    anims.append(Create(target, rate_func = ease_out_quint))
                self.edge_views[edge_id] = target

            for node_id, target in target_nodes.items():
                if node_id in self.node_views:
                    current = self.node_views[node_id]
                    anims.append(Transform(current, target, rate_func = ease_out_quint))
                else:
                    anims.append(Create(target, rate_func = ease_out_quint))
                self.node_views[node_id] = target

        if extra_anims:
            anims.extend(extra_anims)

        if anims:
            self.play(*anims, duration=duration)

        self.current_snapshot = snapshot
        self.node_positions = positions
        self.parent_map = parents

    def describe_insert_step(self, node: SnapshotNode, trace: SearchTrace, step_idx: int) -> str:
        if step_idx < len(trace.chosen_edges):
            return f'比较 {self.format_keys(node.keys)} 后继续下降。'
        return f'到达叶节点 {self.format_keys(node.keys)}。'

    def describe_split_path(self, node: SnapshotNode, is_target: bool) -> str:
        if is_target:
            return f'目标节点 {self.format_keys(node.keys)} 已满。'
        return f'沿插入路径下降到 {self.format_keys(node.keys)}。'

    def describe_query_step(self, node: SnapshotNode, trace: SearchTrace, step_idx: int) -> str:
        if step_idx < len(trace.chosen_edges):
            return f'比较 {self.format_keys(node.keys)}，继续查找。'
        if trace.found:
            return f'在节点 {self.format_keys(node.keys)} 中找到目标键。'
        return f'到达叶节点 {self.format_keys(node.keys)}。'

    def animate_insert(self, step: StepRecord) -> None:
        assert step.target_node is not None
        headline = f'插入 {step.key}'
        success_slot = find_key_slot(step.snapshot, step.target_node, step.key)
        assert success_slot is not None

        target_positions, _ = self.layout_snapshot(step.snapshot)
        token = self.make_key_token(step.key, INSERT_TOKEN_HEX)
        self.play(FadeIn(token), duration=0.25)

        if self.current_snapshot is not None:
            trace = trace_search(self.current_snapshot, step.key)
            for idx, node_id in enumerate(trace.path):
                node = find_node(self.current_snapshot, node_id)
                edge_focus = set()
                if idx < len(trace.chosen_edges):
                    edge_focus.add(trace.chosen_edges[idx])

                self.sync_scene_to_snapshot(
                    self.current_snapshot,
                    highlight=HighlightState(
                        active_nodes={node_id},
                        compare_slots={node_id: trace.compare_slots.get(node_id, ())},
                        edge_focus=edge_focus,
                    ),
                    headline=headline,
                    detail=self.describe_insert_step(node, trace, idx),
                    duration=2,
                    extra_anims=[token.anim(rate_func = ease_out_quint).points.move_to(self.node_positions[node_id] + UP * 0.95)],
                )
                self.forward(0.08)

        self.sync_scene_to_snapshot(
            step.snapshot,
            highlight=HighlightState(
                active_nodes={step.target_node},
                success_slot=(step.target_node, success_slot),
            ),
            headline=headline,
            detail=step.note,
            duration=2,
            extra_anims=[token.anim(rate_func = ease_out_quint).points.move_to(target_positions[step.target_node])],
        )
        self.play(FadeOut(token), duration=0.25)
        self.forward(0.24)

    def animate_split(self, step: StepRecord) -> None:
        assert self.current_snapshot is not None
        assert step.source_node is not None
        assert step.target_node is not None
        assert step.promoted_key is not None

        trace = trace_search(self.current_snapshot, step.key)
        if step.source_node in trace.path:
            stop = trace.path.index(step.source_node) + 1
            path = list(trace.path[:stop])
        else:
            path = path_to_node(self.current_snapshot, step.source_node)

        for idx, node_id in enumerate(path):
            node = find_node(self.current_snapshot, node_id)
            edge_focus = {path[idx + 1]} if idx + 1 < len(path) else set()
            compared = trace.compare_slots.get(node_id, ())
            self.sync_scene_to_snapshot(
                self.current_snapshot,
                highlight=HighlightState(
                    active_nodes={node_id},
                    compare_slots={node_id: compared},
                    edge_focus=edge_focus,
                ),
                headline='准备分裂满节点',
                detail=self.describe_split_path(node, node_id == step.source_node),
                duration=2,
            )
            self.forward(0.08)

        median_slot = find_key_slot(self.current_snapshot, step.source_node, step.promoted_key)
        assert median_slot is not None
        self.sync_scene_to_snapshot(
            self.current_snapshot,
            highlight=HighlightState(
                split_nodes={step.source_node},
                compare_slots={step.source_node: (median_slot,)},
            ),
            headline='节点分裂',
            detail=step.note,
            duration=2,
        )

        token = self.make_key_token(
            step.promoted_key,
            PROMOTE_TOKEN_HEX,
            position=self.node_positions[step.source_node],
        )
        self.play(FadeIn(token), duration=0.2)

        target_positions, _ = self.layout_snapshot(step.snapshot)
        promoted_slot = find_key_slot(step.snapshot, step.target_node, step.promoted_key)
        assert promoted_slot is not None
        self.sync_scene_to_snapshot(
            step.snapshot,
            highlight=HighlightState(
                active_nodes={step.target_node},
                success_slot=(step.target_node, promoted_slot),
            ),
            headline='完成分裂',
            detail=step.note,
            duration=2,
            extra_anims=[token.anim(rate_func = ease_out_quint).points.move_to(target_positions[step.target_node])],
        )
        self.play(FadeOut(token), duration=0.25)
        self.forward(0.2)

    def animate_query(self, snapshot: SnapshotNode, key: int) -> None:
        trace = trace_search(snapshot, key)
        token = self.make_key_token(key, QUERY_TOKEN_HEX)
        self.play(FadeIn(token), duration=0.25)

        for idx, node_id in enumerate(trace.path):
            node = find_node(snapshot, node_id)
            edge_focus = set()
            if idx < len(trace.chosen_edges):
                edge_focus.add(trace.chosen_edges[idx])

            self.sync_scene_to_snapshot(
                snapshot,
                highlight=HighlightState(
                    active_nodes={node_id},
                    compare_slots={node_id: trace.compare_slots.get(node_id, ())},
                    edge_focus=edge_focus,
                ),
                headline=f'查询 {key}',
                detail=self.describe_query_step(node, trace, idx),
                duration=2,
                extra_anims=[token.anim(rate_func = ease_out_quint).points.move_to(self.node_positions[node_id] + DOWN * 0.95)],
            )
            self.forward(0.08)

        last_node = trace.path[-1]
        if trace.found:
            assert trace.found_node is not None and trace.found_slot is not None
            self.sync_scene_to_snapshot(
                snapshot,
                highlight=HighlightState(
                    active_nodes={trace.found_node},
                    success_slot=(trace.found_node, trace.found_slot),
                ),
                headline=f'查询 {key} 成功',
                detail='命中目标键，搜索结束。',
                duration=2,
                extra_anims=[token.anim(rate_func = ease_out_quint).points.move_to(self.node_positions[trace.found_node])],
            )
        else:
            fail_slot = None
            if trace.insertion_slot is not None and trace.insertion_slot < self.MAX_KEYS:
                fail_slot = (last_node, trace.insertion_slot)
            self.sync_scene_to_snapshot(
                snapshot,
                highlight=HighlightState(
                    active_nodes={last_node},
                    fail_nodes={last_node},
                    compare_slots={last_node: trace.compare_slots.get(last_node, ())},
                    fail_slot=fail_slot,
                ),
                headline=f'查询 {key} 失败',
                detail='叶节点未命中，查询结束。',
                duration=2,
                extra_anims=[token.anim(rate_func = ease_out_quint).points.move_to(self.node_positions[last_node] + DOWN * 0.18)],
            )

        self.play(FadeOut(token), duration=0.25)
        self.forward(0.35)