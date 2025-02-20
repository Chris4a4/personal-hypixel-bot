import discord
from discord.ext import commands, tasks
import requests
from time import time
from datetime import datetime, timedelta, UTC


PING_ID = 173286963451789314
SERVER_ID = 328820770224472067
CHANNEL_ID = 1251658648795611197


class Forge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.no_ping = set()

        self.update_forge.start()


    def cog_unload(self):
        self.update_forge.cancel()


    @tasks.loop(minutes=1)
    async def update_forge(self):
        #from datetime import datetime
        #from pprint import pprint

        # Get current timestamp
        #current_timestamp = datetime.now()

        # Format timestamp as string
        #timestamp_string = current_timestamp.strftime("%Y-%m-%d %H:%M:%S")


        # Wait until the bot is fully loaded and attached to the guild to do this stuff
        guild = self.bot.get_guild(SERVER_ID)
        if not guild:
            return
        channel = guild.get_channel(CHANNEL_ID)

        result = requests.get(f'http://backend:8000/forge_tracker').json()

        #print("-----------------------")
        #pprint(result)

        # Update forge ping channel
        message = ""
        for user, forge in result.items():
            for slot, item in forge.items():
                if not item:
                    continue

                if item['predicted_finish'] is None:
                    continue

                if time() < item['predicted_finish']:
                    continue

                uuid = f'{slot}-{item["start_time"]}'
                if uuid in self.no_ping:
                    #print(f"{timestamp_string} -      already posted {uuid}")
                    continue

                self.no_ping.add(uuid)

                message += f'<@{PING_ID}> {user}\'s **{item["item_name"]}** has finished forging!\n'

        if message:
            await channel.send(message)
            #print(f"{timestamp_string} - Updating forge channel - update posted")
        #else:
        #    print(f"{timestamp_string} - Updating forge channel - nothing to post")

        try:
            # Delete old messages in the ping channel
            async for message in channel.history(limit=None):
                if message.created_at < datetime.now(UTC) - timedelta(days=1):
                    try:
                        await message.delete()
                    except discord.Forbidden:
                        print(f"Missing permissions to delete message from {message.author}")
                    except discord.HTTPException:
                        print(f"Failed to delete message: {message.id}")
        except discord.DiscordServerError as e:
            print(f"Error retrieving message history: {e}")


    @commands.slash_command(name="forgecalc", description="Shows resources required to make a forge recipe")
    async def forgecalc(self,
        ctx,
        item: discord.Option(description="Name of item to calculate materials for", choices=["Skeleton Key", "Mithril Plate", "Perfect Plate", "Titanium Drill DR-X655"]),
        count: discord.Option(int, description="Number of items to calculate materials for", min_value=1, max_value=1000),
        username: discord.Option(description="Minecraft username"),
        profile: discord.Option(description="Profile name to use. If left blank, uses currently selected profile", required=False)
    ):
        await ctx.defer()

        if item == "Titanium Drill DR-X655":
            item_codename = "TITANIUM_DRILL_4"
        else:
            item_codename = item.upper().replace(" ", "_")

        query = f'http://backend:8000/forge_calc/{username}'
        if profile is not None:
            query += f'/{profile}'

        data = {
            'items': {
                item_codename: count
            }
        }
        result = requests.post(query, json=data).json()

        # Raw
        raw_materials = []
        for mat in result["raw"]:
            if mat["have"] == mat["need"]:
                raw_materials.append(f":white_check_mark: {mat['id']}: {mat['have']}/{mat['need']}")
            else:
                raw_materials.append(f":red_square: {mat['id']}: {mat['have']}/{mat['need']}")

        # Forge
        forge_materials = []
        for mat in result["forge"]:
            if mat["have"] == mat["need"]:
                forge_materials.append(f":white_check_mark: {mat['id']}: {mat['have']}/{mat['need']}")
            else:
                forge_materials.append(f":red_square: {mat['id']}: {mat['have']}/{mat['need']}")

        # Embed
        embed = discord.Embed(
            title=f"{count}x {item} for {username}",
            color=discord.Color(0xb02222)
        )
        embed.add_field(name="Raw Materials", value="\n".join(raw_materials), inline=False)
        embed.add_field(name="Items to Forge", value="\n".join(forge_materials), inline=False)

        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Forge(bot))
