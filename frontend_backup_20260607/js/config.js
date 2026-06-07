// ==========================================
// API 地址配置 - 根据环境自动切换
// ==========================================
(function() {
    var host = window.location.hostname;
    var isLocal = host === 'localhost' || host === '127.0.0.1' || host === '0.0.0.0';
    window.APP_CONFIG = {
        API_BASE: isLocal ? 'http://localhost:8000/api' : '/api'
    };
})();
