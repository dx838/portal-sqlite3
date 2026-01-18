# Portal 后台服务 `nodejs` `ts` `sqlite3`

一个基于 Node.js + TypeScript + SQLite3 的后端服务，提供五笔码表管理功能。

## 一、项目简介

该后台服务主要提供以下功能：

- 用户管理（登录）
- 五笔码表管理（上传、下载、编辑）


## 二、技术栈

- **后端框架**: Express.js
- **开发语言**: TypeScript
- **数据库**: SQLite3
- **构建工具**: TypeScript Compiler (tsc)
- **依赖管理**: npm

## 三、接口列表

### 用户管理
- `/user/login` - 用户登录

### 五笔码表管理
- `/wubi/word/list` - 词条列表
- `/wubi/word/add` - 添加词条
- `/wubi/word/add-batch` - 批量添加词条
- `/wubi/word/modify` - 修改词条
- `/wubi/word/delete` - 删除词条
- `/wubi/word/export-extra` - 导出词条
- `/wubi/word/upload-dict` - 上传码表文件
- `/wubi/word/check-exist` - 检查词条是否存在

### 其他
- `/init` - 初始化数据库

## 四、安装说明

### 服务器要求
- 已安装 `nodejs 18+`
- 已安装 `npm`
- 可选：已安装 `nginx`，用于路径映射（非必须）

### 安装步骤

1. **克隆或下载项目**
   ```bash
   git clone <repository-url>
   cd portal-sqlite3
   ```

2. **安装依赖**
   ```bash
   npm install
   ```

3. **构建项目**
   ```bash
   npm run build
   ```
   构建完成后，可执行文件将生成在 `/dist` 目录下

4. **启动项目**
   - 使用 PM2 管理（推荐）
     ```bash
     pm2 start ./dist/bin/portal.js --name portal
     ```
   - 直接启动
     ```bash
     npm run start
     ```
   - 开发模式（带热重载）
     ```bash
     npm run dev:watch
     ```

5. **访问服务**
   项目启动后默认运行在 `localhost:3000`

6. **初始化数据库**
   - 删除项目目录中的 `DATABASE_LOCK` 文件（如果存在）
   - 访问 `http://localhost:3000/init` 初始化数据库
   - 初始化完成后会自动创建 `DATABASE_LOCK` 文件，防止重复初始化

### 配置文件

项目配置文件位于 `/config` 目录下：

- `configDatabase.json` - 数据库配置（SQLite3 无需复杂配置）
- `configProject.json` - 项目配置


## 五、开发说明

### 开发流程
1. 修改 TypeScript 源码（位于 `/src` 目录下）
2. 执行 `npm run build` 构建项目
3. 执行 `npm run dev` 或 `npm run dev:watch` 启动开发服务器

### 密码加密
密码使用 `bcryptjs` 进行加密存储

### 返回数据格式

所有 API 返回统一格式：

```json
{
  "success": true,  // 操作是否成功
  "message": "提示信息",  // 操作结果描述
  "data": {}  // 返回数据
}
```

## 六、项目结构

```bash
portal-sqlite3/
├── bin/                 # 入口文件
│   ├── portal.ts        # 主服务入口
│   └── ws.ts            # WebSocket 服务入口
├── config/              # 配置文件
│   ├── configDatabase.json
│   └── configProject.json
├── cron/                # 定时任务
│   └── updateUserInfo.ts
├── db/                  # 数据库文件
│   └── portal.db
├── dist/                # 构建后的可执行文件
├── src/                 # TypeScript 源码
│   ├── entity/          # 数据实体
│   ├── init/            # 数据库初始化
│   ├── response/        # 统一响应格式
│   ├── user/            # 用户相关功能
│   ├── wubi/            # 五笔码表相关功能
│   ├── index.ts         # 主路由
│   └── utility.ts       # 工具函数
├── app.ts               # 应用入口
├── package.json         # 项目配置
└── tsconfig.json        # TypeScript 配置
```

## 七、部署说明

### 使用 Nginx 反向代理（可选）

如果你需要将服务部署到生产环境，可以使用 Nginx 进行反向代理，将 `/portal` 路径映射到服务端口。

1. 打开 Nginx 配置文件
2. 添加以下配置：
   ```nginx
   upstream portal_server {
       server localhost:3000;
       keepalive 2000;
   }
   
   server {
       # 其他配置...
       
       location /portal/ {
           proxy_pass http://portal_server/;
           proxy_set_header Host $host:$server_port;
       }
   }
   ```
3. 重启 Nginx 服务

### 设置管理员账户
1. 直接修改数据库，在 `users` 表中添加或修改用户记录
2. 将用户的 `group_id` 字段设置为 `1`
3. 使用该用户登录，即可拥有管理员权限

## 八、历程
- 迁移到 SQLite3 数据库 `2025`

## 九、注意事项

1. 数据库文件位于 `/db/portal.db`，请定期备份
2. 生产环境建议使用 PM2 或其他进程管理器来管理服务
3. 首次启动需要初始化数据库
4. 项目使用 SQLite3 数据库，无需额外安装数据库服务



## 十、鸣谢
1. 感谢 KyleBing 提供的开源项目 [portal](https://github.com/KyleBing/portal) 、 [wubi-dict-editor](https://github.com/KyleBing/wubi-dict-editor)。
2. 感谢 Trae、CodeBuddy 两位大佬的帮助。

