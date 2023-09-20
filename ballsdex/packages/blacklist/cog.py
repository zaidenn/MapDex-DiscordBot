import discord
import random
import logging

from typing import TYPE_CHECKING

from discord import app_commands
from discord.ext import commands

from ballsdex.settings import settings
from ballsdex.core.models import Player, BallInstance
from ballsdex.packages.countryballs.countryball import CountryBall

log = logging.getLogger("ballsdex.packages.info")


if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot

@app_commands.default_permissions(manage_guild=True)
@app_commands.guild_only()
class Blacklist(commands.GroupCog, group_name="blacklist"):
    """
    Report blacklist management.
    """

    def __init__(self, bot: "BallsDexBot"):
        self.bot = bot

    @app_commands.command(name="report")
    @app_commands.checks.cooldown(1, 30, key=lambda i: i.user.id)
    async def blacklist_report(
        self, 
        interaction: discord.Interaction,
        user: discord.User | None = None,
        user_id: str | None = None,
        reason: str | None = None,
        proof: discord.Attachment | None = None):
        """
        Report a user for breaking rules.

        Parameters
        ----------
        user: discord.User
            The user you want to report, if they are in the current server.
        user_id: str
            The user id you want to report, if they are not in the current server.
        reason: discord.message
            The reason for report.
        proof: discord.Attachment 
            Proof in form of an attachment.
        """

        if (user and user_id) or (not user and not user_id):
            await interaction.response.send_message(
                "You must provide either `user` or `user_id`.", ephemeral=True
            )
            return

        if not reason or len(reason)<4:
            await interaction.response.send_message(
                "You must provide an appropriate reason", ephemeral=True
            )
            return

        if len(user_id)<16 or len(user_id)>18:
            await interaction.response.send_message(
                "You must provide a real discord id", ephemeral=True
            )
            return
        
        await interaction.response.send_message(f"Thank you for submitting your report! {interaction.user.mention}", ephemeral=True)
        channel = self.bot.get_channel("Your reports channel")
        embedVar = discord.Embed(title="Blacklist Report", colour=discord.Colour.blue())
        if user:
            embedVar.add_field(name="Who?", value=user, inline=False)
        if user_id:
            embedVar.add_field(name="Who?", value=f"<@{user_id}>", inline=False)
        embedVar.add_field(name="Reason?", value=reason, inline=False)
        embedVar.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embedVar.set_image(url=proof)


        await channel.send(embed=embedVar)

    @app_commands.command(name="request")
    @app_commands.checks.cooldown(1, 10, key=lambda i: i.user.id)
    async def blacklist_request(
        self, 
        interaction: discord.Interaction,
        reason: str):
        """
        Submit to blacklist yourself (security reasons)

        Parameters
        ----------
        reason: discord.message
            The reason for request.
        """

        if not reason or len(reason)<4:
            await interaction.response.send_message(
                "You must provide an appropriate reason", ephemeral=True
            )
            return
        
        await interaction.response.send_message(f"Thank you for submitting your request! {interaction.user.mention}", ephemeral=True)
        channel = self.bot.get_channel("Your reports channel")
        embedVar2 = discord.Embed(title="Self-Blacklist Request", colour=discord.Colour.blue())
        embedVar2.add_field(name="Who?", value=f"<@{interaction.user.id}>", inline=False)
        embedVar2.add_field(name="Reason?", value=reason, inline=False)
        embedVar2.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)


        await channel.send(embed=embedVar2)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        guild = self.bot.get_guild("Your server")
        if guild:
            if message == discord.MessageType.premium_guild_subscription:
                sendchannel_id = "Your boost channel" # Channel to send reward info
                sendchannel = self.bot.get_channel(sendchannel_id)
                special = None
                cob = await CountryBall.get_random()
                UserID = message.author.id
                player, created = await Player.get_or_create(discord_id=UserID)
                instance = await BallInstance.create(
                    ball=cob.model,
                    player=player,
                    shiny=(random.randint(1, 2048) == 1),
                    attack_bonus=random.randint(-20, 20),
                    health_bonus=random.randint(-20, 20),
                    special=special,
                )
                messages = (
                    f"<@{UserID}> got a free `{instance.ball.country}` {settings.collectible_name} after boosting the server!\n"
                    f"• HP:`{instance.health_bonus:+d}` • "
                    f"• ATK:`{instance.attack_bonus:+d}` • "
                )
                log.info(f"{UserID} got {instance.ball.country} for boosting the server")
                await sendchannel.send(messages)