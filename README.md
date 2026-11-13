# 员工管理系统

## 启动方式

### 一键启动

```bash
cd backend
./run.sh
```

### 手动启动

```bash
cd backend

# 1. 创建并激活虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动后端
python run.py
```

服务启动后：
- 前端：用浏览器打开 `frontend/login.html`


### 数据库说明

- 默认数据库文件位于系统临时目录：`/tmp/emp_mgmt_employees.db`。
- 可通过环境变量自定义位置：
  EMP_DB_PATH="/path/to/your/employees.db"
- 切换 MySQL 只需设置：
  DATABASE_URL="mysql+pymysql://user:pass@host:3306/emp_mgmt"

## 五、默认账号

| 账号 | 密码 |
|------|------|
| `admin` | `admin123` |

```
a1b2c3d feat(frontend): 完成部门统计页（柱状图 + KPI 卡片 + 明细表）
e4f5g6h feat(frontend): 完成员工列表页与新增/编辑弹窗表单
i7j8k9l feat(backend): 实现员工管理全部后端接口与统一响应
ed33a6e chore: 初始化项目结构，搭建后端骨架
```
