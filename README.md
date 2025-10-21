# Claudy

A streaming shell assistant powered by Claude. Type natural language in your terminal and press **Ctrl+G** to get instant command suggestions that stream in character-by-character.

https://github.com/user-attachments/assets/04a1221b-9417-4111-8321-842211dfd6fe

## Features

- 🚀 **Real-time streaming** - Commands appear character-by-character as Claude generates them
- ⏳ **Visual feedback** - Spinner animation while waiting for response
- 🧹 **Clean UX** - Natural language prompt is replaced with the command suggestion
- 🎯 **Context-aware** - Uses your shell history to provide relevant suggestions
- 📦 **Zero dependencies** - Python standard library only
- 🔐 **Secure** - Uses your Anthropic API key

## Installation

### Prerequisites

- Python 3.7+
- Zsh shell
- Anthropic API key ([get one here](https://console.anthropic.com/))

### Quick Install

1. Clone this repository:
```bash
git clone https://github.com/giansegato/claudy.git ~/claudy
```

2. Add to your `~/.zshrc`:
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
source ~/claudy/claudy.zsh
```

3. Reload your shell:
```bash
source ~/.zshrc
```

### Alternative: Install to PATH

```bash
# Copy script to a directory in your PATH
cp ~/claudy/claudy.py /usr/local/bin/claudy.py
chmod +x /usr/local/bin/claudy.py

# Add to ~/.zshrc
export ANTHROPIC_API_KEY="your-api-key-here"
source ~/claudy/claudy.zsh
```

## Usage

1. Type a natural language command in your terminal:
```bash
list all python files
```

2. Press **Ctrl+G**

3. Watch as the command appears in real-time:
```bash
find . -name "*.py" -type f
```

4. Press **Enter** to execute, or edit the command before executing

## Examples

```bash
# File operations
find large files → find . -type f -size +100M

# Git commands
commit all changes → git add . && git commit -m "Update files"

# Process management
show running docker containers → docker ps

# Network diagnostics
test connection to google → ping -c 4 google.com
```

## Configuration

### Custom Context

Create a `~/.claudy-prompt` file to add custom context for your commands:

```bash
echo "I prefer using ripgrep (rg) over grep" > ~/.claudy-prompt
echo "I work primarily with Python and Node.js" >> ~/.claudy-prompt
```

### Custom Key Binding

To use a different key binding, modify the last line in `claudy.zsh`:

```bash
# Use Ctrl+K instead
bindkey '^K' claudy-widget
```

## Contributing

Contributions welcome! Please open an issue or PR.

## License

MIT License - see [LICENSE](LICENSE) file for details

## Acknowledgments

Built with [Claude](https://claude.ai) by Anthropic

---

## Legal Disclaimer

This project is a personal creation by Gian Segato and is provided "as is" without warranty of any kind, express or implied.

**Important:**
- This is a personal project and does NOT represent Anthropic or any organization
- No guarantees or warranties are provided regarding functionality, security, or fitness for any purpose
- Use at your own risk
- The author is not responsible for any damages, data loss, or issues arising from the use of this software
- Users are responsible for complying with Anthropic's API Terms of Service and usage policies
- Shell history and commands are sent to Anthropic's API - review their privacy policy before use

By using this software, you acknowledge that you have read this disclaimer and agree to use it at your own discretion and risk.
