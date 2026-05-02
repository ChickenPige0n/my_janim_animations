---
name: janim-workflow
description: 'Use for JAnim animation authoring, debugging, explanation, and refactoring in Python. Covers Timeline, construct, play, forward, Create, Transform, Uncreate, .anim, TypstText, TypstMath, GUI preview, uv run janim run/write, janim-toolbox, and mapping requests to the official Chinese docs. 适用于 JAnim 动画编写、调试、Typst 排版、API 解释、GUI 预览、导出视频、以及从官方中文文档快速定位教程与参考。'
argument-hint: '描述你想实现的 JAnim 动画效果、代码修改、报错、API 疑问或 Typst 排版需求'
---

# JAnim 工作流

## 这个技能解决什么问题

当用户想在 JAnim 项目中：

- 新建或修改 `Timeline` 动画
- 为 B 树、平衡树、搜索路径、节点分裂等算法过程制作教学动画
- 解释 `construct()`、`play()`、`forward()`、`.anim`、`Create`、`Transform`、`Uncreate`
- 处理 `TypstText`、`TypstMath`、`TypstDoc` 的排版与索引
- 使用 GUI 做预览、定位、子物件选择或热重载
- 导出视频，或排查与 Typst / FFmpeg / VS Code 插件相关的问题
- 把 Manim 的思路迁移到 JAnim

就使用这个技能。

此技能默认以官方中文文档为准，并优先结合当前工作区的实际运行方式来给出建议。

## 当前工作区假设

在类似当前仓库的 JAnim 项目中：

- 当前仓库主题可视为 **B 树 / 算法可视化**，因此在通用 JAnim 工作流之外，可以额外参考 [B 树可视化手册](./references/btree-viz-playbook.md)
- 优先检查 `pyproject.toml` 是否使用 `uv`
- 如果存在 `uv.lock` 或项目已通过 `uv` 管理，则优先使用 `uv run janim ...`
- 默认预览命令通常是 `uv run janim run main.py`
- 如果文件中有多个 `Timeline` 类，优先显式指定类名，例如：`uv run janim run main.py HelloJAnimExample`
- 导出视频通常会写入 `videos/` 目录

## 先做哪类判断

### 1. 判断用户要的是哪一类帮助

把请求归到以下一种或多种：

- **讲解型**：解释概念、API、参数、GUI 行为
- **实现型**：新增或修改动画代码
- **调试型**：报错、运行失败、预览异常、导出失败
- **排版型**：Typst 文本、公式、标签、索引、嵌入物件
- **迁移型**：把 Manim 写法换成 JAnim 写法

### 2. 判断优先查哪份官方文档

优先使用这些页面：

- 总入口：<https://janim.readthedocs.io/zh-cn/latest/>
- 安装与环境：<https://janim.readthedocs.io/zh-cn/latest/installation.html>
- 入门与标准起手式：<https://janim.readthedocs.io/zh-cn/latest/get_started.html>
- 动画系统：<https://janim.readthedocs.io/zh-cn/latest/tutorials/animations.html>
- Typst：<https://janim.readthedocs.io/zh-cn/latest/tutorials/typst_usage.html>
- GUI：<https://janim.readthedocs.io/zh-cn/latest/tutorials/use_gui.html>
- 常用导入：<https://janim.readthedocs.io/zh-cn/latest/janim/imports.html>
- FAQ：<https://janim.readthedocs.io/zh-cn/latest/other/faq.html>

如果问题涉及具体类或函数，再顺着参考文档继续查对应 API 页面。

如果想更快地把问题映射到页面，可以先看：

- [JAnim 文档地图](./references/docs-map.md)
- [B 树可视化手册](./references/btree-viz-playbook.md)

## 标准工作流程

### 1. 读项目，再读代码

先确认：

- 当前目标文件
- 有哪些 `Timeline` 子类
- 项目是否由 `uv` 管理
- 是否已经存在可复用的物件、颜色、布局方式
- 用户要“解释”还是“直接改代码”

如果是代码修改任务：

- 保持 `Timeline` 子类结构不变
- 动画主体写在 `construct()` 中
- 优先做小而可验证的改动
- 保留用户已有命名和节奏，除非这些本身妨碍实现

### 2. 选对 JAnim 机制

根据目标选择实现方式：

- **只想静态显示物件**：优先 `show()`
- **想播放内置动画**：优先 `Create(...)`、`Uncreate(...)`、`Transform(...)`、`FadeIn(...)` 等
- **想让属性逐渐变化**：优先 `item.anim...`
- **想并行播放多个动画**：把多个动画放进同一个 `play(...)`，必要时使用 `AnimGroup`
- **想串联多个阶段**：优先 `Succession`
- **想提前预约某段动画但不立即推进时间**：优先 `prepare()`
- **想在组件链式调用后回到物件层级**：使用 `.r`

常用参数优先考虑：

- `duration`：控制时长
- `at`：控制开始时机
- `rate_func`：控制缓动

### 3. 处理 Typst 时的分支逻辑

当需求涉及 Typst：

- 普通文本或混排文本：优先 `TypstText`
- 纯公式：优先 `TypstMath`
- 整体文档式布局：考虑 `TypstDoc`
- 需要高亮/着色某部分：优先使用字符索引，例如 `typ['cos']`
- 有重复匹配：使用编号或省略号，例如 `typ['theta', 1]`、`typ['theta', ...]`
- 需要嵌入 JAnim 物件：使用 `vars=`，必要时加 `vars_size_unit='em'`
- 需要在 VS Code 里提升 Typst 可读性：建议结合 `janim-toolbox`

注意：

- `TypstMath` 的内容会被包裹在公式环境中
- `TypstText` 更适合文本主导或文中夹公式的场景
- `TypstDoc` 默认有更像“文档顶部对齐”的观感

### 4. 运行、预览、导出

优先按项目环境选择命令风格：

- `uv` 项目：优先 `uv run janim ...`
- 非 `uv` 项目：使用 `janim ...`

常见工作方式：

- 预览：`run`
- 导出视频：`write`
- 想保存后自动重建：在预览时考虑 `-i`

在 VS Code 工作流中：

- 可以配合 `janim-toolbox` 获得重建、代码定位、Typst 高亮等能力
- GUI 中可以做子物件选择、绘制取点、字体/颜色查询

### 5. 调试顺序

如果结果不对，不要直接乱改。按下面顺序查：

1. 当前运行的是不是目标 `Timeline`
2. 命令是否需要显式指定类名
3. 物件是没创建、没显示，还是被移动到视野外
4. 是动画参数问题，还是组件/布局问题
5. Typst 问题是出在文本类型、索引方式、还是颜色/环境差异
6. 导出问题是否与 FFmpeg 缺失有关
7. GUI/语言显示问题是否与 VS Code 插件或语言包有关

## 完成标准

任务完成前，至少确认以下几点：

- 代码结构仍符合 JAnim 的 `Timeline -> construct()` 模式
- 动画机制选型合理，不是“能跑就行”的硬拼
- 如果做了代码改动，已经尝试预览或以其他方式验证
- 对外说明中给出了对应文档落点，而不是只给拍脑袋结论
- 如果用户是初学者，顺手解释关键概念；如果用户是熟手，优先给直接可执行的改法

## 高价值提示

- `from janim.imports import *` 是官方文档里常见的起手式；除非用户明确要求，否则不要强行改成零散导入
- `play()` 可以理解为“安排动画并推进时间”
- `prepare()` 可以理解为“安排动画但先不推进时间”
- 在同一个 `play()` 里的动画默认并行
- 热重载与 GUI 工具通常能显著减少“改一点，重开一次”的痛苦值
- 导出视频前若缺少 FFmpeg，预览可能仍然没问题；别把这两件事混为一谈

## 附加参考资料

- [JAnim 文档地图](./references/docs-map.md)：按“问题类型 -> 文档页面”快速跳转
- [B 树可视化手册](./references/btree-viz-playbook.md)：面向当前仓库的布局、过渡和教学节奏建议

## 示例提示词

- “用 JAnim 给 B 树插入过程做一个 10 秒动画，先从 `main.py` 开始。”
- “请按 B 树可视化手册，把节点分裂做成更清楚的过渡动画。”
- “解释 `Create`、`Transform`、`Uncreate` 在 JAnim 里的区别，并顺便改进当前示例节奏。”
- “把这个 `TypstText` 改成更适合公式展示的写法，并告诉我为什么该用 `TypstMath`。”
- “我想在 VS Code 里边改边看 JAnim 预览，帮我配置最顺手的工作流。”
- “把一个 Manim 动画片段按 JAnim 风格重写，并指出 API 对应关系。”
- “为什么我的导出失败但预览正常？请按 JAnim 的常见问题思路排查。”

## 不该怎么做

- 不要凭记忆硬猜 JAnim API，尤其是冷门类和参数
- 不要跳过当前项目的运行方式，先确认是 `uv run janim ...` 还是直接 `janim ...`
- 不要把 Typst 的文本环境和公式环境混用后再怪渲染“闹脾气”
- 不要一次性重写整个时间轴，除非用户明确要求大改
