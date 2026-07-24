/* ============================================================
   扬州古城 · 盛唐风华 — WebClient JavaScript (原生 WebSocket 版)
   功能：Evennia WebSocket 通信、三栏布局、点击移动、响应式
   ============================================================ */

(function() {
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

    // ============ 状态 ============
    var ws = null;
    var reconnectTimer = null;
    var isConnecting = false;
    var messageBuffer = '';
    var currentRoomName = '';
    var currentRoomDesc = '';

    // ============ WebSocket 通信 ============
    
    function connectWebSocket() {
        if (isConnecting || (ws && ws.readyState === WebSocket.OPEN)) {
            return;
        }
        
        isConnecting = true;
        setStatus('connecting', '● 连接中...');
        
        try {
            // Evennia 的 WebSocket 地址格式
            ws = new WebSocket(ws_url);
        } catch (e) {
            console.error('WebSocket 创建失败:', e);
            scheduleReconnect();
            return;
        }

        ws.onopen = function() {
            isConnecting = false;
            setStatus('connected', '● 已连接');
            addChatMsg('system', '── 欢迎来到扬州古城 · 盛唐风华 ──');
            addChatMsg('system', '点击方向按钮移动，或输入中文指令。');
            clearTimeout(reconnectTimer);
        };

        ws.onmessage = function(event) {
            handleServerMessage(event.data);
        };

        ws.onclose = function(event) {
            isConnecting = false;
            setStatus('disconnected', '● 已断开');
            if (event.wasClean) {
                addChatMsg('system', '连接已关闭。');
            } else {
                addChatMsg('system', '连接异常断开，正在重连...');
                scheduleReconnect();
            }
        };

        ws.onerror = function(error) {
            console.error('WebSocket 错误:', error);
            // onclose 会在 onerror 后触发，所以重连逻辑在 onclose 中处理
        };
    }

    function scheduleReconnect() {
        if (reconnectTimer) {
            clearTimeout(reconnectTimer);
        }
        reconnectTimer = setTimeout(function() {
            addChatMsg('system', '尝试重新连接...');
            connectWebSocket();
        }, 3000);
    }

    function disconnectWebSocket() {
        if (ws) {
            ws.close();
            ws = null;
        }
        if (reconnectTimer) {
            clearTimeout(reconnectTimer);
        }
    }

    function sendCommand(cmd) {
        if (!ws || ws.readyState !== WebSocket.OPEN) {
            addChatMsg('system', '尚未连接到服务器。');
            return;
        }

        // Evennia WebSocket 消息格式: ["text", {"text": "内容"}]
        var message = JSON.stringify(["text", { text: cmd + "\n" }]);
        ws.send(message);
        addChatMsg('sent', '> ' + cmd);
    }

    function handleServerMessage(data) {
        try {
            var parsed = JSON.parse(data);
            
            // Evennia 返回格式: ["text", {"text": "服务器输出"}]
            if (Array.isArray(parsed) && parsed[0] === 'text' && parsed[1]) {
                var text = parsed[1].text || '';
                handleTextMessage(text);
            }
        } catch (e) {
            // 可能是纯文本或其他格式
            handleTextMessage(String(data));
        }
    }

    // ============ 消息处理 ============

    function handleTextMessage(text) {
        var cleanText = stripAnsi(text);
        messageBuffer += cleanText;

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

    // ============ 工具函数 ============

    function stripAnsi(text) {
        return text.replace(/\x1b\[[0-9;]*m/g, '')
                   .replace(/\x1b\]0;.*?\x07/g, '')
                   .replace(/\r/g, '');
    }

    function setStatus(cls, text) {
        connStatus.className = 'connection-status ' + cls;
        connStatus.textContent = text;
    }

    function addChatMsg(type, text) {
        var div = document.createElement('div');
        div.className = 'msg-line msg-' + type;
        div.textContent = text;
        chatMessages.appendChild(div);
        chatMessages.scrollTop = chatMessages.scrollHeight;
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

    // 发送函数
    function sendInput() {
        var text = chatInput.value.trim();
        if (!text) return;
        sendCommand(text);
        chatInput.value = '';
    }

    // 方向按钮
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

    // 键盘快捷键 (仅在桌面端非输入状态)
    document.addEventListener('keydown', function(e) {
        // 不在输入框中时才触发快捷键
        if (document.activeElement === chatInput) return;
        // 移动端不拦截键盘（避免与虚拟键盘冲突）
        if (window.innerWidth <= 768) return;

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

    // 页面隐藏时关闭连接，可见时重新连接
    document.addEventListener('visibilitychange', function() {
        if (document.visibilityState === 'hidden') {
            disconnectWebSocket();
        } else {
            connectWebSocket();
        }
    });

    // ============ 启动 ============
    function start() {
        connectWebSocket();
        chatInput.focus();
    }

    // DOM 就绪后启动
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', start);
    } else {
        start();
    }

})();