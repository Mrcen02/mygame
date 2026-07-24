/* ============================================================
   扬州古城 · 盛唐风华 — WebClient JavaScript
   使用原生 WebSocket，兼容 Evennia 协议
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
    var everOpen = false;
    var messageBuffer = '';
    var currentRoomName = '';
    var currentRoomDesc = '';
    var initialized = false;

    // ============ WebSocket 连接 ============
    
    function connectWebSocket() {
        if (isConnecting || (ws && ws.readyState !== WebSocket.CLOSED)) {
            return;
        }
        
        isConnecting = true;
        setStatus('connecting', '● 连接中...');
        console.log('[WebSocket] 连接到:', ws_query_url);
        
        try {
            // 复刻 evennia.js：使用 subprotocol "v1.evennia.com"
            ws = new WebSocket(ws_query_url, ['v1.evennia.com']);
        } catch (e) {
            console.error('[WebSocket] 创建失败:', e);
            setStatus('disconnected', '● 不支持 WebSocket');
            scheduleReconnect();
            return;
        }

        ws.onopen = function() {
            isConnecting = false;
            everOpen = true;
            initialized = true;
            clearTimeout(reconnectTimer);
            setStatus('connected', '● 已连接');
            addChatMsg('system', '── 欢迎来到扬州古城 · 盛唐风华 ──');
            addChatMsg('system', '点击方向按钮移动，或输入中文指令。');
        };

        ws.onmessage = function(event) {
            handleServerMessage(event.data);
        };

        ws.onclose = function(event) {
            isConnecting = false;
            setStatus('disconnected', '● 已断开');
            
            if (everOpen) {
                addChatMsg('system', '连接已断开，正在重连...');
                scheduleReconnect();
            } else {
                // 如果从来没有成功打开过，可能是地址或配置问题
                console.error('[WebSocket] 连接从未打开过，code:', event.code);
                addChatMsg('system', '无法连接服务器 (code:' + event.code + ')，3秒后重试...');
                scheduleReconnect();
            }
        };

        ws.onerror = function(error) {
            console.error('[WebSocket] 错误:', error);
            // onclose 会在 onerror 后触发
        };
    }

    function scheduleReconnect() {
        if (reconnectTimer) {
            clearTimeout(reconnectTimer);
        }
        reconnectTimer = setTimeout(function() {
            console.log('[WebSocket] 尝试重连...');
            connectWebSocket();
        }, 3000);
    }

    function disconnectWebSocket() {
        if (ws) {
            try {
                ws.send(JSON.stringify(['websocket_close', [], {}]));
            } catch (e) {
                // ignore
            }
            ws.close();
            ws = null;
        }
        if (reconnectTimer) {
            clearTimeout(reconnectTimer);
            reconnectTimer = null;
        }
    }

    function sendCommand(cmd) {
        if (!ws || ws.readyState !== WebSocket.OPEN) {
            addChatMsg('system', '尚未连接到服务器。');
            return;
        }

        // Evennia 协议: ["text", args, kwargs]
        // args 是数组，kwargs 是对象
        var message = JSON.stringify(['text', [cmd + '\n'], {}]);
        ws.send(message);
        addChatMsg('sent', '> ' + cmd);
    }

    function handleServerMessage(data) {
        try {
            var parsed = JSON.parse(data);
            
            // Evennia 返回格式: [cmdname, args, kwargs]
            // 文本消息: ["text", [text], kwargs]
            if (Array.isArray(parsed)) {
                var cmdname = parsed[0];
                var args = parsed[1] || [];
                var kwargs = parsed[2] || {};
                
                if (cmdname === 'text' && args.length > 0) {
                    handleTextMessage(String(args[0]));
                }
            }
        } catch (e) {
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
        parseObjects(line);
    }

    function parseRoomInfo(line) {
        // 匹配 "你来到了 XXXX" 或单独的房间名
        var comeMatch = line.match(/你来到了\s*(.{2,30})\s*[。！.!]?\s*$/);
        if (comeMatch) {
            currentRoomName = comeMatch[1].trim();
            updateRoomInfo();
            return;
        }

        var roomPatterns = [
            /^(.{2,30}(?:城|门|府|寺|院|楼|驿|渡|湖|园|市|码头|之上|之路|之滨|馆|堂|阁|亭|坛|庙|观|庵|殿|宫|坊|铺|店|村|镇|寨|庄|关|口|道|径|路|街|巷|弄|桥|洞|穴|谷|峰|岭|山|坡|岸|滩|岛|洲|海|江|河))$/,
        ];

        for (var p = 0; p < roomPatterns.length; p++) {
            var match = line.match(roomPatterns[p]);
            if (match) {
                currentRoomName = match[1];
                updateRoomInfo();
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
            line.indexOf('上') !== -1 ||
            line.indexOf('下') !== -1
        )) {
            if (currentRoomDesc) currentRoomDesc += '\n';
            currentRoomDesc += line;
            roomDescEl.textContent = currentRoomDesc;
        }
    }

    function updateRoomInfo() {
        roomNameEl.textContent = currentRoomName;
        statusRoomEl.textContent = currentRoomName;
    }

    function parseObjects(line) {
        // 简单解析房间内的人物/物品
        // 例如 "[|cR店小二|n]" 等 Evennia 格式
        var clean = stripAnsi(line);
        
        if (clean.indexOf('这里 obvious_exits_key') !== -1 || clean.indexOf('出口') !== -1) {
            // 出口信息，忽略
            return;
        }
    }

    // ============ 工具函数 ============

    function stripAnsi(text) {
        if (typeof text !== 'string') return '';
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
        
        // 限制消息数量，防止内存泄漏
        while (chatMessages.children.length > 500) {
            chatMessages.removeChild(chatMessages.firstChild);
        }
    }

    // ============ 事件绑定 ============

    sendBtn.addEventListener('click', sendInput);

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

    document.querySelectorAll('.dir-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var cmd = this.getAttribute('data-cmd');
            if (cmd) sendCommand(cmd);
        });
    });

    document.querySelectorAll('.action-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var cmd = this.getAttribute('data-cmd');
            if (cmd) sendCommand(cmd);
        });
    });

    document.addEventListener('keydown', function(e) {
        if (document.activeElement === chatInput) return;
        if (window.innerWidth <= 768) return;

        switch (e.key) {
            case 'ArrowUp':    e.preventDefault(); sendCommand('北'); break;
            case 'ArrowDown':  e.preventDefault(); sendCommand('南'); break;
            case 'ArrowLeft':  e.preventDefault(); sendCommand('西'); break;
            case 'ArrowRight': e.preventDefault(); sendCommand('东'); break;
            case 'l': case 'L':
                if (!e.ctrlKey && !e.metaKey) { e.preventDefault(); sendCommand('看'); }
                break;
            case 'i': case 'I':
                if (!e.ctrlKey && !e.metaKey) { e.preventDefault(); sendCommand('背包'); }
                break;
            case 'm': case 'M':
                if (!e.ctrlKey && !e.metaKey) { e.preventDefault(); sendCommand('地图'); }
                break;
        }
    });

    chatMessages.addEventListener('click', function() {
        chatInput.focus();
    });

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

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', start);
    } else {
        start();
    }

})();