# FLARE — Ghana

**Flood-Linked Alert for Regional Epidemics** - a proof-of-concept dashboard for
flood-triggered malaria early warning in Accra and Kumasi.

Sentinel-1 radar detects new mosquito breeding pools after a flood, and FLARE
issues neighbourhood-level alerts that direct the National Malaria Elimination
Programme's (NMEP) Larval Source Management teams to the right places before the
malaria surge.

**The data are realistic simulated values, not a live feed**, so the app runs
anywhere with no external services or API keys.

## Run it on your computer

    pip install -r requirements.txt
    streamlit run flare_app.py

Opens at http://localhost:8501

## Deploy it online (free)

1. Create a GitHub repository (e.g. `flare-ghana`).
2. Upload `flare_app.py`, `requirements.txt`, and `README.md`.
3. Go to https://share.streamlit.io and sign in with GitHub.
4. New app → pick the repo → main file `flare_app.py` → Deploy.
5. You get a public link like `https://flare-ghana.streamlit.app`.
