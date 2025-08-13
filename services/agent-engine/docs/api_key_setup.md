# API Key Configuration Guide

## Quick Start

To use the agent-engine service with Google Gemini models, you need to configure your API keys.

## Step 1: Get a Google API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Get API key"
3. Create a new API key or use an existing one
4. Copy the API key

## Step 2: Configure Your Environment

### Option A: Using .env file (Recommended)

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your Google API key:
```bash
# Model Provider API Keys
GOOGLE_API_KEY=your_actual_api_key_here
```

### Option B: Export as Environment Variable

```bash
export GOOGLE_API_KEY="your_actual_api_key_here"
```

## Step 3: Verify Configuration

Run the test script to verify your configuration:

```bash
cd services/agent-engine
python scripts/test_gemini.py
```

You should see:
- ✓ GOOGLE_API_KEY found
- ✓ Provider initialized successfully
- ✓ API key validated successfully
- ✓ Available models listed
- ✓ Test generation successful

## Available Models

Once configured, you can use these Gemini models:

- **gemini-2.0-flash-exp** - Latest experimental flash model
- **gemini-1.5-flash** - Fast, efficient model (recommended for most tasks)
- **gemini-1.5-flash-8b** - Smaller, faster variant
- **gemini-1.5-pro** - More capable model for complex tasks
- **gemini-1.0-pro** - Stable production model

## Configuration in Agent Templates

When creating agent templates, specify the model in the configuration:

```python
template = {
    "name": "compliance_specialist",
    "model": "gemini-1.5-flash",  # Specify Gemini model
    "modelConfig": {
        "temperature": 0.3,
        "max_tokens": 2000,
        "top_p": 0.95
    }
}
```

## Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `GOOGLE_API_KEY` | **Yes** | Google AI Studio API key | `AIza...` |
| `OPENAI_API_KEY` | No | OpenAI API key (optional) | `sk-...` |
| `ANTHROPIC_API_KEY` | No | Anthropic API key (optional) | `sk-ant-...` |

## Security Best Practices

1. **Never commit API keys** to version control
2. Add `.env` to `.gitignore` (should already be there)
3. Use different API keys for development/staging/production
4. Rotate API keys regularly
5. Set usage limits in Google Cloud Console

## Troubleshooting

### API Key Not Found
```
❌ GOOGLE_API_KEY not found in environment
```
**Solution**: Ensure your `.env` file exists and contains `GOOGLE_API_KEY=your_key`

### Invalid API Key
```
❌ API key validation failed
```
**Solution**: 
- Verify the API key is correct
- Check if the API is enabled in Google Cloud Console
- Ensure you have billing enabled (free tier is usually sufficient)

### Rate Limits
```
Gemini quota exceeded
```
**Solution**:
- Wait a few minutes and retry
- Consider upgrading to a paid plan
- Implement retry logic with exponential backoff

## Cost Considerations

Google Gemini offers:
- **Free tier**: Sufficient for development and testing
  - 60 requests per minute
  - Daily token limits
- **Pay-as-you-go**: For production use
  - Higher rate limits
  - Priority access

For current pricing, see: [Google AI Pricing](https://ai.google.dev/pricing)

## Next Steps

Once your API key is configured:

1. Test the orchestration engine:
```bash
python scripts/test_orchestration.py
```

2. Start the API server:
```bash
uvicorn src.main:app --reload --port 8001
```

3. Create and test agents via the API:
```bash
curl -X POST http://localhost:8001/analyze \
  -H "Content-Type: application/json" \
  -d '{"interaction": {...}, "scorecard_id": "...", "portfolio_id": "..."}'
```