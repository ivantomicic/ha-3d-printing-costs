# HACS Setup Guide - Ivan's HA Stuff

This guide will help you prepare and publish this integration to HACS.

## ✅ Pre-requisites

1. **GitHub Account**: You need a GitHub account
2. **Repository Created**: Create a repository named `ha-3d-printing-costs` under your GitHub account (or organization)
3. **Git Initialized**: Initialize git in this directory

## 📝 Current Configuration

### Brand Name: **Ivan's HA Stuff**
### Repository: `ivans-ha-stuff/ha-3d-printing-costs`
### Integration Name: **3D Printer Energy Tracker**

## 🚀 Setup Steps

### 1. Initialize Git Repository (if not done)

```bash
cd /Users/ivantomicic/Desktop/hass-plugins/ha-3d-printing-costs
git init
git add .
git commit -m "Initial commit - 3D Printer Energy Tracker v1.0.0"
```

### 2. Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `ha-3d-printing-costs`
3. Description: `Home Assistant integration for tracking 3D printer energy consumption, material usage, and costs`
4. Visibility: **Public** (required for HACS)
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click **Create repository**

### 3. Connect and Push

```bash
git remote add origin https://github.com/ivans-ha-stuff/ha-3d-printing-costs.git
git branch -M main
git push -u origin main
```

### 4. Update Repository URLs (if your GitHub username differs)

If your GitHub username is NOT `ivans-ha-stuff`, update these files:

**Files to update:**
- `custom_components/printer_energy/manifest.json` - Update `codeowners`, `documentation`, and `issue_tracker` URLs
- `README.md` - Update all GitHub URLs

**Example:**
If your username is `ivan123`, update:
```json
"codeowners": ["@ivan123"],
"documentation": "https://github.com/ivan123/ha-3d-printing-costs",
"issue_tracker": "https://github.com/ivan123/ha-3d-printing-costs/issues"
```

### 5. Enable GitHub Actions

1. Go to your repository on GitHub
2. Click **Settings** → **Actions** → **General**
3. Under "Workflow permissions", select **"Read and write permissions"**
4. Check **"Allow GitHub Actions to create and approve pull requests"**
5. Click **Save**

### 6. Create First Release

#### Option A: Using GitHub Actions (Recommended)

1. Update version in `custom_components/printer_energy/manifest.json`:
   ```json
   "version": "1.0.0"
   ```

2. Commit and push:
   ```bash
   git add custom_components/printer_energy/manifest.json
   git commit -m "Release v1.0.0"
   git push
   ```

3. Create and push tag:
   ```bash
   git tag -a v1.0.0 -m "Release v1.0.0"
   git push origin v1.0.0
   ```

4. GitHub Actions will automatically create the release with archives

#### Option B: Manual Release

1. Go to GitHub → **Releases** → **Draft a new release**
2. Tag: `v1.0.0` (create new tag)
3. Title: `Release v1.0.1`
4. Description: Use auto-generated release notes or add your own
5. Upload files manually:
   - Download the repository as ZIP
   - Extract `custom_components` folder
   - Create ZIP of `custom_components` folder
   - Upload as release asset
6. Click **Publish release**

## 📦 Adding to HACS

### For Users (when published):

Users can add your integration via:

1. **HACS** → **Integrations**
2. Click **⋮** (three dots) → **Custom repositories**
3. Add: `https://github.com/ivans-ha-stuff/ha-3d-printing-costs`
4. Category: **Integration**
5. Click **Add**
6. Search for "3D Printer Energy Tracker"
7. Click **Download**

### For HACS Default Repository:

To be included in HACS default repository (optional, requires approval):
- The integration must meet HACS requirements
- Open an issue at https://github.com/hacs/default
- Request inclusion with repository link

## 🔄 Easy Update Process

### Making Updates

1. **Make your changes** in the code
2. **Update version** in `manifest.json`:
   ```json
   "version": "1.0.1"  // Increment version
   ```
3. **Commit changes**:
   ```bash
   git add .
   git commit -m "Description of changes"
   git push
   ```
4. **Create release tag**:
   ```bash
   git tag -a v1.0.1 -m "Release v1.0.1"
   git push origin v1.0.1
   ```
5. **GitHub Actions** creates the release automatically!

### Quick Update Script

You can create a simple script to automate this:

```bash
#!/bin/bash
# update.sh

read -p "Version number (e.g., 1.0.1): " VERSION
read -p "Release message: " MESSAGE

# Update manifest.json (requires manual edit or use sed)
sed -i '' "s/\"version\": \"[^\"]*\"/\"version\": \"$VERSION\"/" custom_components/printer_energy/manifest.json

git add .
git commit -m "$MESSAGE"
git push
git tag -a "v$VERSION" -m "Release v$VERSION"
git push origin "v$VERSION"

echo "✅ Release v$VERSION created!"
```

## 📋 Checklist Before First Release

- [x] All files committed to git
- [x] Repository is public
- [x] `hacs.json` exists and is correct
- [x] `manifest.json` has correct URLs and version
- [x] `README.md` is comprehensive
- [x] `LICENSE` file exists
- [x] GitHub Actions workflows are in place
- [x] All GitHub URLs match your repository
- [ ] Codeowners GitHub username is correct
- [ ] Tested integration locally
- [ ] First release created

## 🎯 Repository Structure

```
ha-3d-printing-costs/
├── .github/
│   ├── workflows/
│   │   ├── release.yml          # Auto-creates releases
│   │   └── validate.yml         # Validates integration
│   └── RELEASE.md               # Release process guide
├── custom_components/
│   └── printer_energy/
│       ├── __init__.py
│       ├── config_flow.py
│       ├── const.py
│       ├── coordinator.py
│       ├── manifest.json        # Integration manifest
│       ├── sensor.py
│       └── storage.py
├── .gitignore
├── hacs.json                     # HACS metadata
├── LICENSE                       # MIT License
├── README.md                     # Documentation
└── HACS_SETUP.md                # This file
```

## ⚠️ Important Notes

1. **Keep version in sync**: Always update version in `manifest.json` before releasing
2. **Tag format**: Use `v1.0.0` format (with 'v' prefix)
3. **Public repository**: Repository must be public for HACS
4. **Release format**: HACS will automatically detect releases tagged with `v*`
5. **Breaking changes**: Update major version number (e.g., 2.0.0)

## 🆘 Troubleshooting

### HACS not finding integration
- ✅ Ensure repository is public
- ✅ Check `hacs.json` exists and is valid JSON
- ✅ Verify tag format is `v*` (e.g., `v1.0.0`)
- ✅ Check `manifest.json` has correct domain

### GitHub Actions not working
- ✅ Enable Actions in repository settings
- ✅ Check workflow permissions
- ✅ Verify `.github/workflows/` files are committed

### Users can't install
- ✅ Verify release has correct archive format
- ✅ Check `custom_components/printer_energy/` structure
- ✅ Ensure all required files are included

## 📞 Support

For issues with this setup guide or integration:
- Open an issue on GitHub
- Check HACS documentation: https://hacs.xyz/docs/publish/integration

---

**Happy publishing! 🚀**
