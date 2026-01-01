# Todo App Backend

REST API for Todo application built with Express, TypeScript, and Prisma.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env` file:
```bash
cp .env.example .env
```

3. Generate Prisma client and run migrations:
```bash
npm run prisma:generate
npm run prisma:migrate
```

4. Start development server:
```bash
npm run dev
```

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Create new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user (protected)

### Todos
- `GET /api/todos` - Get all todos (protected)
- `GET /api/todos/:id` - Get todo by ID (protected)
- `POST /api/todos` - Create todo (protected)
- `PATCH /api/todos/:id` - Update todo (protected)
- `DELETE /api/todos/:id` - Delete todo (protected)

## Testing

```bash
npm test
```

## Build

```bash
npm run build
npm start
```
