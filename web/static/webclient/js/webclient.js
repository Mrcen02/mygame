/* ============================================================
   扬州古城 · 盛唐风华 — WebClient JavaScript
   使用 Evennia 的 evennia.js 库进行 WebSocket 通信
   功能：三栏布局、点击移动、消息解析、面板更新
   ============================================================ */

$(document).ready(function() {
    'use strict';

    // ============ DOM 引用 ============
    var chatMessages   = document.getElementById('chat-messages');
    var chatInput      = document.getElementById('chat-input');
    var sendBtn        = document.getElementById('send-btn');
    var connStatus     = document.getElementById('conn-status');
    var roomNameEl     = document.getElementById('room-name');
    var roomDescEl     = document.getElementById('room-desc');
    var playerListEl   = document.getElementById('player-list');
    var charListEl     = document.getElementById('char-list');
    var itemListEl     = document.getElementById('item-list');
    var statusRoomEl   = document.getElementById('status-room');
    var statusCoordsEl = document.getElementById('status-coords');

    // ============ 状态 ============
    var currentRoomName = '';
    var currentRoomDesc = '';
    var messageBuffer = '';
    var initialized = false;

    // ============ 初始化 Evennia 连接 ============
    function initConnection() {
        if (typeof Evennia === 'undefined') {
            setStatus('disconnected', '● Evennia.js 未加载');
            return;
        }

        // 初始化 Evennia 通信
        Evennia.init({
            connection: Evennia.WebsocketConnection
        });

        // 监听文本消息
        Evennia.emitter.on('text', function(args, kwargs) {
            if (args && args.length >= 2) {
                handleTextMessage(args[1].text || '');
            }
        });

        // 监听连接状态
        Evennia.emitter.on('connection_open', function() {
            setStatus('connected', '● 已连接');
            addChatMsg('system', '── 欢迎来到扬州古城 · 盛唐风华 ──');
            addChatMsg('system', '点击方向按钮移动，或输入中文指令。');
        });

        Evennia.emitter.on('connection_close', function() {
            setStatus('disconnected', '● 已断开');
        });

        Evennia.emitter.on('connection_error', function() {
            setStatus('disconnected', '● 连接出错');
        });

        // 监听提示符
        Evennia.emitter.on('prompt', function(args, kwargs) {
            // 提示符，可用于检测命令完成
        });

        initialized = true;
    }

    function setStatus(cls, text) {
        connStatus.className = 'connection-status ' + cls;
        connStatus.textContent = text;
    }

    // ============ 消息处理 ============
    function handleTextMessage(text) {
        // 去除 ANSI 转义码
        var cleanText = stripAnsi(text);

        // 累积到缓冲区
        messageBuffer += cleanText;

        // 按换行分割处理
        var lines = messageBuffer.split('\n');
        messageBuffer = '';

        for (var i = 0; i < lines.length; i++) {
            var line = lines[i].trim();
            if (line) {
                processLine(line);
            }
        }
    }

    function processLine(line) {
        addChatMsg('normal', line);
        parseRoomInfo(line);
    }

    function parseRoomInfo(line) {
        // 匹配房间名
        var roomPatterns = [
            /^(.{2,30}(?:城|门|府|寺|院|楼|驿|渡|湖|园|市|码头|之上|之路|之滨|馆|堂|阁|亭|坛|庙|观|庵|殿|宫|坊|铺|店|村|镇|寨|庄|关|口|道|径|路|街|巷|弄|桥|洞|穴|谷|峰|岭|山|坡|岸|滩|岛|洲|海|江|河))$/,
            /^(.{2,30}(?:运河|运河之上))$/,
        ];

        for (var p = 0; p < roomPatterns.length; p++) {
            var match = line.match(roomPatterns[p]);
            if (match && match[1].length >= 2 && match[1].length <= 30) {
                currentRoomName = match[1];
                roomNameEl.textContent = currentRoomName;
                statusRoomEl.textContent = currentRoomName;
                currentRoomDesc = '';
                return;
            }
        }

        // 累积房间描述
        if (currentRoomName && (
            line.indexOf('你站在') !== -1 ||
            line.indexOf('这里是') !== -1 ||
            line.indexOf('东边') !== -1 ||
            line.indexOf('西边') !== -1 ||
            line.indexOf('南边') !== -1 ||
            line.indexOf('北边') !== -1 ||
            line.indexOf('东去') !== -1 ||
            line.indexOf('西去') !== -1 ||
            line.indexOf('南去') !== -1 ||
            line.indexOf('北去') !== -1 ||
            line.indexOf('东门') !== -1 ||
            line.indexOf('西门') !== -1 ||
            line.indexOf('南门') !== -1 ||
            line.indexOf('北门') !== -1 ||
            line.indexOf('东面') !== -1 ||
            line.indexOf('西面') !== -1 ||
            line.indexOf('南面') !== -1 ||
            line.indexOf('北面') !== -1
        )) {
            if (currentRoomDesc) currentRoomDesc += '\n';
            currentRoomDesc += line;
            roomDescEl.textContent = currentRoomDesc;
        }
    }

    // ============ ANSI 转义码去除 ============
    function stripAnsi(text) {
        return text.replace(/\x1b\[[0-9;]*m/g, '')
                   .replace(/\x1b\]0;.*?\x07/g, '')
                   .replace(/\r/g, '');
    }

    // ============ 聊天消息 ============
    function addChatMsg(type, text) {
        var div = document.createElement('div');
        div.className = 'msg-line msg-' + type;
        div.textContent = text;
        chatMessages.appendChild(div);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // ============ 发送指令 ============
    function sendCommand(cmd) {
        if (!initialized) {
            addChatMsg('system', '尚未连接到服务器。');
            return;
        }

        Evennia.msg('text', ['text', { text: cmd + '\n' }]);
        addChatMsg('sent', '> ' + cmd);
    }

    // ============ 事件绑定 ============

    // 发送按钮
    sendBtn.addEventListener('click', function() {
        sendInput();
    });

    // 回车发送
    chatInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            sendInput();
        }
    });

    function sendInput() {
        var text = chatInput.value.trim();
        if (!text) return;
        sendCommand(text);
        chatInput.value = '';
    }

    // 方向按钮点击
    document.querySelectorAll('.dir-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var cmd = this.getAttribute('data-cmd');
            if (cmd) {
                sendCommand(cmd);
            }
        });
    });

    // 快速操作按钮
    document.querySelectorAll('.action-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var cmd = this.getAttribute('data-cmd');
            if (cmd) {
                sendCommand(cmd);
            }
        });
    });

    // 键盘快捷键
    document.addEventListener('keydown', function(e) {
        if (document.activeElement === chatInput) return;

        switch (e.key) {
            case 'ArrowUp':    e.preventDefault(); sendCommand('北'); break;
            case 'ArrowDown':  e.preventDefault(); sendCommand('南'); break;
            case 'ArrowLeft':  e.preventDefault(); sendCommand('西'); break;
            case 'ArrowRight': e.preventDefault(); sendCommand('东'); break;
            case 'l': case 'L':
                if (!e.ctrlKey && !e.metaKey) {
                    e.preventDefault(); sendCommand('看');
                }
                break;
            case 'i': case 'I':
                if (!e.ctrlKey && !e.metaKey) {
                    e.preventDefault(); sendCommand('背包');
                }
                break;
            case 'm': case 'M':
                if (!e.ctrlKey && !e.metaKey) {
                    e.preventDefault(); sendCommand('地图');
                }
                break;
        }
    });

    // 点击消息区域聚焦输入框
    chatMessages.addEventListener('click', function() {
        chatInput.focus();
    });

    // ============ 启动 ============
    function start() {
        initConnection();
        chatInput.focus();
    }

    start();
});