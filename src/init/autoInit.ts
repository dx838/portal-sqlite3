import { statSync, writeFileSync, readFileSync } from 'fs';
import { dateFormatter, logInfo, logError } from '../utility';
import path from 'path';
import configDatabase from '../../config/configDatabase.json';

// 创建 SQLite 数据库连接，从配置文件中读取路径
const databasePath = configDatabase.database || './portal.db';
const sqliteLibrary = configDatabase.sqliteLibrary || 'node:sqlite';

const LOCK_FILE_NAME = 'DATABASE_LOCK';

// 动态选择 SQLite 库
let database: any;

/**
 * 自动初始化数据库
 * 在服务启动时调用，检查数据库是否需要初始化
 */
export function autoInitDatabase() {
    return new Promise<void>((resolve, reject) => {
        try {
            // 检查锁文件是否存在
            statSync(LOCK_FILE_NAME);
            // 如果有锁文件，说明数据库已经初始化过
            logInfo('数据库已初始化，跳过初始化步骤');
            resolve();
            return;
        } catch (err) {
            // 如果没有锁文件，说明数据库没有初始化过
            logInfo('检测到数据库未初始化，开始初始化...');
            
            // 读取初始化脚本
            const sqlFilePath = path.join(__dirname, 'init.sqlite.sql');
            const sqlCreateTables = readFileSync(sqlFilePath, 'utf8');
            
            if (sqliteLibrary === 'sqlite3') {
                // 使用 sqlite3 异步 API
                const sqlite3 = require('sqlite3').verbose();
                database = new sqlite3.Database(databasePath, (err: any) => {
                    if (err) {
                        logError('数据库连接失败：', err.message);
                        reject(err);
                        return;
                    }
                    
                    // 执行初始化脚本
                    database.exec(sqlCreateTables, (err: any) => {
                        if (err) {
                            logError('数据库初始化失败：', err.message);
                            reject(err);
                            return;
                        }
                        
                        // 创建锁文件
                        writeFileSync(LOCK_FILE_NAME, 'Database has been locked, file add in ' + dateFormatter(new Date()));
                        logInfo(`数据库初始化成功：${databasePath}`);
                        resolve();
                    });
                });
            } else {
                // 使用 node:sqlite 同步 API
                const { DatabaseSync } = require('node:sqlite');
                database = new DatabaseSync(databasePath);
                
                try {
                    // 执行初始化脚本
                    database.exec(sqlCreateTables);
                    
                    // 创建锁文件
                    writeFileSync(LOCK_FILE_NAME, 'Database has been locked, file add in ' + dateFormatter(new Date()));
                    logInfo(`数据库初始化成功：${databasePath}`);
                    resolve();
                } catch (initErr: any) {
                    logError('数据库初始化失败：', initErr.message);
                    reject(initErr);
                }
            }
        }
    });
}
