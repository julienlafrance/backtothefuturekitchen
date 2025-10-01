# 🍽️ Mangetamain Analytics

Data AI project for Telecom Paris - Food recommendation system based on Kaggle Food.com dataset

## 📁 Project Structure

```
mangetamain/
├── 00_preprod/          # Development environment
│   ├── src/             # Streamlit app source code
│   ├── tests/           # Unit & integration tests
│   ├── data/            # Food.com dataset (excluded from Git)
│   └── requirements.txt # Python dependencies
├── 10_prod/           # Production environment (coming soon)
├── 30_docker/           # Docker containerization
├── 90_doc/              # Documentation & reports
└── README.md            # This file
```

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/julienlafrance/backtothefuturekitchen
cd backtothefuturekitchen

# Run with Docker Compose
cd 30_docker/
docker-compose up -d
```

Access the app at: **http://localhost:8501**

### Option 2: Local Development

```bash
cd 00_preprod/
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# Run the Streamlit app
streamlit run src/mangetamain_analytics/main.py
```

## 📊 Data Setup

Download the Food.com dataset from Kaggle and place CSV files in `00_preprod/data/`:
- `RAW_interactions.csv`
- `RAW_recipes.csv` 
- `PP_recipes.csv`
- `PP_users.csv`
- etc.

> **Note**: Data files are excluded from Git due to size. You need to download them separately.

## 🐳 Docker Usage

### Frontend with Docker

```bash
cd 30_docker/

# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

### Environment Variables

Copy and configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## 🔧 Environments

- **00_preprod/** - Full development setup with Streamlit analytics app
- **30_docker/** - Production-ready Docker containerization with frontend
- **90_doc/** - Project documentation and analysis reports

## 📊 Features

- Interactive data visualization with Streamlit
- DuckDB database for efficient data processing
- Food recommendation analytics
- User behavior analysis
- Recipe clustering and insights
- Dockerized deployment for production

## 🛠️ Tech Stack

- **Frontend**: Streamlit (Dockerized)
- **Database**: DuckDB
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly, Matplotlib
- **Package Management**: UV
- **Containerization**: Docker, Docker Compose

## 📝 Documentation

Detailed documentation available in:
- `00_preprod/README.md` - Development setup
- `30_docker/README_DOCKER.md` - Docker deployment guide
- `90_doc/` - Analysis reports and guides

## 🤝 Contributing

1. Clone the repository
2. Setup development environment in `00_preprod/` or use Docker
3. Make your changes
4. Run tests: `pytest tests/`
5. Test with Docker: `cd 30_docker && docker-compose up`
6. Submit a pull request

## 🚀 Deployment

For production deployment, use the Docker setup:

```bash
cd 30_docker/
docker-compose -f docker-compose.yml up -d
```

The application will be available on port 8501 with automatic restarts and proper logging.

---

**Mangetamain Analytics** - Transform culinary data into actionable insights! 🍽️📊
