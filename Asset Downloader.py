import requests
import time
import re
import os
import yaml
import discord
from discord.ext import commands
from discord import app_commands
from colorama import init, Fore, Style

init()

CONFIG_FILE = "config.yaml"

default_config = {
    "roblox_cookie": "",
    "discord_bot": False,
    "discord_token": "",
    "discord_channel_id": ""
}

def load_config():
    """Load configuration from config.yaml, prompt for missing values, and save them."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            config = yaml.safe_load(file) or {}
    else:
        config = {}

    for key, default_value in default_config.items():
        if key not in config or config[key] == "":
            if isinstance(default_value, bool):
                user_input = input(Fore.CYAN + f"Enable {key.replace('_', ' ')}? (yes/no): " + Style.RESET_ALL)
                config[key] = user_input.strip().lower() == "yes"
            else:
                config[key] = input(Fore.CYAN + f"Enter {key.replace('_', ' ')}: " + Style.RESET_ALL)

    with open(CONFIG_FILE, "w") as file:
        yaml.dump(config, file)

    return config

def fetch_creator_info(asset_id):
    """Fetch the creators user ID and type for the given asset ID."""
    response = requests.get(f"https://economy.roproxy.com/v2/assets/{asset_id}/details")
    if response.status_code == 200:
        asset_info = response.json()
        creator_id = asset_info.get("Creator", {}).get("CreatorTargetId")
        creator_type = asset_info.get("Creator", {}).get("CreatorType")
        return creator_id, creator_type
    return None, None

def fetch_game_place_id_by_owner(target_id, creator_type):
    """Fetch place ID by the creators user ID by querying the user's games."""
    if creator_type == "User":
        response = requests.get(f"https://games.roblox.com/v2/users/{target_id}/games?sortOrder=Asc&limit=50")
    elif creator_type == "Group":
        response = requests.get(f"https://games.roblox.com/v2/groups/{target_id}/games?accessFilter=2&limit=100&sortOrder=Asc")
    else:
        return None

    if response.status_code == 200:
        games_info = response.json()
        place_id = games_info.get("data", [{}])[0].get("rootPlace", {}).get("id")
        return str(place_id)
    return None

def fetch_audio_location(asset_id, place_id, roblox_cookie):
    """Fetch audio URL based on asset_id and place_id."""
    body_array = [{
        "assetId": asset_id,
        "assetType": "Audio",
        "requestId": "0"
    }]
    headers = {
        "User-Agent": "Roblox/WinInet",
        "Content-Type": "application/json",
        "Cookie": f".ROBLOSECURITY={roblox_cookie}",
        "Roblox-Place-Id": place_id,
        "Accept": "*/*",
        "Roblox-Browser-Asset-Request": "false"
    }
    response = requests.post('https://assetdelivery.roblox.com/v2/assets/batch', headers=headers, json=body_array)
    if response.status_code == 200:
        locations = response.json()
        if locations and len(locations) > 0:
            obj = locations[0]
            if obj.get("locations") and obj["locations"][0].get("location"):
                return obj["locations"][0]["location"]
    return None

def sanitize_filename(name):
    """Sanitize filename by removing special characters and spaces."""
    return re.sub(r'[\\/*?"<>|]', '', name).replace(" ", "_")

def fetch_asset_name(asset_id):
    """Fetch the asset name based on asset ID."""
    response = requests.get(f"https://economy.roproxy.com/v2/assets/{asset_id}/details")
    if response.status_code == 200:
        asset_info = response.json()
        return asset_info.get("Name")
    return "Unknown_Asset"

def download_audio_file(roblox_cookie, asset_id):
    """Download audio file for a given asset ID and return the file path and asset details."""
    creator_id, creator_type = fetch_creator_info(asset_id)
    place_id = fetch_game_place_id_by_owner(creator_id, creator_type)
    asset_name = fetch_asset_name(asset_id)
    sanitized_asset_name = sanitize_filename(asset_name)
    audio_url = fetch_audio_location(asset_id, place_id, roblox_cookie)

    if audio_url:
        response = requests.get(audio_url)
        if response.status_code == 200:
            os.makedirs("audio_files", exist_ok=True)
            file_path = os.path.join("audio_files", sanitized_asset_name + ".ogg")
            with open(file_path, "wb") as f:
                f.write(response.content)
            return file_path, creator_id, creator_type, place_id
    return None, creator_id, creator_type, place_id

class MyDiscordBot(commands.Bot):
    def __init__(self, roblox_cookie, config):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)
        self.roblox_cookie = roblox_cookie
        self.config = config

    async def setup_hook(self):
        await self.tree.sync()
        print(Fore.GREEN + "Discord bot is ready and commands are synced!" + Style.RESET_ALL)

bot = None

def initialize_discord_bot(roblox_cookie, config):
    global bot
    bot = MyDiscordBot(roblox_cookie, config)

    @bot.tree.command(name="download", description="Download an audio file by asset ID")
    async def download(interaction: discord.Interaction, asset_id: str):
        await interaction.response.defer()

        file_path, creator_id, creator_type, place_id = download_audio_file(roblox_cookie, asset_id)
        
        if file_path:
            file_name = os.path.basename(file_path)
            with open(file_path, "rb") as file:
                await interaction.followup.send(
                    content=f"Downloaded audio for asset ID {asset_id}\n"
                            f"**Owner ID**: {creator_id}\n"
                            f"**Owner Type**: {creator_type}\n"
                            f"**Root Place ID**: {place_id}",
                    file=discord.File(file, filename=file_name)
                )
        else:
            await interaction.followup.send(f"Failed to download audio for asset ID {asset_id}")

    bot.run(config["discord_token"])

def main():
    config = load_config()
    roblox_cookie = config.get("roblox_cookie", "")
    
    if config.get("discord_bot", False):
        if config.get("discord_token"):
            try:
                initialize_discord_bot(roblox_cookie, config)
            except discord.LoginFailure:
                print(Fore.RED + "Invalid Discord token provided. Discord bot will not run." + Style.RESET_ALL)
        else:
            print(Fore.RED + "Discord bot is enabled, but no token is provided." + Style.RESET_ALL)
    else:
        print(Fore.YELLOW + "Running in normal mode" + Style.RESET_ALL)
    
    while True:
        asset_ids_input = input(Fore.CYAN + "Enter asset IDs (comma-separated, e.g., 123,456,789) or type 'exit' to quit: " + Style.RESET_ALL)
        
        if asset_ids_input.lower() == 'exit':
            print(Fore.CYAN + "Exiting the program. Goodbye!" + Style.RESET_ALL)
            break
        
        asset_ids = [id.strip() for id in asset_ids_input.split(',') if id.strip()]
        download_audio_file(roblox_cookie, asset_ids)
        
        print(Fore.CYAN + "All specified audio assets have been downloaded." + Style.RESET_ALL)


if __name__ == "__main__":
    main()
