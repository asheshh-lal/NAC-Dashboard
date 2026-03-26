# Nepal Airlines Dashboard

A Streamlit dashboard built from the Nepal Airlines FY 2079/80 annual report and financial statement extracts.

## Files
- `app.py` - main dashboard app
- `*.csv` - cleaned operations, delay, cancellation, market-share, and route-share datasets
- `financial_snapshot.json` - financial metrics used by the dashboard
- `requirements.txt` - Python dependencies
- `render.yaml` - optional Render blueprint

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud
1. Create a new GitHub repo.
2. Upload all files from this folder.
3. In Streamlit Community Cloud, create a new app from that repo.
4. Set the main file path to `app.py`.
5. Deploy.

## Deploy on Render
1. Push this folder to a GitHub repo.
2. Create a new Web Service on Render.
3. Use:
   - Build command: `pip install -r requirements.txt`
   - Start command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
4. Deploy.

## Notes
- The dashboard is designed for FY 2079/80 report data.
- If you want to extend the dashboard, add new CSV files and update `app.py`.
