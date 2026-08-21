# Azure Deployment Guide for Juriscope

This guide describes how to deploy Juriscope to Microsoft Azure using Azure App Service for the backend, Azure Static Web Apps for the frontend, and GitHub Actions for CI/CD automation.

## Prerequisites

- Azure Subscription
- GitHub repository
- Docker Hub or Azure Container Registry (ACR) account
- GitHub secrets configured (see section below)

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Microsoft Azure                       │
│                                                          │
│  ┌──────────────────┐      ┌────────────────────────┐   │
│  │ Azure Static     │      │  Azure App Service     │   │
│  │ Web Apps         │─────▶│  FastAPI (Docker)      │   │
│  │ React Frontend   │HTTPS │  Port 8000             │   │
│  └──────────────────┘      └───────┬────────────────┘   │
│                                    │                     │
│              ┌─────────────────────┼──────────────┐     │
│              ▼                     ▼              ▼     │
│  ┌──────────────────┐  ┌─────────────────┐  ┌────────┐ │
│  │ Azure Blob       │  │ Pinecone        │  │ Groq   │ │
│  │ Storage          │  │ Serverless      │  │ Cloud  │ │
│  │ (PDF files)      │  │ Vector DB       │  │ API    │ │
│  │                  │  │ (text chunks)   │  │Llama3.3│ │
│  └──────────────────┘  └─────────────────┘  └────────┘ │
└─────────────────────────────────────────────────────────┘

GitHub Actions → Azure Container Registry → App Service (CI/CD)
```

## Step 1: Set Up Azure Resources

### 1.1 Create Resource Group

```bash
az group create \
  --name juriscope-rg \
  --location eastus
```

### 1.2 Create Azure Container Registry (ACR)

```bash
az acr create \
  --resource-group juriscope-rg \
  --name juriscoperegistry \
  --sku Basic
```

### 1.3 Create App Service Plan

```bash
az appservice plan create \
  --name juriscope-plan \
  --resource-group juriscope-rg \
  --sku B1 \
  --is-linux
```

### 1.4 Create App Service for Backend

```bash
az webapp create \
  --resource-group juriscope-rg \
  --plan juriscope-plan \
  --name juriscope-backend \
  --deployment-container-image-name-user YOUR_REGISTRY.azurecr.io/juriscope-backend:latest
```

### 1.5 Create Static Web App for Frontend

```bash
az staticwebapp create \
  --name juriscope-frontend \
  --resource-group juriscope-rg \
  --source https://github.com/YOUR_GITHUB_USERNAME/juriscope.git \
  --location eastus \
  --branch main \
  --app-location frontend \
  --output-location dist
```

## Step 2: Configure GitHub Secrets

Add the following secrets to your GitHub repository settings:

```
AZURE_REGISTRY_USERNAME=YOUR_ACR_USERNAME
AZURE_REGISTRY_PASSWORD=YOUR_ACR_PASSWORD
AZURE_BACKEND_APP_NAME=juriscope-backend
AZURE_BACKEND_PUBLISH_PROFILE=<copy from App Service>
AZURE_STATIC_WEB_APPS_API_TOKEN=<get from Static Web App>
```

### To get publish profile:
```bash
az webapp deployment list-publishing-profiles \
  --resource-group juriscope-rg \
  --name juriscope-backend \
  --query "[0].publishUrl" --output tsv
```

### To get ACR credentials:
```bash
az acr credential show \
  --resource-group juriscope-rg \
  --name juriscoperegistry
```

## Step 3: Configure App Settings

Set environment variables for App Service:

```bash
az webapp config appsettings set \
  --resource-group juriscope-rg \
  --name juriscope-backend \
  --settings \
    GROQ_API_KEY="your-groq-key" \
    PINECONE_API_KEY="your-pinecone-key" \
    INDEX_NAME="legal-rag" \
    PINECONE_CLOUD="aws" \
    PINECONE_REGION="us-east-1" \
    GROQ_MODEL="llama-3.3-70b-versatile" \
    AZURE_STORAGE_CONNECTION_STRING="your-blob-connection-string"
```

## Step 4: Configure Container Registry Integration

Enable Azure Container Registry integration with App Service:

```bash
az webapp config container set \
  --name juriscope-backend \
  --resource-group juriscope-rg \
  --docker-custom-image-name juriscoperegistry.azurecr.io/juriscope-backend:latest \
  --docker-registry-server-url https://juriscoperegistry.azurecr.io \
  --docker-registry-server-user $ACR_USERNAME \
  --docker-registry-server-password $ACR_PASSWORD
```

## Step 5: Deploy via GitHub Actions

The `.github/workflows/deploy.yml` pipeline will:

1. **Test:** Run backend tests and linting
2. **Build:** Build frontend and Docker images
3. **Push:** Push images to Azure Container Registry
4. **Deploy:** Deploy to App Service and Static Web Apps

Just push to `main` branch:

```bash
git push origin main
```

GitHub Actions will automatically:
- Build Docker images
- Push to ACR
- Deploy to Azure App Service
- Deploy frontend to Static Web Apps

## Step 6: Verify Deployment

```bash
# Check backend health
curl https://juriscope-backend.azurewebsites.net/

# Check frontend
curl https://juriscope-frontend.azurestaticapps.net/

# View logs
az webapp log tail \
  --resource-group juriscope-rg \
  --name juriscope-backend
```

## Step 7: Optional - Add Azure Blob Storage

For persistent PDF storage:

```bash
az storage account create \
  --name juriscopestorage \
  --resource-group juriscope-rg \
  --location eastus \
  --sku Standard_LRS

# Get connection string
az storage account show-connection-string \
  --name juriscopestorage \
  --resource-group juriscope-rg \
  --query connectionString --output tsv
```

Update App Service with `AZURE_STORAGE_CONNECTION_STRING`.

## Step 8: Optional - Add Application Insights

```bash
az monitor app-insights component create \
  --app juriscope-insights \
  --location eastus \
  --resource-group juriscope-rg

# Add instrumentation key to App Service
az webapp config appsettings set \
  --resource-group juriscope-rg \
  --name juriscope-backend \
  --settings APPINSIGHTS_INSTRUMENTATION_KEY="<key>"
```

## Troubleshooting

### Deployment fails - Docker image not found
- Verify ACR has the image: `az acr repository show-tags --name juriscoperegistry --repository juriscope-backend`
- Check ACR login in GitHub Actions secrets

### App Service won't start
- Check logs: `az webapp log tail --resource-group juriscope-rg --name juriscope-backend`
- Verify environment variables are set
- Ensure PORT is set to 8000 in App Service configuration

### Frontend not loading
- Verify Static Web App deployment: Check Azure Portal → Static Web Apps → juriscope-frontend
- Check build logs in GitHub Actions

## Monitoring

Access monitoring dashboard:

```bash
# Application Insights
az monitor app-insights app show \
  --app juriscope-insights \
  --resource-group juriscope-rg
```

## Rollback

To rollback to previous version:

```bash
# Re-deploy from previous commit
git revert <commit-hash>
git push origin main
```

GitHub Actions will automatically deploy the previous version.

## Cost Estimation

- **App Service Plan (B1):** ~$50/month
- **Static Web Apps:** Free tier available ($0-15/month)
- **Container Registry:** ~$5/month
- **Blob Storage:** ~$0.50/month
- **Total:** ~$55-75/month

## References

- [Azure App Service Documentation](https://docs.microsoft.com/en-us/azure/app-service/)
- [Azure Static Web Apps Documentation](https://docs.microsoft.com/en-us/azure/static-web-apps/)
- [Azure Container Registry Documentation](https://docs.microsoft.com/en-us/azure/container-registry/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
