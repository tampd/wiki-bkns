module.exports = {
  apps: [
    {
      name: 'vertex-proxy',
      script: 'tools/vertex-proxy.js',
      cwd: '/wiki',
      env: {
        NODE_ENV: 'production',
        GOOGLE_APPLICATION_CREDENTIALS: '/wiki/service-account.json',
        GOOGLE_CLOUD_PROJECT: 'ai-test-491016',
        GOOGLE_CLOUD_LOCATION: 'us-central1'
      },
      max_restarts: 10,
      restart_delay: 3000,
      autorestart: true,
      watch: false,
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      error_file: '/wiki/logs/vertex-proxy-error.log',
      out_file: '/wiki/logs/vertex-proxy-out.log'
    },
    {
      name: 'openclaw-gateway',
      script: 'openclaw',
      args: 'gateway',
      interpreter: 'none',
      cwd: '/wiki',
      env: {
        NODE_ENV: 'production',
        GOOGLE_APPLICATION_CREDENTIALS: '/wiki/service-account.json',
        GOOGLE_CLOUD_PROJECT: 'ai-test-491016',
        GOOGLE_CLOUD_LOCATION: 'us-central1'
      },
      max_restarts: 10,
      restart_delay: 5000,
      autorestart: true,
      watch: false,
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      error_file: '/wiki/logs/openclaw-error.log',
      out_file: '/wiki/logs/openclaw-out.log'
    }
  ]
};
