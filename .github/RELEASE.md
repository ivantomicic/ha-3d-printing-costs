# Release Process

## Quick Release Steps

1. **Update Version** in `custom_components/printer_energy/manifest.json`:
   ```json
   "version": "1.0.1"
   ```

2. **Commit and Push**:
   ```bash
   git add .
   git commit -m "Release v1.0.1"
   git push
   ```

3. **Create Tagged Release**:
   ```bash
   git tag -a v1.0.1 -m "Release v1.0.1"
   git push origin v1.0.1
   ```

4. **GitHub Actions** will automatically:
   - Create release archives (zip and tar.gz)
   - Create a GitHub release
   - Generate release notes

## What Gets Included in Release

- `custom_components/printer_energy/` - All integration files
- `hacs.json` - HACS metadata
- `README.md` - Documentation
- `LICENSE` - License file

## Manual Release (Alternative)

If you prefer manual releases:

1. Go to GitHub → Releases → Draft a new release
2. Tag: `v1.0.1` (or next version)
3. Title: `Release v1.0.1`
4. Upload `custom_components` folder as zip
5. Publish release

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH` (e.g., `1.0.0`, `1.1.0`, `2.0.0`)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes
