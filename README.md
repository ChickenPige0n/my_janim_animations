# Janim 动画仓库

## 初始化：
如未安装 [uv](https://docs.astral.sh/uv/) ：
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
安装项目依赖：

```bash
uv sync
```

## 运行：

安装 [janim-toolbox](https://marketplace.visualstudio.com/items?itemName=jkjkil4.janim-toolbox)

```bash
uv run janim run .\btree_visualization\main.py -i
```
按下 ctrl + j, ctrl + c

## 导出视频：

```bash
uv run janim write .\btree_visualization\main.py 
```

## AI使用历史
./github/skills/janim-workflow 存放生成的Janim skill

./ai_interaction_log 存放历史对话内容

This README is written by human.