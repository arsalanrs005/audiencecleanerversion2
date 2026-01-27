# Push Code Using Personal Access Token

Since the SSH key is already in use, we'll use HTTPS with a Personal Access Token instead.

## Step 1: Create Personal Access Token

1. **Go to GitHub Settings** (while logged in as alyanmr738-cyber):
   - Visit: https://github.com/settings/tokens
   - Or: Profile picture → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **Click "Generate new token" → "Generate new token (classic)"**

3. **Fill in the form:**
   - **Note**: `Audience Cleaner Push` (or any name)
   - **Expiration**: Choose how long (90 days, 1 year, or no expiration)
   - **Select scopes**: Check `repo` (this gives full repository access)

4. **Click "Generate token"** at the bottom

5. **IMPORTANT: Copy the token immediately!** 
   - It looks like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - You won't be able to see it again after you leave the page
   - Save it somewhere safe

## Step 2: Push the Code

Once you have the token, I'll help you push. The command will be:

```bash
git push -u origin main
```

When prompted:
- **Username**: `alyanmr738-cyber`
- **Password**: Paste your personal access token (NOT your GitHub password)

## Alternative: Generate New SSH Key

If you prefer SSH, I can help you generate a new SSH key specifically for alyan's account.


