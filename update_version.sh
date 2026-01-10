#!/bin/bash
# Quick update script for Ivan's HA Stuff - 3D Printer Energy Tracker
# Usage: ./update_version.sh 1.0.1 "Release message"

if [ -z "$1" ]; then
    echo "Usage: ./update_version.sh VERSION [MESSAGE]"
    echo "Example: ./update_version.sh 1.0.1 \"Bug fixes and improvements\""
    exit 1
fi

VERSION=$1
MESSAGE=${2:-"Release v$VERSION"}

echo "🔄 Updating to version $VERSION..."

# Update manifest.json
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s/\"version\": \"[^\"]*\"/\"version\": \"$VERSION\"/" custom_components/printer_energy/manifest.json
else
    # Linux
    sed -i "s/\"version\": \"[^\"]*\"/\"version\": \"$VERSION\"/" custom_components/printer_energy/manifest.json
fi

echo "✅ Updated manifest.json to version $VERSION"

# Commit changes
git add custom_components/printer_energy/manifest.json
git commit -m "$MESSAGE"

echo "✅ Committed changes"

# Push to main
git push

echo "✅ Pushed to main branch"

# Create and push tag
git tag -a "v$VERSION" -m "$MESSAGE"
git push origin "v$VERSION"

echo ""
echo "🎉 Release v$VERSION created successfully!"
echo "📦 GitHub Actions will automatically create the release with archives"
echo "🔗 Check: https://github.com/ivans-ha-stuff/ha-3d-printing-costs/releases"
