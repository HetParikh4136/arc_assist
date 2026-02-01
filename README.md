   git clone https://github.com/HetParikh4136/arc_assist.git
   cd arc_assist
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   Create a `.env` file in the project root with the following required variable:
   ```
   PORCUPINE_ACCESS_KEY=your_api_key_from_https://console.picovoice.ai
   ```
   
   Optional configuration (defaults provided):
   ```
   WAKE_WORD_PATH=Hey arc.ppn
   CLAP_THRESHOLD=1800
   CLAP_INTERVAL=0.7
   ACTIVE_DURATION=5
   TRIPLE_WAIT_DURATION=30
   DEBUG=false
   VS_CODE_PATH=code
   SPOTIFY_PATH=
   DISCORD_PATH=
   BRAVE_PATH=brave
   CHROME_URL=https://claude.ai
   GITHUB_URL=https://github.com/HetParikh4136
   ```

## Usage

Run the main script to initiate the wake-up assistant:

```bash
python main.py
```

Optional debug logging:

```bash
python main.py --debug
```

Or enable debug mode via environment variable:
```bash
DEBUG=true python main.py
```

## Personalization

All settings are configured via environment variables in the `.env` file:

### Audio Configuration
- `WAKE_WORD_PATH`: Path to your wake word `.ppn` file (default: `Hey arc.ppn`). Use built-in Porcupine keywords (e.g., "jarvis", "computer", "alexa", "hey google", "ok google") or custom wake words from [Porcupine Console](https://console.picovoice.ai/).
- `CLAP_THRESHOLD`: Sensitivity for clap detection, range 1000-3000 (default: 1800). Higher values = less sensitive.
- `CLAP_INTERVAL`: Time window in seconds for multi-clap detection (default: 0.7).
- `ACTIVE_DURATION`: How long the assistant stays active after a wake event in seconds (default: 5).
- `TRIPLE_WAIT_DURATION`: Cooldown time in seconds after a triple-clap (default: 30).

### Application Launcher Configuration
- `VS_CODE_PATH`: Path to VS Code executable (default: `code`).
- `SPOTIFY_PATH`: Path to Spotify executable (leave empty to disable).
- `DISCORD_PATH`: Path to Discord executable (leave empty to disable).
- `BRAVE_PATH`: Path to Brave browser executable (default: `brave`).
- `CHROME_URL`: URL to open on double-clap (default: `https://claude.ai`).
- `GITHUB_URL`: URL to open on triple-clap (default: `https://github.com/HetParikh4136`).

### Debug Mode
- `DEBUG`: Enable debug logging (default: `false`). Set to `true` for verbose output, or use `python main.py --debug`.

## Tweakables Reference

Complete list of all configurable settings and where to find them:

| Setting | Environment Variable | Default | Type | File | Purpose |
|---------|---------------------|---------|------|------|---------|
| **Wake Word** | `WAKE_WORD_PATH` | `Hey arc.ppn` | string (file path or keyword) | [config.py](config.py#L39) | Porcupine wake word file or built-in keyword |
| **Porcupine API Key** | `PORCUPINE_ACCESS_KEY` | (required) | string | [config.py](config.py#L33) | API key from https://console.picovoice.ai |
| **Clap Threshold** | `CLAP_THRESHOLD` | `1800` | integer | [config.py](config.py#L52) | Audio amplitude threshold for clap detection (1000-3000) |
| **Clap Interval** | `CLAP_INTERVAL` | `0.7` | float (seconds) | [config.py](config.py#L55) | Time window for detecting multi-clap sequences |
| **Active Duration** | `ACTIVE_DURATION` | `5` | integer (seconds) | [config.py](config.py#L53) | How long assistant stays active after wake word |
| **Triple Clap Cooldown** | `TRIPLE_WAIT_DURATION` | `30` | integer (seconds) | [config.py](config.py#L54) | Cooldown after triple-clap before listening again |
| **Debug Mode** | `DEBUG` | `false` | boolean | [config.py](config.py#L58) | Enable verbose debug logging |
| **VS Code Path** | `VS_CODE_PATH` | `code` | string (executable) | [launcher/app_launcher.py](launcher/app_launcher.py#L28) | Command to launch VS Code |
| **Spotify Path** | `SPOTIFY_PATH` | (empty) | string (executable) | [launcher/app_launcher.py](launcher/app_launcher.py#L29) | Path to Spotify executable |
| **Discord Path** | `DISCORD_PATH` | (empty) | string (executable) | [launcher/app_launcher.py](launcher/app_launcher.py#L30) | Path to Discord executable |
| **Brave Browser Path** | `BRAVE_PATH` | `brave` | string (executable) | [launcher/app_launcher.py](launcher/app_launcher.py#L31) | Command to launch Brave browser |
| **Double-Clap URL** | `CHROME_URL` | `https://claude.ai` | string (URL) | [launcher/app_launcher.py](launcher/app_launcher.py#L32) | URL opened on double-clap |
| **Triple-Clap URL** | `GITHUB_URL` | `https://github.com/HetParikh4136` | string (URL) | [launcher/app_launcher.py](launcher/app_launcher.py#L33) | URL opened on triple-clap |

### Core Implementation Files

If you need to modify advanced behavior (not recommended without understanding the code):

- **[config.py](config.py)**: Central configuration management, environment variable loading, and validation
- **[audio/wake_word.py](audio/wake_word.py)**: Porcupine wake word detection logic
- **[audio/clap_detector.py](audio/clap_detector.py)**: Clap detection algorithm and multi-clap recognition
- **[audio/stream.py](audio/stream.py)**: Audio stream management and PCM processing
- **[launcher/controller.py](launcher/controller.py)**: Main control loop orchestrating wake/clap detection and actions
- **[launcher/app_launcher.py](launcher/app_launcher.py)**: Application launching logic for each OS (Windows, macOS, Linux)
