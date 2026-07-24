/* ============================================================
   扬州古城 · 盛唐风华 — WebClient JavaScript
   功能：WebSocket通信、消息解析、点击移动、面板更新
   ============================================================ */

(function() {
    'use strict';

    // ============ DOM 引用 ============
    const chatMessages   = document.getElementById('chat-messages');
    const chatInput      = document.getElementById('chat-input');
    const sendBtn        = document.getElementById('send-btn');
    const connStatus     = document.getElementById('conn-status');
    const roomNameEl     = document.getElementById('room-name');
    const roomDescEl     = document.getElementById('room-desc');
    const playerListEl   = document.getElementById('player-list');
    const charListEl     = document.getElementById('char-list');
    const itemListEl     = document.getElementById('item-list');
    const statusRoomEl   = document.getElementById('status-room');
    const statusCoordsEl = document.getElementById('status-coords');

    // ============ 状态 ============
    let ws = null;
    let reconnectTimer = null;
    let reconnectDelay = 2000;
    let currentRoomName = '扬州城中心';
    let currentRoomDesc = '';
    let players = [];
    let characters = [];
    let items = [];
    let messageBuffer = '';
    let isConnected = false;

    // ============ WebSocket 连接 ============
    function connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = protocol + '//' + window.location.host + '/webclient/ws';

        setStatus('connecting', '● 连接中...');

        try {
            ws = new WebSocket(wsUrl);
        } catch (e) {
            setStatus('disconnected', '● 连接失败');
            scheduleReconnect();
            return;
        }

        ws.onopen = function() {
            isConnected = true;
            setStatus('connected', '● 已连接');
            reconnectDelay = 2000;
            addChatMsg('system', '── 欢迎来到扬州古城 · 盛唐风华 ──');
            addChatMsg('system', '点击方向按钮移动，或输入中文指令。');
        };

        ws.onmessage = function(event) {
            handleMessage(event.data);
        };

        ws.onclose = function() {
            isConnected = false;
            setStatus('disconnected', '● 已断开');
            scheduleReconnect();
        };

        ws.onerror = function() {
            setStatus('disconnected', '● 连接出错');
        };
    }

    function scheduleReconnect() {
        if (reconnectTimer) return;
        setStatus('connecting', '● ' + (reconnectDelay / 1000) + '秒后重连...');
        reconnectTimer = setTimeout(function() {
            reconnectTimer = null;
            reconnectDelay = Math.min(reconnectDelay * 1.5, 30000);
            connect();
        }, reconnectDelay);
    }

    function setStatus(cls, text) {
        connStatus.className = 'connection-status ' + cls;
        connStatus.textContent = text;
    }

    // ============ 消息处理 ============
    function handleMessage(rawData) {
        // Evennia 发送 JSON 数组
        let data;
        try {
            data = JSON.parse(rawData);
        } catch (e) {
            return;
        }

        if (!Array.isArray(data)) return;

        const msgType = data[0];
        const payload = data[1] || {};

        switch (msgType) {
            case 'text':
                handleTextMessage(payload.text || '');
                break;
            case 'prompt':
                // 提示符，忽略
                break;
            case 'url':
                // URL 消息
                if (payload.url) {
                    addChatMsg('url', '[链接] ' + payload.url);
                }
                break;
            default:
                break;
        }
    }

    function handleTextMessage(text) {
        // 去除 ANSI 转义码
        const cleanText = stripAnsi(text);

        // 累积到缓冲区
        messageBuffer += cleanText;

        // 检查是否收到完整的房间描述或其他内容
        // 用换行分割
        const lines = messageBuffer.split('\n');

        // 如果最后一行不完整（没有结束标记），保留在缓冲区
        // 否则全部处理
        if (lines.length > 1 || messageBuffer.length > 200) {
            // 处理每一行
            for (let i = 0; i < lines.length; i++) {
                const line = lines[i].trim();
                if (line) {
                    processLine(line);
                }
            }
            messageBuffer = '';
        }
    }

    function processLine(line) {
        // 添加到聊天屏
        addChatMsg('normal', line);

        // 尝试解析房间信息
        // 房间名通常以一些特殊标记开头或包含特定关键词
        parseRoomInfo(line);
        parseExits(line);
        parseContents(line);
    }

    function parseRoomInfo(line) {
        // 房间名通常单独一行，包含城门、城、府、寺、院、楼、驿、渡、湖、园等
        const roomPatterns = [
            /^(.{2,20}(?:城|门|府|寺|院|楼|驿|渡|湖|园|市|码头|之上|之路|之滨|馆|堂|阁|亭|坛|庙|观|庵|殿|宫|坊|铺|店|村|镇|寨|庄|关|口|道|径|路|街|巷|弄|桥|洞|穴|谷|峰|岭|山|坡|岸|滩|岛|洲|海|江|河|运河|运河之上))$/,
        ];

        for (const pattern of roomPatterns) {
            const match = line.match(pattern);
            if (match) {
                const name = match[1];
                if (name.length >= 2 && name.length <= 30) {
                    currentRoomName = name;
                    roomNameEl.textContent = name;
                    statusRoomEl.textContent = name;
                    // 发送看命令获取完整描述
                    // (不在这里发送，避免循环)
                }
            }
        }
    }

    function parseExits(line) {
        // 解析出口信息: "东边是..." "北去..." "西边通往..."
        // 这主要用于更新方向按钮的可用性
    }

    function parseContents(line) {
        // 解析房间内的玩家和物品
        // Evennia 通常不直接发送列表，需要通过 "看" 命令获取
    }

    // ============ ANSI 转义码去除 ============
    function stripAnsi(text) {
        // 去除 ANSI 颜色码
        return text.replace(/\x1b\[[0-9;]*m/g, '')
                   .replace(/\x1b\]0;.*?\x07/g, '')  // 终端标题
                   .replace(/\r/g, '');
    }

    // ============ 聊天消息 ============
    function addChatMsg(type, text) {
        const div = document.createElement('div');
        div.className = 'msg-line msg-' + type;

        // 转义 HTML
        const escaped = escapeHtml(text);
        div.innerHTML = ansiToHtml(escaped);

        chatMessages.appendChild(div);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, function(ch) { return map[ch]; });
    }

    // 将 ANSI 颜色码转换为 HTML span
    function ansiToHtml(text) {
        // 这里处理的是已经去除 ANSI 码的纯文本
        // 如果有需要可以保留颜色
        return text;
    }

    // ============ 发送指令 ============
    function sendCommand(cmd) {
        if (!isConnected || !ws || ws.readyState !== WebSocket.OPEN) {
            addChatMsg('system', '未连接到服务器。');
            return;
        }

        const data = JSON.stringify(['text', { text: cmd + '\n' }]);
        ws.send(data);

        // 在聊天区显示发送的指令
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
        const text = chatInput.value.trim();
        if (!text) return;
        sendCommand(text);
        chatInput.value = '';
    }

    // 方向按钮点击
    document.querySelectorAll('.dir-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const cmd = this.getAttribute('data-cmd');
            if (cmd) {
                sendCommand(cmd);
            }
        });
    });

    // 快速操作按钮
    document.querySelectorAll('.action-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const cmd = this.getAttribute('data-cmd');
            if (cmd) {
                sendCommand(cmd);
            }
        });
    });

    // 键盘快捷键
    document.addEventListener('keydown', function(e) {
        // 如果焦点在输入框，不处理快捷键
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

    // 点击消息区域，自动聚焦输入框
    chatMessages.addEventListener('click', function() {
        chatInput.focus();
    });

    // ============ 监听房间变化并更新面板 ============
    // 通过劫持消息来解析房间内容
    const originalProcessLine = processLine;
    processLine = function(line) {
        originalProcessLine(line);

        // 解析房间描述（多行文本，包含出口信息）
        if (line.includes('你站在') || line.includes('这里是') || line.includes('东边') ||
            line.includes('西边') || line.includes('南边') || line.includes('北边') ||
            line.includes('东去') || line.includes('西去') || line.includes('南去') || line.includes('北去') ||
            line.includes('东门') || line.includes('西门') || line.includes('南门') || line.includes('北门')) {

            // 累积房间描述
            if (currentRoomDesc && !currentRoomDesc.endsWith('\n')) {
                currentRoomDesc += '\n';
            }
            currentRoomDesc += line;
            roomDescEl.textContent = currentRoomDesc;
        }

        // 检测是否有玩家/人物/物品信息
        // 这些通常由 "看" 命令返回
        if (line.startsWith('这里') && line.includes('有')) {
            // "这里有 xxx" - 物品
            updateItemList(line);
        }
    };

    function updateItemList(line) {
        // 简单解析物品
        const match = line.match(/这里有[：:]?\s*(.+)/);
        if (match) {
            const content = match[1];
            const parts = content.split(/[，,]/);
            const newItems = parts.map(function(p) {
                return p.trim().replace(/[。.]$/, '');
            }).filter(function(p) { return p.length > 0; });

            items = newItems;
            renderSideList(itemListEl, items, '📦');
        }
    }

    function renderSideList(el, list, icon) {
        el.innerHTML = '';
        if (list.length === 0) {
            const empty = document.createElement('div');
            empty.className = 'side-empty';
            empty.textContent = '暂无';
            el.appendChild(empty);
        } else {
            list.forEach(function(item) {
                const div = document.createElement('div');
                div.className = 'side-item';
                div.innerHTML = '<span class="icon">' + icon + '</span>' + escapeHtml(item);
                div.title = '点击交互: ' + item;
                div.addEventListener('click', function() {
                    // 点击物品/人物时发送交互命令
                    chatInput.value = '看 ' + item;
                    chatInput.focus();
                });
                el.appendChild(div);
            });
        }
    }

    // ============ 定期刷新房间信息 ============
    // 每次移动后自动 "看" 一下
    let lastAutoLook = 0;
    function autoLook() {
        const now = Date.now();
        if (now - lastAutoLook > 500 && isConnected) {
            lastAutoLook = now;
            // 不自动发送 "看"，避免干扰
            // 用户在移动后会自然收到房间描述
        }
    }

    // ============ 初始化 ============
    function init() {
        connect();
        chatInput.focus();

        // 保持连接活跃
        setInterval(function() {
            if (isConnected && ws && ws.readyState === WebSocket.OPEN) {
                // 发送心跳（空命令）
                // ws.send(JSON.stringify(['text', { text: '\n' }]));
            }
        }, 30000);
    }

    // 启动
    init();

})();