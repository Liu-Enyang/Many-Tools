# JP Test Spec Generator（测试式样书生成工具 - MVP）

一个面向 ASP.NET WebForms 项目的**测试式样书自动生成工具（MVP版本）**。

通过解析前台页面、后台代码以及简单设计资料，自动生成：

- 测试分析（analysis）
- 测试观点评（viewpoints）
- 测试用例（testcases）
- Excel 格式测试式样书

---

## 一、功能说明（MVP能力）

当前版本支持以下能力：

### 1. 输入解析
自动解析 `sample_input` 目录中的文件：

- `.aspx`（前台页面）
- `.aspx.cs`（后台代码）
- `.js`（前端逻辑）
- `.xlsx`（简单设计资料，可选）

无需写死文件名，工具会自动识别。

---

### 2. 自动分析（analysis）
生成：

- 画面信息（画面ID / 画面名）
- 控件列表
- 后台事件
- 输入检查候选
- 画面模式（参照模式等）
- JavaScript 前端逻辑（按钮、下载、排序等）

输出文件：

```text
output/analysis.json
```

---

### 3. 测试观点评生成（viewpoints）
自动生成测试观点评，包括：

- 初期表示
- 输入检查
- 桁数检查
- 按钮 / 事件处理
- 一览表显示 / 排序
- 参照模式控制
- JavaScript 逻辑验证

输出文件：

```text
output/viewpoints.json
```

---

### 4. 测试用例生成（testcases）
根据观点评自动展开测试用例：

- 正常系 / 异常系
- 输入不足 / 桁数超限 / 非法值
- 事件执行结果验证
- 前端逻辑（JS）验证

输出文件：

```text
output/testcases.json
```

---

### 5. Excel 测试式样书生成
根据模板生成最终测试式样书：

- 自动填充
  - チェック条件
  - アクション
  - 確認内容
- 自动打圈（○）
- 保留模板格式

输出文件：

```text
output/{画面名}_単体テスト仕様書.xlsx
```

---

## 二、目录结构

```text
jp_test_spec_generator/
├── sample_input/        # 输入文件（ASPX / CS / JS / Excel）
├── output/              # 输出结果
├── src/
│   ├── main.py          # 主入口
│   └── generator/       # 各类生成逻辑
└── README.md
```

---

## 三、使用方法

### 1. 创建虚拟环境

Mac / Linux：

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows：

```powershell
python -m venv venv
venv\Scripts\activate
```

---

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

---

### 3. 准备输入文件
将以下文件放入：

```text
sample_input/
```

示例：

```text
sample_input/
├── Summary.aspx
├── Summary.aspx.cs
├── Summary.js
├── design.xlsx（可选）
```

---

### 4. 执行生成

```bash
python src/main.py
```

---

### 5. 查看输出
生成结果在：

```text
output/
```

包括：

- analysis.json
- viewpoints.json
- testcases.json
- Excel 测试式样书

---

## 四、当前限制（MVP）

当前版本为最小可用版本（MVP），存在以下限制：

- 默认只处理一个画面（取目录中第一个 aspx）
- JS 解析为规则匹配（非语法解析）
- 复杂业务逻辑理解有限
- 输入设计书解析较简单

---

## 五、后续优化方向

建议下一步优化：

- 支持多画面批量生成
- JS 逻辑精细化分析（按钮级别）
- 更精准的字段识别（与 DB / 设计书联动）
- GUI 界面（选择目录，一键生成）
- Excel 模板多版本支持

---

## 六、适用场景

- 对日开发项目（WebForms）测试式样书生成
- 旧系统（遗留系统）测试补充
- 测试自动化前的用例基线生成

---

## 七、总结

该工具当前已具备：

- 从代码到测试式样书的自动转换能力
- 前后端（ASPX / CS / JS）联合分析
- Excel 测试式样书自动生成

适合作为测试自动化与 AI 测试平台的基础模块。