# kb-structure-bench

这个仓库跟踪一件还没有被测清楚的事：长周期、多智能体工作里，**知识库的结构**是否决定效果和开销。下游任务用来衡量知识库质量，范围是程序分析与漏洞发现（判断、定位、关联、交接），不包括编写利用代码或攻击步骤。

当前状态：**设计与文献笔记，没有实验，没有实现，没有结果。** 任何数字如果出现，都是来源里的原话，或是本仓库明确标成“待定参数”的设计选择。

## 为什么先看结构

长周期工作会把上下文撑满。会话结束、代理换人之后，后继者能用的只剩外置记忆。记忆怎么组织，会同时影响三件事：找不找得到先前的结论，结论和证据还在不在，以及每轮塞进上下文的 token 有多少。

[nvwabase](https://github.com/N1nEmAn/nvwabase)（女娲基座）把这件事做成一张分层的事实—意图图，并在 [sapper-v2](https://github.com/N1nEmAn/sapper-v2) 的比赛复盘里把图当作共享历史。那些复盘是一场战役的自述，混杂了编排、模型分层、教令和知识库结构。它们不能代替本仓库要做的对照实验。细节和出处见 [docs/01-nvwabase.md](docs/01-nvwabase.md)。

## 仓库地图

| 路径 | 内容 |
|---|---|
| [docs/01-nvwabase.md](docs/01-nvwabase.md) | 对照源码核对后的 nvwabase / sapper-v2 笔记 |
| [docs/02-related-work.md](docs/02-related-work.md) | 已打开来源的相关结构，以及谁进入 v1 |
| [docs/03-benchmark-design.md](docs/03-benchmark-design.md) | v1 设计（设计，不是结果） |
| [docs/references.md](docs/references.md) | 本仓库引用过的 URL |
| [docs/status.md](docs/status.md) | 日期日志 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 怎样追加来源和设计，而不写成未做的实验 |

## 准备怎样评

v1 只比较少数几种**可以接到同一套读写接口**上的结构。设计里的第一组是：nvwabase 式事实—意图图、会话中可写的向量分块、带长度上限的扁平 markdown。模型、工具、任务、每轮注入预算保持相同，变的是结构。任务从带公开标签的程序集里取样，标签放在代理看不见的地方。指标同时记有效性（判断、完整性、证据是否忠于原文）和效率（token、时延、取回的上下文大小），并单独定义交接、并发写和自相矛盾怎么记。测量方法写在设计文档里；本仓库还没有跑过。

## 现在还不声称的事

- 没有哪种结构更好。没有分数、没有 token 节省比例、没有统计检验。
- sapper-v2 与 Cairn 的比赛名次、flag 数、token 数是项目自己的叙述。本仓库没有独立核验，也不把它们当成结构优劣的证据。
- nvwabase 中文/英文 README 里的“类型化事实”命令，和当前 `master` 上的 `lib/fg.py` 不一致。类型化事实目前在 sapper-v2 的 `lib/sapper.py`。见笔记。
- 本仓库不提供漏洞利用、PoC 或攻击步骤。

## 下一步

最小的有信息量的一步是设计文档里的 **v0.1**：在剥离了标签泄漏的一小撮 Juliet C/C++ 1.3 用例上，跑“写入会话 + 只读知识库的交接”，三臂共用同一接口。开工前还要定的参数和未决问题列在 [docs/03-benchmark-design.md](docs/03-benchmark-design.md) 末尾。
