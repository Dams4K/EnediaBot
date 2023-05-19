from discord import Colour, Embed


class SucceedEmbed(Embed):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = Colour.brand_green()

class WarningEmbed(Embed):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = Colour.gold()

class DangerEmbed(Embed):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = Colour.brand_red()

class InformativeEmbed(Embed):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = Colour.blurple()