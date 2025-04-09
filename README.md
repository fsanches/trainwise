# TrainWise 🏃🚴 | Strava Data Viewer

**TrainWise** is a FastAPI-based backend that authenticates with the Strava API and fetches athlete activity data.

## 🔧 Features

- OAuth2 integration with Strava
- Secure token storage and refresh
- Endpoint `/strava/sync` returns raw activity data
- Ready for integration with Streamlit dashboards

## 🚀 Getting Started

```bash
git clone https://github.com/YOUR_USERNAME/trainwise.git
cd trainwise
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
./run.sh
