# nvwabase：核对后的笔记

结论先写在这里。2026-11-18 对照的 `master` 上，[nvwabase](https://github.com/N1nEmAn/nvwabase) 交付的是一张**项目内、分层的事实—意图图**，外加 Claude Code 钩子和子代理派发。安装脚本还会装一个 `nvwa` 命令，用 tmux 起代理、给代理发文字。它是长周期多智能体的外置工作记忆，不是从文档里抽取实体的传统知识图谱。

另一件必须分开的事：**渗透用的类型化事实不在当前的 `lib/fg.py` 里。** `host / service / cred / vuln / loot / flag / note` 和 `-d key=value` 实现在 [sapper-v2](https://github.com/N1nEmAn/sapper-v2) 的 `lib/sapper.py`。nvwabase 的中英文 README 把这组命令写在自己的功能列表里，和代码不一致。下面分“代码里有的”和“文档写了、代码里没有的”。

比赛成绩是 sapper-v2 与公众号长文的自述。它们描述一场攻防赛，不描述一次只改变知识库结构的实验。

核对时的仓库事实（GitHub API，2026-11-18）：默认分支 `master`，语言 Python，许可证 MIT，homepage 指向 sapper-v2。`lib/fg.py` 文件头的版本号是 `0.2.0`。

## 1. 仓库自己怎么定位

中文 README 的首句把本仓称为“面向长周期多智能体协作的分层事实意图图谱工作记忆”，并声明纯标准库、零依赖、按项目启用。英文 README 有一段“诚实的作用域”：本仓交付历史支柱（通用分层事实意图图、项目级钩子、子代理派发）；造人与语言的完整编排在 sapper-v2 的战场层，路线图再抽成通用运行时。

同一份英文 README 的快速开始，以及仓库里的 `nvwa` 脚本，已经实现了 `nvwa spawn` / `nvwa say` / `nvwa listen`。`install.sh` 在 `./nvwa` 存在时把它链接到 `~/.local/bin/nvwa`，并把 `lib/fg.py` 链接为 `fgc`。因此“完整编排仍只在 sapper-v2”和“本仓已经有一个 tmux 版造人/语言命令”两句话同时出现在当前树上。本笔记两句都保留，不替作者选一个。

`nvwa` 脚本头注释写明：图命令转发给 `fgc`，底层是 tmux（`send-keys -l` 写、`capture-pane` 读）。默认会话名 `nvwa`，默认代理命令 `claude`，`NVWA_MAX_WORKERS` 默认 8。

作者在中英文 README 里感谢 [Cairn](https://github.com/oritera/Cairn)（淚笑）：需要给 AI 记历史时参考了他们的思路。Cairn 的模型见 [02-related-work.md](02-related-work.md)。

`SKILL.md` 还写了一句更早的来源：fact graph 是 StarVoya `Star` 后端思路的提炼，StarVoya 被描述成约 9600 行、带 SQLite 和调度器的系统。本次没有打开 StarVoya 的仓库，所以不对那句做核实，只记 `SKILL.md` 如此写。sapper-v2 的 `SKILL.md` 则把自己称为 `claude-fact-graph/fgc` 的分支。nvwabase `CHANGELOG.md` 写过：2026-09-24 查询 `N1nEmAn/claude-fact-graph` 的 Issues / PR / Releases API 得到零条记录。那份旧仓库本次没有打开。

## 2. 事实—意图模型

`lib/fg.py` 模块文档写明：

- 事实是节点，意图是超边。
- 意图的 `from` 是它依赖的事实 id 列表；`to` 是它产生的事实，未完成时为 `null`。
- 特殊事实 `goal` 表示终点。存在一条指向 `goal` 的意图时，项目完成。
- 状态编码在图结构里，而不是一台独立状态机里。
- 存储是项目本地 `.fg/` 下每个节点一个 JSON 文件。

`add_fact` 写入的字段是 `id`、`title`、`description`、`doc`、`created_at`、`creator`、`source_intent`。没有类型字段，没有 `data` 字典。

`add_intent` 写入 `id`、`title`、`from`、`to`、`description`、`doc`、`creator`、`status`、`worker`、`requires_confirmation`、`confirmed_at`、`created_at`、`concluded_at`。`status` 初始为 `"open"`。就绪判断 `is_ready` 看的是：意图仍开放（`to is None`）、`from` 里的事实都还在、以及需要确认的意图已经确认。所以“开放/完成”主要由 `to` 表达，同时 JSON 里又有一个 `status` 字段。文档说的“没有独立状态机”和代码里的 `status` 字段并存；比较结构时以 `to` / `from` / 确认位为准，不要把 `status` 字符串当成另一套状态机已经测过。

`goal` 在 `init` 时写成一个事实，字段只有 `id`、`description`、`created_at`、`creator`、`source_intent`。

还有第三类对象 `hint`：人写给指挥官的短消息。`dispatch blindspot` 也会把模型指出的盲点写成 hint（`lib/fg.py` 的 `_apply_blindspot`）。

## 3. 三层记忆

代码和 README 一致的部分是三层，不是两个同义词：

| 层 | 字段 | 谁看得到 |
|---|---|---|
| 标题 | `title` | 图视图、钩子里的历史行、`fgc recall` |
| 摘要 | `description` | 同上；写事实时的必填位置参数 |
| 证据文档 | `doc` | 默认不进提示词。`fgc doc <id>` 读取；`--set` / `--set-file` / `--edit` 改写 |

`render_prompt` 的注释写明：给模型的图只含 title 和 description，带 `(has doc)` 标记，详细层要用 `fgc doc <id>` 另读。`lib/fg-hook.py` 的 `UserPromptSubmit` 在图已存在时注入状态，正文截断上限是 6000 字符，超出后提示去跑 `fgc graph`。注入块包含 `render_status` 和 `render_history_block`。历史块默认最近 8 条事实和 4 条已完成意图，描述截到 90 字符，只在有 `doc` 时打一个标记。钩子还要求：历史看起来相关就去 `fgc doc`，不明显时跑 `fgc recall`。

`recall` 的实现注释写得很明确：对 title（计两次）和 description 做 token 重叠，辅以 `difflib`；重叠为 0 时，序列相似度低于 0.45 则记 0。中文按字切开。**没有嵌入，没有向量库。** 中文 README 写的是“零依赖 token 重叠打分”，和代码相符。英文 README 写的 “semantic search” 比代码更强，本笔记以 `lib/fg.py` 为准。

`SKILL.md` 的命令表没有 `doc` 和 `recall`，并写“事实一旦写下即不可变”。代码里 `description` 没有通用的改写接口；`update_doc` 可以改事实或意图的 `doc`，并带期望值，避免盲目覆盖。`render_history_block` 的注释仍写 “facts are immutable”。准确说法是：摘要层按当前接口是追加的，文档层可以更新。`SKILL.md` 落后于 `lib/fg.py`。

## 4. 类型化事实：文档与代码

nvwabase 中文 README 第 3 节写：

> `fgc fact ... -k host/service/cred/vuln/loot/flag/note -d key=value`（渗透模式；通用场景可不带类型）

`nvwa` 的用法注释也有 `nvwa fact "..." -k note`。

当前 `lib/fg.py` 的 `fact` 子命令参数是 `description`、`--title` / `-t`、`--doc`、`--doc-file`、`--creator`、`--from-intent`、`--json`。没有 `-k`，没有 `-d`。`recall` 的 `--kind` 只接受 `fact`、`intent`、`any`，表示节点种类，不是渗透类型。

sapper-v2 `lib/sapper.py` 模块文档写明它是 “Offensive specialization on top of fgc”，并定义：

```text
FACT_KINDS = ("host", "service", "cred", "vuln", "loot", "flag", "note")
```

`add_fact` 在那里接受 `kind` 和 `data`。存储目录是 `.sapper/`，安装出的命令是 `sapper`（`install.sh` 把 `lib/sapper.py` 链到 `~/.local/bin/sapper`）。sapper 的 `SKILL.md` 用 `sapper fact -k service -d host=... -d port=...` 作为类型化事实的例子。

因此：工作笔记里的“类型化事实”是 sapper 分支上的事实，不是 2026-11-18 的 nvwabase `fgc` 行为。若基准要比较“无类型三层图”和“带 kind/data 的图”，这是同一拓扑上的模式差异，而且今天它们分属两个 CLI。

## 5. CLI 与工作流

`install.sh` 不写全局 Claude 配置。进某个项目要执行 `fgc setup --goal "..." --agents`（或 `nvwa` 转发的同一子命令）。它在该项目建立 `.fg/`，把钩子写进 `./.claude/settings.json`，并可写 `AGENTS.md`。`fgc teardown` 只删除 fgc 生成的 `AGENTS.md`；`--purge` 才删图。`CHANGELOG.md` 0.2.0（文内日期 2026-09-24）记录了这些边界，并指向 `tests/test_fg.py`。本次没有运行这套测试。

图命令（均在 `lib/fg.py` 的 argparse 中）：`init`、`status`、`graph`、`validate`、`frontier`、`pick`、`fact`、`intent`、`hint`、`peers`、`send`、`capture`、`show`、`doc`、`recall`、`claim`、`release`、`done`、`complete`、`confirm`、`dispatch`、`brainstorm-pick`、`setup`、`teardown`、`view`、`auto`。

`dispatch` 的目标：

| 目标 | 行为 |
|---|---|
| `reason` | 渲染 `templates/reason.md`，调用 `claude`，把返回的意图写回图 |
| `<intent-id>` | 探索该意图（`explore.md`），写回产生的事实 |
| `verify` | 检查已完成意图的事实 |
| `brainstorm` | 生成多个待确认选项 |
| `blindspot` | 盲点写成 hint |

默认 `--model` 来自 `FG_MODEL`，否则 `sonnet`；默认超时 `FG_TIMEOUT` 或 600 秒。`auto` 循环是 reason → explore，可选 `--verify`；默认 `--max-steps 8`、`--max-explore 6`。停止条件在 `SKILL.md` 里写成：目标完成、reason 连续两次 noop/rejected、一步之内图没有变化、或步数/探索预算用尽。

`view` 生成自包含 HTML，或 `--serve` 在本机刷新。默认绑定 `127.0.0.1:8765`。

并发方面，写路径拿 `.fg/.lock` 的 `fcntl.LOCK_EX`，JSON 用同目录临时文件加 `os.replace`。这是“一次写坏不了单个文件”的实现，不是语义冲突检测。两个代理可以先后写入互相矛盾的事实；`fgc validate` 查的是模式、悬空引用、重复 id、目标事实是否和项目目标一致，不查两句话是否矛盾。

`SKILL.md` 有一段提示注入说明：派发执行者时，整张图的描述会进提示词；防御是把图标成不可信数据。它明确这是文本约束，不是沙箱，并警告不要对不可信的 `.fg/` 使用 `fgc auto --skip-permissions`。基准若用真实代理跑这张图，这条要算进威胁，而不是当成已解决。

## 6. 在 sapper-v2 里怎么用

sapper-v2 不是“调用 nvwabase 包”的薄封装。它带自己的 `lib/sapper.py`（2026-11-18 约 4700 行）、自己的 `.sapper/` 存储和 `sapper` 命令。英文 README 在介绍基座时，示例命令写成 `nvwabase setup` / `nvwabase fact`。nvwabase 的 `install.sh` 不安装名为 `nvwabase` 的可执行文件。这是 sapper README 与 nvwabase 安装脚本之间的命名差，本次没有在机器上安装任何一方来运行它。

sapper 在图之外还有一个离线知识库：`lib/kb.py` 说明每条是 `kb/entries/kbNNN.json`，字段包括 `title`、`description`、`detail`、`commands`、`tags`、`source`，搜索同样是 title 加权的 token 重叠。默认根目录是仓库里的 `kb/`，可用 `SAPPER_KB_ROOT` 覆盖。这是另一份静态资料，不是 `.sapper/` 里的工作图。本笔记不摘录条目正文。

英文 README 与公众号长文把图的用法说成：知识沉到分层事实图里；个体会话可以结束，后继者读图接上。长文还把早期“单一字符串事实图”的失败写成两点：一个错误事实污染下游，以及长字符串本身消耗上下文；分层之后先看标题，再下钻证据。这和现在 `fg.py` 的三层设计同向。长文没有给出只切换这一层、其余不变的对照数据。

README 与长文中的战役叙述（均为作者自述，本仓库未核验）包括：第三届腾讯云智能攻防挑战赛线上赛，634 支队伍，8 小时无人值守，分数 80.18，85 个 flag；英文 README 的表里第二名 79.29 分、同样 85 个 flag、4.5B token，sapper-v2 为 1.0B token。中文 README 写“10 亿 token”。公众号长文写 token 为 10.3 亿对 45 亿。同一叙述里的 token 数目并不相同。长文还提到一份未在本次打开的 V-Mesh 材料；该数字不进入本仓库的引用。

README 把省 token 同时归因于模型分层（指挥官/将军与士兵/侦察用不同模型）、调度和“只给精简知识库”。这些因素和图结构绑在一起。所以 sapper-v2 可以说明这张图被用在一场长周期多智能体战役里，不能说明图结构优于向量库或扁平笔记。

## 7. 局限，以及对公平比较必须拆开的部分

若把“nvwabase 式事实—意图图”放进基准，下面这些不能算进结构本身：

1. **类型化模式。** 它在 sapper，不在当前 `fgc`。v1 的图臂应固定为无类型的 title / description / doc，除非单独立项比较 kind/data。
2. **召回算法。** token 重叠是这个实现的检索器。换一种结构时，检索器也会变。比较时要写明：图臂的搜索就是这段重叠打分，向量臂的搜索是嵌入，扁平臂的搜索是线性扫描或全文交给模型。不要把“结构”说成已经排除了检索器。
3. **派发循环、默认模型和模板。** `dispatch` / `auto` 会调用 `claude` 并使用仓库里的提示模板。基准的代理循环必须在结构之外，三臂共用，否则比的是模板和调度。
4. **钩子注入的具体截断（6000 字符、8 条事实）。** 这是上下文策略。公平比较要把“每轮注入预算”定成同一个数，而不是沿用某一臂的默认值。
5. **`nvwa` 的 tmux 造人与说话。** 那是运行时。结构实验里代理数量和通信方式要另定，不能只有图臂能派子代理。
6. **sapper 的离线 `kb/`、竞技场接口、flag 账本、教令。** 全部在结构比较之外。基准任务也不使用 flag 提交或利用步骤。
7. **文档与代码漂移。** `SKILL.md` 的命令表、英文 README 的 “semantic search”、中英文 README 的 `-k`，都不能当作 `fgc` 的当前行为。引用实现时指向 `lib/fg.py`。

本仓库还没有把 `fgc` 接到任何基准驱动上，也没有测量过锁在多进程下的等待时间。
