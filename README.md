## Setup env

`GOOGLE_API_KEY=`

`MODEL_NAME=`

`RAG_FORCE_REFRESH= # true or false` reload Vector DB 

## Run source

- `uv venv`
- `source .venv/bin/activate`
-  `python -m uvicorn server:app --host 0.0.0.0 --port 8005 --reload`