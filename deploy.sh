#!/bin/bash
# ==============================================================================
# KashviMusic / AnonXMusic - One-Command VPS Deployment Script
# Supports: Ubuntu 20.04+, 22.04+, 24.04+, Debian 11+
# ==============================================================================

set -e

# Terminal colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "=========================================================="
echo "         KASHVI MUSIC - ONE COMMAND VPS DEPLOYMENT        "
echo "=========================================================="
echo -e "${NC}"

# 1. Determine privilege level (root vs sudo)
if [ "$(id -u)" -eq 0 ]; then
    SUDO=""
else
    if command -v sudo &>/dev/null; then
        SUDO="sudo"
    else
        echo -e "${RED}[!] sudo is not installed and you are not running as root.${NC}"
        echo -e "${YELLOW}Please switch to root (su -) or install sudo.${NC}"
        exit 1
    fi
fi

# 2. Check if we need to clone the repository or if we're already inside it
REPO_URL="https://github.com/VBIT-BOT-ADDA/Kashvimusic.git"
REPO_DIR="Kashvimusic"

if [ ! -f "config.py" ] || [ ! -d "anony" ]; then
    echo -e "${YELLOW}[*] Not currently inside Kashvimusic directory. Setting up repository...${NC}"
    $SUDO apt-get update -y
    $SUDO apt-get install -y git
    if [ ! -d "$REPO_DIR" ]; then
        git clone "$REPO_URL" "$REPO_DIR"
    fi
    cd "$REPO_DIR"
fi

WORKDIR="$(pwd)"
echo -e "${GREEN}[✓] Working directory: ${WORKDIR}${NC}"

# 3. Update system and install required apt packages
echo -e "\n${CYAN}[1/5] Installing system packages (FFmpeg, Curl, Unzip, Tmux, Python)...${NC}"
$SUDO apt-get update -y
$SUDO apt-get install -y \
    curl \
    wget \
    unzip \
    git \
    ffmpeg \
    python3 \
    python3-pip \
    python3-venv \
    tmux \
    build-essential

# 4. Install Deno properly and setup global symlinks
echo -e "\n${CYAN}[2/5] Setting up Deno (JavaScript runtime)...${NC}"
# Remove any broken symlinks from previous attempts
$SUDO rm -f /usr/local/bin/deno /usr/bin/deno 2>/dev/null || true

DENO_BIN="$HOME/.deno/bin/deno"
if [ ! -x "$DENO_BIN" ]; then
    echo -e "${YELLOW}[*] Downloading and installing Deno...${NC}"
    curl -fsSL https://deno.land/install.sh | sh
fi

# Link to global PATH so every user and service can access it
if [ -x "$DENO_BIN" ]; then
    $SUDO ln -sf "$DENO_BIN" /usr/local/bin/deno
    export DENO_INSTALL="$HOME/.deno"
    export PATH="$DENO_INSTALL/bin:$PATH"
fi

if ! grep -q 'DENO_INSTALL' "$HOME/.bashrc" 2>/dev/null; then
    echo 'export DENO_INSTALL="$HOME/.deno"' >> "$HOME/.bashrc"
    echo 'export PATH="$DENO_INSTALL/bin:$PATH"' >> "$HOME/.bashrc"
fi

# Verify Deno
if command -v deno &>/dev/null; then
    echo -e "${GREEN}[✓] Deno installed successfully: $(deno --version | head -n1)${NC}"
else
    echo -e "${RED}[!] Warning: Deno binary not found in PATH.${NC}"
fi

# Verify FFmpeg
if command -v ffmpeg &>/dev/null; then
    echo -e "${GREEN}[✓] FFmpeg installed successfully: $(ffmpeg -version | head -n1 | cut -d ' ' -f3)${NC}"
else
    echo -e "${RED}[!] Warning: FFmpeg not found in PATH.${NC}"
fi

# 5. Install uv (lightning-fast Python package & environment manager)
echo -e "\n${CYAN}[3/5] Installing uv package manager & Python dependencies...${NC}"
if ! command -v uv &>/dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    UV_BIN="$HOME/.local/bin/uv"
    if [ -x "$UV_BIN" ]; then
        $SUDO ln -sf "$UV_BIN" /usr/local/bin/uv 2>/dev/null || true
        export PATH="$HOME/.local/bin:$PATH"
    fi
    if ! grep -q '.local/bin' "$HOME/.bashrc" 2>/dev/null; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    fi
fi

# Sync python environment using uv
export PATH="$HOME/.local/bin:$HOME/.deno/bin:/usr/local/bin:$PATH"
echo -e "${YELLOW}[*] Installing project dependencies...${NC}"
if [ -f "pyproject.toml" ]; then
    uv sync
else
    uv pip install -r requirements.txt
fi
echo -e "${GREEN}[✓] Python dependencies installed successfully.${NC}"

# 6. Configure environment variables (.env)
echo -e "\n${CYAN}[4/5] Checking configuration (.env)...${NC}"
if [ -f ".env" ]; then
    echo -e "${GREEN}[✓] Existing .env file found.${NC}"
    read -rp "Do you want to reconfigure .env? (y/N): " RECONFIG
    RECONFIG=${RECONFIG:-n}
else
    RECONFIG="y"
fi

if [[ "$RECONFIG" =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Enter your Telegram bot details below:${NC}"
    read -rp "API_ID: " input_api_id
    read -rp "API_HASH: " input_api_hash
    read -rp "BOT_TOKEN: " input_bot_token
    read -rp "OWNER_ID: " input_owner_id
    read -rp "MONGO_URL: " input_mongo_url
    read -rp "LOGGER_ID: " input_logger_id
    read -rp "SESSION (Pyrogram String Session): " input_session

    cat > .env <<EOF
# Core Telegram Credentials
API_ID=${input_api_id}
API_HASH=${input_api_hash}
BOT_TOKEN=${input_bot_token}
OWNER_ID=${input_owner_id}
LOGGER_ID=${input_logger_id}
MONGO_URL=${input_mongo_url}
SESSION=${input_session}

# YouTube Streaming & Download Engine
YT_API_URL=https://api.arcmusic.fun
YT_API_KEY=ARC5c354b8ef8b2b1ef5d9e8b

# Bot Images & Settings
PING_IMG=https://files.catbox.moe/xmcz1p.jpg
AUTO_LEAVE=False
AUTO_END=True
EOF
    echo -e "${GREEN}[✓] .env file saved successfully!${NC}"
fi

# 7. Start options
echo -e "\n${CYAN}[5/5] Ready to start!${NC}"
echo -e "Choose how you want to start the bot:"
echo "  1) Start in background with tmux (Recommended - keeps running after closing terminal)"
echo "  2) Start in current terminal (Foreground)"
echo "  3) Do not start now (I will run 'bash start' manually)"
read -rp "Selection [1-3] (Default: 1): " START_CHOICE
START_CHOICE=${START_CHOICE:-1}

case "$START_CHOICE" in
    1)
        tmux kill-session -t kashvi 2>/dev/null || true
        tmux new-session -d -s kashvi "cd ${WORKDIR} && bash start"
        echo -e "\n${GREEN}==========================================================${NC}"
        echo -e "${GREEN}[✓] Bot is now running in background inside tmux!${NC}"
        echo -e "Useful tmux commands:"
        echo -e "  • View live bot logs : ${CYAN}tmux attach -t kashvi${NC}"
        echo -e "  • Detach from logs   : Press ${CYAN}Ctrl+B${NC} then press ${CYAN}D${NC}"
        echo -e "  • Restart bot        : ${CYAN}tmux kill-session -t kashvi && tmux new-session -d -s kashvi 'cd ${WORKDIR} && bash start'${NC}"
        echo -e "${GREEN}==========================================================${NC}"
        ;;
    2)
        echo -e "\n${GREEN}[*] Starting bot in foreground... Press Ctrl+C to stop.${NC}\n"
        bash start
        ;;
    3)
        echo -e "\n${GREEN}[✓] Setup complete! You can start the bot anytime using:${NC}"
        echo -e "  ${CYAN}cd ${WORKDIR} && bash start${NC}\n"
        ;;
esac
