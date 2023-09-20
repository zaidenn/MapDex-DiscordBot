from typing import TYPE_CHECKING

from ballsdex.packages.blacklist.cog import Blacklist

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot


async def setup(bot: "BallsDexBot"):
    await bot.add_cog(Blacklist(bot))
