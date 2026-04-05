'use strict';

/**
 * POST /api/trigger
 * Body: { action: "extract" | "compile" | "full" }
 */
function triggerRoute(router, pipelineRunner) {
  router.post('/api/trigger', async (req, res) => {
    try {
      const { action } = req.body;
      const validActions = ['extract', 'compile', 'full'];

      if (!action || !validActions.includes(action)) {
        return res.status(400).json({
          error: `Action không hợp lệ. Cho phép: ${validActions.join(', ')}`,
        });
      }

      if (pipelineRunner.isRunning()) {
        return res.status(409).json({
          error: 'Pipeline đang chạy. Vui lòng đợi hoàn tất.',
        });
      }

      const jobId = await pipelineRunner.trigger(action);

      res.json({
        job_id: jobId,
        status: 'started',
        action,
      });
    } catch (err) {
      console.error('[TRIGGER] Error:', err);
      res.status(500).json({ error: err.message || 'Trigger failed' });
    }
  });
}

module.exports = { triggerRoute };
