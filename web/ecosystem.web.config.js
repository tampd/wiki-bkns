module.exports = {
  apps: [
    {
      name: 'wiki-portal',
      script: './server.js',
      cwd: '/wiki/web',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '256M',
      env: {
        NODE_ENV: 'production',
        WEB_PORT: 3000,
      },
      error_file: '/wiki/logs/web-portal-error.log',
      out_file: '/wiki/logs/web-portal-out.log',
      merge_logs: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    },
  ],
};
