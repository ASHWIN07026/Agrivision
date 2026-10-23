"""Build a signed demo APK with official Android command-line tools, without Gradle.
Required: Java 17+, Android platform 35, build-tools 35.0.0, Eclipse ECJ 3.40.0.
Signing key is temporary, private and intentionally excluded from deliverables.
"""
import argparse
import os
from pathlib import Path
import secrets
import subprocess
import tempfile
import zipfile

parser = argparse.ArgumentParser()
parser.add_argument('--tools', type=Path, required=True, help='Extracted build-tools directory')
parser.add_argument('--android-jar', type=Path, required=True)
parser.add_argument('--ecj', type=Path, required=True)
parser.add_argument('--output', type=Path, default=Path('release/AgriVision-Android.apk'))
args = parser.parse_args()
root = Path(__file__).resolve().parent
args.output = args.output.resolve(); args.output.parent.mkdir(parents=True, exist_ok=True)
for tool in ['aapt2', 'd8', 'zipalign', 'apksigner']:
    path = args.tools / tool; path.chmod(path.stat().st_mode | 0o111)

def run(*command, **kwargs):
    subprocess.run([str(item) for item in command], check=True, **kwargs)

with tempfile.TemporaryDirectory(prefix='agrivision-apk-') as temporary:
    build = Path(temporary); (build / 'classes').mkdir()
    run('java', '-jar', args.ecj, '-source', '8', '-target', '8', '-bootclasspath', str(args.android_jar) + os.pathsep + str(args.tools / 'core-lambda-stubs.jar'), '-d', build / 'classes', *sorted((root / 'src').rglob('*.java')))
    classes = build / 'classes.jar'
    with zipfile.ZipFile(classes, 'w') as jar:
        for file in (build / 'classes').rglob('*.class'): jar.write(file, file.relative_to(build / 'classes'))
    run(args.tools / 'd8', '--lib', args.android_jar, '--min-api', '23', '--output', build / 'dex.zip', classes)
    run(args.tools / 'aapt2', 'compile', '--dir', root / 'res', '-o', build / 'resources.zip')
    unsigned = build / 'unsigned.apk'
    run(args.tools / 'aapt2', 'link', '-I', args.android_jar, '--manifest', root / 'AndroidManifest.xml', '-o', unsigned, build / 'resources.zip')
    with zipfile.ZipFile(build / 'dex.zip') as dex, zipfile.ZipFile(unsigned, 'a') as apk:
        for name in dex.namelist():
            if name.endswith('.dex'): apk.writestr(name, dex.read(name))
    run(args.tools / 'zipalign', '-p', '-f', '4', unsigned, build / 'aligned.apk')
    signing = dict(os.environ, AGRIVISION_APK_PASSWORD=secrets.token_urlsafe(32))
    run('keytool', '-genkeypair', '-keystore', build / 'demo.p12', '-storetype', 'PKCS12', '-storepass:env', 'AGRIVISION_APK_PASSWORD', '-keypass:env', 'AGRIVISION_APK_PASSWORD', '-alias', 'agrivision-demo', '-keyalg', 'RSA', '-keysize', '2048', '-validity', '3650', '-dname', 'CN=AgriVision Student Demo', env=signing)
    run(args.tools / 'apksigner', 'sign', '--ks', build / 'demo.p12', '--ks-pass', 'env:AGRIVISION_APK_PASSWORD', '--key-pass', 'env:AGRIVISION_APK_PASSWORD', '--out', args.output, build / 'aligned.apk', env=signing)
    run(args.tools / 'apksigner', 'verify', '--verbose', '--print-certs', args.output)
    run(args.tools / 'zipalign', '-c', '4', args.output)
print('Built:', args.output)
