import discord
from discord.ext import commands
import requests

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="events", description="Shows current skyblock mining events")
    async def events(self, ctx, category: discord.Option(description="What type of lobby", choices=["Dwarven Mines", "Crystal Hollows", "Mineshaft"])):
        category_codename = category.upper().replace(" ", "_")

        # Query event API
        response = requests.get('https://api.soopy.dev/skyblock/chevents/get')
        if response.status_code != 200:
            await ctx.respond(f"Web request received error code {response.status_code} :(")
            return

        data = response.json()

        if not data['success']:
            await ctx.respond("Soopy API returned an error.")
            return

        cur_events = data['data']['event_datas']
        total_lobbys = data['data']['total_lobbys'][category_codename]

        # Create embed
        embed = discord.Embed(
            color=0x10e84b,
            title=f"{category}: Mining Events (as of <t:{int(data['data']['curr_time'] / 1000)}:R>)"
        )

        # Code to Name mapping
        code_to_name = {
            'GONE_WITH_THE_WIND': 'Gone with the Wind',
            'DOUBLE_POWDER': '2x Powder',
            'GOBLIN_RAID': 'Goblin Raid',
            'BETTER_TOGETHER': 'Better Together',
            'RAFFLE': 'Raffle',
            'MITHRIL_GOURMAND': 'Mithril Gourmand'
        }

        location_events = cur_events[category_codename]

        # Populate embed
        for event_name, event_data in location_events.items():
            desc = (f"Starting <t:{int(event_data['starts_at_min'] / 1000)}:R> - "
                    f"<t:{int(event_data['starts_at_max'] / 1000)}:R>\n"
                    f"Ending <t:{int(event_data['ends_at_min'] / 1000)}:R> - "
                    f"<t:{int(event_data['ends_at_max'] / 1000)}:R>")
            if event_data['lobby_count'] != total_lobbys:
                desc += (f"\n\nIn {event_data['lobby_count']}/{total_lobbys} "
                         f"({(event_data['lobby_count'] / total_lobbys * 100):.1f}%) lobbies")
            embed.add_field(name=code_to_name.get(event_name, event_name), value=desc, inline=False)

        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Events(bot))
