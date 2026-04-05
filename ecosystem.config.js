module.exports = {
  apps: [{
    name: 'bkns-wiki-bot',
    script: 'bot/wiki_bot.py',
    interpreter: 'python3',
    args: '--daemon',
    cwd: '/home/openclaw/wiki',
    env: {
      PYTHONPATH: '/home/openclaw/wiki',
    },
    // Auto-restart
    autorestart: true,
    max_restarts: 10,
    restart_delay: 5000,
    
    // Logging
    log_file: '/home/openclaw/wiki/logs/wiki-bot-pm2.log',
    error_file: '/home/openclaw/wiki/logs/wiki-bot-error.log',
    out_file: '/home/openclaw/wiki/logs/wiki-bot-out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss',
    merge_logs: true,
    
    // Memory limit (restart if exceeds)
    max_memory_restart: '200M',
    
    // Watch (don't watch, manual restart only)
    watch: false,
  }]
};
