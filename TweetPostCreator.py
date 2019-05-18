from PostCreator import *

class TweetPostCreator(PostCreator):
    TWITTER_CHAR_LIMIT = 280

    # Tags is a list or tuple of hashtags (be sure to include the pound sign)
    def __init__(self, text, tags=None, **kwargs):
        self.__text = text
        self.__tags = tags
        super().__init__(**kwargs)
    
    def get_image(self):
        return None
    
    def get_text(self):
        content = self.__text
        tags = (' '+' '.join(self.__tags)) if self.__tags is not None else ""
        # Truncate content if it exceeds character limit
        if len(content) + len(tags) > TweetPostCreator.TWITTER_CHAR_LIMIT:
            content = content[
                :(TweetPostCreator.TWITTER_CHAR_LIMIT - len(tags) - 3)
            ] + "..."
        return content + tags