#import "@preview/cmarker:0.1.8"

= 总结
选用 janim (#link("https://janim.readthedocs.io/zh-cn/latest/")) 作为动画生成引擎

首先使用 

`/create-skill https://janim.readthedocs.io/zh-cn/latest` 

让 Copilot 读取分析 janim 的文档， 随后调用skill

`/janim-workflow 编写动画呈现b树的构建操作、动态变化过程、查询过程`

生成可视化代码文件

向ai反馈并让其尝试修复了部分布局偏移、对象重叠的问题并成功修复。
#image("/assets/733681d4b612d1cc607b98682ccf6099.png")
Copilot根据skill自行编写代码导出了关键帧进行查看，并感知到了问题所在
#image("/assets/637e9dbc18e42a4928256c98470c094a.png")

最后手动调整了部分动画的时长、缓动这类无法被AI感知的细节问题，结束。
\
\
\
完整对话过程如下：
\
\
\

== Create Skill Step
#cmarker.render(read("../skill_process.md"))

#box(width: 100%, height: 2em, fill: gradient.linear(oklch(40%, 0.5, 30deg), oklch(81.49%, 0.252, 142.3deg)))
== Implementation Step
#cmarker.render(read("../write_process.md"))