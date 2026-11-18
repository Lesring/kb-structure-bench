# 论文大纲（未成稿）

这是以后写文章时用的骨架，不是已经有结果的论文。每一节只指向仓库里已经写下来的材料。没有实验数字可以填进“结果”。

工作题目（暂定，可改）：知识库结构是否决定长周期代理在程序分析中的交接质量与上下文开销。

## 1. 问题与贡献

写什么：长周期、可换人的代理工作里，外置记忆的**结构**是不是自变量；下游任务用漏洞发现来测量记忆质量，而不是测量攻击是否成功。

材料：

- 研究问题和计划中的贡献：[claims-and-scope.md](claims-and-scope.md)
- 仓库目前的公开说法：[../README.md](../README.md)
- 为什么 sapper-v2 / Cairn 的比赛叙述回答不了这个问题：[claims-and-scope.md](claims-and-scope.md) 第 3 节，以及 [../01-nvwabase.md](../01-nvwabase.md) 第 6 节

本节在有结果之前只能写“我们打算测量什么”。不能写“我们发现某种结构更好”。

## 2. 相关工作

写什么：按记忆结构分组，而不是按产品时间线堆砌。每篇只保留和“结构作为自变量”有关的一句，分数留在原文。

材料：

- 可直接改写成相关工作的笔记：[literature.md](literature.md)
- 哪几种结构进入 v1、哪些只作背景：[../02-related-work.md](../02-related-work.md) 第 7 节

分组已经定在文献笔记里：分层/代理记忆，图与向量，程序分析与漏洞发现的评价资源，以及黑板图这一支（Cairn、nvwabase）。

## 3. 方法 / 基准设计

写什么：三臂、同一套工具、同一预算；图臂是冻结的字段适配器，不是上游 `fgc dispatch`。

材料：

- 接口、任务、指标、协议：[../03-benchmark-design.md](../03-benchmark-design.md)
- 已经做成决定、但仍不是结果的部分：[design-decisions.md](design-decisions.md)
- 图的字段以哪一次源码阅读为准：[../01-nvwabase.md](../01-nvwabase.md)，提交号写在设计决定里

方法节要写明：比较的是“结构加上该结构自带的读取方式”。检索器还没有被拆成单独因素。

## 4. 实验方案

写什么：v0.1 的样本、脱敏、交接、失败如何计分。方案可以写进论文的“实验设置”，结果表留空。

材料：

- 样本与指标：[../03-benchmark-design.md](../03-benchmark-design.md) 第 4–6 节
- Juliet 如何取得、哪些名字和注释会泄题、跑之前要核对什么：[juliet-sanitization.md](juliet-sanitization.md)
- 模型、`B_inject`、步数仍待定；选定模型后的清单：[design-decisions.md](design-decisions.md) 第 4 节

本节不要出现虚构的准确率或 token 节省。

## 5. 讨论与局限

写什么：合成数据、泄题、地板效应、结构与检索器缠在一起、比赛自述不能外推。

材料：

- 效度威胁：[../03-benchmark-design.md](../03-benchmark-design.md) 第 7 节
- 不声称的清单：[claims-and-scope.md](claims-and-scope.md)
- 文献里已经证明“漏洞检测数字可以被数据泄漏抬高”的工作，只用来说明评价必须防泄漏，不用来代替我们自己的实验：[literature.md](literature.md) 的 PrimeVul 条

## 还缺、因此还不能投稿的东西

- 选定的模型与冻结的预算
- 官方 Juliet 压缩包的校验和抽查记录（见脱敏笔记；第三方单文件不能代替）
- 任何一次按协议跑完的轨迹
- 向量臂的嵌入模型
