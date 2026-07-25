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
    var retryCount = 0;
    var MAX_RETRIES = 10;

    // ============ WebSocket URL 构建 ============

    // 尝试多个可能的 WebSocket URL
    var candidateUrls = [];

    // 1. 如果 evennia 模板变量提供了 wsurl
    if (typeof wsurl !== 'undefined' && wsurl) {
        candidateUrls.push(wsurl + '?' + csessid + '&' + cuid + '&' + browser);
    }

    // 2. 如果模板提供了 ws_query_url
    if (typeof ws_query_url !== 'undefined' && ws_query_url) {
        candidateUrls.push(ws_query_url);
    }

    // 3. 自动检测：从当前页面 URL 推断
    // Evennia WebSocket 是独立 TCP 服务，不需要路径，直接 ws://host:port?csessid&cuid&browser
    var pageHost = window.location.hostname || 'localhost';
    var pagePort = window.location.port || (window.location.protocol === 'https:' ? '443' : '80');
    var pageScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';

    // 尝试 Evennia 默认端口 4002（无路径）
    candidateUrls.push(pageScheme + '://' + pageHost + ':4002?' + csessid + '&' + cuid + '&' + browser);

    // 尝试与页面同端口
    if (pagePort !== '4002') {
        candidateUrls.push(pageScheme + '://' + pageHost + ':' + pagePort + '?' + csessid + '&' + cuid + '&' + browser);
    }

    // 去重
    candidateUrls = candidateUrls.filter(function(url, idx, arr) {
        return arr.indexOf(url) === idx;
    });

    var currentUrlIndex = 0;

    // ============ WebSocket 连接 ============

    function connectWebSocket() {
        if (isConnecting || (ws && ws.readyState !== WebSocket.CLOSED)) {
            return;
        }

        if (retryCount >= MAX_RETRIES) {
            setStatus('disconnected', '● 无法连接');
            addChatMsg('system', '多次尝试连接失败，请确认 Evennia 服务已启动。');
            addChatMsg('system', '运行: evennia start');
            return;
        }

        isConnecting = true;
        setStatus('connecting', '● 连接中...');

        var url = candidateUrls[currentUrlIndex];
        console.log('[WebSocket] 尝试连接 (' + (currentUrlIndex + 1) + '/' + candidateUrls.length + '):', url);

        try {
            ws = new WebSocket(url, ['v1.evennia.com']);
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
            retryCount = 0;
            clearTimeout(reconnectTimer);
            setStatus('connected', '● 已连接');
            addChatMsg('system', '── 欢迎来到扬州古城 · 盛唐风华 ──');
            addChatMsg('system', '点击方向按钮移动，或输入中文指令。');
            console.log('[WebSocket] 连接成功:', url);
        };

        ws.onmessage = function(event) {
            handleServerMessage(event.data);
        };

        ws.onclose = function(event) {
            isConnecting = false;
            setStatus('disconnected', '● 已断开');

            if (everOpen) {
                addChatMsg('system', '连接已断开，正在重连...');
                retryCount++;
                scheduleReconnect();
            } else {
                // 从未成功打开，尝试下一个 URL
                currentUrlIndex++;
                retryCount++;
                if (currentUrlIndex < candidateUrls.length) {
                    console.log('[WebSocket] 当前 URL 失败，尝试下一个...');
                    setTimeout(connectWebSocket, 1000);
                } else {
                    console.error('[WebSocket] 所有 URL 都失败了, code:', event.code);
                    addChatMsg('system', '无法连接服务器 (code:' + event.code + ')');
                    addChatMsg('system', '请确认 Evennia 服务已启动: evennia start');
                    retryCount++;
                    scheduleReconnect();
                }
            }
        };

        ws.onerror = function(error) {
            console.error('[WebSocket] 错误:', error);
        };
    }

    function scheduleReconnect() {
        if (reconnectTimer) {
            clearTimeout(reconnectTimer);
        }
        reconnectTimer = setTimeout(function() {
            console.log('[WebSocket] 尝试重连...');
            connectWebSocket();
        }, 5000);
    }

    function disconnectWebSocket() {
        if (ws) {
            try {
                ws.send(JSON.stringify(['websocket_close', [], {}]));
            } catch (e) {}
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
        var message = JSON.stringify(['text', [cmd + '\n'], {}]);
        ws.send(message);
        addChatMsg('sent', '> ' + cmd);
    }

    function handleServerMessage(data) {
        try {
            var parsed = JSON.parse(data);

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
    }

    function parseRoomInfo(line) {
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
        // 显示调试信息
        console.log('[WebSocket] 候选 URL:');
        candidateUrls.forEach(function(url, i) {
            console.log('  ' + (i + 1) + '. ' + url);
        });
        addChatMsg('system', '正在连接服务器...');
        connectWebSocket();
        chatInput.focus();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', start);
    } else {
        start();
    }

})();