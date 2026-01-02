import request from 'supertest';
import express from 'express';
import authRouter from '../routes/auth.routes';
import * as authService from '../services/auth.service';

const app = express();
app.use(express.json());
app.use('/api/auth', authRouter);

jest.mock('../services/auth.service');

describe('Auth Controller', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('POST /api/auth/signup', () => {
    it('should register a new user with valid data', async () => {
      const mockResult = {
        user: { id: '1', email: 'test@example.com', name: 'Test User' },
        token: 'mock-token',
      };

      (authService.signup as jest.Mock).mockResolvedValue(mockResult);

      const response = await request(app)
        .post('/api/auth/signup')
        .send({
          email: 'test@example.com',
          password: 'Password123!',
          name: 'Test User',
        });

      expect(response.status).toBe(201);
      expect(response.body).toHaveProperty('token');
      expect(response.body).toHaveProperty('user');
    });

    it('should return 400 with invalid email', async () => {
      const response = await request(app)
        .post('/api/auth/signup')
        .send({
          email: 'invalid-email',
          password: 'Password123!',
        });

      expect(response.status).toBe(400);
    });

    it('should return 400 with weak password', async () => {
      const response = await request(app)
        .post('/api/auth/signup')
        .send({
          email: 'test@example.com',
          password: '123',
        });

      expect(response.status).toBe(400);
    });
  });

  describe('POST /api/auth/login', () => {
    it('should login with valid credentials', async () => {
      const mockResult = {
        user: { id: '1', email: 'test@example.com', name: 'Test User' },
        token: 'mock-token',
      };

      (authService.login as jest.Mock).mockResolvedValue(mockResult);

      const response = await request(app)
        .post('/api/auth/login')
        .send({
          email: 'test@example.com',
          password: 'Password123!',
        });

      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('token');
    });

    it('should return 400 with missing credentials', async () => {
      const response = await request(app)
        .post('/api/auth/login')
        .send({
          email: 'test@example.com',
        });

      expect(response.status).toBe(400);
    });
  });
});
