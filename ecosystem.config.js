module.exports = {
  apps: [
    {
      name: 'bkns-wiki-bot',
      script: 'bot/wiki_bot.py',
      interpreter: 'python3',
      args: '--daemon',
      cwd: '/home/openclaw/wiki',
      env: {
        PYTHONPATH: '/home/openclaw/wiki',
      },
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000,
      log_file: '/home/openclaw/wiki/logs/wiki-bot-pm2.log',
      error_file: '/home/openclaw/wiki/logs/wiki-bot-error.log',
      out_file: '/home/openclaw/wiki/logs/wiki-bot-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      merge_logs: true,
      max_memory_restart: '200M',
      watch: false,
    },
    {
      // Daily health check + conflict scan at 7:00 AM Vietnam time (00:00 UTC)
      name: 'bkns-cron-daily',
      script: 'tools/cron_tasks.py',
      interpreter: 'python3',
      args: '--task all',
      cwd: '/home/openclaw/wiki',
      env: {
        PYTHONPATH: '/home/openclaw/wiki',
      },
      cron_restart: '0 0 * * *',  // Daily at midnight UTC (7am Vietnam)
      autorestart: false,
      watch: false,
      out_file: '/home/openclaw/wiki/logs/cron-daily-out.log',
      error_file: '/home/openclaw/wiki/logs/cron-daily-error.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
    },
    {
      // Weekly promo scrape on Monday 9:00 AM Vietnam time (02:00 UTC)
      name: 'bkns-cron-promo',
      script: 'tools/cron_tasks.py',
      interpreter: 'python3',
      args: '--task promo-scrape',
      cwd: '/home/openclaw/wiki',
      env: {
        PYTHONPATH: '/home/openclaw/wiki',
      },
      cron_restart: '0 2 * * 1',  // Monday 2:00 UTC (9am Vietnam)
      autorestart: false,
      watch: false,
      out_file: '/home/openclaw/wiki/logs/cron-promo-out.log',
      error_file: '/home/openclaw/wiki/logs/cron-promo-error.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
    },
  ]
};
