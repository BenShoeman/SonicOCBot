from collections import OrderedDict
import random
import schedule

from FanfictionGenerator import TwitterFanfictionGenerator
from OC import *
from OCPostCreator import *
from SonicSezGenerator import *
from TwitterPoster import *
from TextImagePostCreator import *
from TweetPostCreator import *

ffic_generator = TwitterFanfictionGenerator()
ssez_generator = SonicSezGenerator()
twit_poster = TwitterPoster()

post_probability = OrderedDict({
    "oc": 0.825,
    "sonicsez": 0.1,
    "fanfic": 0.075
})
def make_post(post_probability=post_probability):
    n = random.random()
    for typ, p_typ in post_probability.items():
        if n < p_typ:
            post_typ = typ
            break
        n -= p_typ
    
    if post_typ == "fanfic":
        title, text = ffic_generator.get_fanfiction()
        post_creator = TextImagePostCreator(
            text=text, title=title, tags=("#SonicTheHedgehog", "#fanfic")
        )
    elif post_typ == "sonicsez":
        text = ssez_generator.get_text()
        post_creator = TweetPostCreator(
            text=text, tags=("#SonicSez",)
        )
    else:
        oc = OC.generate_oc()
        post_creator = OCPostCreator(oc=oc)
    twit_poster.make_tweet(post_creator)

def main():
    schedule.every().hour.at(":00").do(make_post)
    schedule.every().hour.at(":30").do(make_post)

    try:
        while True:
            schedule.run_pending()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()