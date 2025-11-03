# GitHub Actions CI to build Windows EXE

This repository contains a GitHub Actions workflow that builds a Windows executable for WordTwitch.
To use it:

1. Create a GitHub repository and push this project (including this `.github/workflows/build-windows.yml` file) to the `main` branch.
2. On GitHub, go to Actions → Workflows and run the "Build WordTwitch Windows EXE" workflow manually or push a commit to `main`.
3. After the workflow completes, download the artifact named `WordTwitch-windows-exe` from the workflow run (it contains `WordTwitchFull.exe`).

Notes:
- The workflow installs PyInstaller and required Python packages and runs PyInstaller on the script.
- If your project uses additional non-Python assets (sound files, etc.), consider adding them to `datas` in the `.spec` or ensure they're bundled separately.
