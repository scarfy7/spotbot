########################################################################
##  Spot Bot
##  A simple discord bot intended for use in the Pet Tax server
##  Author: Reva Scharf
##  
##  Uses:
##    > Automatically tag users who improperly post NYT puzzle results
##    > Collect Pet Tax pictures and display Pet Tax when requested
##  
##  Available Commands:
##   /updog `dog_name` `photo_file`
##   /upcat `cat_name` `photo_file`
##   /givetax `tax_val`
##   
##  Potential Future Commands:
##   /coinflip - flip a coin and display heads or tails
##   /rolldie - roll a number of dice with a number of faces
##
########################################################################
import discord, os, random
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

###########################################################################################################
## Utility functions (thx chatGPT)
###########################################################################################################
def get_all_files_from_folders(folders):
    all_files = []
    for folder in folders:
        for root,dirs,files in os.walk(folder):
            for file in files:
                full_path = os.path.join(root, file)
                all_files.append(full_path)
    return all_files
    
def select_random_file(folders):
    all_files = get_all_files_from_folders(folders)
    if not all_files:
        return None
    return random.choice(all_files)

###########################################################################################################
## Load .env file and pull needed EVs
###########################################################################################################
load_dotenv()
## discord bot token
TOKEN = os.getenv('DISCORD_TOKEN')
## server location to store uploaded pictures
DB_LOC = os.getenv('PIC_DB_LOC')

## Setup bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!",intents=intents)

###########################################################################################################
## Constants
###########################################################################################################
nyt_substrings = ("Wordle ", "Strands #", "Connections\nPuzzle #")
dog_names = ["lulu", "odie", "tucker", "goose", "holden", "judith", "neptune", "dog"]
cat_names = ["olive", "bonnie", "laila", "cat"]
dog_folders = [DB_LOC + "/" + item for item in dog_names]
cat_folders = [DB_LOC + "/" + item for item in cat_names]
tax_folders = dog_folders + cat_folders

###########################################################################################################
## Connect bot to server
###########################################################################################################
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s).")
    except Exception as e:
        print(f"Error syncing commands: {e}")

###########################################################################################################
## Set up slash commands
##    NOTE: it seems every time a new slash command is added, the bot needs to be re-added to the server
##          either that or I'm impatient when testing and not waiting long enough for it to sync     
###########################################################################################################

##  Leaving sample commands so I don't have to find pseudocode later
# /hello
# note: this is a sample test command, remove later
#@bot.tree.command(name="hello")
#async def hello(interaction: discord.Interaction):
#        await interaction.response.send_message(f"hey {interaction.user.mention}! This is a slash command!", ephemeral=True)

# /say
# note: this is a sample test command, remove later        
#@bot.tree.command(name="say")
#@app_commands.describe(thing_to_say = "What should I say?")
#async def say(interaction: discord.Interaction, thing_to_say: str):
#        await interaction.response.send_message(f"{interaction.user.name} said: `{thing_to_say}`")

# /updog
@bot.tree.command(name="updog", description="Command to upload a dog photo for spotbot tax commands")
@app_commands.describe(photo_file = "Photo to upload")
@app_commands.describe(dog_name = "Name of dog pictured (enter 'dog' for non-pack dog)")
@app_commands.choices(dog_name=[
                app_commands.Choice(name="lulu", value="lulu"),
                app_commands.Choice(name="odie", value="odie"),
                app_commands.Choice(name="tucker", value="tucker"),
                app_commands.Choice(name="goose", value="goose"),
                app_commands.Choice(name="holden", value="holden"),
                app_commands.Choice(name="judith", value="judith"),
                app_commands.Choice(name="neptune", value="neptune"),
                app_commands.Choice(name="dog", value="dog")
                ])
async def updog(interaction: discord.Interaction, dog_name: app_commands.Choice[str], photo_file: discord.Attachment):
    if photo_file.content_type.startswith("image/"):
        await interaction.response.send_message(f"Uploading `{photo_file.filename}` for `{dog_name.value}`")
        os.makedirs(DB_LOC+"/"+dog_name.value, exist_ok=True)
        new_filename = photo_file.filename
        if photo_file.filename.endswith(".jfif"):
            new_filename = new_filename.replace(".jfif",".jpg",1)
        await photo_file.save(DB_LOC + "/" + dog_name.value + "/" + new_filename)
        await interaction.channel.send(file=discord.File(DB_LOC + "/" + dog_name.value + "/" + new_filename))
    else:
        await interaction.response.send_message(f"`{photo_file.filename}` has invalid file type (not a photo), nothing processed")

# /upcat
@bot.tree.command(name="upcat", description="Command to upload a cat photo for spotbot tax commands")
@app_commands.describe(photo_file = "Photo to upload")
@app_commands.describe(cat_name = "Name of cat pictured (enter 'cat' for non-pack cat)")
@app_commands.choices(cat_name=[
                app_commands.Choice(name="olive", value="olive"),
                app_commands.Choice(name="bonnie", value="bonnie"),
                app_commands.Choice(name="laila", value="laila"),
                app_commands.Choice(name="cat", value="cat")
                ])
async def upcat(interaction: discord.Interaction, cat_name: app_commands.Choice[str], photo_file: discord.Attachment):
    if photo_file.content_type.startswith("image/"):
        await interaction.response.send_message(f"Uploading `{photo_file.filename}` for `{cat_name.value}`")
        os.makedirs(DB_LOC+"/"+cat_name.value, exist_ok=True)
        new_filename = photo_file.filename
        if photo_file.filename.endswith(".jfif"):
            new_filename = new_filename.replace(".jfif",".jpg",1)
        await photo_file.save(DB_LOC + "/" + cat_name.value + "/" + new_filename)
        await interaction.channel.send(file=discord.File(DB_LOC + "/" + cat_name.value + "/" + new_filename))
    else:
        await interaction.response.send_message(f"`{photo_file.filename}` has invalid file type (not a photo), nothing processed")
            
# /givetax
@bot.tree.command(name="givetax", description="Command to get random pet tax")
@app_commands.choices(tax_val=[
                app_commands.Choice(name="tax", value="tax"),
                app_commands.Choice(name="lulu", value="lulu"),
                app_commands.Choice(name="odie", value="odie"),
                app_commands.Choice(name="tucker", value="tucker"),
                app_commands.Choice(name="goose", value="goose"),
                app_commands.Choice(name="holden", value="holden"),
                app_commands.Choice(name="judith", value="judith"),
                app_commands.Choice(name="neptune", value="neptune"),
                app_commands.Choice(name="dog", value="dog"),
                app_commands.Choice(name="olive", value="olive"),
                app_commands.Choice(name="bonnie", value="bonnie"),
                app_commands.Choice(name="laila", value="laila"),
                app_commands.Choice(name="cat", value="cat")
                ])
async def givetax(interaction: discord.Interaction, tax_val: app_commands.Choice[str]):
    # Give a random tax based on what kind was requested
    tax = ""
    if tax_val.value == "dog":
        tax = select_random_file(dog_folders)
    elif tax_val.value == "cat":
        tax = select_random_file(cat_folders)
    elif tax_val.value == "tax":
        tax = select_random_file(tax_folders)
    else:
        tax = select_random_file([DB_LOC + "/" + tax_val.value])
            
    await interaction.response.send_message(file=discord.File(tax))

###########################################################################################################
## Set up message-based bot interactions
###########################################################################################################
@bot.event
async def on_message(message):
    # Don't send a message if message was from the bot
    if message.author == bot.user:
        return

    # shame those who misclick
    if str(message.channel) != 'nyt-dailies' and message.content.startswith(nyt_substrings):
        await message.reply(f"Hello {message.author.mention}, this is not the proper channel for NYT Puzzle results. You have been assigned {random.randint(5,48)} arbitrary demerits")
        return

# Run da bot
bot.run(TOKEN)

