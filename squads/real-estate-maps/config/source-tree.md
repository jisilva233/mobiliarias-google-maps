# Source Tree — real-estate-maps

```
real-estate-maps/
├── scan_agencies.py        # CLI: python scan_agencies.py --city "Curitiba"
├── dashboard.py            # Streamlit: streamlit run dashboard.py
├── requirements.txt
├── .env.example
├── scraper/
│   ├── __init__.py
│   ├── google_maps.py      # Playwright scraper
│   └── parser.py           # Extração de dados do DOM
├── db/
│   ├── __init__.py
│   ├── client.py           # Conexão Supabase
│   └── repository.py       # CRUD real_estate_agencies
├── models/
│   ├── __init__.py
│   └── agency.py           # Dataclass Agency
└── dashboard/
    ├── __init__.py
    ├── components.py        # Componentes Streamlit
    └── map_view.py          # Mapa Pydeck
```
