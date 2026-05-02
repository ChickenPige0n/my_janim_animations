# JAnim 官方文档地图

这个文件用于在处理 JAnim 任务时，快速把问题映射到官方中文文档页面。

## 推荐入口顺序

### 初学者顺序

1. 首页：<https://janim.readthedocs.io/zh-cn/latest/>
2. 安装：<https://janim.readthedocs.io/zh-cn/latest/installation.html>
3. 入门：<https://janim.readthedocs.io/zh-cn/latest/get_started.html>
4. 动画系统：<https://janim.readthedocs.io/zh-cn/latest/tutorials/animations.html>
5. Typst：<https://janim.readthedocs.io/zh-cn/latest/tutorials/typst_usage.html>
6. GUI：<https://janim.readthedocs.io/zh-cn/latest/tutorials/use_gui.html>

### 按问题类型跳转

| 问题类型 | 先查哪里 | 关键点 |
| --- | --- | --- |
| 安装 / 环境 / 命令怎么跑 | `installation.html` | `uv add janim[gui]`、`uv run janim --version`、FFmpeg/Typst、VS Code |
| 第一个时间轴怎么写 | `get_started.html` | `from janim.imports import *`、`Timeline`、`construct()`、`forward()`、`play()` |
| 动画节奏 / 并行 / 串联 | `tutorials/animations.html` | `duration`、`at`、`rate_func`、`AnimGroup`、`Succession`、`prepare()` |
| 组件动画怎么做 | `get_started.html` + `tutorials/animations.html` | `show()`、`.anim`、组件链式调用、`.r` |
| Typst 文本 / 公式 / 嵌入 | `tutorials/typst_usage.html` | `TypstText`、`TypstMath`、`TypstDoc`、字符索引、`vars=` |
| GUI 预览 / 热重载 / 取点 | `tutorials/use_gui.html` | 时间轴、窗口位置、`janim-toolbox`、子物件选择、绘制 |
| 常用 API 从哪导入 | `janim/imports.html` | `from janim.imports import *` |
| 奇怪现象 / 常见坑 | `other/faq.html` | `TypstDoc` 黑边框、语言和系统语言不一致 |

## 当前项目最相关的事实

- 当前仓库使用 `pyproject.toml` + `uv.lock`
- 依赖中包含 `janim[gui]`
- 因此优先采用 `uv run janim ...` 风格
- 当前示例文件是 `main.py`
- 导出视频默认会落在 `videos/`

## 任务到文档的快速映射

### “我要做一个新动画”

先看：

- `get_started.html`
- `tutorials/animations.html`

重点关注：

- `Timeline` / `construct()` 的结构
- `Create`、`Transform`、`Uncreate`
- `.anim`、`duration`、`rate_func`

### “我要把数学/文字排版做好看”

先看：

- `tutorials/typst_usage.html`

重点关注：

- `TypstText` vs `TypstMath`
- 字符索引，如 `typ['cos']`
- `vars=` 与 `vars_size_unit='em'`

### “我要边改边看预览”

先看：

- `get_started.html` 的实时预览
- `tutorials/use_gui.html`

重点关注：

- `run` 与 `-i`
- `janim-toolbox`
- GUI 中的自动定位与子物件选择

### “为什么预览正常但导出失败”

先看：

- `installation.html`
- `get_started.html`
- `faq.html`

重点关注：

- FFmpeg 是否已安装并在 `PATH` 中
- 预览与导出依赖不同，不要混淆

## 本技能建议的默认命令风格

- 预览：`uv run janim run main.py`
- 指定时间轴预览：`uv run janim run main.py HelloJAnimExample`
- 导出：`uv run janim write main.py HelloJAnimExample`
- 交互重建：在预览时加入 `-i`

## 需要优先记住的概念

- `play()`：安排动画并推进时间
- `prepare()`：安排动画但先不推进时间
- `.anim`：让属性变化变成动画
- 同一个 `play()` 中的动画默认并行
- `TypstMath` 在公式环境中，`TypstText` 在文本环境中
- `from janim.imports import *` 是官方常见起手式
