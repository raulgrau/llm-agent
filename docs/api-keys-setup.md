# 🔑 API Keys Setup Guide

This guide will walk you through obtaining all the necessary API keys for the Automated Lecture Notetaker.

## 📋 Required API Keys

1. **YouTube Data API v3** - For accessing YouTube video metadata and transcripts
2. **Google AI Studio API** - For AI-powered content processing with Gemini
3. **Notion API** - For creating structured notes in Notion

---

## 🎥 YouTube Data API v3 Setup

### Step 1: Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a project"** → **"New Project"**
3. Enter a project name (e.g., "Lecture Notetaker")
4. Click **"Create"**

### Step 2: Enable YouTube Data API v3

1. In your Google Cloud project dashboard
2. Go to **"APIs & Services"** → **"Library"**
3. Search for **"YouTube Data API v3"**
4. Click on it and press **"Enable"**

### Step 3: Create API Credentials

1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"+ Create Credentials"** → **"API Key"**
3. Copy the generated API key
4. (Optional) Click **"Restrict Key"** to limit usage:
   - Under "API restrictions", select "Restrict key"
   - Choose "YouTube Data API v3"
   - Save changes

### Step 4: Add to Environment

Add to your `.env` file:
```env
YOUTUBE_API_KEY=your_youtube_api_key_here
```

### ⚠️ Important Notes

- **Free Quota**: 10,000 units per day (sufficient for ~100 videos)
- **Rate Limits**: 100 requests per 100 seconds per user
- **Keep it secure**: Never commit API keys to version control

---

## 🤖 Google AI Studio (Gemini) API Setup

### Step 1: Access Google AI Studio

1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account

### Step 2: Create API Key

1. Click **"Get API Key"** in the left sidebar
2. Click **"Create API Key"**
3. Choose **"Create API key in new project"** (recommended)
4. Copy the generated API key

### Step 3: Add to Environment

Add to your `.env` file:
```env
GOOGLE_AI_API_KEY=your_google_ai_api_key_here
```

### ⚠️ Important Notes

- **Free Tier**: Generous free usage limits for Gemini
- **Models Available**: Currently using `gemini-2.5-flash-lite`
- **Security**: Keep your API key confidential

---

## 📝 Notion API Setup

> **Note**: You can use `--no-notion` flag to skip this and output notes to console only.

### Step 1: Create Notion Integration

1. Go to [Notion Developers](https://www.notion.so/my-integrations)
2. Click **"+ New integration"**
3. Fill in the details:
   - **Name**: "Lecture Notetaker"
   - **Logo**: Upload an icon (optional)
   - **Associated workspace**: Select your workspace
4. Click **"Submit"**

### Step 2: Get Integration Token

1. After creation, you'll see the **"Internal Integration Token"**
2. Click **"Show"** and copy the token
3. It should start with `secret_`

### Step 3: Create a Database

1. In Notion, create a new page
2. Add a database (table) to the page
3. Make sure it has at least one property:
   - **Name** (Title property) - this is required

### Step 4: Share Database with Integration

1. Click the **"Share"** button on your database page
2. Click **"Invite"**
3. Search for your integration name ("Lecture Notetaker")
4. Give it **"Can edit"** permissions
5. Click **"Invite"**

### Step 5: Get Database ID

1. Copy the database URL from your browser
2. The database ID is the long string between the last `/` and the `?`
   ```
   https://www.notion.so/workspace/DatabaseName-DATABASE_ID_HERE?v=...
   ```
3. Copy just the database ID part

### Step 6: Add to Environment

Add to your `.env` file:
```env
NOTION_TOKEN=secret_your_notion_token_here
NOTION_DATABASE_ID=your_database_id_here
```

### ⚠️ Important Notes

- **Database Structure**: Only requires a "Name" title property
- **Permissions**: Integration needs "Can edit" access
- **Sharing**: Make sure the database is shared with your integration

---

## 🔧 Environment Configuration

### Complete .env File Example

```env
# YouTube API
YOUTUBE_API_KEY=AIzaSyC-your-youtube-api-key-here

# Google AI (Gemini)
GOOGLE_AI_API_KEY=AIzaSyD-your-google-ai-api-key-here

# Notion API (Optional)
NOTION_TOKEN=secret_your_notion_integration_token_here
NOTION_DATABASE_ID=12345678-1234-1234-1234-123456789abc

# Optional: Custom settings
DEFAULT_MODEL=gemini-2.5-flash-lite
SUMMARY_LENGTH=300
DEFAULT_CHAPTERS=5
```

### Security Best Practices

1. **Never commit `.env` files** to version control
2. **Use environment variables** in production
3. **Regularly rotate API keys** if compromised
4. **Restrict API key permissions** where possible
5. **Monitor usage** to detect unauthorized access

---

## ✅ Verification

After setting up your API keys, verify everything works:

```bash
python quick_start.py
```

This will test all your API connections and confirm everything is working properly.




