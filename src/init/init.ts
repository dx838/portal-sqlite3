import express from "express"
import {ResponseError} from "../response/Response";
import { DatabaseSync } from 'node:sqlite';
import configDatabase from "../../config/configDatabase.json";
import {
    dateFormatter,
} from "../utility";
const router = express.Router()

import {stat, writeFile, readFileSync } from "fs"
import path from "path"

// 创建 SQLite 数据库连接，从配置文件中读取路径
const databasePath = configDatabase.database || './portal.db';
const database = new DatabaseSync(databasePath);

const LOCK_FILE_NAME = 'DATABASE_LOCK'

router.get('/', (_req, res) => {

    stat(LOCK_FILE_NAME, ((err, _) => {
        if (err) {
            // 如果没有该文件，说明数据库没有初始化过
            createTables()
                .then(() => {
                    writeFile(LOCK_FILE_NAME, 'Database has been locked, file add in ' + dateFormatter(new Date()),err => {
                        if (err){
                            res.send('初始化失败')
                        } else {
                            res.send(
                                '数据库初始化成功：<br>' +
                                `数据库名： ${databasePath} (SQLite)<br>` +
                                '创建了所有必要的表 <br>' +
                                '已创建数据库锁定文件： ' + LOCK_FILE_NAME
                            )
                        }
                    })
                })
                .catch(msg => {
                    res.send(msg)
                })
        } else {
            // 如果已经初始化过了
            res.send('该数据库已被初始化过，如果想重新初始化，请先删除项目中 <b>DATABASE_LOCK</b> 文件')
        }
    }))
})

function createTables(){
    return new Promise((resolve, reject) => {
        try {
            // Read SQL from external SQLite-specific file
            const sqlFilePath = path.join(__dirname, 'init.sqlite.sql')
            const sqlCreateTables = readFileSync(sqlFilePath, 'utf8')
            
            // 直接使用 SQLite 语法，不需要转换
            
            // 执行 SQL 语句
            database.exec(sqlCreateTables)
            
            console.log('-- 2. success: create all tables')
            resolve('成功：新建所有表')
        } catch (err: any) {
            console.log('-- 2. fail: create tables fails, \nwith err info: \n' + err.message)
            reject('失败：新建表失败，\ninfo: \n' + err.message)
        }
    })
}

export default router
