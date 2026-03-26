# Nepal Airlines vs Druk Air Dashboard

This Streamlit dashboard compares Nepal Airlines and Druk Air using data extracted from:
- Nepal Airlines annual report FY 2079/80
- Nepal Airlines financial statements FY 2079/80
- Drukair Annual Report 2023
- NAC.xlsx analysis workbook

## Files
- `app.py` - main Streamlit app
- `data/` - CSV and JSON source files used by the app
- `images/` - local aircraft images used by the dashboard

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy
Push this folder to GitHub and deploy `app.py` on Streamlit Community Cloud.

## Notes
- Images are stored locally in the repo, so they load reliably on Streamlit.
- The language and layout are intentionally simple for presentation use.
