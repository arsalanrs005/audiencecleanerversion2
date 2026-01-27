# SSH Key Setup for GitHub

## Your SSH Key

Your existing SSH public key:
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIM3K08SElfbYHruyFE4f0i+vt97LqT0bN03AJr/Gf7pB arsalanrs@github
```

## Add SSH Key to alyanmr738-cyber Account

1. **Copy your SSH public key** (already shown above)

2. **Go to GitHub Settings:**
   - Visit: https://github.com/settings/keys
   - Make sure you're logged in as `alyanmr738-cyber`

3. **Add New SSH Key:**
   - Click "New SSH key"
   - Title: `Mac - Audience Cleaner` (or any name)
   - Key: Paste the key above
   - Click "Add SSH key"

4. **Test the connection:**
   ```bash
   ssh -T git@github.com
   ```
   Should show: `Hi alyanmr738-cyber! You've successfully authenticated...`

5. **Push your code:**
   ```bash
   git push -u origin main
   ```

## Alternative: Use Personal Access Token (Easier)

If you prefer not to add SSH keys, use HTTPS with a token:

1. **Create Personal Access Token:**
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Name: `Audience Cleaner`
   - Select scope: `repo` (full control)
   - Click "Generate token"
   - **Copy the token immediately** (you won't see it again)

2. **Switch back to HTTPS:**
   ```bash
   git remote set-url origin https://github.com/alyanmr738-cyber/audiencecleaner.git
   ```

3. **Push using token:**
   ```bash
   git push -u origin main
   ```
   - Username: `alyanmr738-cyber`
   - Password: Paste your personal access token


