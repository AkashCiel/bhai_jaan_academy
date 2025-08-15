# GitHub Sync Setup Guide

This guide explains how to set up automatic synchronization of `users.json` from your Render deployment back to the reports repository.

## Overview

The system now automatically syncs changes to `users.json` to the reports repository whenever:
- A new user registers
- An existing user's data is updated
- Users are deleted

## Prerequisites

1. **GitHub Personal Access Token**: You need a GitHub token with write access to your repository
2. **Repository Permissions**: The repository must allow commits to the main branch

## Step 1: Create GitHub Personal Access Token

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a descriptive name like "Bhai Jaan Academy Auto-Sync"
4. Select the following scopes:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again)

## Step 2: Configure Environment Variables

### For Local Development

Add the token to your `backend/.env` file:

```bash
# GitHub Configuration for Reports Repository (users.json sync)
REPORTS_GITHUB_TOKEN=your_github_token_here
```

### For Render Deployment

1. Go to your Render dashboard
2. Select your backend service
3. Go to "Environment" tab
4. Add the environment variable:
   - **Key**: `REPORTS_GITHUB_TOKEN`
   - **Value**: Your GitHub token from Step 1
5. Click "Save Changes"
6. Redeploy your service

## Step 3: Verify Configuration

The system will automatically check if GitHub sync is configured. You'll see these log messages:

- ✅ **Configured**: `[User Repository] Successfully synced users.json to reports repository`
- ❌ **Not Configured**: `[User Repository] GitHub sync not configured, skipping sync`

## Step 4: Test the Setup

Run the test script to verify everything works:

```bash
cd backend
python test_github_sync.py
```

Expected output:
```
=== GitHub Sync Test ===
Testing GitHub Sync Service...
GitHub Sync configured: True
Repository: AkashCiel/bhai_jaan_academy_reports
Branch: main
Token configured: Yes

Testing sync with sample data...
[GitHub Sync] Successfully committed users.json to reports repository
✅ GitHub sync test successful!

Testing User Repository with GitHub Sync...
Adding test user...
[User Repository] Successfully synced users.json to reports repository
✅ User repository test successful!

🎉 All tests passed! GitHub sync is working correctly.
```

## How It Works

### Automatic Sync Triggers

The sync happens automatically when:

1. **New User Registration**: When `user_repository.save()` is called
2. **User Updates**: When `user_repository.update()` is called  
3. **Bulk Updates**: When `user_repository.save_all()` is called
4. **User Deletion**: When `user_repository.delete()` is called

### Commit Messages

Each sync creates a commit with a timestamp:
```
Auto-sync users.json - 2024-01-15 14:30:25 UTC
```

### Error Handling

- If GitHub sync fails, the main operation (user save/update) still succeeds
- Errors are logged but don't break the application
- The system gracefully degrades if GitHub is unavailable

## Troubleshooting

### Common Issues

1. **"GitHub sync not configured"**
   - Check that `REPORTS_GITHUB_TOKEN` is set in your environment
   - Verify the token has the correct permissions

2. **"Error committing file: 401"**
   - Your token is invalid or expired
   - Generate a new token and update the environment variable

3. **"Error committing file: 403"**
   - Your token doesn't have write access to the repository
   - Check that the token has the `repo` scope

4. **"Error committing file: 404"**
   - Repository or branch doesn't exist
   - Check the repository name and branch in your configuration

### Debug Mode

To see detailed logs, check your Render logs or run locally with debug output.

## Security Considerations

1. **Token Security**: Never commit your GitHub token to version control
2. **Repository Access**: The token only needs access to this specific repository
3. **Token Rotation**: Consider rotating the token periodically
4. **Environment Variables**: Always use environment variables, never hardcode tokens

## Repository Structure

The sync will maintain this structure in your repository:

```
bhai_jaan_academy/
├── backend/
│   ├── users.json  ← This file gets synced
│   └── ...
├── frontend/
└── ...
```

## Monitoring

You can monitor the sync by:

1. **Checking Render Logs**: Look for sync-related log messages
2. **GitHub Commits**: Check the commit history in your repository
3. **Test Script**: Run the test script periodically to verify functionality

## Rollback

If you need to disable sync temporarily:

1. Remove or comment out the `MAIN_GITHUB_TOKEN` environment variable
2. The system will continue working but won't sync to GitHub
3. Re-enable by setting the token again

## Support

If you encounter issues:

1. Check the logs for specific error messages
2. Verify your GitHub token permissions
3. Test with the provided test script
4. Check that your repository allows commits to the main branch 