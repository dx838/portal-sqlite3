import express from "express";
import {ResponseError, ResponseSuccess} from "./response/Response";
import configDatabase from "../config/configDatabase.json";
import configProject from "../config/configProject.json";

import {Response} from "express-serve-static-core";
import { EntityUser } from "./entity/User"; // 使用相对路径而不是别名

// 创建 SQLite 数据库连接，从配置文件中读取路径
const databasePath = configDatabase.database || './portal.db';
const sqliteLibrary = configDatabase.sqliteLibrary || 'node:sqlite';

// 动态选择 SQLite 库
let database: any;
let DatabaseClass: any;

if (sqliteLibrary === 'sqlite3') {
    // 使用 sqlite3 库
    const sqlite3 = require('sqlite3').verbose();
    database = new sqlite3.Database(databasePath);
} else {
    // 默认使用 node:sqlite 库
    const { DatabaseSync } = require('node:sqlite');
    database = new DatabaseSync(databasePath);
}

// 日志配置
const LOG_ENABLED = configProject.log_enabled !== undefined ? configProject.log_enabled : true;

// 日志工具函数
export function logInfo(...args: any[]) {
    if (LOG_ENABLED) {
        console.log(...args);
    }
}

export function logError(...args: any[]) {
    if (LOG_ENABLED) {
        console.error(...args);
    }
}

// 确保数据库表存在
function ensureDatabaseTables() {
    // 这里将在 init.ts 中实现完整的表结构
}



// 运行 SQL 并返回 DB 结果
export function getDataFromDB(
    dbName: string,
    sqlArray: Array<string>,
    isSingleValue?: boolean
): Promise<any> {
    return new Promise((resolve, reject) => {
        try {
            // 执行 SQL 语句
            const sql = sqlArray.join(' ');
            // console.log('---- SQL', sql);
            
            // 处理多语句SQL：如果包含多个语句，分割并依次执行
            const statements = sql.split(';').filter(statement => statement.trim().length > 0);
            let result: any[] = [];
            
            if (sqliteLibrary === 'sqlite3') {
                // 使用 sqlite3 异步 API
                const executeStatement = async (index: number) => {
                    if (index >= statements.length) {
                        // 所有语句执行完成
                        if (isSingleValue) {
                            resolve(result && result.length > 0 ? result[0] : null);
                        } else {
                            resolve(result || []);
                        }
                        return;
                    }
                    
                    const statement = statements[index];
                    const trimmedStatement = statement.trim();
                    if (!trimmedStatement) {
                        executeStatement(index + 1);
                        return;
                    }
                    
                    // 判断是查询语句还是修改语句
                    const lowerStmt = trimmedStatement.toLowerCase();
                    const isSelect = lowerStmt.startsWith('select');
                    const isInsert = lowerStmt.startsWith('insert');
                    
                    try {
                        if (isSelect) {
                            // 执行查询语句
                            database.all(trimmedStatement, [], (err: any, rows: any[]) => {
                                if (err) {
                                    logError('数据库请求错误', err.message, 'SQL:', trimmedStatement);
                                    reject(err);
                                    return;
                                }
                                result = result.concat(rows);
                                executeStatement(index + 1);
                            });
                        } else if (isInsert) {
                            // 执行插入语句，获取插入ID
                            database.run(trimmedStatement, [], function(err: any) {
                                if (err) {
                                    logError('数据库请求错误', err.message, 'SQL:', trimmedStatement);
                                    reject(err);
                                    return;
                                }
                                result.push({ insertId: this.lastID });
                                executeStatement(index + 1);
                            });
                        } else {
                            // 执行其他修改语句
                            database.run(trimmedStatement, [], (err: any) => {
                                if (err) {
                                    logError('数据库请求错误', err.message, 'SQL:', trimmedStatement);
                                    reject(err);
                                    return;
                                }
                                result.push({ affectedRows: 1 }); // 模拟受影响行数
                                executeStatement(index + 1);
                            });
                        }
                    } catch (err: any) {
                        logError('数据库请求错误', err.message, 'SQL:', trimmedStatement);
                        reject(err);
                    }
                };
                
                executeStatement(0);
            } else {
                // 使用 node:sqlite 同步 API
                for (const statement of statements) {
                    const trimmedStatement = statement.trim();
                    if (!trimmedStatement) continue;
                    
                    // 判断是查询语句还是修改语句
                    const lowerStmt = trimmedStatement.toLowerCase();
                    const isSelect = lowerStmt.startsWith('select');
                    const isInsert = lowerStmt.startsWith('insert');
                    
                    if (isSelect) {
                        // 执行查询语句
                        const stmt = database.prepare(trimmedStatement);
                        const queryResult = stmt.all();
                        result = result.concat(queryResult);
                    } else if (isInsert) {
                        // 执行插入语句，获取插入ID
                        const stmt = database.prepare(trimmedStatement);
                        const insertResult = stmt.run();
                        // 获取插入ID，注意 SQLite 使用 lastInsertRowid 而不是 lastInsertRowId
                        result.push({ insertId: insertResult.lastInsertRowid });
                    } else {
                        // 执行其他修改语句
                        database.exec(trimmedStatement);
                        result.push({ affectedRows: 1 }); // 模拟受影响行数
                    }
                }
                
                // 处理结果
                if (isSingleValue) {
                    resolve(result && result.length > 0 ? result[0] : null);
                } else {
                    resolve(result || []);
                }
            }
        } catch (err: any) {
            logError('数据库请求错误', err.message, 'SQL:', sqlArray.join(' '));
            reject(err);
        }
    })
}


// 验证用户是否有权限
export function verifyAuthorization(req: express.Request): Promise<EntityUser>{
    let token = req.get('Diary-Token') || req.query.token
    let uid = req.get('Diary-Uid')
    return new Promise((resolve, reject) => {
        if (!token){
            reject ('无 token')
        } else if (!uid){
            reject ('程序已升级，请关闭所有相关窗口，再重新访问该网站')
        } else {
            let sqlArray = []
            sqlArray.push(`select * from users where password = '${token}' and uid = ${uid}`)
            getDataFromDB( 'diary', sqlArray, true)
                .then(userInfo => {
                    if (userInfo){
                        resolve(userInfo) // 如果查询成功，返回 用户id
                    } else {
                        reject('身份验证失败：查无此人')
                    }
                })
                .catch(() => {
                    reject('mysql: 获取身份信息错误')
                })
        }
    })
}

// SQLite 不需要单独的连接管理，直接使用全局数据库对象



// 格式化时间，输出字符串
export function dateFormatter(date: Date, formatString = 'yyyy-MM-dd hh:mm:ss') {
    let dateRegArray = {
        "M+": date.getMonth() + 1,                      // 月份
        "d+": date.getDate(),                           // 日
        "h+": date.getHours(),                          // 小时
        "m+": date.getMinutes(),                        // 分
        "s+": date.getSeconds(),                        // 秒
        "q+": Math.floor((date.getMonth() + 3) / 3), // 季度
        "S": date.getMilliseconds()                     // 毫秒
    }
    if (/(y+)/.test(formatString)) {
        formatString = formatString.replace(RegExp.$1, (date.getFullYear() + "").substr(4 - RegExp.$1.length))
    }
    for (let section in dateRegArray) {
        if (new RegExp("(" + section + ")").test(formatString)) {
            formatString = formatString.replace(RegExp.$1, (RegExp.$1.length === 1) ? (dateRegArray[section]) : (("00" + dateRegArray[section]).substr(("" + dateRegArray[section]).length)))
        }
    }
    return formatString
}

// unicode -> text
export function unicodeEncode(str: string){
    if(!str)return '';
    if(typeof str !== 'string') return str
    let text = escape(str);
    text = text.replace(/(%u[ed][0-9a-f]{3})/ig, (source, replacement) => {
        // logInfo('source: ',source)
        return source.replace('%', '\\')
    })
    return unescape(text);
}

// text -> unicode
export function  unicodeDecode(str: string)
{
    let text = escape(str);
    text = text.replace(/(%5Cu[ed][0-9a-f]{3})/ig, source=>{
        return source.replace('%5C', '%')
    })
    return unescape(text);
}

export function updateUserLastLoginTime(uid: number){
    let timeNow = dateFormatter(new Date())
    getDataFromDB( 'diary', [`update users set last_visit_time='${timeNow}' where uid='${uid}'`])
        .then(() => {
            logInfo(`--- 成功：记录用户最后操作时间 ${timeNow} ${uid}`)
        })
        .catch(() => {
            logError('--- 失败：记录用户最后操作时间 ${timeNow} ${uid}`')
        })
}

/**
 * 通用操作，数据库操作： 返回添加的记录 id
 * @param uid  用户id
 * @param dbId 数据库标识
 * @param dbTitle 数据库名
 * @param sqlArray 操作的 sql 语句数组
 * @param operationName 操作的名字：添加|删除|修改
 * @param res  express.Response
 */
export function operate_db_and_return_added_id(
    uid: number,
    dbId: string,
    dbTitle: string,
    sqlArray: Array<string>,
    operationName: string,
    res: Response,
){
    getDataFromDB( dbId, sqlArray)
        .then(data => {
            // logInfo(data)
            if (data) { // 没有记录时会返回  undefined
                updateUserLastLoginTime(uid)
                // 添加成功之后，返回添加后的日记类别 id
                res.send(new ResponseSuccess({id: data.insertId}, `${operationName}成功`))
            } else {
                res.send(new ResponseError('', `${dbTitle}操作错误`))
            }
        })
        .catch(err => {
            res.send(new ResponseError(err, `${dbTitle}${operationName}失败`))
        })
}

/**
 * 通用操作，数据库操作 不返回结果
 * @param uid  用户id
 * @param dbId 数据库标识
 * @param dbTitle 数据库名
 * @param sqlArray 操作的 sql 语句数组
 * @param operationName 操作的名字：添加|删除|修改
 * @param res  express.Response
 */
export function operate_db_without_return(
    uid: number,
    dbId: string,
    dbTitle: string,
    sqlArray: Array<string>,
    operationName: string,
    res: Response,
){
    getDataFromDB( dbId, sqlArray)
        .then(data => {
            updateUserLastLoginTime(uid)
            // 编辑成功之后，返回添加后的日记类别 id
            res.send(new ResponseSuccess(null, `${operationName}成功`))
        })
        .catch(err => {
            res.send(new ResponseError(err, `${dbTitle}${operationName}失败`))
        })
}



