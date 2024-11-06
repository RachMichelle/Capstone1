class Result():
    """build result object from API response"""

    def __init__(self, name, artist, image, medium):
        
        self.name = name 
        self.artist = artist
        self.image = image
        self.medium = medium