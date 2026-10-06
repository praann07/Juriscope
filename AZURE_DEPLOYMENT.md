# Azure Deployment Guide for Juriscope

Juriscope runs as **one Azure App Service** (Linux, Docker). The same container serves:

- the FastAPI API (`/chat`, `/upload`, sessions, sources, `/api/health`)
- the built React frontend (`/`)

Pinecone (vector database) and Groq (LLM) are external hosted services. The browser talks to the same origin it was loaded from, so no CORS setup is needed.

```
Browser ──HTTPS──▶ Azure App Service (B1, Docker container)
                     ├─ /            React frontend (built into the image)
                     └─ /chat, /upload, ...  FastAPI
                          ├─▶ Pinecone (vector index)
                          └─▶ Groq (Llama/Qwen LLM)
```

Images are pushed to Docker Hub (free) rather than Azure Container Registry, to save credits.

## Before you start

- An Azure subscription (student or free trial) and the Azure CLI (`az`)
- Docker Desktop, running
- A Docker Hub account. Replace `YOUR_DOCKERHUB_USER` below with your username.
- Your `.env` values: `GROQ_API_KEY`, `PINECONE_API_KEY`, `INDEX_NAME`

## Step 1: Build and test the image locally

```bash
docker build -t YOUR_DOCKERHUB_USER/juriscope:v1 .
docker run --rm -p 8000:8000 --env-file .env juriscope:v1
```

Open http://localhost:8000 and check that the app loads. `.env` is excluded from the image, so keys are passed in at run time and never baked in.

## Step 2: Push the image to Docker Hub

```bash
docker login
docker push YOUR_DOCKERHUB_USER/juriscope:v1
```

Make the repository **public** on Docker Hub, which lets App Service pull it without credentials. The image contains no secrets. If you prefer a private repository, add `--container-registry-user` and `--container-registry-password` to the `az webapp create` command below.

## Step 3: Create the Azure resources

```bash
az login
az group create --name juriscope-rg --location eastus

az appservice plan create \
  --name juriscope-plan \
  --resource-group juriscope-rg \
  --sku B1 \
  --is-linux

az webapp create \
  --resource-group juriscope-rg \
  --plan juriscope-plan \
  --name YOUR-UNIQUE-APP-NAME \
  --container-image-name YOUR_DOCKERHUB_USER/juriscope:v1
```

`YOUR-UNIQUE-APP-NAME` must be unique across all of Azure. Your site will be at `https://YOUR-UNIQUE-APP-NAME.azurewebsites.net`.

`B1` has 1.75 GB of RAM, which is the smallest paid tier that can hold the embedding model. The free `F1` tier has 1 GB and will not fit it.

## Step 4: Set the app settings

Replace the placeholders with your real values. Do not commit these to Git.

```bash
az webapp config appsettings set \
  --resource-group juriscope-rg \
  --name YOUR-UNIQUE-APP-NAME \
  --settings \
    GROQ_API_KEY="your-groq-key" \
    PINECONE_API_KEY="your-pinecone-key" \
    INDEX_NAME="legal-rag" \
    PINECONE_CLOUD="aws" \
    PINECONE_REGION="us-east-1" \
    GROQ_MODEL="qwen/qwen3.8-27b" \
    JURISCOPE_USERNAME="choose-a-username" \
    JURISCOPE_PASSWORD="choose-a-strong-password" \
    WEBSITES_PORT="8000"
```

- `WEBSITES_PORT` tells App Service which port the container listens on.
- `JURISCOPE_USERNAME` and `JURISCOPE_PASSWORD` turn on the login prompt. Turn them on for any public URL, so strangers cannot use your Groq and Pinecone quota.

You can also set these in the Azure portal under **Settings → Environment variables**.

## Step 5: Verify

```bash
curl https://YOUR-UNIQUE-APP-NAME.azurewebsites.net/api/health
```

You should get `{"status":"ok", ...}`. Then open the site in a browser. With login enabled, the browser asks for the username and password first.

Check the logs in the portal (**Monitoring → Log stream**), or run:

```bash
az webapp log tail --resource-group juriscope-rg --name YOUR-UNIQUE-APP-NAME
```

## Updating the app later

Use a new tag each time, so App Service pulls the new image reliably:

```bash
docker build -t YOUR_DOCKERHUB_USER/juriscope:v2 .
docker push YOUR_DOCKERHUB_USER/juriscope:v2

az webapp config container set \
  --resource-group juriscope-rg \
  --name YOUR-UNIQUE-APP-NAME \
  --container-image-name YOUR_DOCKERHUB_USER/juriscope:v2
```

## Troubleshooting

- **Site shows "Application Error" or never starts:** check the log stream. Confirm `WEBSITES_PORT=8000` is set and all three keys (`GROQ_API_KEY`, `PINECONE_API_KEY`, `INDEX_NAME`) are present.
- **The first chat or upload is very slow:** this is expected. The embedding model (several hundred MB) downloads and loads on first use. Later requests are faster.
- **Out of memory during an upload or chat:** the container is restarting because B1's 1.75 GB is not enough. Scale up with `az appservice plan update --name juriscope-plan --resource-group juriscope-rg --sku B2` (roughly double the price).
- **Login prompt keeps appearing:** check that `JURISCOPE_USERNAME` and `JURISCOPE_PASSWORD` match what you type.

## Cost

Prices change, so check the Azure pricing calculator before you deploy. Rough figures:

- **App Service Plan (B1, 1.75 GB RAM):** about $13/month
- **Docker Hub:** free for public images
- **Total:** about $13/month while running

**To protect your credits, delete everything when you are not presenting:**

```bash
az group delete --name juriscope-rg --yes
```

Redeploying later means repeating Step 3 (or re-creating the app with the same name).

## Not covered by this guide

- **GitHub Actions CI/CD:** `.github/workflows/deploy.yml.disabled` still targets the old Azure Container Registry and Static Web Apps setup. It is disabled and needs rewriting before you use it.
- **Azure Blob Storage and Application Insights:** not used by the current code.

## Verification status

The commands above were checked against the installed Azure CLI's help text, and the Docker image was run and tested locally. The Azure commands themselves have not been run against a live subscription yet, so expect small adjustments on the first real deployment (for example, region or SKU availability on a student subscription).
