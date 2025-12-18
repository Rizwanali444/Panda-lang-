#!/bin/bash
echo "Installing Panda 🐼 v0.1..."
pkg update && pkg upgrade -y
pkg install python -y
pip install lark rich requests

# Engine ko system bin mein move karna
cp panda.py /data/data/com.termux/files/usr/bin/panda_engine.py

# 'panda' command ka shortcut banana
echo -e '#!/bin/bash\npython /data/data/com.termux/files/usr/bin/panda_engine.py "$1"' > /data/data/com.termux/files/usr/bin/panda
chmod +x /data/data/com.termux/files/usr/bin/panda

echo "---------------------------------------"
echo "Mubarak ho! Panda 🐼 Install ho gaya!"
echo "Ab aap sirf likhein: panda file.pd"
echo "---------------------------------------"
