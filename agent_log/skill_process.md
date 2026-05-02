User: /create-skill https://janim.readthedocs.io/zh-cn/latest/

GitHub Copilot: Optimizing tool selection...我先把相关说明和 JAnim 文档脉络摸清，再起草一个可复用的 SKILL.md，目标是把它落成到当前工作区里并尽量做到可直接用。



已提取 https://janim.readthedocs.io/zh-cn/latest/

Read skill [agent-customization](file:///d%3A/Program%20Files/Microsoft%20VS%20Code/034f571df5/resources/app/extensions/copilot/assets/prompts/skills/agent-customization/SKILL.md?vscodeLinkType%3Dskill)

我已经拿到定制化规范和 JAnim 文档首页；下一步把技能模板、当前项目上下文和 JAnim 关键章节拼起来，做成一个靠谱的初稿。

Read [](file:///[data_deleted]/btree_viz)

Read [](file:///[data_deleted]/btree_viz/main.py)

已创建 5 个待办事项

Read skill `agent-customization`: [](file:///d%3A/Program%20Files/Microsoft%20VS%20Code/034f571df5/resources/app/extensions/copilot/assets/prompts/skills/agent-customization/references/skills.md)

Read [](file:///[data_deleted]/btree_viz/README.md)

Read [](file:///[data_deleted]/btree_viz/pyproject.toml)

现在项目侧信息也齐了：这是个极简 JAnim 项目。我再抓几页关键文档，把技能说明写得“既会找路，又会动手”，避免只会背目录不会干活。



已提取 7 资源

我开始落地技能文件了：做成工作区范围、偏 JAnim 实战工作流的版本，先保证它现在就能用，后面再根据你的偏好微调。

Created [](file:///[data_deleted]/btree_viz/.github/skills/janim-workflow/SKILL.md)

技能草稿已经写进工作区了；我现在做一次快速自检，确认 frontmatter、路径和内容都没有“看起来像 YAML、实际上像薛定谔配置”的问题。

Checked [](file:///[data_deleted]/btree_viz/.github/skills/janim-workflow/SKILL.md), no problems found

Read [](file:///[data_deleted]/btree_viz/.github/skills/janim-workflow)

Read skill [janim-workflow](file:///[data_deleted]/btree_viz/.github/skills/janim-workflow/SKILL.md?vscodeLinkType%3Dskill)

草稿通过自检了，我接着把最需要你拍板的地方浓缩成三个小问题，这样后续要么我帮你精修，要么你直接开用都行。

正在分析你的回答...

你已经替这个技能定了方向：工作区内使用、兼顾通用 JAnim 和 B 树可视化、还要补参考资料。我这就把它升级成“主流程 + 两份随查手册”的版本。

Created [](file:///[data_deleted]/btree_viz/.github/skills/janim-workflow/references/docs-map.md)

Created [](file:///[data_deleted]/btree_viz/.github/skills/janim-workflow/references/btree-viz-playbook.md)

主流程和两份参考手册都准备好了；我再把入口文件串起来，让技能正文能显式指向这些附加资料。

Generating patch (63 lines) in [](file:///[data_deleted]/btree_viz/.github/skills/janim-workflow/SKILL.md)


```

```
我做最后一轮检查，确保主技能和两份参考资料都能在工作区里干净落地，然后就给你总结怎么用。

Checked [](file:///[data_deleted]/btree_viz/.github/skills/janim-workflow/SKILL.md), [](file:///[data_deleted]/btree_viz/.github/skills/janim-workflow/references/docs-map.md), [](file:///[data_deleted]/btree_viz/.github/skills/janim-workflow/references/btree-viz-playbook.md), no problems found

Read [](file:///[data_deleted]/btree_viz/.github/skills/janim-workflow/references)

Read skill [janim-workflow](file:///[data_deleted]/btree_viz/.github/skills/janim-workflow/SKILL.md?vscodeLinkType%3Dskill)

收尾一下进度板：主体技能、补充参考、校验和可用示例都已经就位，我把清单标成完成后给你一个精炼总结。

已完成: *读取技能模板规范* (1/5)

已按 `#prompt:SKILL.md` 的流程把它做成了一个**工作区级 JAnim 技能**，并且根据你刚才的选择，把它强化成了 **通用 JAnim 开发 + B 树/算法可视化** 的版本。顺手还补了两份参考资料，避免技能只会“讲流程”不会“指路”。

## 已落地的文件

- SKILL.md  
  主技能文件，定义触发词、适用场景、分支逻辑、完成标准和示例提示词。

- docs-map.md  
  JAnim 官方中文文档地图：把“问题类型”快速映射到对应文档页面。

- btree-viz-playbook.md  
  面向当前 `btree_viz` 仓库的 B 树可视化手册：讲布局、过渡、节点分裂、查找路径、教学节奏。

## 这个技能现在会产出什么

它现在能比较稳定地处理这几类请求：

- JAnim 动画编写与修改
- `Timeline` / `construct()` / `play()` / `forward()` / `.anim` 等 API 解释
- `TypstText` / `TypstMath` / `TypstDoc` 的排版与索引
- GUI 预览、热重载、子物件选择相关工作流
- `uv run janim ...` 风格的当前仓库运行方式
- B 树、平衡树、搜索路径、节点分裂等算法可视化场景
- Manim 到 JAnim 的思路迁移

而且它会优先参考我已经核对过的官方页面，包括：

- `installation.html`
- `get_started.html`
- `tutorials/animations.html`
- `tutorials/typst_usage.html`
- `tutorials/use_gui.html`
- `janim/imports.html`
- `other/faq.html`

## 怎么试用

在聊天里可以直接调用 `/janim-workflow`，后面接你的需求。比如：

- `/janim-workflow 用 JAnim 给 B 树插入 37 的过程做一个带节点分裂的教学动画，从 main.py 开始`
- `/janim-workflow 解释 main.py 里 Create、Transform、Uncreate 的区别，并顺便改进节奏`
- `/janim-workflow 把当前 TypstText 改成更适合公式展示的写法，并说明为什么用 TypstMath`
- `/janim-workflow 按 B 树可视化手册重构节点布局，让变换尽量用 Transform 而不是整棵树重画`

## 我做过的校验

这次新增的 3 个文件都已检查过：

- 路径正确
- frontmatter 合法
- 内容可读
- 无错误报告

小结一句：现在它不是一个“空壳技能”，而是一个**会先查官方文档、再结合当前 repo 的 `uv + JAnim + B 树可视化` 习惯来做事**的版本。

## 接下来值得补的相关定制

如果你想把这个工作流继续打磨成“更像你自己的助手”，下一步最值的通常是这几个：

- `janim.instructions.md`  
  做成**常驻指令**，让代理在这个仓库里默认遵循：
  - 优先 `uv run janim ...`
  - 优先小步修改
  - 动画逻辑和树结构逻辑分离
  - B 树过渡尽量保留对象连续性

- `btree-scene.prompt.md`  
  做成一个**一键场景脚手架提示**，例如“生成插入动画骨架 / 生成分裂动画骨架”。

- `janim-review.agent.md`  
  做成一个**专门审查 JAnim 动画质量**的代理，重点看：
  - 动画节奏
  - Typst 选型
  - 布局函数是否统一
  - 是否过度重绘

## 当前清单

- [x] 读取技能模板规范
- [x] 梳理项目与 JAnim 上下文
- [x] 起草工作区 JAnim 技能
- [x] 校验技能文件位置与内容
- [x] 指出待确认项并给示例用法

如果你愿意，我下一步可以直接继续帮你补一个 `.github/instructions/janim.instructions.md`，把这个仓库的 JAnim/B 树约定变成默认行为。

已进行更改。