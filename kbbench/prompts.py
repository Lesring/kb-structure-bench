"""Shared prompts. No CWE menu and no arm-specific advice."""

WRITE_INSTRUCTIONS = """你在阅读已经去掉原路径和原文件名的源码。把确认下来的观察写入知识库。
不要写利用步骤、载荷或攻击过程。
每条观察的正文里单独占一行，写成 CLAIM vulnerable=yes 或 CLAIM vulnerable=no。
这一行只是记录格式，不是对答案的提示。
写完即可，不要给出最终判定。只能使用提供的工具。
"""

HANDOFF_INSTRUCTIONS = """你看不到源码，只能读知识库。根据知识库回答一个 JSON 对象，不要写别的文字。
字段：
- vulnerable: yes、no 或 unknown
- category: 你判断的类别编号，不能判断就写 unknown。不要假设有一份类别清单。
- location: 知识库里出现的函数标识，不能判断就写 unknown
- evidence_ids: 你依据的知识库记录 id 列表
- notes: 很短的说明。不要写利用步骤或载荷。
"""

TOOL_SPECS = [
    {
        "name": "kb_write",
        "description": "记录一条观察。title 是短标题，body 是正文，depends_on 是可选的已有记录 id。",
        "parameters": ["title", "body", "depends_on"],
    },
    {
        "name": "kb_search",
        "description": "按查询取回最多 limit 条证据。返回条数和总长度由统一预算截断。",
        "parameters": ["query"],
    },
    {
        "name": "kb_read",
        "description": "按 id 读取一条记录的全文。",
        "parameters": ["id"],
    },
    {
        "name": "kb_list",
        "description": "列出已有记录的 id 和一行摘要。",
        "parameters": [],
    },
]

FILE_TOOL_SPECS = [
    {
        "name": "list_dir",
        "description": "列出任务源码目录中的文件名。",
        "parameters": [],
    },
    {
        "name": "read_file",
        "description": "读取任务源码目录中的一个文件。",
        "parameters": ["path"],
    },
    {
        "name": "search_file",
        "description": "在指定文件中做字面搜索。",
        "parameters": ["path", "query"],
    },
]
