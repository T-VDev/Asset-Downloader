# Asset-Downloader

This tool allows you to download non-public Roblox audio files with ease. It supports both **Normal Mode** and **Discord Mode**, providing flexibility depending on your needs.

---

## **Features**

- **Normal Mode**: Download multiple audio files at once by providing a list of Audio IDs.
- **Discord Mode**: Allows interaction through Discord, where you can send a command to download audio files. The program will return the audio file directly to Discord.
- **Automatic Folder Creation**: The tool will create a folder named `audio_files` in the same directory as the `.exe` or where the script is being executed.

---

## **Usage Instructions**

### **1. First Launch: Initial Setup**

- Upon the **first launch**, the program will prompt you to enter your **Roblox cookie**.
- You will then be asked whether you want to use **Normal Mode** or **Discord Mode**.
  - If you choose **Normal Mode**, simply input the audio file IDs (separated by commas) when prompted.
  - If you choose **Discord Mode**, you’ll need to input a **valid Discord token** to interact via Discord commands.
  
After these initial steps, the program will create a `config.yaml` file in the current directory to store your settings.

---

### **2. Modes**

#### **Normal Mode**:  
- In **Normal Mode**, you can download multiple audio files at once.
- Simply input the **Audio IDs** separated by commas when prompted, like so: 123, 456, 789
- The program will then download each audio file and save them into the `audio_files` folder.

#### **Discord Mode**:  
- In **Discord Mode**, the tool will interact with Discord through your provided token.
- You can run the following command in Discord: /assetdownload ASSETID
- The program will download the audio file and send it back to Discord.
- **Note**: In Discord mode, the program does not launch the normal terminal interface, so you cannot interact with it while it's running.

---

### **3. Configuration & Setup**

When you launch the program for the first time:

- **Roblox Cookie**: You will need to provide a valid Roblox cookie.
- **Discord Token**: If you choose **Discord Mode**, enter your **Discord token** for authentication, else enter 0.

The settings will be saved in a file called **`config.yaml`**, located in the same directory as the tool. This allows you to change modes and tokens later without re-entering them.

---

## **Requirements**

- **Python 3 or above** is required to run this tool.
- Install the necessary Python modules:
```bash
pip install discord requests
```
- For the .exe version, simply download and run the .exe file. No installation is necessary.
- Stable internet connection is required to download audio files.

---

### **How to Run**

- Download the .exe file or run the Python script.
- For Normal Mode: Follow the on-screen instructions to input the audio IDs.
- For Discord Mode: Provide your Discord token when prompted. You can run /assetdownload ASSETID in Discord to fetch the audio file.

---

### **Configuration File (config.yaml)**

- The program saves your preferences in the config.yaml file, including your Roblox cookie and Discord token. 
- You can edit this file later if needed.
