import aiohttp
import discord
from ddm import *
from utils.references import References

class MinecraftMemberData(Saveable):
    USERNAME_2_UUID = "https://api.mojang.com/users/profiles/minecraft/%s"
    UUID_2_PROFILE = "https://sessionserver.mojang.com/session/minecraft/profile/%s"

    def __init__(self, member, guild):
        self._member = member
        self._guild = guild

        self.uuid = None

        super().__init__(References.get_guild_folder(f"{self._guild.id}/minecraft_links/{self._member.id}.json"))
    
    @Saveable.update()
    def set_uuid(self, uuid):
        self.uuid = uuid

    async def get_minecraft_name(self) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(MinecraftMemberData.UUID_2_PROFILE % self.uuid) as response:
                data = await response.json()
                if name := data.get("name"):
                    return name

    async def set_uuid_from_name(self, name):
        async with aiohttp.ClientSession() as session:
            async with session.get(MinecraftMemberData.USERNAME_2_UUID % name) as response:
                data = await response.json()
                if uuid := data.get("id"):
                    self.set_uuid(uuid)
                    return True
        return False