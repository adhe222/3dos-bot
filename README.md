# 3DOS BOT

This script connects to the `api.dashboard.3dos.io` API using multiple accounts, proxies, and keys. It supports authentication via keys from `keygen.txt`, handles cookies dynamically, and works with or without proxies.
## REGISTER
https://dashboard.3dos.io/register?ref_code=1c744d
## Features
- **Multi-Account Support**: Handles multiple accounts with unique usernames and auth keys.
- **Dynamic Proxies**: Uses proxies from `proxy.txt` or runs without proxies if none are available.
- **Dynamic Keys**: Loads API keys from `keygen.txt` for dynamic endpoint generation.
- **Error Handling**: Displays detailed error messages for failed requests.
- **Colorful Output**: Uses `colorama` for styled and readable terminal output.

## Requirements
- Python 3.x
- Required libraries: `requests`, `colorama`

Install dependencies:
```bash
pip install requests colorama
```
## Usage
Prepare Files :
Create proxy.txt with proxies (optional). Example:
```bash
http://123.45.67.89:8080
http://98.76.54.32:3128
```
Create keygen.txt with API keys. Example:
```bash
63f67d9f5d45fd9fbdb1
abc1234567890abcdef1234567890
```
## clone repo
```bash
git clone https://github.com/adhe222/3dos-bot.git
cd 3dos-bot
```
## Run script
```bash
python kontlijo.py
```
