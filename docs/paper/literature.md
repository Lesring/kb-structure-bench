# 文献笔记

供以后写相关工作时改写。每条都是 2026-11-18 打开过的页面。书目用英文；一句 takeaway 用中文，并且只复述打开文本里能指回的内容。原文里的实验数字不是本仓库的结果。

分组按论文相关工作的写法：代理记忆与分层记忆，图记忆与向量记忆，程序分析 / 漏洞发现的评价资源，黑板工作记忆。

## 1. 代理记忆与分层记忆

### Generative Agents

- **Title:** Generative Agents: Interactive Simulacra of Human Behavior
- **Authors:** Joon Sung Park, Joseph C. O’Brien, Carrie J. Cai, Meredith Ringel Morris, Percy Liang, Michael S. Bernstein
- **Year / venue:** 2023; UIST ’23. 打开的 arXiv HTML 写明 DOI 10.1145/3586183.3606763
- **URL:** <https://arxiv.org/html/2304.03442v2>
- **Takeaway:** 记忆是一条自然语言的 memory stream。检索把相关性、新近度和重要度合在一起；reflection 把经历收成更高层的推断，再写回记忆流。这是“先全量记下，再检索和摘要”的分层，不是事实—意图图。论文任务是虚拟小镇里的行为连贯，不是漏洞发现，也没有把记忆结构和其他结构做消融。

### MemGPT

- **Title:** MemGPT: Towards LLMs as Operating Systems
- **Authors:** Charles Packer, Sarah Wooders, Kevin Lin, Vivian Fang, Shishir G. Patil, Ion Stoica, Joseph E. Gonzalez
- **Year / venue:** arXiv:2310.08560v2，页面日期 2024-02-12。打开的 HTML 没有写正式会议名
- **URL:** <https://arxiv.org/html/2310.08560v2>
- **Takeaway:** 把上下文当主存，把 archival 与 recall 当外存，用函数调用换页。队列溢出时做递归摘要。文档问答实验里，归档检索用的是余弦相似度（文中为 `text-embedding-ada-002` 与 pgvector）。这证明“分页策略 + 向量外存”是一套系统；它没有把存储结构从换页策略里拆出来。本基准不把文中的嵌入模型定为我们的向量臂。

### Letta（MemGPT 之后的框架说明）

- **Title:** MemGPT Is Now Part of Letta；Agent Memory: How to Build Agents That Learn and Remember；Archival memory
- **Authors:** Letta 站点文章，未在页面上另列论文作者表
- **Year / venue:** 命名说明无单独日期（页面打开于 2026-11-18）；Agent Memory 文标 CONCEPTS — JUL 7, 2025；归档文档无期刊
- **URL:** <https://www.letta.com/blog/memgpt-and-letta/>；<https://www.letta.com/blog/agent-memory>；<https://docs.letta.com/v1-sdk/memory/archival-memory/>
- **Takeaway:** “MemGPT” 被收成设计模式，框架叫 Letta。概念文把记忆写成消息缓冲、钉在上下文里的 memory blocks、可搜索对话和归档层，并写归档可以是向量库或图数据库。本次打开的 API 文档则把归档层写成向量库：片段不能钉在窗口里，用工具按语义存取。两份材料不能合成“Letta 已经提供图归档”这一实现事实。概念文还写：检索是记忆的工具，检索本身不等于记忆。

### A-Mem

- **Title:** A-Mem: Agentic Memory for LLM Agents
- **Authors:** Wujiang Xu, Zujie Liang, Kai Mei, Hang Gao, Juntao Tan, Yongfeng Zhang
- **Year / venue:** arXiv:2502.12110。打开的 HTML 含 NeurIPS 2025 检查清单式附录，正文首页没有写“已发表于某会议”。会议状态记为未核实
- **URL:** <https://arxiv.org/abs/2502.12110>
- **Takeaway:** 新记忆被写成带上下文描述、关键词和标签的笔记，再按相似度和属性连到旧笔记；新笔记还可以改写旧笔记的上下文。这是可演化的链接笔记，边由模型在写入时决定。论文比较的是它自己的记忆系统与基线，不是“只改结构、编排不变”的协议。文中把 Mem0 一类系统描述为用图数据库做存储，本次没有打开 Mem0 原文，故不单独列 Mem0。

### Claude Code 的产品记忆（不是论文）

- **Title:** How Claude remembers your project
- **Authors:** Anthropic Claude Code 文档
- **Year / venue:** 无。2026-11-18 打开
- **URL:** <https://code.claude.com/docs/en/memory>
- **Takeaway:** `CLAUDE.md` 在不超过 4 MiB 时整文件进入会话；自动记忆只把 `MEMORY.md` 的前 200 行或前 25 KB 放进每轮，主题文件按需再读。这是扁平全文注入和“索引 + 按需文件”两种产品机制。v1 的笔记臂只借鉴前者。

## 2. 图记忆与向量记忆

### 向量 RAG（原论文）

- **Title:** Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks
- **Authors:** Patrick Lewis, Ethan Perez, Aleksandra Piktus, Fabio Petroni, Vladimir Karpukhin, Naman Goyal, Heinrich Küttler, Mike Lewis, Wen-tau Yih, Tim Rocktäschel, Sebastian Riedel, Douwe Kiela
- **Year / venue:** arXiv:2005.11401v4，页面日期 2021-04-12
- **URL:** <https://arxiv.org/html/2005.11401>
- **Takeaway:** 非参数记忆是预先建好的稠密向量索引（论文里是维基百科），生成模型条件于检索到的段落。这是“静态语料上的检索增强生成”，不是代理在工作中追加的笔记。v1 的向量臂只借用“块 + 相似度取回”，不借用这篇的训练方式和语料。

### GraphRAG

- **Title:** From Local to Global: A GraphRAG Approach to Query-Focused Summarization
- **Authors:** 打开的 arXiv HTML（2404.16130v2，2025-02-19）首页列出 Darren Edge, Ha Trinh, Newman Cheng, Joshua Bradley, Alex Chao, Apurva Mody, Steven Truitt, Dasha Metropolitansky, Robert Osazuwa Ness, Jonathan Larson，并写这些作者贡献相同
- **Year / venue:** arXiv:2404.16130v2。打开的 HTML 与仓库 README 都没有把它写成某一会议的正式版本
- **URL:** <https://arxiv.org/html/2404.16130>；实现仓库 <https://github.com/microsoft/graphrag>
- **Takeaway:** 用 LLM 从文档抽出实体图，用社区检测（文中例子为 Leiden）做层级划分，再为社区写摘要，全局问题用 map-reduce 回答。摘要写，在约一百万 token 量级的全局问题上，相对常规 RAG，答案的 comprehensiveness 和 diversity 有明显提升。优化的是对静态语料的全局问答，不是边做边写的工作记忆。仓库 README 在 2026-11-18 把项目标为维护模式。不进入 v1 运行臂。

### HippoRAG

- **Title:** HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models
- **Authors:** Bernal Jiménez Gutiérrez, Yiheng Shu, Yu Gu, Michihiro Yasunaga, Yu Su
- **Year / venue:** arXiv:2405.14831v3，页面日期 2025-01-14。打开的文本没有写会议名
- **URL:** <https://arxiv.org/abs/2405.14831>；代码链接文中为 <https://github.com/OSU-NLP-Group/HippoRAG>
- **Takeaway:** 用 LLM、知识图和 Personalized PageRank 做多跳检索。摘要报告相对当时的 RAG 方法最高约 20% 的提升，并且单步检索比文中比较的迭代检索更便宜、更快。任务是多跳问答，图是从语料抽出的关联索引，不是“意图作为边”的工作图。摘要中的百分比是原文结果，本仓库未复现。可作为以后“索引型图”的背景，不进入 v0.1。

### 代码属性图

- **Title:** Modeling and Discovering Vulnerabilities with Code Property Graphs
- **Authors:** Fabian Yamaguchi, Nico Golde, Daniel Arp, Konrad Rieck
- **Year / venue:** IEEE Symposium on Security and Privacy, 2014。打开的是会议站点 PDF
- **URL:** <https://www.ieee-security.org/TC/SP2014/papers/ModelingandDiscoveringVulnerabilitieswithCodePropertyGraphs.pdf>
- **现行说明:** Joern, Code Property Graph, <https://docs.joern.io/code-property-graph/>
- **Takeaway:** CPG 把抽象语法树、控制流和程序依赖放进同一张属性图，用遍历描述漏洞模式。论文摘要写在 Linux 内核中找出 18 个先前未知的漏洞。这是程序中间表示，不是代理的工作记忆。Joern 文档确认 2014 年的核心想法仍是这三层程序视图的合并，后来又加了别的层。若只有一臂能查询 CPG，比的是静态分析工具。v0.1 不提供 Joern。

## 3. 程序分析与漏洞发现的评价资源

这些文献用来说明**任务和标签该怎么设**，不用来充当知识库结构实验。

### Juliet 用户指南与 1.3 变更说明

- **Title:** Juliet Test Suite v1.2 for C/C++ User Guide；Juliet 1.3 Test Suite: Changes From 1.2（NIST Technical Note 1995）
- **Authors:** Center for Assured Software, NSA（用户指南，2012 年 12 月）；Paul E. Black（TN 1995，2018 年 6 月）
- **Year / venue:** 用户指南 2012；TN 1995，DOI 10.6028/NIST.TN.1995
- **URL:** <https://samate.nist.gov/SARD/downloads/documents/Juliet_Test_Suite_v1.2_for_C_Cpp_-_User_Guide.pdf>；<https://samate.nist.gov/SARD/downloads/documents/Juliet_1.3_Changes_From_1.2.pdf>
- **Takeaway:** 用例为静态分析工具而设计，每个用例针对一种缺陷，并通常带有一个不做该缺陷的对照构造。用户指南写明频率不像自然代码，因此工具在用例上的假阳性不能直接当成自然代码上的假阳性。TN 1995 写 C/C++ 1.3 有 64 099 个用例，独立套件仍附带 1.2 的 CAS 文档，目录按 `CWE338_Weak_PRNG` 这样的名字组织。命名和注释如何泄题，以及本仓库抽查到的一个文件，写在 [juliet-sanitization.md](juliet-sanitization.md)。

### PrimeVul

- **Title:** Vulnerability Detection with Code Language Models: How Far Are We?
- **Authors:** 打开的 arXiv HTML 与仓库 README 的 bibtex 一致：Yangruibo Ding, Yanjun Fu, Omniyyah Ibrahim, Chawin Sitawarin, Xinyun Chen, Basel Alomair, David Wagner, Baishakhi Ray, Yizheng Chen
- **Year / venue:** arXiv:2403.18624。仓库 README 写已被 ICSE 2025 接收；本次在 arXiv HTML 中检索会议名，没有看到这篇自身的会议归属，故会议信息只记 README 的说法
- **URL:** <https://arxiv.org/html/2403.18624>；数据仓库 <https://github.com/DLVulDet/PrimeVul>
- **Takeaway:** 论文认为既有漏洞数据集有标签噪声、重复和泄漏，并给出 PrimeVul：文中为 6,968 个有缺陷函数与 228,800 个良性函数、140 个 CWE（README 的约数与此同向，但不是同一个写法）。切分按提交时间，同一提交不跨集合。摘要中的例子是 StarCoder2 在 BigVul 上 68.26% F1、在 PrimeVul 上 3.09% F1。对我们有用的是评价教训：随机切分和重复样本会抬高检测分数；配对的漏洞/修补函数能暴露模型只看表面文本。这不是知识库结构实验。v0.1 仍不用它，原因见设计文档：数据在网盘、CVE 描述和提交说明可能泄题、本次没有下载文件。

### OWASP Benchmark

- **Title:** OWASP Benchmark（项目页与 BenchmarkJava README，不是一篇论文）
- **Authors:** 项目页列出负责人 Dave Wichers。本次没有打开一篇以该基准为主题的学术论文
- **Year / venue:** 仓库与项目页称最新版 v1.2
- **URL:** <https://owasp.org/www-project-benchmark/>；<https://github.com/OWASP-Benchmark/BenchmarkJava>
- **Takeaway:** 可运行的 Java 测试应用，用来衡量检测工具的速度和准确度；页面写明被计入分数的缺陷意图是可利用的。`expectedresults-1.2.csv` 有表头“测试名、类别、是否真缺陷、CWE”，共 2740 条数据行。类别名会出现在表里，抽到的前两行类别为 `pathtraver`。适合作为以后的带金标签的检测任务，不适合在 v0.1 里运行应用。`LICENSE` 文件开头是 GNU GPL v2 文本，全文是否另有例外本次没有通读。

### Magma

- **Title:** Magma: A Ground-Truth Fuzzing Benchmark
- **Authors:** Ahmad Hazimeh, Adrian Herrera, Mathias Payer
- **Year / venue:** Proc. ACM Meas. Anal. Comput. Syst., Vol. 4, No. 3, Article 49, December 2020. DOI 10.1145/3428334。另有 arXiv:2009.01120
- **URL:** <https://hexhive.epfl.ch/publications/files/21SIGMETRICS.pdf>；项目页 <https://hexhive.epfl.ch/magma/>
- **Takeaway:** 把真实缺陷放进真实程序，并用插桩区分 reached 与 triggered，从而不靠崩溃去重来评价模糊测试。论文摘要写的是七个目标；2026-11-18 打开的项目页列出九个库（libpng、libsndfile、libtiff、libxml2、lua、poppler、openssl、sqlite3、php）。两者不要写成同一清单。它衡量的是模糊器有没有碰到缺陷，不是知识库能否交接结论。

## 4. 黑板 / 事实—意图工作记忆

### Cairn

- **Title:** 仓库 README；公众号《国内最强 AI 渗透测试 Agent —— …唯一 AK 战队复盘》；公众号《无径之径：Cairn AI 从渗透测试到通用问题的求解》
- **Authors:** 仓库为 oritera/Cairn。两篇公众号为作者自述，页面署名风格是第一人称，本次没有另见学术论文作者表
- **Year / venue:** 无学术会议版本。README 与两篇公众号于 2026-11-18 打开
- **URL:** <https://github.com/oritera/Cairn>；<https://mp.weixin.qq.com/s/DlpEH7bVr0xi0VawPJs3XA>；<https://mp.weixin.qq.com/s/2rEqFLvkxvYWM3gW170C2w>
- **Takeaway:** README 定义黑板三原语 Fact、Intent、Hint，工人只通过板协调，没有固定角色。这和 nvwabase 的事实—意图图是近亲，但是整套 Server / Dispatcher / 容器。复盘文写比赛系统反对传统 RAG 和按阶段拆开的多代理，除 flag 提交外没有 Skill、MCP 或 RAG 知识库，并写第四天晚上做过人工复盘后第五天才 AK。排名自述互相不一致：README 表为第 3；复盘文写动态计分下唯一 AK 仍是第 4；《无径之径》写最终总成绩全国第 3。因此这些名次不能进论文的结果，只能作为“作者认为黑板可以不靠 RAG 完成一场比赛”的未核验自述。没有找到 Cairn 的同行评审论文。

### nvwabase 与 sapper-v2

书目和代码级 takeaway 已在 [../01-nvwabase.md](../01-nvwabase.md)，不在这里重写。论文相关工作只需要一句：nvwabase `lib/fg.py` 在提交 `c9ec790a99c01641d566e38d8d7d7e6c63a24bcc`（2026-11-11）上是无类型的三层事实—意图图；类型化事实在 sapper-v2 的 `lib/sapper.py`。设计长文 <https://mp.weixin.qq.com/s/nibHYWmDTf6TkNhPhtvFdw> 把分层解释成对“单字符串事实”的替换，并给出比赛自述。该文不是对照实验。

## 5. 写相关工作时不要做的事

- 不要把上述论文的 F1、提升百分比或 CPU 小时写进我们的结果表。
- 不要把未打开的 Mem0、BigVul、DiverseVul 论文写成我们读过。PrimeVul 论文里对它们的转述，只能写成“Ding 等人如此描述既有数据集”。
- 不要把 HippoRAG 或 GraphRAG 的实体图写成事实—意图图。边的含义不同：前者连接抽取出的实体，后者连接“已确认的观察”和“待做的工作”。
