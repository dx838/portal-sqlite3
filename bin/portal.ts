#!/usr/bin/env node

/**
 * Module dependencies.
 */

import app from "../app"
import { autoInitDatabase } from "../src/init/autoInit"
import configProject from "../config/configProject.json"
import { logInfo, logError } from "../src/utility"

const debug = require('debug')('portal:server')

import http from "http"

// 日志配置
const LOG_ENABLED = configProject.log_enabled !== undefined ? configProject.log_enabled : true;

// 全局错误处理
process.on('uncaughtException', (err) => {
    if (LOG_ENABLED) {
        console.error('未捕获的异常:', err);
        console.error(err.stack);
    }
    process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
    if (LOG_ENABLED) {
        console.error('未处理的Promise拒绝:', reason);
        console.error('Promise:', promise);
    }
    process.exit(1);
});

/**
 * Get port from environment and store in Express.
 */

const port = normalizePort(process.env.PORT || configProject.port || '3001')
app.set('port', port)

/**
 * Create HTTP server.
 */

logInfo('正在创建HTTP服务器...');
const server = http.createServer(app)

/**
 * 先初始化数据库，然后启动服务器
 */
logInfo('正在初始化数据库...');
autoInitDatabase()
    .then(() => {
        logInfo('数据库初始化成功，正在启动服务器...');
        
        /**
         * Listen on provided port, on all network interfaces.
         */
        server.listen(port, () => {
            logInfo(`服务器已经成功启动，正在监听端口 ${port}`);
            logInfo(`访问地址: http://localhost:${port}`);
        })
        
        server.on('error', (error) => {
            logError('服务器启动错误:', error);
            onError(error);
        })
        
        server.on('listening', () => {
            logInfo('服务器监听事件触发');
            onListening();
        })
        
        // 保持进程运行
        logInfo('服务器启动完成，进程ID:', process.pid);
    })
    .catch(err => {
        logError('数据库初始化失败，无法启动服务器:', err);
        if (LOG_ENABLED) {
            console.error(err.stack);
        }
        process.exit(1);
    })

/**
 * Normalize a port into a number, string, or false.
 */

function normalizePort(val) {
    const port = parseInt(val, 10)

    if (isNaN(port)) {
        // named pipe
        return val
    }

    if (port >= 0) {
        // port number
        return port
    }

    return false
}

/**
 * Event listener for HTTP server "error" event.
 */

function onError(error: any) {
  if (error.syscall !== 'listen') {
    logError('非监听错误:', error);
    throw error
  }

  var bind = typeof port === 'string'
    ? 'Pipe ' + port
    : 'Port ' + port

  // handle specific listen errors with friendly messages
  switch (error.code) {
    case 'EACCES':
      logError(bind + ' 需要更高的权限');
      process.exit(1)
      break
    case 'EADDRINUSE':
      logError(bind + ' 端口已被占用');
      process.exit(1)
      break
    default:
      logError('其他服务器错误:', error);
      throw error
  }
}

/**
 * Event listener for HTTP server "listening" event.
 */

function onListening() {
  const addr = server.address()
  if (!addr) {
    logError('服务器地址为空');
    process.exit(1);
  }
  
  const bind = typeof addr === 'string'
    ? 'pipe ' + addr
    : 'port ' + addr.port
  
  logInfo('服务器成功监听:', bind)
  logInfo('访问地址: http://localhost:' + port)
  debug('Listening on ' + bind)
}
