#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加用户脚本
用于为Portal项目添加管理员账户和普通账户
"""

import sqlite3
import bcrypt
import datetime
import getpass


def get_db_connection():
    """获取数据库连接"""
    # 从配置文件读取数据库路径
    import json
    try:
        with open('./config/configDatabase.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            db_path = config.get('database', './portal.db')
    except (FileNotFoundError, json.JSONDecodeError):
        # 如果配置文件不存在或解析错误，使用默认路径
        db_path = './portal.db'
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def generate_password_hash(password):
    """生成密码哈希值"""
    # bcrypt加密，cost factor设为10
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(10))
    return hashed.decode('utf-8')


def check_email_or_username_exist(email, username):
    """
    检查邮箱或用户名是否已存在
    
    Args:
        email: 邮箱
        username: 用户名
    
    Returns:
        bool: 如果邮箱或用户名已存在，返回True，否则返回False
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 查询邮箱或用户名是否已存在
    sql = "SELECT * FROM users WHERE email = ? OR username = ?"
    cursor.execute(sql, (email, username))
    result = cursor.fetchall()
    
    conn.close()
    
    return len(result) > 0


def add_user(email, nickname, username, password, group_id=2, **kwargs):
    """
    添加用户
    
    Args:
        email: 邮箱
        nickname: 昵称
        username: 用户名
        password: 密码
        group_id: 用户组别ID，1为管理员，2为普通用户
        **kwargs: 其他可选参数
    """
    # 检查邮箱或用户名是否已存在
    if check_email_or_username_exist(email, username):
        print(f"❌ 添加失败：邮箱 '{email}' 或用户名 '{username}' 已被注册")
        return None
    
    # 生成密码哈希
    hashed_password = generate_password_hash(password)
    
    # 获取当前时间
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 构建SQL语句
    sql = '''
    INSERT INTO users (
        email, nickname, username, password, register_time, last_visit_time,
        comment, wx, phone, homepage, gaode, group_id,
        count_diary, count_dict, count_qr, count_words, count_map_route,
        count_map_pointer, sync_count, avatar, city, geolocation
    ) VALUES (
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
    )
    '''
    
    # 准备参数
    params = [
        email, nickname, username, hashed_password, now, now,
        kwargs.get('comment', ''), kwargs.get('wx', ''), kwargs.get('phone', ''),
        kwargs.get('homepage', ''), kwargs.get('gaode', ''), group_id,
        kwargs.get('count_diary', 0), kwargs.get('count_dict', 0), kwargs.get('count_qr', 0),
        kwargs.get('count_words', 0), kwargs.get('count_map_route', 0),
        kwargs.get('count_map_pointer', 0), kwargs.get('sync_count', 0),
        kwargs.get('avatar', ''), kwargs.get('city', ''), kwargs.get('geolocation', '')
    ]
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        conn.close()
        print(f"✅ 用户添加成功：{email} (UID: {cursor.lastrowid})")
        return cursor.lastrowid
    except sqlite3.IntegrityError as e:
        print(f"❌ 添加失败：{e}")
        return None
    except Exception as e:
        print(f"❌ 添加失败：{e}")
        return None


def list_users():
    """列出所有用户"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT uid, email, username, nickname, group_id, register_time FROM users')
        users = cursor.fetchall()
        conn.close()
        
        if not users:
            print("📭 暂无用户")
            return
        
        print("\n📋 用户列表：")
        print("-" * 80)
        print(f"{'UID':<5} {'邮箱':<30} {'用户名':<15} {'昵称':<15} {'组别':<8} {'注册时间':<20}")
        print("-" * 80)
        
        for user in users:
            group_name = "管理员" if user['group_id'] == 1 else "普通用户"
            print(f"{user['uid']:<5} {user['email']:<30} {user['username']:<15} {user['nickname']:<15} {group_name:<8} {user['register_time']:<20}")
        print("-" * 80)
    except Exception as e:
        print(f"❌ 获取用户列表失败：{e}")


def get_user_by_id(uid):
    """
    根据用户ID获取用户信息
    
    Args:
        uid: 用户ID
    
    Returns:
        dict: 用户信息，如果用户不存在返回None
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    sql = "SELECT uid, email, username, nickname, group_id FROM users WHERE uid = ?"
    cursor.execute(sql, (uid,))
    result = cursor.fetchone()
    
    conn.close()
    
    return dict(result) if result else None


def update_password(uid, new_password):
    """
    修改用户密码
    
    Args:
        uid: 用户ID
        new_password: 新密码
    
    Returns:
        bool: 修改成功返回True，否则返回False
    """
    # 检查用户是否存在
    user = get_user_by_id(uid)
    if not user:
        print(f"❌ 修改失败：用户ID {uid} 不存在")
        return False
    
    # 生成密码哈希
    hashed_password = generate_password_hash(new_password)
    
    # 构建SQL语句
    sql = "UPDATE users SET password = ? WHERE uid = ?"
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (hashed_password, uid))
        conn.commit()
        conn.close()
        print(f"✅ 密码修改成功：用户 {user['email']} (UID: {uid})")
        return True
    except Exception as e:
        conn.close()
        print(f"❌ 修改密码失败：{e}")
        return False


def delete_user(uid):
    """
    删除用户
    
    Args:
        uid: 用户ID
    
    Returns:
        bool: 删除成功返回True，否则返回False
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 开始事务
        conn.execute('BEGIN TRANSACTION')
        
        # 删除关联数据
        # 1. 删除用户的码表
        cursor.execute("DELETE FROM wubi_dict WHERE uid = ?", (uid,))
        
        # 2. 删除用户的词条
        cursor.execute("DELETE FROM wubi_words WHERE uid = ?", (uid,))
        
        # 3. 删除用户的邀请码
        cursor.execute("DELETE FROM invitations WHERE binding_uid = ?", (uid,))
        
        # 4. 删除用户
        cursor.execute("DELETE FROM users WHERE uid = ?", (uid,))
        
        # 提交事务
        conn.commit()
        conn.close()
        print(f"✅ 用户删除成功：UID = {uid}")
        return True
    except Exception as e:
        # 回滚事务
        conn.rollback()
        conn.close()
        print(f"❌ 删除用户失败：{e}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("🔐 Portal 项目用户管理脚本")
    print("=" * 60)
    print("\n1. 查看用户列表")
    print("2. 添加管理员账户")
    print("3. 添加普通账户")
    print("4. 删除用户")
    print("5. 修改用户密码")
    print("6. 退出")
    print("=" * 60)
    
    while True:
        choice = input("\n请选择操作 (1-6): ")
        
        if choice == '1':
            list_users()
        elif choice == '2' or choice == '3':
            # 获取用户信息
            email = input("请输入邮箱: ")
            username = input("请输入用户名: ")
            nickname = input("请输入昵称: ")
            password = getpass.getpass("请输入密码: ")
            confirm_password = getpass.getpass("请确认密码: ")
            
            if password != confirm_password:
                print("❌ 两次输入的密码不一致！")
                continue
            
            # 判断用户组别
            group_id = 1 if choice == '2' else 2
            group_name = "管理员" if group_id == 1 else "普通用户"
            
            # 确认添加
            confirm = input(f"\n确认添加{group_name}账户吗？(y/n): ")
            if confirm.lower() == 'y' or confirm.lower() == 'yes':
                add_user(email, nickname, username, password, group_id)
            else:
                print("❌ 添加已取消")
        elif choice == '4':
            # 删除用户
            list_users()
            uid_str = input("\n请输入要删除的用户ID: ")
            
            try:
                uid = int(uid_str)
            except ValueError:
                print("❌ 无效的用户ID，请输入数字！")
                continue
            
            # 确认删除
            confirm = input(f"\n确认删除用户ID为 {uid} 的用户吗？(y/n): ")
            if confirm.lower() == 'y' or confirm.lower() == 'yes':
                delete_user(uid)
            else:
                print("❌ 删除已取消")
        elif choice == '5':
            # 修改密码
            list_users()
            uid_str = input("\n请输入要修改密码的用户ID: ")
            
            try:
                uid = int(uid_str)
            except ValueError:
                print("❌ 无效的用户ID，请输入数字！")
                continue
            
            # 获取新密码
            new_password = getpass.getpass("请输入新密码: ")
            confirm_password = getpass.getpass("请确认新密码: ")
            
            if new_password != confirm_password:
                print("❌ 两次输入的密码不一致！")
                continue
            
            # 确认修改
            confirm = input(f"\n确认修改用户ID为 {uid} 的密码吗？(y/n): ")
            if confirm.lower() == 'y' or confirm.lower() == 'yes':
                update_password(uid, new_password)
            else:
                print("❌ 修改已取消")
        elif choice == '6':
            print("👋 退出脚本")
            break
        else:
            print("❌ 无效的选择，请重新输入！")


if __name__ == "__main__":
    main()
