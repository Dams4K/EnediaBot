from discord import Embed

class NormalEmbed(Embed):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = discord.Colour.brand_green()

class WarningEmbed(Embed):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = discord.Colour.orange()

class DangerEmbed(Embed):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = discord.Colour.brand_red()

class InformativeEmbed(Embed):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = discord.Colour.blurple()