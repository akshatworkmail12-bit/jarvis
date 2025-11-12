# JARVIS AI - Professional Modular Architecture

<div align="center">
  <img src="https://img.shields.io/badge/version-2.0.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/react-18+-blue.svg" alt="React">
  <img src="https://img.shields.io/badge/typescript-5+-blue.svg" alt="TypeScript">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
</div>

JARVIS AI is a professional, modular artificial intelligence assistant with comprehensive system control capabilities. This project has been completely restructured from a monolithic prototype into a production-ready, scalable application.

## 🚀 Features

### Core Capabilities
- **AI Assistant**: Advanced LLM integration with OpenAI/OpenRouter compatibility
- **Voice Control**: Speech recognition and text-to-speech functionality
- **Screen Analysis**: AI-powered screen vision and interaction
- **System Automation**: Complete keyboard, mouse, and application control
- **File Management**: Intelligent file search and operations
- **Web Integration**: YouTube playback, web browsing, and URL management

### Professional Architecture
- **Modular Design**: Separated concerns with clean service architecture
- **API Versioning**: RESTful API with versioning and comprehensive documentation
- **Security**: Input validation, rate limiting, and secure credential management
- **Logging**: Structured logging with performance monitoring
- **Testing**: Comprehensive testing framework with unit and integration tests
- **CI/CD**: Automated testing, building, and deployment pipelines
- **Containerization**: Docker support for development and production

## 🏗️ Architecture

### Backend (Python/Flask)
```
backend/
├── app/
│   ├── core/              # Core application logic
│   │   ├── config.py      # Configuration management
│   │   ├── exceptions.py  # Custom exceptions
│   │   ├── logging.py     # Logging configuration
│   │   └── security.py    # Security utilities
│   ├── api/               # API routes and handlers
│   │   ├── v1/            # API versioning
│   │   │   ├── commands.py
│   │   │   ├── files.py
│   │   │   ├── media.py
│   │   │   └── system.py
│   │   └── middleware.py  # API middleware
│   ├── services/          # Business logic services
│   │   ├── ai_service.py      # AI/LLM integration
│   │   ├── voice_service.py   # Voice recognition/TTS
│   │   ├── vision_service.py  # Screen analysis
│   │   ├── system_service.py  # System automation
│   │   ├── file_service.py    # File management
│   │   └── media_service.py   # YouTube/web browsing
│   └── extensions/        # Plugin/extension system
├── tests/                 # Test suite
├── requirements/          # Environment-specific dependencies
└── main.py                # Application entry point
```

### Frontend (React/TypeScript)
```
frontend/
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── common/        # Generic components
│   │   ├── layout/        # Layout components
│   │   ├── chat/          # Chat interface
│   │   ├── voice/         # Voice controls
│   │   └── diagnostics/   # System monitoring
│   ├── pages/             # Page components
│   │   ├── Dashboard.tsx
│   │   ├── Chat.tsx
│   │   ├── SystemInfo.tsx
│   │   ├── FileManager.tsx
│   │   ├── VoiceControl.tsx
│   │   └── Settings.tsx
│   ├── services/          # API services
│   ├── hooks/             # Custom React hooks
│   ├── store/             # State management
│   ├── types/             # TypeScript definitions
│   └── styles/            # CSS/styling
├── package.json
└── vite.config.ts         # Build configuration
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- Git

### Backend Setup
```bash
# Clone the repository
git clone <repository-url>
cd jarvis

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements/dev.txt

# Copy environment configuration
cp ../.env.example .env

# Configure your API keys in .env
# LLM_API_KEY=your_api_key_here
```

### Frontend Setup
```bash
# Install Node.js dependencies
cd frontend
npm install

# Start development server
npm run dev
```

### Running the Application
```bash
# Start backend server
cd backend
python main.py --port 5000

# Start frontend (in separate terminal)
cd frontend
npm run dev
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- API Documentation: http://localhost:5000/api/docs

## 🔧 Configuration

### Environment Variables
Create a `.env` file based on `.env.example`:

```env
# Application Settings
NODE_ENV=development
API_HOST=0.0.0.0
API_PORT=5000

# LLM Configuration
LLM_PROVIDER=openrouter
LLM_API_KEY=your_api_key_here
LLM_API_BASE=https://openrouter.ai/api/v1
LLM_MODEL=openai/gpt-oss-20b:free

# Security
SECURITY_JWT_SECRET=your_jwt_secret_key_change_this_in_production

# Voice Configuration
VOICE_ENABLED=true
VOICE_RATE=230
VOICE_VOLUME=1.0
```

## 📚 API Documentation

### Core Endpoints

#### Commands
- `POST /api/v1/commands/execute` - Execute AI command
- `POST /api/v1/commands/interpret` - Interpret command without execution
- `GET /api/v1/commands/history` - Get command history

#### System
- `GET /api/v1/system/info` - Get system information
- `GET /api/v1/system/status` - Get system status and capabilities
- `GET /api/v1/system/screen/capture` - Capture screen
- `POST /api/v1/system/screen/analyze` - Analyze screen with AI

#### Files
- `POST /api/v1/files/search` - Search files and folders
- `GET /api/v1/files/<path>/info` - Get file information
- `POST /api/v1/files/<path>/open` - Open file or folder

#### Media
- `POST /api/v1/media/youtube/search` - Search YouTube
- `POST /api/v1/media/youtube/play` - Play YouTube video
- `POST /api/v1/media/web/search` - Search web

### Example Usage
```javascript
// Execute command
const response = await fetch('/api/v1/commands/execute', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    command: 'open chrome',
    user_id: 'user123'
  })
});

const result = await response.json();
console.log(result.data.response);
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v --cov=app
```

### Frontend Tests
```bash
cd frontend
npm test
npm run test:coverage
```

### Integration Tests
```bash
# Run full test suite
npm run test:e2e
```

## 🚀 Deployment

### Docker Development
```bash
# Build and run with Docker Compose
docker-compose up --build
```

### Production Deployment
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d
```

## 📊 Monitoring & Logging

### Application Logs
```bash
# View real-time logs
tail -f logs/jarvis.log

# View error logs
grep ERROR logs/jarvis.log
```

### Performance Monitoring
- API response times
- Memory usage
- CPU utilization
- Request rates
- Error rates

## 🔒 Security

- Input validation and sanitization
- Rate limiting
- API key protection
- Secure credential storage
- HTTPS enforcement
- Regular security audits

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript strict mode for frontend
- Write comprehensive tests
- Update documentation
- Use conventional commit messages

## 📈 Future Enhancements

### Planned Features
- [ ] Plugin marketplace
- [ ] Multi-modal AI capabilities
- [ ] Cloud synchronization
- [ ] Advanced workflow automation
- [ ] Team collaboration features
- [ ] Mobile app support

### Extension System
The modular architecture supports easy extension:

```python
# Example extension
from backend.app.extensions.base import BaseExtension

class CustomExtension(BaseExtension):
    def __init__(self):
        super().__init__(
            name="custom-extension",
            version="1.0.0",
            description="A custom extension for JARVIS"
        )

    def execute(self, command, context):
        # Custom logic here
        return {"success": True, "response": "Custom command executed"}
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT models
- OpenRouter for AI model access
- The React and Flask communities
- All contributors and beta testers

## 📞 Support

- Issues: [GitHub Issues](https://github.com/your-repo/jarvis/issues)
- Documentation: [Wiki](https://github.com/your-repo/jarvis/wiki)
- Discussions: [GitHub Discussions](https://github.com/your-repo/jarvis/discussions)

---

<div align="center">
  <p>Made with ❤️ by the JARVIS AI team</p>
  <p>Transforming AI interaction from prototype to production</p>
</div>