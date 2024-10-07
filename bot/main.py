import discord

bot = discord.Bot(intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')

bot.load_extension('cogs.forge')
bot.load_extension('cogs.events')

with open("token.txt", "r") as f:
    bot.run(f.read())