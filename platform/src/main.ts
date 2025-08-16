import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import dotenv from 'dotenv';
import { initializeDatabase, connectDatabase } from './config/database';
import { redisClient } from './config/redis';
import { AuthController } from './controllers/auth.controller';
import { requireAuthentication, validateInternalServiceToken } from './middleware/auth';
import { logger } from './utils/logger';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 9200;
const authController = new AuthController();

app.use(helmet());
app.use(cors());
app.use(morgan('combined'));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    service: 'tahoe-platform',
    version: '1.0.0',
  });
});

app.get('/', (req, res) => {
  res.json({
    message: 'Tahoe Platform Service',
    version: '1.0.0',
    endpoints: {
      health: '/health',
      auth: '/api/v1/auth',
    },
  });
});

// Authentication routes
app.post('/api/v1/auth/login', authController.login.bind(authController));
app.post('/api/v1/auth/logout', requireAuthentication, authController.logout.bind(authController));
app.post('/api/v1/auth/refresh', authController.refresh.bind(authController));
app.post('/api/v1/auth/validate', validateInternalServiceToken, authController.validate.bind(authController));
app.get('/api/v1/auth/me', requireAuthentication, authController.me.bind(authController));

async function startServer() {
  try {
    initializeDatabase();
    await connectDatabase();
    await redisClient.connect();
    
    app.listen(PORT, () => {
      logger.info(`Platform service started on port ${PORT}`);
      logger.info(`Health check available at http://localhost:${PORT}/health`);
      logger.info(`Authentication API available at http://localhost:${PORT}/api/v1/auth`);
    });
  } catch (error) {
    logger.error('Failed to start server:', error);
    process.exit(1);
  }
}

process.on('SIGTERM', async () => {
  logger.info('SIGTERM received, shutting down gracefully');
  await redisClient.disconnect();
  process.exit(0);
});

process.on('SIGINT', async () => {
  logger.info('SIGINT received, shutting down gracefully');
  await redisClient.disconnect();
  process.exit(0);
});

startServer();

export default app;