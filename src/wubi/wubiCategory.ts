import express from "express"
import {ResponseError, ResponseSuccess} from "../response/Response";
import {
    dateFormatter,
    getDataFromDB, operate_db_and_return_added_id, operate_db_without_return,
    verifyAuthorization
} from "../utility";
import {EnumUserGroup} from "../entity/User";
const router = express.Router()

const DB_NAME = 'wubi'
const DATA_NAME = '五笔码表类别'
const CURRENT_TABLE = 'wubi_category'

router.get('/list', (req, res) => {
    verifyAuthorization(req)
        .then(() => {
            // 1. get categories list
            getDataFromDB(DB_NAME, [` select * from ${CURRENT_TABLE} order by sort_id asc`])
                .then(categoryListData => {
                    if (categoryListData) {
                        // categoryListData = [{"id": 1, "name": "主码表", "sort_id": 1, "date_init": "2022-12-09T08:27:08.000Z"}]
                        let tempArray = categoryListData.map(item => {
                            return `count(case when category_id=${item.id} then 1 end) as '${item.id}'`
                        })
                        let sqlArray = []
                        sqlArray.push(`
                                select  
                               ${tempArray.join(', ')},
                                count(*) as amount
                                from wubi_words
                        `)

                        getDataFromDB(DB_NAME, sqlArray, true)
                            .then(countData => {
                                categoryListData.forEach(category => {
                                    category.count = countData[category.id]
                                })
                                res.send(new ResponseSuccess(categoryListData))
                            })
                            .catch(err => {
                                res.send(new ResponseError(err))
                            })
                    } else {
                        res.send(new ResponseError('', '类别列表查询出错'))
                    }
                })
                .catch(err => {
                    res.send(new ResponseError(err,))
                })
        })
        .catch(errInfo => {
            res.send(new ResponseError('', errInfo))
        })
})
router.post('/add', (req, res) => {
    checkCategoryExist(req.body.name)
        .then(dataCategoryExistenceArray => {
            // email 记录是否已经存在
            if (dataCategoryExistenceArray.length > 0){
                return res.send(new ResponseError('', `${DATA_NAME}已存在`))
            } else {
                verifyAuthorization(req)
                    .then(userInfo => {
                        if (userInfo.group_id === EnumUserGroup.ADMIN){
                            let timeNow = dateFormatter(new Date())
                            // query.name_en
                            let sqlArray = []
                            sqlArray.push(`
                                insert into ${CURRENT_TABLE}(name, sort_id, date_init)
                                values ('${req.body.name}', ${req.body.sort_id}, '${timeNow}')`
                            )
                            operate_db_and_return_added_id(userInfo.uid, DB_NAME, DATA_NAME, sqlArray, '添加', res,)
                        } else {
                            res.send(new ResponseError('', '无权操作'))
                        }
                    })
                    .catch(err => {
                        res.send(new ResponseError('', err.message))
                    })
            }
        })
})
router.put('/modify', (req, res) => {
    verifyAuthorization(req)
        .then(userInfo => {
            if (userInfo.group_id === EnumUserGroup.ADMIN){
                let timeNow = dateFormatter(new Date())
                // query.name_en
                let sqlArray = []
                sqlArray.push(`
                    update ${CURRENT_TABLE} set 
                    name = '${req.body.name}',
                    sort_id = '${req.body.sort_id}'
                    where id = '${req.body.id}'
                    `)
                operate_db_and_return_added_id(userInfo.uid, DB_NAME, DATA_NAME, sqlArray, '修改', res,)
            } else {
                res.send(new ResponseError('', '无权操作'))
            }

        })
        .catch(err => {
            res.send(new ResponseError('', err.message))
        })
})
router.delete('/delete', (req, res) => {
    verifyAuthorization(req)
        .then(userInfo => {
            if (userInfo.group_id === EnumUserGroup.ADMIN){
                let sqlArray = []
                sqlArray.push(` delete from ${CURRENT_TABLE} where id = '${req.body.id}' `)
                operate_db_without_return(userInfo.uid, DB_NAME, DATA_NAME, sqlArray, '删除', res)
            } else {
                res.send(new ResponseError('', '无权操作'))
            }
        })
        .catch(err => {
            res.send(new ResponseError('', err.message))
        })
})

// 检查类别是否存在
function checkCategoryExist(categoryName: string){
    let sqlArray = []
    sqlArray.push(`select * from ${CURRENT_TABLE} where name='${categoryName}'`)
    return getDataFromDB( DB_NAME, sqlArray)
}

// 检查类别是否被使用
function checkCategoryInUse(categoryId: number){
    let sqlArray = []
    sqlArray.push(`select count(*) as count from wubi_words where category_id=${categoryId}`)
    return getDataFromDB( DB_NAME, sqlArray, true)
}

// 添加词条类别
router.post('/add-category', (req, res) => {
    const categoryName = req.body.name
    if (!categoryName) {
        return res.send(new ResponseError('', '参数错误，缺少类别名称'))
    }
    
    checkCategoryExist(categoryName)
        .then(existCategory => {
            if (existCategory.length > 0) {
                return res.send(new ResponseError('', '类别名称已存在'))
            }
            
            verifyAuthorization(req)
                .then(userInfo => {
                    if (userInfo.group_id === EnumUserGroup.ADMIN) {
                        let timeNow = dateFormatter(new Date())
                        let sqlArray = []
                        sqlArray.push(`
                            insert into ${CURRENT_TABLE}(name, sort_id, date_init)
                            values ('${categoryName}', 0, '${timeNow}')
                        `)
                        
                        getDataFromDB(DB_NAME, sqlArray)
                            .then(data => {
                                res.send(new ResponseSuccess({ id: data.insertId, name: categoryName }, '添加成功'))
                            })
                            .catch(err => {
                                res.send(new ResponseError(err, '添加失败'))
                            })
                    } else {
                        res.send(new ResponseError('', '无权操作'))
                    }
                })
                .catch(err => {
                    res.send(new ResponseError(err, '认证失败'))
                })
        })
        .catch(err => {
            res.send(new ResponseError(err, '检查类别存在失败'))
        })
})

// 删除词条类别
router.delete('/delete-category', (req, res) => {
    const categoryName = req.body.name
    if (!categoryName) {
        return res.send(new ResponseError('', '参数错误，缺少类别名称'))
    }
    
    verifyAuthorization(req)
        .then(userInfo => {
            if (userInfo.group_id === EnumUserGroup.ADMIN) {
                // 先根据名称获取id
                let sqlArray = []
                sqlArray.push(`select id from ${CURRENT_TABLE} where name='${categoryName}'`)
                
                getDataFromDB(DB_NAME, sqlArray, true)
                    .then(categoryInfo => {
                        if (!categoryInfo) {
                            return res.send(new ResponseError('', '类别不存在'))
                        }
                        
                        const categoryId = categoryInfo.id
                        
                        // 检查类别是否被使用
                        checkCategoryInUse(categoryId)
                            .then(useCount => {
                                if (useCount.count > 0) {
                                    return res.send(new ResponseError('', `类别正在被使用，无法删除。当前使用数量：${useCount.count}`))
                                }
                                
                                // 执行删除
                                let deleteSqlArray = []
                                deleteSqlArray.push(`delete from ${CURRENT_TABLE} where id=${categoryId}`)
                                
                                operate_db_without_return(userInfo.uid, DB_NAME, DATA_NAME, deleteSqlArray, '删除', res)
                            })
                            .catch(err => {
                                res.send(new ResponseError(err, '检查类别使用情况失败'))
                            })
                    })
                    .catch(err => {
                        res.send(new ResponseError(err, '获取类别信息失败'))
                    })
            } else {
                res.send(new ResponseError('', '无权操作'))
            }
        })
        .catch(err => {
            res.send(new ResponseError(err, '认证失败'))
        })
})

export default router

