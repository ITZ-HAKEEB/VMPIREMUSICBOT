# VAMPIRE-MUSIC

## 🚀 Deploy on Heroku 
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://dashboard.heroku.com/new?template=https://github.com/VBIT-BOT-ADDA/Kashvimusic)

<h1 align="center">─「 ǫᴜɪᴄᴋ sᴇᴛᴜᴘ 」─</h1>

 1. **🔧 ᴜᴘᴅᴀᴛᴇ & ᴜᴘɢʀᴀᴅᴇ**
   ```bash
   sudo apt-get update && sudo apt-get upgrade -y
   ```

 2. **📦 ɪɴsᴛᴀʟʟ ʀᴇǫᴜɪʀᴇᴅ ᴘᴀᴄᴋᴀɢᴇs**
   ```bash
   sudo apt-get install python3-pip ffmpeg -y
   ```
 3. **📌 sᴇᴛᴛɪɴɢ ᴜᴘ ᴘɪᴘ**
   ```bash
   sudo pip3 install -U pip
   ```
 4. **⚡ ɪɴsᴛᴀʟʟɪɴɢ ɴᴏᴅᴇ**
   ```bash
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.38.0/install.sh | bash && source ~/.bashrc && nvm install v18
   ```
 5. **📥 ᴄʟᴏɴᴇ ᴛʜᴇ ʀᴇᴘᴏsɪᴛᴏʀʏ**
   ```bash
   git clone https://github.com/VBIT-BOT-ADDA/Kashvimusic && cd Kashvimusic
   ```
 6. **📂 ɪɴsᴛᴀʟʟ ʀᴇǫᴜɪʀᴇᴍᴇɴᴛs**
   ```bash
   pip3 install -U -r requirements.txt
   ```
 7. **📝 ᴄʀᴇᴀᴛᴇ .env ᴡɪᴛʜ sᴀᴍᴘʟᴇ.env**
   ```bash
   cp sample.env .env
   ```
   - Edit .env with your vars
 8. **✏️ ᴇᴅɪᴛɪɴɢ ᴠᴀʀs**
   ```bash
   vi .env
   ```
   - Edit .env with your values.
   - Press `I` button on keyboard to start editing.
   - Press `Ctrl + C`  once you are done with editing vars and type `:wq` to save .env or `:qa` to exit editing.
9. **🔗 ɪɴsᴛᴀʟʟɪɴɢ ᴛᴍᴜx**
    ```bash
    sudo apt install tmux -y && tmux
    ```
11. **🚀 ʀᴜɴ ᴛʜᴇ ʙᴏᴛ**
    ```bash
    bash start
    ```

