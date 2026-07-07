# Cryptography Learning Sandbox & Cybersecurity Toolkit

A production-grade, enterprise-level Cryptography & Cybersecurity Learning Platform built for universities, security bootcamps, and cybersecurity labs.

## Features

- **Symmetric Cryptography**: AES-GCM, AES-CBC, AES-CTR, ChaCha20, Fernet
- **Asymmetric Cryptography**: RSA, ECC, Ed25519 (Key Generation, Encryption, Signatures)
- **Hashing**: SHA-2, SHA-3, BLAKE2, MD5 comparison and avalanche effect demonstration
- **Password Security**: Strength analysis, KDFs (bcrypt, argon2, pbkdf2), Password Generator
- **Digital Signatures**: PKI fundamentals, message signing, and tamper detection
- **Classical Ciphers**: Caesar, Vigenere, Playfair, Rail Fence, One-Time Pad
- **Steganography**: LSB (Least Significant Bit) image steganography
- **Key Exchange**: Interactive Diffie-Hellman simulation
- **Security Tools**: JWT Decoder, HMAC Generator, Base64, Hex Converter, UUID/CSPRNG

## Architecture

This project is built using a decoupled architecture:

- **Backend (Python / FastAPI)**:
  - Asynchronous endpoints and DB operations (`asyncpg` / `aiosqlite`).
  - Production security libraries: `cryptography`, `bcrypt`, `argon2-cffi`, `jose`.
  - Layered design: Controllers -> Services -> Repositories/Models.
  - SQLite database for easy development and portability.

- **Frontend (React / Next.js)**:
  - Next.js 14 (App Router) with React Server Components paradigm where applicable.
  - Enterprise UI/UX with Tailwind CSS, customized with cyber/neon themes.
  - Interactive charts (`recharts`), customized components, dynamic client-side lab simulations.
  - Fully responsive, accessible, and fast.

## Setup & Deployment

### Quick Start with Docker (Recommended)

Make sure you have Docker and Docker Compose installed.

1. Clone the repository (if not already done).
2. Run the application:
   ```bash
   docker-compose up --build
   ```
3. Open your browser:
   - Frontend app: [http://localhost:3000](http://localhost:3000)
   - Backend API Docs (Swagger): [http://localhost:8000/docs](http://localhost:8000/docs)

### Manual Setup (Local Development)

#### 1. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
The backend will run on `http://localhost:8000`.

#### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```
The frontend will run on `http://localhost:3000`.

## Directory Structure

```
crypto/
├── backend/                  # FastAPI Application
│   ├── app/
│   │   ├── api/              # Route controllers
│   │   ├── core/             # Config, DB, Security
│   │   ├── models/           # SQLAlchemy Models
│   │   ├── schemas/          # Pydantic validation schemas
│   │   └── services/         # Cryptography logic
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                 # Next.js Application
│   ├── src/
│   │   ├── app/              # Next.js App Router (Pages & Layout)
│   │   ├── components/       # Reusable UI components
│   │   ├── hooks/            # Custom React hooks
│   │   ├── lib/              # API clients & utilities
│   │   └── types/            # TypeScript definitions
│   ├── tailwind.config.ts    # UI theming
│   ├── package.json
│   └── Dockerfile
└── docker-compose.yml        # Multi-container setup
```

## Contributing

Designed as a B.E./B.Tech final-year project, the platform is structured for easy extension. To add a new lab:
1. Create a service in `backend/app/services/`
2. Expose an endpoint in `backend/app/api/v1/`
3. Add API definitions in `frontend/src/lib/api.ts`
4. Build the UI in `frontend/src/app/labs/`

## License

This project is licensed under the MIT License.
