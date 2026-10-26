# THREAD web client

The client is a Next.js App Router experience for the P0 flow: **discover → inspect → challenge → confirm → create**. It uses the synthetic project by default and can explicitly request Muse Spark from the model selector.

## Run locally

From `backend/`, install the API extra and start the local API:

```sh
pip install -e '.[api]'
uvicorn thread_engine.api:app --reload
```

From `apps/web/`, install and start the client:

```sh
npm install
npm run dev
```

Open `http://localhost:3000`. For Muse Spark, install the backend `meta` extra, set `MODEL_API_KEY`, verify credits and a spend alert in Meta Billing, then choose Muse Spark in the selector. The fixture path makes no model calls.

The API keeps demo workflow sessions in memory and binds to local development by default. Restarting the backend resets sessions. The generated direction note is deliberately local and requires both a creator context note and explicit confirmation.
