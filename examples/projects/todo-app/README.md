# Todo App - Full Stack Application

A full-stack todo application built with React, TypeScript, Express, and Prisma.

## Project Structure

```
todo-app/
├── backend/          # Express API server
│   ├── src/
│   ├── prisma/
│   └── package.json
├── frontend/         # React application
│   ├── src/
│   └── package.json
└── README.md
```

## Quick Start

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file:
```bash
cp .env.example .env
```

4. Generate Prisma client and run migrations:
```bash
npm run prisma:generate
npm run prisma:migrate
```

5. Start development server:
```bash
npm run dev
```

Backend will run on http://localhost:3001

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

Frontend will run on http://localhost:5173

## Features

- ✅ User authentication (signup/login)
- ✅ Create, read, update, delete todos
- ✅ Toggle todo status (pending/completed)
- ✅ Filter todos by status
- ✅ Responsive design
- ✅ Secure JWT authentication
- ✅ Input validation
- ✅ Error handling

## Tech Stack

### Backend
- Node.js + TypeScript
- Express.js
- Prisma ORM
- SQLite database
- JWT authentication
- Bcrypt password hashing
- Zod validation
- Helmet security
- Rate limiting

### Frontend
- React 18 + TypeScript
- Vite
- Zustand state management
- Tailwind CSS
- Responsive design

## Testing

### Backend Tests
```bash
cd backend
npm test
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Production Build

### Backend
```bash
cd backend
npm run build
npm start
```

### Frontend
```bash
cd frontend
npm run build
npm run preview
```

## API Documentation

See `backend/README.md` for detailed API documentation.

## License

MIT
