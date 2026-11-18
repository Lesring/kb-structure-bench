# Juliet 脱敏笔记

结论：Juliet C/C++ 1.3 可以做 v0.1 的金标签来源，但**目录名、文件名、函数名和文件头注释会把 CWE 与 good/bad 直接交给模型**。官方用户指南把这套命名写成设计的一部分，不是偶然。本次没有下载 SARD 上 146 MB / Zenodo 上 153 MB 的官方压缩包。下面的协议来自官方文档，并用一个第三方仓库里的单个文件做了模式抽查。抽查文件不能代替官方包的校验。

## 1. 怎样取得官方数据

2026-11-18 打开的页面：

- SARD 套件 112：<https://samate.nist.gov/SARD/test-suites/112>。语言 C++，64,099 个用例，118 个 CWE，146 MB，提交日 2017-10-01。页面给出的 sha256 为 `ada9d7e1c323d283446df3f55bdee0d00bda1fed786785fe98764d58688f38eb`。许可文字：在美国不受版权保护、属于公有领域；NIST 可主张外国权利的范围内以 CC0 1.0 提供。
- 文档目录：<https://samate.nist.gov/SARD/documentation>，其中 Juliet 文档链到下面两份 PDF。
- 用户指南（v1.2，2012 年 12 月，CAS / NSA）：<https://samate.nist.gov/SARD/downloads/documents/Juliet_Test_Suite_v1.2_for_C_Cpp_-_User_Guide.pdf>。NIST TN 1995 写明 1.3 的独立套件仍包含这份 1.2 文档。
- Paul E. Black，*Juliet 1.3 Test Suite: Changes From 1.2*，NIST Technical Note 1995，2018 年 6 月，DOI 10.6028/NIST.TN.1995：<https://samate.nist.gov/SARD/downloads/documents/Juliet_1.3_Changes_From_1.2.pdf>。C/C++ 部分 64 099 个用例。每个 CWE 一个目录，例如 `CWE338_Weak_PRNG`；超过一千个文件时再分 `s01`、`s02`。
- Zenodo 上的 1.3 压缩包记录：<https://zenodo.org/records/4701387>，DOI 10.5281/zenodo.4701387，文件 `Juliet_Test_Suite_v1.3_for_C_Cpp.zip`，页面写 153.0 MB。本次没有下载。

跑实验之前必须：下载上述官方 zip 之一，核对 SARD 页面上的 sha256（Zenodo 页面另给了 md5，两套校验值都要记在 `docs/status.md` 里，不一致就停），再从解压结果里抽查，而不是从第三方镜像抽查。

## 2. 官方文档已经写明的泄漏点

用户指南第 3 节和第 4 节把名字当成用例结构。和脱敏相关的规则如下。

**路径和文件名。** 每个文件对应一个 CWE。名字包含 CWE 编号、缩短的 CWE 名称、功能变体和流变体编号。指南中的例子是 `CWE476_NULL_Pointer_Dereference__char_01.c`。多文件用例用 `a`/`b` 或 `_bad`/`_good1` 区分。TN 1995 的目录例子是 `CWE338_Weak_PRNG`。只改文件名、留下目录名，标签还在。

**函数名（非类缺陷，指南 4.1）。** C 的主缺陷函数是“用例名 + `_bad`”，主对照函数是“用例名 + `_good`”。指南给出的正则是 `^(CWE.*_)?bad$` 与 `^(CWE.*_)?good$`。次级对照函数名为 `goodG2B`、`goodB2G` 或 `good1` 等，正则 `^good(\d+|G2B\d*|B2G\d*)$`。可选的 helper / source / sink 使用 `helperBad`、`BadSource`、`BadSink`、`goodG2BSource`、`goodB2GSink`，跨文件时函数名还会再带上整段 CWE 用例名。

**C++ 类缺陷（指南 4.2）。** 文件名以 `_bad` 或 `_good1` 结尾。类名是 `BadClass` 或 `GoodClass`（以及 Base/Derived 变体）。

**注释。** 指南用 BadSource、GoodSource、sink、flaw、non-flaw 描述构造。它没有把“删除注释”当作发布形式。因此协议必须假设源文件里有这些词，并用抽查确认，而不是假设只有文件名有问题。

**SARD 网页本身也会泄题。** 打开的用例页 <https://samate.nist.gov/SARD/test-cases/61940> 在描述里写了 “CWE: 114”、“BadSource”、“GoodSource”、“BadSink”。这个页面不能放进代理可读目录。

**用户指南自己的效度警告（第 1 节）。** 用例里每种缺陷出现的频率不像自然代码；两个工具在用例上结果接近，在自然代码上仍可能差很多。论文里的 Juliet 结果不能写成真实漏洞分布上的结果。

## 3. 单文件抽查（第三方副本，不是官方包）

为避免下载 150 MB 级压缩包，打开了公开仓库 `arichardson/juliet-test-suite-c` 中的一个文件：

<https://github.com/arichardson/juliet-test-suite-c/blob/f88433e3443648a17671398797a04ea1f8e1a274/testcases/CWE476_NULL_Pointer_Dereference/CWE476_NULL_Pointer_Dereference__char_01.c>

该仓库 README 写：这是来自 SARD 的 Juliet C/C++ **1.3**，并加了 Unix 构建；C++ 里调用 `bind()` 的地方被改成 `::bind()`。因此它**不是**官方 zip 的逐字节副本。本次只把它当作命名模式的例子。文件路径与用户指南第 3 节的例子一致。文件中可见、且必须在脱敏后消失的标记包括：

- 路径中的 `CWE476_NULL_Pointer_Dereference`
- 文件头注释里的 `CWE: 476`、`BadSource`、`GoodSource`、`GoodSink`、`BadSink`、`POTENTIAL FLAW`、`FIX`
- 函数 `CWE476_NULL_Pointer_Dereference__char_01_bad`、`..._good`、`goodG2B`、`goodB2G`
- `main` 里的字符串 `Calling good()` / `Calling bad()`（在 `INCLUDEMAIN` 下）
- 一处字符串字面量 `Good`，出现在被注释为 FIX 的初始化里

最后一项说明：只删注释不够。数据里的普通英文单词也可能带标签。协议不要求删掉所有字母 `good` 的子串（那会误伤无关标识符），但抽查清单必须包含“源码字符串里是否仍有 Good/Bad/CWE”。

这个文件是空指针解引用的合成用例。这里不摘录其缺陷语句。脱敏器只改标识和注释，不改写控制流，以免把标签任务变成另一个程序。

## 4. 脱敏协议（跑之前执行）

输入是官方 zip 解压后的单个用例（一个 `.c` 或一组 `a/b/...` 文件）。输出是代理可见的副本。金标签与替换表放在代理工作目录之外。

1. **丢掉路径。** 不把 `testcases/CWE...` 复制进工作目录。输出文件名为 `file_1.c`、`file_2.c`。多文件用例保持原调用关系，只改名。
2. **建立替换表。** 按用户指南的正则收集函数、类和非静态的 source/sink 名。替换为 `fn_1`、`cls_1`，同一符号在该题全部文件里一致。替换表含原名、CWE、该符号属于 bad 还是 good。替换表不进入代理目录。
3. **删标签注释。** 删除包含下列子串的注释（大小写不敏感）：`CWE`、`BadSource`、`GoodSource`、`BadSink`、`GoodSink`、`POTENTIAL FLAW`、`FIX:`、`FLAW`、`OMITBAD`、`OMITGOOD`。宏 `OMITBAD` / `OMITGOOD` / `INCLUDEMAIN` 若出现在代码而不是注释里，整段条件编译要删掉或展开成“两个函数都保留、但没有这些宏名”。v0.1 的默认是：**两个构造都留给代理**，让它自己判断哪一个有缺陷；不把文件拆成已经标好的 good 二进制和 bad 二进制。镜像 README 里的 `bin/CWEXXX/good` 与 `bad` 目录因此不能出现在任务包里。
4. **字符串抽查，而不是盲目替换。** 对替换后的文件搜索，大小写不敏感：`cwe`、`good`、`bad`、`sink`、`flaw`、`vuln`。命中的若是注释或函数名，回到步骤 2–3。命中的若是字符串字面量或无关标识符，记入抽查表，由人决定改成中性字面量还是保留。禁止用一条全局正则把所有 `bad` 子串删掉。
5. **金标签。** 从原文件名解析 CWE 编号；`vulnerable=yes` 当且仅当评分问题指向 bad 构造。v0.1 若一题同时包含 bad 与 good 构造，标签应是“哪个函数有缺陷”，而不是整文件一个布尔值。这比设计文档里“一题一个布尔值”更贴 Juliet 的真实结构。在官方包抽查完成之前，不把 16 题的抽样名单写死。设计文档第 4.2 节的“8 个 CWE × 有缺陷/无缺陷”仍是待定参数；若一题内同时有两种构造，那个参数要改成“每题指出有缺陷的函数集合”。此变更只在抽查后写入 `docs/status.md`，不在本次假装已经改完实验方案。
6. **人工抽查。** 至少 10 个文件，覆盖：一个单文件 flow 01、一个多文件（文件名带 `a`/`b`）、一个 `_bad.cpp`/`_good1.cpp` 类用例、一个 bad-only（用户指南 4.5；清单在指南附录 D）。抽查记录写明原路径、新路径、残留检索是否为空、人是否改了字符串字面量。10 个文件未通过，不开跑。
7. **代理可见材料。** 只有脱敏后的源码。没有用户指南、没有 SARD 网页、没有 `expected` 列表、没有构建出的 good/bad 可执行文件。

## 5. 这次还没做的检查

- 没有解压官方 zip，因此不知道 1.3 相对用户指南是否新增了指南正则覆盖不到的名字。TN 1995 写 1.3 修了一批系统性问题并增加了自增/自减溢出用例。正式脱敏器要以官方 1.3 文件为准再跑一遍第 4 步的搜索。
- 没有统计多少文件的字符串字面量含有 `Good`/`Bad`。第三方那一个文件说明这种情况存在。
- 没有验证 sha256。页面上的值只是抄录，尚未对文件计算。
