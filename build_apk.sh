#!/bin/bash

# ============================================
# Biggest Chess APK Builder for Termux
# © 2025 AmirAli Kamrani
# ============================================

echo "🚀 Starting Biggest Chess APK Build..."
echo ""

# Set SDK and NDK paths for Termux
export ANDROID_SDK_ROOT="/data/data/com.termux/files/home/android-sdk"
export ANDROID_NDK_ROOT="/data/data/com.termux/files/home/android-sdk/ndk/25.1.8937393"
export GRADLE_OPTS="-Xmx4096m -Xms1024m"
export JAVA_TOOL_OPTIONS="-Dfile.encoding=UTF-8"

# Check if SDK exists
if [ ! -d "$ANDROID_SDK_ROOT" ]; then
    echo "❌ ERROR: Android SDK not found at $ANDROID_SDK_ROOT"
    echo "Please ensure Android SDK is installed in ~/android-sdk"
    exit 1
fi

# Check if NDK exists
if [ ! -d "$ANDROID_NDK_ROOT" ]; then
    echo "❌ ERROR: Android NDK not found at $ANDROID_NDK_ROOT"
    echo "Please ensure NDK 25.1.8937393 is installed"
    exit 1
fi

echo "✅ SDK found: $ANDROID_SDK_ROOT"
echo "✅ NDK found: $ANDROID_NDK_ROOT"
echo ""

# Create local.properties for gradle
echo "📝 Creating local.properties..."
mkdir -p .buildozer/android/platform/build
cat > .buildozer/android/platform/build/local.properties << EOF
sdk.dir=$ANDROID_SDK_ROOT
ndk.dir=$ANDROID_NDK_ROOT
EOF

echo "✅ local.properties created"
echo ""

# Install requirements if needed
echo "📦 Checking Python packages..."
pip install -q buildozer cython

echo "✅ Python packages ready"
echo ""

# Build APK
echo "🔨 Building APK for Biggest Chess..."
echo "This may take 5-15 minutes..."
echo ""

buildozer android debug

echo ""
if [ -f "bin/biggestchess-0.1-debug.apk" ]; then
    echo "✅ SUCCESS! APK created: bin/biggestchess-0.1-debug.apk"
    echo ""
    echo "📊 APK Info:"
    ls -lh bin/biggestchess-0.1-debug.apk
    echo ""
    echo "📱 To install on device:"
    echo "   adb install bin/biggestchess-0.1-debug.apk"
else
    echo "❌ Build failed. Check logs above."
    exit 1
fi
