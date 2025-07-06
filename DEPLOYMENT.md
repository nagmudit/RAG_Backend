# Deployment Guide for Render

This guide explains how to deploy your RAG Backend to Render.

## 🚀 Quick Deployment Steps

### Method 1: Using Render Dashboard

1. **Fork/Clone Repository**
   - Push your code to GitHub
   - Make sure `start.sh` is executable: `chmod +x start.sh`

2. **Create New Web Service on Render**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New" → "Web Service"
   - Connect your GitHub repository

3. **Configure Service**
   - **Name**: `rag-backend` (or your preferred name)
   - **Runtime**: `Python 3`
   - **Build Command**: `./start.sh`
   - **Start Command**: `./start.sh`
   - **Plan**: Free (or paid for better performance)

4. **Set Environment Variables**
   ```
   MISTRAL_API_KEY=your_actual_mistral_api_key_here
   FAISS_INDEX_PATH=./data/faiss_index
   LOG_LEVEL=INFO
   LLM_MIN_REQUEST_INTERVAL=2.0
   LLM_BASE_DELAY=5.0
   LLM_MAX_RETRIES=3
   EMBEDDING_MIN_REQUEST_INTERVAL=1.0
   EMBEDDING_MAX_RETRIES=2
   EMBEDDING_BATCH_SIZE=20
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete

### Method 2: Using render.yaml (Infrastructure as Code)

1. **Add render.yaml to Repository**
   - The `render.yaml` file is already included
   - Commit and push to your GitHub repository

2. **Connect to Render**
   - Go to Render Dashboard
   - Click "New" → "Blueprint"
   - Connect your repository
   - Render will automatically detect the `render.yaml` configuration

3. **Set Sensitive Environment Variables**
   - Go to your service settings
   - Add your `MISTRAL_API_KEY` in the Environment tab

## 🔧 Production Configuration

### Environment Variables Required:
- **MISTRAL_API_KEY** (required): Your Mistral AI API key
- **FAISS_INDEX_PATH** (optional): Path for FAISS index storage
- **LOG_LEVEL** (optional): Logging level (INFO, DEBUG, WARNING, ERROR)

### Rate Limiting Configuration (optional):
- **LLM_MIN_REQUEST_INTERVAL**: Minimum seconds between LLM requests
- **LLM_BASE_DELAY**: Base delay for LLM rate limiting
- **LLM_MAX_RETRIES**: Maximum retries for LLM requests
- **EMBEDDING_MIN_REQUEST_INTERVAL**: Minimum seconds between embedding requests
- **EMBEDDING_MAX_RETRIES**: Maximum retries for embedding requests
- **EMBEDDING_BATCH_SIZE**: Batch size for embedding requests

## 📊 Production Features

### Gunicorn Configuration:
- **Workers**: 2 (optimized for free tier)
- **Worker Class**: Uvicorn workers for async support
- **Timeout**: 120 seconds (for long-running operations)
- **Max Requests**: 1000 (worker recycling)
- **Bind**: 0.0.0.0:$PORT (Render requirement)

### Health Checks:
- **Health Check Path**: `/api/v1/health`
- **Automatic monitoring**: Render will restart if health check fails

### Persistent Storage:
- **Disk Mount**: 1GB persistent disk for FAISS index storage
- **Mount Path**: `/opt/render/project/src/data`

## 🌐 After Deployment

### Your API will be available at:
```
https://your-service-name.onrender.com
```

### Key Endpoints:
- **API Docs**: `https://your-service-name.onrender.com/docs`
- **Health Check**: `https://your-service-name.onrender.com/api/v1/health`
- **Scrape**: `POST https://your-service-name.onrender.com/api/v1/scrape`
- **Ask**: `POST https://your-service-name.onrender.com/api/v1/ask`
- **Clear**: `POST https://your-service-name.onrender.com/api/v1/clear`

## 🐛 Troubleshooting

### Common Issues:

1. **Build Fails**
   - Check that `start.sh` is executable: `chmod +x start.sh`
   - Verify all dependencies are in `requirements.txt`

2. **Service Won't Start**
   - Check logs in Render dashboard
   - Verify `MISTRAL_API_KEY` is set correctly

3. **Memory Issues**
   - Consider upgrading from free tier
   - Reduce `EMBEDDING_BATCH_SIZE` if needed

4. **Rate Limiting**
   - Adjust rate limiting parameters in environment variables
   - Monitor logs for rate limit errors

### Log Monitoring:
- View logs in Render dashboard
- All application logs are output to stdout/stderr
- Health check status is monitored automatically

## 🔒 Security Notes

- Never commit API keys to your repository
- Use Render's environment variable system for secrets
- Consider using Render's paid plans for production workloads
- CORS is configured to allow all origins (adjust for production if needed)

## 💰 Cost Optimization

### Free Tier Limitations:
- Service sleeps after 15 minutes of inactivity
- 512MB RAM, shared CPU
- 100GB bandwidth per month

### For Production:
- Consider Starter plan ($7/month) or higher
- Provides persistent running and better performance
- More RAM and dedicated CPU resources
