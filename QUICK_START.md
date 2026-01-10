# Quick Start Guide - Publishing to HACS

## 🚀 Quick Setup (5 minutes)

### Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `ha-3d-printing-costs`
3. **Visibility: Public** ⚠️ (Required for HACS)
4. **DO NOT** add README, .gitignore, or license (we have them)
5. Click **Create repository**

### Step 2: Initialize and Push

```bash
cd /Users/ivantomicic/Desktop/hass-plugins/ha-3d-printing-costs

# Initialize git (if not done)
git init

# Add all files
git add .

# First commit
git commit -m "Initial commit - 3D Printer Energy Tracker v1.0.0"

# Add remote (UPDATE WITH YOUR USERNAME if different from 'ivans-ha-stuff')
git remote add origin https://github.com/ivans-ha-stuff/ha-3d-printing-costs.git

# Push to main
git branch -M main
git push -u origin main
```

### Step 3: Update GitHub Username (if needed)

If your GitHub username is **NOT** `ivans-ha-stuff`, update these files:
- `custom_components/printer_energy/manifest.json` - Replace `ivans-ha-stuff` with your username
- `README.md` - Replace all `ivans-ha-stuff` with your username
- `update_version.sh` - Update the GitHub URL

### Step 4: Enable GitHub Actions

1. Go to your repository on GitHub
2. **Settings** → **Actions** → **General**
3. Workflow permissions: **Read and write permissions**
4. **Save**

### Step 5: Create First Release

```bash
# Tag and push
git tag -a v1.0.0 -m "Initial release v1.0.0"
git push origin v1.0.0
```

GitHub Actions will automatically create the release! 🎉

## 📦 Easy Updates

### Using the Update Script (Easiest)

```bash
./update_version.sh 1.0.1 "Bug fixes and improvements"
```

This script:
- ✅ Updates version in manifest.json
- ✅ Commits changes
- ✅ Pushes to main
- ✅ Creates and pushes release tag
- ✅ GitHub Actions creates the release automatically

### Manual Update

```bash
# 1. Update version in manifest.json
# 2. Commit and push
git add .
git commit -m "Release v1.0.1"
git push

# 3. Create tag
git tag -a v1.0.1 -m "Release v1.0.1"
git push origin v1.0.1
```

## 📋 Checklist

Before publishing:
- [ ] GitHub repository created and is **PUBLIC**
- [ ] All files committed and pushed
- [ ] GitHub username updated everywhere (if different from `ivans-ha-stuff`)
- [ ] GitHub Actions enabled
- [ ] First release created (v1.0.0)

## 🎯 What Users Will See

When users add your repository to HACS:
1. They add: `https://github.com/ivans-ha-stuff/ha-3d-printing-costs`
2. HACS shows: **"3D Printer Energy Tracker"**
3. They can download and install directly
4. Updates show up automatically in HACS

## 📚 Full Documentation

For detailed information:
- **HACS_SETUP.md** - Complete setup guide
- **.github/RELEASE.md** - Release process details
- **README.md** - User documentation

## ⚠️ Important Notes

1. **Repository MUST be public** for HACS
2. **Version format**: Use semantic versioning (1.0.0, 1.1.0, 2.0.0)
3. **Tag format**: Always use `v*` prefix (v1.0.0, not 1.0.0)
4. **Brand name**: "Ivan's HA Stuff" is set in documentation

## 🔧 Troubleshooting

**"HACS can't find integration"**
- ✅ Check repository is public
- ✅ Verify `hacs.json` exists
- ✅ Ensure first release is created with `v*` tag

**"GitHub Actions not working"**
- ✅ Enable Actions in Settings → Actions → General
- ✅ Check workflow permissions

**"Users can't install"**
- ✅ Verify release has correct structure
- ✅ Check `custom_components/printer_energy/` exists in release

---

**Ready to publish! 🚀**

For detailed instructions, see `HACS_SETUP.md`
