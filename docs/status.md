# 状态日志

只记本仓库自己做过的事。不记未运行的实验，不记来源里未核对的数字。

## 2026-11-18

- 仓库此前只有一行标题 `kb-structure-bench`（`main` 上的初始提交）。本次写入研究笔记和 v1 设计，没有基准实现。
- 对照阅读了 nvwabase `master` 的 README（中/英）、`SKILL.md`、`CHANGELOG.md`、`install.sh`、`nvwa`、`lib/fg.py`、`lib/fg-hook.py`，以及 sapper-v2 的 README、`install.sh`、`SKILL.md`、`lib/sapper.py` 文件头与事实类型常量、`lib/kb.py` 的存储说明。
- 阅读了设计长文《女娲测试及其理论：Sapper-v2 的原理》（公众号，2026-11-18 打开）。文中的比赛数字按原文记录，未独立核验。文中提到的 V-Mesh 白皮书本次没有打开，因此不引用其中的成功率。
- 相关工作和候选数据集只收录本次实际打开过页面或仓库文件的来源，列表见 [references.md](references.md)。
- 已知的文档/代码不一致已经写进 [01-nvwabase.md](01-nvwabase.md)，不在 README 里抹平。

## 2026-11-18（论文笔记）

- PR #1 以 squash 提交 `102884db128807755746142849dedc458f2439c6` 进入 `main`。本轮从该提交之后的 `main` 开工，不改写已合并笔记的结论。
- 新增 `docs/paper/`：大纲、主张与范围、文献笔记、Juliet 脱敏、v0.1 设计决定。仍无基准实现，无实验结果。
- 新打开的主要来源包括 Juliet 1.2 用户指南、NIST TN 1995、PrimeVul 的 arXiv HTML、Magma 论文 PDF、Generative Agents、HippoRAG、A-Mem，以及 Cairn 的两篇公众号。书目见 [references.md](references.md) 与 [paper/literature.md](paper/literature.md)。
- Cairn 的名次自述不一致：README 为第 3，一篇复盘写动态计分下为第 4，另一篇写全国第 3。这不是对旧笔记的更正（旧笔记只转述 README），而是不能把名次写进论文结果的附加理由。
- 图臂决定为冻结适配器，字段对照 nvwabase 提交 `c9ec790a99c01641d566e38d8d7d7e6c63a24bcc`。没有下载 Juliet 官方 zip（约 146–153 MB）；脱敏协议依据用户指南，并用第三方仓库中的一个 CWE476 文件做了模式抽查。该镜像 README 写明改过部分 `bind()` 调用，不能代替官方包校验。

## 2026-11-18（v0.1 骨架）

- PR #2 已 squash 合并为 `c0b737e4293e1c083fc8b448f697e3e6fdf5612b`。本轮从该提交后的 `main` 实现三臂骨架，没有改写设计文档的结论。
- 从 Zenodo 记录 <https://zenodo.org/records/4701387> 下载 `Juliet_Test_Suite_v1.3_for_C_Cpp.zip`。本机计算的 sha256 是 `ada9d7e1c323d283446df3f55bdee0d00bda1fed786785fe98764d58688f38eb`，文件大小 152957342 字节。这与 SARD 套件 112 页面公布的 sha256 相同。SARD 页面写 146 MB，Zenodo 页面写 153.0 MB；摘要一致，因此视为同一文件，没有因为两种十进制写法而停。直接试过的 `samate.nist.gov` zip URL 返回 404，所以文件来源是 Zenodo，校验对象是 SARD 页面上的摘要。
- 用官方包做了抽查，不是第三方镜像。候选清单是 7 个 `agent_ready` 的 flow-01 文件，见 `config/tasks.v0.1.json`。CWE 562 和带 `Good` 字面量或 `badClassObject` 的文件被排除，没有改写这些字面量。
- 跑了 stub 模型：合成夹具上的 `pipeline-check`（3 臂），以及 7 题 × 3 臂 × 1 次。答案都是脚本写死的 `unknown`。没有在线模型，没有论文数字。轨迹在 gitignore 的 `runs/`，不提交。
- 模型、真实嵌入模型、`B_inject` 的正式取值、16 题拆分，仍然待定。设计决定第 4 节的清单还没有填。
