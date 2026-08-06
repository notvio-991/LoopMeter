✨LoopMeter


LoopMeter is an open-source, modular desktop widget utility and overlay tool for Windows. It provides a lightweight, borderless, and always-on-top workspace designed to host custom desktop widgets, media loopers, and system tools.
The project is developed as an open-source hobby tool. While more widgets and features will be added over time, contributions from the community are highly welcome! Anyone is free to help improve the code, fix bugs, or build new widgets and tools.


🛠️ Features & Capabilities
Modular Widget Support: Built to host various custom desktop tools, such as hardware telemetry monitors, media loopers, and user profile widgets, with support for future additions.
Dynamic Window Management: Transparent, borderless windowing that stays on top of other applications by default, supporting free positioning (drag-and-drop) and on-the-fly resizing (Right-Click + Drag).
Zero-Install Portability: Packaged as a single, standalone executable that runs directly without requiring installation, external dependencies, or Python setup.


🚀 Future Development & Contributions
LoopMeter is designed with a modular codebase, making it easy to add new features. Future plans include continuous development of new widgets, code optimization, and bug fixes.
If you have a widget idea or want to improve the codebase, feel free to open a Pull Request or contribute to the repository!


🚀Usage
Download the latest executable from the Releases section.
Run the application as Administrator (required for system window management and correct overlay rendering).
Authorize using your credentials in the startup console window (default: admin / admin).

⚠️⚠️⚠️Note on Antivirus⚠️⚠️⚠️
Antivirus software (including Windows Defender) might flag this executable because it is an unsigned .exe file compiled from Python using PyInstaller and requests Administrator rights (--uac-admin) to manage overlay windows. This is a common false positive for portable compiled utilities. The source code is completely open-source and can be inspected directly in this repository.
