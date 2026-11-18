# 实现说明

这是 v0.1 的可运行骨架，不是论文结果。三臂共用 `kbbench.budget.cap_evidence`：先按该臂自己的顺序取回，再按同一个 `limit` 和同一个字符预算截断；放不下的那条被截断，后面更短的条不会顶上来。

## 图臂

`kbbench/arms/recall.py` 复制了 nvwabase `lib/fg.py` 在提交 `c9ec790a99c01641d566e38d8d7d7e6c63a24bcc` 的 token 重叠打分（MIT）。进程内写 JSON，不调用 `fgc dispatch`。类型化事实没有加进去。

## 向量臂与笔记臂

向量臂目前只有名为 `stub-hash-v0`、32 维的确定性哈希，用来让管道和测试能跑。它不是嵌入模型，日志里必须写成这个名字。`embedding_model` 在 `config/v0.1.json` 里仍是 null。设计决定写明未选定嵌入模型时不能把向量臂当作正式实验；因此 `pipeline-check` 和 `run` 只在这个显式的 stub 上工作。笔记臂是单个 `NOTES.md`，搜索是子串。

## 模型

没有接入在线模型。环境里若设置了 `KBBENCH_MODEL`，命令会拒绝运行，而不是假装已经调过。`config/v0.1.json` 里的 `pipeline_check_placeholders` 只给 stub 管道用，不是调参结果。字符预算不是 token；轨迹里的 `token_count_source` 为 `unset_tokenizer_char_proxy`。

## Juliet

下载与校验见 [status.md](status.md)。官方压缩包放在 gitignore 的 `data/juliet/`，不提交源码。

```bash
python3 -m kbbench hash-zip --zip data/juliet/Juliet_Test_Suite_v1.3_for_C_Cpp.zip
python3 -m kbbench prepare-tasks \
  --zip data/juliet/Juliet_Test_Suite_v1.3_for_C_Cpp.zip \
  --tasks config/tasks.v0.1.json \
  --out data/tasks
python3 -m kbbench pipeline-check --config config/v0.1.json
python3 -m kbbench run --task-id t190 --arm graph --source-dir data/tasks/agent/t190
```

`prepare-tasks` 把脱敏后的 `file_1.c` 放进 `data/tasks/agent/<id>/`，把金标签放进 `data/tasks/gold/`。金标签不在 agent 目录里。

批量 stub 运行：

```bash
python3 -m kbbench batch --manifest config/batch.stub.json --config config/v0.1.json --out runs/stub-batch
```

`config/batch.stub.json` 要在 `prepare-tasks` 之后才有 `source_dir`。下面的文件是占位，路径指向 `data/tasks`。没有模型密钥时不要把 stub 的 `unknown` 答案写成结构比较。

## 官方文件抽查（2026-11-18）

抽查的是 Zenodo 压缩包里的成员，不是第三方镜像。脱敏后用泄漏词表再扫一遍。

| 官方成员 | 结果 |
|---|---|
| `CWE476_...__char_01.c` | 预处理块已去掉。残留字符串 `Good`。不进入任务清单 |
| `CWE476_...__char_51a.c` | 同上，残留 `Good` |
| `CWE476_...__char_51b.c` | 无残留，但这个文件单独没有 flawed 函数。不单独成题 |
| `CWE563_..._01_bad.cpp` / `_good1.cpp` | 残留标识符 `badClassObject` / `goodClassObject`。不进入任务清单 |
| `CWE480_...__basic_01.c` | 残留 `staticStringBad` / `staticStringGood` |
| `CWE562_...__return_buf_01.c` | 残留 `helperBad` / `helperGood1`。CWE 562 整类没有放进清单 |
| CWE 190、369、401、415、416、457 的第一条 flow-01，以及 CWE 476 的 `binary_if_01.c` | `agent_ready`，没有做字面量改写 |

因此候选清单是 7 题，写在 `config/tasks.v0.1.json`。设计文档里的 16 题拆分仍未冻结：Juliet 的 flow-01 文件同时包含有缺陷和无缺陷函数，本实现按脱敏笔记把标签做成“脱敏后的缺陷函数 id + 从原路径解析的 CWE”，而不是把文件拆成两题。
