import datetime
import pytz

from django import template

from ..models import Tweet, User


register = template.Library()

@register.assignment_tag
def recent_tweets(screen_name=None, limit=10):
    """Returns a QuerySet of recent public Tweets, in reverse-chronological
    order.

    Keyword arguments:
    screen_name -- A Twitter user's screen_name. If not supplied, we fetch
                    Tweets for all Twitter users that have Accounts.
    limit -- Maximum number to fetch. Default is 10.
    """
    if screen_name is None:
        users = User.objects_with_accounts.all()
        tweets = Tweet.public_objects.filter(user=users)
    else:
        tweets = Tweet.public_objects.filter(user__screen_name=screen_name)
    return tweets.select_related()[:limit]

@register.assignment_tag
def recent_favorites(screen_name=None, limit=10):
    """Returns a QuerySet of recent Tweets favorited by the Account associated
    with the Twitter User with screen_name.

    Keyword arguments:
    screen_name -- A Twitter user's screen_name. If not supplied, we fetch
                    Tweets favorited by all public Accounts.
    limit -- Maximum number to fetch. Default is 10.
    """
    if screen_name is None:
        tweets = Tweet.public_favorite_objects.all()
    else:
        user = User.objects.get(screen_name=screen_name)
        if user.is_private:
            tweets = Tweet.objects.none()
        else:
            tweets = Tweet.public_favorite_objects.filter(favoriting_users=user)
    return tweets.select_related()[:limit]

@register.assignment_tag
def day_tweets(date, screen_name=None):
    """Returns a QuerySet of Tweets posted on a specific date by public
    Accounts.

    Arguments:
    date -- A date object.

    Keyword arguments:
    screen_name -- A Twitter user's screen_name. If not supplied, we fetch
                    all public Tweets.
    """
    start = datetime.datetime.combine(date, datetime.time.min).replace(
                                                            tzinfo=pytz.utc)
    end   = datetime.datetime.combine(date, datetime.time.max).replace(
                                                            tzinfo=pytz.utc)
    tweets = Tweet.public_objects.filter(created_at__range=[start, end])
    if screen_name is None:
        users = User.objects_with_accounts.all()
        tweets = tweets.filter(user=users)
    else:
        tweets = tweets.filter(user__screen_name=screen_name)
    return tweets

@register.assignment_tag
def day_favorites(date, screen_name=None):
    """Returns a QuerySet of Tweets posted on a specific date that have been
    favorited by public Accounts.

    NOTE: It is not the date on which the Tweets were favorited.
          The Twitter API doesn't supply that.

    Arguments:
    date -- A date object.

    Keyword arguments:
    screen_name -- A Twitter user's screen_name. If not supplied, we fetch
                    all public Tweets.
    """
    start = datetime.datetime.combine(date, datetime.time.min).replace(
                                                            tzinfo=pytz.utc)
    end   = datetime.datetime.combine(date, datetime.time.max).replace(
                                                            tzinfo=pytz.utc)
    tweets = Tweet.public_favorite_objects.filter(
                                                created_at__range=[start, end])
    if screen_name is None:
        tweets = Tweet.public_favorite_objects.filter(
                                                created_at__range=[start, end])
    else:
        user = User.objects.get(screen_name=screen_name)
        if user.is_private:
            tweets = Tweet.objects.none()
        else:
            tweets = Tweet.public_favorite_objects.filter(
                created_at__range=[start, end]).filter(favoriting_users=user)
    return tweets

