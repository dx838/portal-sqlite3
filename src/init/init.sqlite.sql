-- ----------------------------
-- SQLite 初始化脚本
-- 只包含用户和五笔码表相关的表
-- ----------------------------

-- ----------------------------
-- Table structure for user_group
-- 用户组表
-- ----------------------------
DROP TABLE IF EXISTS user_group;
CREATE TABLE user_group (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  description TEXT NULL DEFAULT NULL
);

-- ----------------------------
-- Records of user_group
-- ----------------------------
INSERT INTO user_group VALUES (1, 'admin', '管理员');
INSERT INTO user_group VALUES (2, 'user', '普通成员');


-- ----------------------------
-- Table structure for users
-- 用户表
-- ----------------------------
DROP TABLE IF EXISTS users;
CREATE TABLE users (
  uid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL,
  nickname TEXT NOT NULL,
  username TEXT NOT NULL,
  password TEXT NOT NULL,
  register_time DATETIME DEFAULT NULL,
  last_visit_time DATETIME DEFAULT NULL,
  comment TEXT DEFAULT NULL,
  wx TEXT DEFAULT '',
  phone TEXT DEFAULT NULL,
  homepage TEXT DEFAULT NULL,
  gaode TEXT DEFAULT NULL,
  group_id INTEGER NOT NULL DEFAULT 2,
  count_diary INTEGER DEFAULT 0,
  count_dict INTEGER DEFAULT 0,
  count_qr INTEGER DEFAULT 0,
  count_words INTEGER DEFAULT 0,
  count_map_route INTEGER DEFAULT 0,
  count_map_pointer INTEGER DEFAULT NULL,
  sync_count INTEGER DEFAULT 0,
  avatar TEXT DEFAULT NULL,
  city TEXT DEFAULT NULL,
  geolocation TEXT DEFAULT NULL,
  FOREIGN KEY (group_id) REFERENCES user_group (id)
);


-- ----------------------------
-- Table structure for invitations
-- 邀请码表
-- ----------------------------
DROP TABLE IF EXISTS invitations;
CREATE TABLE invitations (
  id TEXT NOT NULL PRIMARY KEY,
  date_create DATETIME NOT NULL,
  date_register DATETIME NULL DEFAULT NULL,
  binding_uid INTEGER NULL DEFAULT NULL,
  FOREIGN KEY (binding_uid) REFERENCES users (uid)
);


-- ----------------------------
-- Table structure for wubi_category
-- 五笔词条类别表
-- ----------------------------
DROP TABLE IF EXISTS wubi_category;
CREATE TABLE wubi_category (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  sort_id INTEGER NOT NULL,
  date_init DATETIME NOT NULL
);

-- ----------------------------
-- Records of wubi_category
-- ----------------------------
INSERT INTO wubi_category VALUES (1, '默认类别', 1, CURRENT_TIMESTAMP);
INSERT INTO wubi_category VALUES (2, '常用词', 2, CURRENT_TIMESTAMP);
INSERT INTO wubi_category VALUES (3, '专业词', 3, CURRENT_TIMESTAMP);
INSERT INTO wubi_category VALUES (4, '网络词', 4, CURRENT_TIMESTAMP);


-- ----------------------------
-- Table structure for wubi_dict
-- 五笔码表
-- ----------------------------
DROP TABLE IF EXISTS wubi_dict;
CREATE TABLE wubi_dict (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  content_size INTEGER NULL DEFAULT 0,
  word_count INTEGER NULL DEFAULT 0,
  date_init DATETIME NOT NULL,
  date_update DATETIME NULL DEFAULT NULL,
  comment TEXT NULL DEFAULT NULL,
  uid INTEGER NULL DEFAULT NULL,
  FOREIGN KEY (uid) REFERENCES users (uid)
);


-- ----------------------------
-- Table structure for wubi_words
-- 五笔词条表
-- ----------------------------
DROP TABLE IF EXISTS wubi_words;
CREATE TABLE wubi_words (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  word TEXT NOT NULL,
  code TEXT NOT NULL,
  priority INTEGER NOT NULL DEFAULT 0,
  up INTEGER NOT NULL DEFAULT 0,
  down INTEGER NOT NULL DEFAULT 0,
  date_create DATETIME NOT NULL,
  date_modify DATETIME DEFAULT NULL,
  comment TEXT DEFAULT NULL,
  uid INTEGER NOT NULL,
  category_id INTEGER NOT NULL,
  FOREIGN KEY (category_id) REFERENCES wubi_category (id),
  FOREIGN KEY (uid) REFERENCES users (uid)
);
