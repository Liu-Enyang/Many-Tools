# Business Data Generator（业务测试数据生成工具）

## 📌 项目简介

Business Data Generator 是 Many-Tools 中的一个模块，用于 **快速生成业务测试数据（SQL）**。

它的核心目标是：

> 不再手写多表关联 SQL，而是通过“业务场景 + 配置”自动生成完整数据。

适用于：
- 对日开发项目
- 多表关联复杂系统（如 RiskTaker）
- 画面测试 / 单体测试 / 联调测试

---

## 🎯 核心特点

- ✅ 按“业务场景”生成数据（不是按表）
- ✅ 自动处理多表关联
- ✅ 支持默认值 / 自动生成字段
- ✅ 支持生成多条明细数据
- ✅ 自动生成 rollback SQL
- ✅ 配置驱动（YAML），可扩展性强
- ✅ 支持从 DDL 自动生成表结构 YAML（Base YAML）

---

## 📂 项目结构

```
business-data-generator/
  app.py                  # 启动入口（CLI）
  
  config/
    scenarios/            # 业务场景定义
    tables/
      base/               # 从DDL自动生成（结构定义）
      rules/              # 业务规则定义（后续补充）
  
  src/
    main.py               # 主流程
    scenario_loader.py    # 加载 YAML
    value_resolver.py     # 字段值解析
    sql_builder.py        # 生成 INSERT SQL
    rollback_builder.py   # 生成 DELETE SQL
    schema_parser.py      # 解析DDL
    schema_to_yaml.py     # DDL转Base YAML
  
  templates/
    *.json                # 输入参数示例
  
  output/
    *.sql                 # 输出 SQL
```

---

## 🚀 快速开始

### 1️⃣ 安装依赖

```
pip install -r requirements.txt
```

---

### 2️⃣ 执行生成

```
python app.py --scenario summary_normal --input templates/summary_input.json
```

---

### 2️⃣（新）从DDL生成表结构 YAML

```
python app.py --ddl-dir ddl/
```

输出：
```
config/tables/base/
  *.yaml
```

---

### 2️⃣（新）Clone 模式 — 快速复制单条数据

#### GUI 模式（推荐）

```
streamlit run streamlit_app.py
```

浏览器自动打开 `http://localhost:8501`。

操作步骤：

1. 侧边栏选择目标表
2. 输入 `RGlap_ApprovalNo` 等字段值进行搜索过滤
3. 下拉选择 clone 来源行
4. 主键自动显示为 max+1（可手动修改）
5. 区分字段以下拉框显示 PCC_hanyou 选项，当前值为默认
6. 点击「SQL 生成」按钮

#### CLI 模式

```
python app.py --clone <テーブル名>
```

示例：

```
python app.py --clone PRG_loanapproval
python app.py --clone PJG_saikenmeisai
```

执行流程：列出所有行 → 输入行号 → 主键 max+1 → 区分交互选择 → 输出 SQL

---

输出（两种模式共通）：

```
output/
  clone_<テーブル名>.sql           ← INSERT SQL
  rollback_clone_<テーブル名>.sql  ← DELETE SQL（rollback 用）
```

---

**前提条件：**

| 文件 | 说明 |
|------|------|
| `data/dbo.<テーブル名>.csv` | 表的 sample 数据 |
| `config/tables/base/<テーブル名>.yaml` | 主键定义（由 DDL 生成） |
| `data/dbo.PCC_hanyou.csv` | 汎用テーブル（区分选项来源） |
| `config/dictionaries/field_dictionary_mapping.yaml` | 字段 → 区分 code_key 映射 |

**添加新表的区分映射：**

在 `config/dictionaries/field_dictionary_mapping.yaml` 中添加：

```yaml
JGskm_KengenKubun:
  table: PCC_hanyou
  code_key: KENGEN        # PCC_hanyou の CChny_HanyouCodeKey と一致すること
  description: 権限区分
```

`code_key` の確認方法：対象フィールドの格納値（例: `KENGEN2`）と `dbo.PCC_hanyou.csv` の `CChny_HanyouUniqueKey` を照合する。

---

### 3️⃣ 输出结果

```
output/
  setup_summary_normal.sql
  rollback_summary_normal.sql
```

---

## 🧩 核心概念

### 0️⃣ Base YAML（结构定义）

从数据库 DDL 自动生成，描述表结构。

示例：

```yaml
table_name: PJG_saikenmeisai

primary_key:
- JGskm_SyoriId
- JGskm_ShinseiNo
- JGskm_KasitukeNo

required_fields:
- JGskm_BranchNo
- JGskm_CustomerNo
```

---

### 1️⃣ Scenario（场景）

定义一个业务场景需要哪些表。

示例：

```yaml
scenario_id: summary_normal

tables:
  - table: PJG_saikenmeisai
    rows_from: input.SaikenCount

  - table: PRM_CustomerComment
    include_if: input.HasComment
```

---

### 2️⃣ Table（表配置）

定义一张表如何生成数据。

示例：

```yaml
table_name: PJG_saikenmeisai

required_fields:
  - JGskm_BranchNo
  - JGskm_CustomerNo

field_sources:
  JGskm_BranchNo: input.BranchNo

generated_fields:
  JGskm_ShinseiNo: sequence
```

---

### 3️⃣ Input（输入参数）

用户提供最少信息：

```json
{
  "BranchNo": "001",
  "CustomerNo": "0010001",
  "SaikenCount": 3,
  "HasComment": true
}
```

---

## 🔄 数据生成流程

```
输入 JSON
   ↓
加载 Scenario
   ↓
加载 Table 定义
   ↓
生成每张表数据
   ↓
生成 INSERT SQL
   ↓
生成 DELETE SQL（rollback）
```

---

## 🛠 当前支持功能（MVP）

- [x] 按场景生成数据
- [x] 多表生成
- [x] 条件控制（include_if）
- [x] 动态行数（rows_from）
- [x] 默认值支持
- [x] 自动生成字段（sequence / row_number）
- [x] rollback SQL

---

## 📈 后续计划

- [ ] Base YAML → Rule YAML 自动生成
- [ ] 自动解析 SP → 生成 YAML
- [ ] 自动读取数据库数据生成默认值
- [ ] Master 表自动 lookup
- [ ] Web UI（Streamlit）
- [ ] AI 输入（自然语言 → 场景）
- [ ] 数据复制（clone 现有数据）

---

## ⚠️ 注意事项

- 当前版本为 MVP，字段需根据实际数据库调整
- NOT NULL 字段需要在 YAML 中补齐
- 表依赖顺序暂未自动优化（后续支持）

---

## 🧠 使用建议

开发流程建议：

1. 从DDL生成 Base YAML
2. 分析现有数据补充 Rule YAML
3. 确定最小业务数据结构
4. 编写 scenario YAML
5. 生成 SQL 并验证

---

## 💡 适用场景

- 画面测试数据准备
- 单体测试数据自动生成
- 复杂 SQL 验证
- 回归测试数据构造
- 对日项目高效开发

---

## ✨ 作者说明

本工具专为：

👉 多表复杂业务系统（如金融、信贷、RiskTaker）

设计，目标是：

> 用配置替代重复 SQL，用工具替代人工造数。

---</file>