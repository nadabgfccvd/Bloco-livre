#!/bin/bash
# Monta o APK do Bloco Livre: classes.dex → base.apk → zipalign → assinado.
set -euo pipefail
APP=/home/z/my-project/app
BT=/home/z/my-project/tools/bt34/android-14
AJ=/home/z/my-project/tools/plat34/android-34/android.jar
KS=/home/z/my-project/app/keystore.jks
OUT=/home/z/my-project/download/BlocoLivre.apk

cd "$APP"

# 1. DEX (d8 exige classes em jar/dir; usa --lib para o classpath de bootstrap)
rm -rf build/dex build/apk-unsigned
mkdir -p build/dex build/apk-unsigned
"$BT/d8" --release --lib "$AJ" --min-api 21 --output build/dex $(find build/obj -name '*.class')
ls build/dex

# 2. APK base: RELINK do manifest a cada build (base.apk nunca é stale)
AAPT2="$BT/aapt2"
rm -rf build/apk
mkdir -p build/apk
"$AAPT2" compile --dir res -o build/res.zip
"$AAPT2" link -o build/apk/base.apk -I "$AJ" \
  --manifest AndroidManifest.xml --java build/gen build/res.zip
cp build/apk/base.apk build/apk-unsigned/app.apk
# classes.dex dentro da raiz do APK
cd build/dex && zip -q ../apk-unsigned/app.apk classes.dex && cd "$APP"

# 3. zipalign (alinhamento 4 bytes p/ recursos)
"$BT/zipalign" -f -p 4 build/apk-unsigned/app.apk build/apk-unsigned/app-aligned.apk

# 4. keystore (1ª vez) e assinatura v2
if [ ! -f "$KS" ]; then
  keytool -genkeypair -keystore "$KS" -storepass blocolivre -keypass blocolivre \
    -alias blocolivre -keyalg RSA -keysize 2048 -validity 10950 \
    -dname "CN=Bloco Livre, OU=Apps Livres, O=Bloco Livre, L=Local, ST=Estado, C=BR" >/dev/null 2>&1
  echo "keystore criado"
fi
"$BT/apksigner" sign --ks "$KS" --ks-pass pass:blocolivre --key-pass pass:blocolivre \
  --ks-key-alias blocolivre --out "$OUT" build/apk-unsigned/app-aligned.apk
"$BT/apksigner" verify --print-certs "$OUT"
ls -la "$OUT"
echo "APK PRONTO: $OUT"
