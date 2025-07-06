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
   - **Python Version**: 3.11.5 (specified in runtime.txt)

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

## 🔧 Troubleshooting

### Common Build Issues

#### 1. setuptools.build_meta Import Error
**Error**: `ModuleNotFoundError: No module named 'setuptools.build_meta'`
**Solution**: 
- Python 3.11.5 is specified in `runtime.txt`
- Build dependencies are installed first in `start.sh`
- `pyproject.toml` provides modern build configuration

#### 2. Numpy/FAISS Compatibility Issues
**Error**: Build fails with numpy version conflicts
**Solution**:
- Using numpy 1.24.4 for Python 3.11 compatibility
- FAISS-CPU 1.7.4 is compatible with this numpy version
- Build tools (setuptools, wheel) are installed first

#### 3. Dependency Installation Timeout
**Error**: Build times out during package installation
**Solution**:
- Requirements.txt uses specific, compatible versions
- Consider upgrading to paid plan for faster builds
- Check Render build logs for specific package issues

#### 4. Environment Variable Issues
**Error**: Missing API keys or configuration
**Solution**:
- Set `MISTRAL_API_KEY` in Render dashboard
- Verify all required environment variables are set
- Check `/health` endpoint after deployment

#### 5. Service Won't Start
**Error**: Service fails to start after successful build
**Solution**:
- Check logs for specific error messages
- Verify `start.sh` is executable
- Ensure all dependencies are installed correctly
- Test API key validity

### Testing Deployment

1. **Health Check**: Visit `https://your-service.onrender.com/api/v1/health`
2. **API Documentation**: Visit `https://your-service.onrender.com/docs`
3. **Test Scraping**: Use the `/scrape` endpoint with a simple URL
4. **Test Q&A**: Use the `/ask` endpoint after adding some content

### Performance Optimization

1. **Cold Start Issues**: Free tier services sleep after 15 minutes
2. **Rate Limiting**: Configured for Mistral API limits
3. **Memory Management**: FAISS index stored persistently
4. **Logging**: Comprehensive logging for debugging

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
