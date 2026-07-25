/* ============================================================
   扬州古城 · 盛唐风华 — WebClient JavaScript
   登录流程：先连接 WebSocket → 发送 connect 指令 → 成功后显示游戏
   ============================================================ */

(function() {
    'use strict';

    // ============ DOM 引用 ============
    var loginOverlay  = document.getElementById('login-overlay');
    var loginBox      = document.getElementById('login-box');
    var loginForm     = document.getElementById('login-form');
    var registerForm  = document.getElementById('register-form');
    var loginError    = document.getElementById('login-error');
    var regError      = document.getElementById('reg-error');
    var loginSubmitBtn = document.getElementById('login-submit-btn');
    var showRegLink   = document.getElementById('show-register');
    var showLoginLink = document.getElementById('show-login');

    var appEl         = document.getElementById('app');
    var chatMessages  = document.getElementById('chat-messages');
    var chatInput     = document.getElementById('chat-input');
    var sendBtn       = document.getElementById('send-btn');
    var connStatus    = document.getElementById('conn-status');
    var roomNameEl    = document.getElementById('room-name');
    var roomDescEl    = document.getElementById('room-desc');
    var statusRoomEl  = document.getElementById('status-room');

    // ============ 状态 ============
    var ws = null;
    var reconnectTimer = null;
    var isConnecting = false;
    var everOpen = false;
    var messageBuffer = '';
    var currentRoomName = '';
    var currentRoomDesc = '';
    var retryCount = 0;
    var MAX_RETRIES = 10;
    var loggedIn = false;
    var pendingLogin = null; // {username, password, isRegister}
    var serverOutput = ''; // 累积服务器输出，用于检测登录结果

    // ============ WebSocket URL 构建 ============
    var candidateUrls = [];
    if (typeof wsurl !== 'undefined' && wsurl) {
        candidateUrls.push(wsurl + '?' + csessid + '&' + cuid + '&' + browser);
    }
    if (typeof ws_query_url !== 'undefined' && ws_query_url) {
        candidateUrls.push(ws_query_url);
    }
    var pageHost = window.location.hostname || 'localhost';
    var pagePort = window.location.port || (window.location.protocol === 'https:' ? '443' : '80');
    var pageScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
    candidateUrls.push(pageScheme + '://' + pageHost + ':4002?' + csessid + '&' + cuid + '&' + browser);
    if (pagePort !== '4002') {
        candidateUrls.push(pageScheme + '://' + pageHost + ':' + pagePort + '?' + csessid + '&' + cuid + '&' + browser);
    }
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
            showLoginError('无法连接服务器，请确认 Evennia 已启动。');
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
            showLoginError('浏览器不支持 WebSocket');
            scheduleReconnect();
            return;
        }

        ws.onopen = function() {
            isConnecting = false;
            everOpen = true;
            retryCount = 0;
            clearTimeout(reconnectTimer);
            setStatus('connected', '● 已连接');
            console.log('[WebSocket] 连接成功');

            // 如果有待登录请求，发送登录指令
            if (pendingLogin) {
                if (pendingLogin.isRegister) {
                    // 注册：先创建账号
                    sendRaw('create ' + pendingLogin.username + ' ' + pendingLogin.password);
                    // 注册成功后会自动登录，在消息处理中检测
                } else {
                    // 登录
                    sendRaw('connect ' + pendingLogin.username + ' ' + pendingLogin.password);
                }
            }
        };

        ws.onmessage = function(event) {
            handleServerMessage(event.data);
        };

        ws.onclose = function(event) {
            isConnecting = false;
            if (!loggedIn) {
                setStatus('disconnected', '● 已断开');
            }
            if (everOpen) {
                retryCount++;
                scheduleReconnect();
            } else {
                currentUrlIndex++;
                retryCount++;
                if (currentUrlIndex < candidateUrls.length) {
                    setTimeout(connectWebSocket, 1000);
                } else {
                    showLoginError('无法连接服务器 (code:' + event.code + ')，请确认 Evennia 已启动。');
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
        if (reconnectTimer) clearTimeout(reconnectTimer);
        reconnectTimer = setTimeout(function() {
            console.log('[WebSocket] 尝试重连...');
            connectWebSocket();
        }, 5000);
    }

    function disconnectWebSocket() {
        if (ws) {
            try { ws.send(JSON.stringify(['websocket_close', [], {}])); } catch (e) {}
            ws.close();
            ws = null;
        }
        if (reconnectTimer) { clearTimeout(reconnectTimer); }
    }

    // 发送原始指令（不显示在聊天区）
    function sendRaw(cmd) {
        if (!ws || ws.readyState !== WebSocket.OPEN) return;
        var message = JSON.stringify(['text', [cmd + '\n'], {}]);
        ws.send(message);
        console.log('[WebSocket] 发送:', cmd);
    }

    // 发送指令（显示在聊天区）
    function sendCommand(cmd) {
        if (!ws || ws.readyState !== WebSocket.OPEN) {
            addChatMsg('system', '尚未连接到服务器。');
            return;
        }
        sendRaw(cmd);
        addChatMsg('sent', '> ' + cmd);
    }

    // ============ 消息处理 ============

    function handleServerMessage(data) {
        try {
            var parsed = JSON.parse(data);
            if (Array.isArray(parsed)) {
                var cmdname = parsed[0];
                var args = parsed[1] || [];
                if (cmdname === 'text' && args.length > 0) {
                    handleTextMessage(String(args[0]));
                }
            }
        } catch (e) {
            handleTextMessage(String(data));
        }
    }

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
        // 检测登录成功
        if (!loggedIn && pendingLogin) {
            checkLoginResult(line);
        }

        if (loggedIn) {
            addChatMsg('normal', line);
            parseRoomInfo(line);
        }
    }

    function checkLoginResult(line) {
        // Evennia 登录失败的常见提示
        if (line.indexOf('登录失败') !== -1 ||
            line.indexOf('密码错误') !== -1 ||
            line.indexOf('密码不正确') !== -1 ||
            line.indexOf('没有这个账号') !== -1 ||
            line.indexOf('账号不存在') !== -1 ||
            line.indexOf('Wrong password') !== -1 ||
            line.indexOf('No account') !== -1 ||
            line.indexOf('Authentication failed') !== -1 ||
            line.indexOf('already connected') !== -1 ||
            line.indexOf('已经在别处') !== -1) {
            pendingLogin = null;
            showLoginError(line);
            return;
        }

        // Evennia 注册失败的提示
        if (line.indexOf('创建失败') !== -1 ||
            line.indexOf('账号已存在') !== -1 ||
            line.indexOf('密码太短') !== -1 ||
            line.indexOf('Account already exists') !== -1 ||
            line.indexOf('Password too short') !== -1) {
            pendingLogin = null;
            showRegError(line);
            return;
        }

        // 注册成功 → 自动登录
        if (pendingLogin && pendingLogin.isRegister && line.indexOf('创建成功') !== -1) {
            // 注册成功后延迟一下再登录
            setTimeout(function() {
                sendRaw('connect ' + pendingLogin.username + ' ' + pendingLogin.password);
                pendingLogin.isRegister = false;
            }, 500);
            return;
        }

        // 检测登录成功标识：收到房间名或欢迎信息
        var successPatterns = [
            /^(.{2,30}(?:城|门|府|寺|院|楼|驿|渡|湖|园|市|码头|之上|之路|之滨|馆|堂|阁|亭|坛|庙|观|庵|殿|宫|坊|铺|店|村|镇|寨|庄|关|口|道|径|路|街|巷|弄|桥|洞|穴|谷|峰|岭|山|坡|岸|滩|岛|洲|海|江|河))$/,
            /你来到了/,
            /你站在/,
            /欢迎/,
            /Welcome/,
            /你进入了/,
        ];

        var matched = false;
        for (var p = 0; p < successPatterns.length; p++) {
            if (successPatterns[p].test(line)) {
                matched = true;
                break;
            }
        }

        if (matched) {
            // 登录成功！
            loggedIn = true;
            pendingLogin = null;
            loginOverlay.style.display = 'none';
            appEl.style.display = 'flex';
            addChatMsg('system', '── 欢迎来到扬州古城 · 盛唐风华 ──');
            addChatMsg('system', '点击方向按钮移动，或输入中文指令。');
            addChatMsg('normal', line);
            parseRoomInfo(line);
            return;
        }
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
        if (connStatus) {
            connStatus.className = 'connection-status ' + cls;
            connStatus.textContent = text;
        }
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

    // ============ 登录/注册 UI 逻辑 ============

    function showLoginError(msg) {
        loginError.textContent = msg || '登录失败，请重试。';
        loginError.style.display = 'block';
        if (loginSubmitBtn) {
            loginSubmitBtn.disabled = false;
            loginSubmitBtn.textContent = '登 录';
        }
    }

    function showRegError(msg) {
        regError.textContent = msg || '注册失败，请重试。';
        regError.style.display = 'block';
    }

    function hideErrors() {
        loginError.style.display = 'none';
        regError.style.display = 'none';
    }

    // 登录表单提交
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        hideErrors();

        var username = document.getElementById('login-username').value.trim();
        var password = document.getElementById('login-password').value.trim();

        if (!username) { showLoginError('请输入账号'); return; }
        if (!password) { showLoginError('请输入密码'); return; }

        loginSubmitBtn.disabled = true;
        loginSubmitBtn.textContent = '连接中...';

        pendingLogin = { username: username, password: password, isRegister: false };
        retryCount = 0;
        currentUrlIndex = 0;
        connectWebSocket();
    });

    // 注册表单提交
    registerForm.addEventListener('submit', function(e) {
        e.preventDefault();
        hideErrors();

        var username = document.getElementById('reg-username').value.trim();
        var password = document.getElementById('reg-password').value.trim();
        var password2 = document.getElementById('reg-password2').value.trim();

        if (!username) { showRegError('请输入账号'); return; }
        if (username.length < 2) { showRegError('账号至少 2 个字符'); return; }
        if (!password) { showRegError('请设置密码'); return; }
        if (password.length < 6) { showRegError('密码至少 6 位'); return; }
        if (password !== password2) { showRegError('两次密码不一致'); return; }

        pendingLogin = { username: username, password: password, isRegister: true };
        retryCount = 0;
        currentUrlIndex = 0;
        connectWebSocket();
    });

    // 切换登录/注册
    showRegLink.addEventListener('click', function(e) {
        e.preventDefault();
        loginForm.style.display = 'none';
        registerForm.style.display = 'block';
        showRegLink.style.display = 'none';
        showLoginLink.style.display = 'inline';
        hideErrors();
    });

    showLoginLink.addEventListener('click', function(e) {
        e.preventDefault();
        registerForm.style.display = 'none';
        loginForm.style.display = 'block';
        showLoginLink.style.display = 'none';
        showRegLink.style.display = 'inline';
        hideErrors();
    });

    // ============ 游戏 UI 事件 ============

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
        if (!loggedIn) return;
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
        } else if (loggedIn) {
            connectWebSocket();
        }
    });

    // ============ 启动 ============
    function start() {
        console.log('[WebSocket] 候选 URL:');
        candidateUrls.forEach(function(url, i) {
            console.log('  ' + (i + 1) + '. ' + url);
        });
        // 不自动连接，等待用户登录
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', start);
    } else {
        start();
    }

})();