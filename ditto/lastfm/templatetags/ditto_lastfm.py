import calendar
import datetime
import pytz

from django import template
from django.db.models import Count
from django.utils.html import format_html

from ..models import Account, Album, Artist, Scrobble, Track


register = template.Library()


def check_top_kwargs(**kwargs):
    """
    Used to check the supplied kwargs for top_albums(), top_artist() and
    top_tracks().
    """

    account = kwargs['account']
    limit   = kwargs['limit']
    date    = kwargs['date']
    period  = kwargs['period']

    if account is not None and not isinstance(account, Account):
        raise TypeError('`account` must be an Account instance, '
                        'not a %s' % type(account))

    if limit != 'all' and isinstance(limit, int) == False:
        raise ValueError("`limit` must be an integer or 'all'")

    if date is not None and not isinstance(date, datetime.datetime) \
            and not isinstance(date, datetime.date):
        raise TypeError('`date` must be a datetime or date, '
                        'not a %s' % type(date))

    if period not in ['day', 'month', 'year']:
        raise TypeError('`period` must be one of "day", "month" or "year", '
                        'not %s' % type(period))


def get_post_times(date, period):
    """
    Makes the min_post_time and max_post_time for restricting top_albums(),
    top_artists() or top_tracks() to a particular time period.

    Arguments:
    date -- A datetime or date.
    period -- String, 'day', 'month' or 'year'.
    """
    if isinstance(date, datetime.datetime):
        min_post_time = date.replace(hour=0, minute=0, second=0)
        max_post_time = date.replace(
                            hour=23, minute=59, second=59, microsecond=999999)
    else:
        # `date` is a datetime.date
        min_post_time = datetime.datetime.combine(
                                            date, datetime.datetime.min.time()).replace(tzinfo=pytz.utc)
        max_post_time = datetime.datetime.combine(
                                            date, datetime.datetime.max.time()).replace(tzinfo=pytz.utc)

    if period == 'month':
        min_post_time = min_post_time.replace(day=1)
        # Last day of month:
        end_day = calendar.monthrange(
                                max_post_time.year, max_post_time.month)[1]
        max_post_time = max_post_time.replace(day=end_day)

    elif period == 'year':
        min_post_time = min_post_time.replace(month=1, day=1)
        max_post_time = max_post_time.replace(month=12, day=31)

    return min_post_time, max_post_time


@register.assignment_tag
def top_albums(account=None, artist=None, limit=10, date=None, period='day'):
    """Returns a QuerySet of most-scrobbled Albums, with the most-scrobbled
    first.

    Restrict to Albums by one Artist by suppling the `artist`.
    Restrict to only one user's scrobbles by supplying the `account`.

    By default gets all Albums.
    Restrict to a day, month or year by supplying a `date` within that
    day/month/year AND the `period` of 'day', 'month' or 'year'.

    Keyword arguments:
    account -- An Account object or None (for Scrobbles by all Accounts).
    artist -- An Artist object or None.
    limit -- Maximum number to fetch. Default is 10. 'all' for all Albums.
    date -- A datetime or date, for getting Albums from a single time period.
    period -- A String: 'day', 'month', or 'year'.
    """

    check_top_kwargs(**{
        'account': account,
        'limit': limit,
        'date': date,
        'period': period,
    })

    if artist is not None and not isinstance(artist, Artist):
        raise TypeError('artist must be an Artist instance, '
                        'not a %s' % type(artist))

    qs_kwargs = {}

    if account:
        qs_kwargs['account'] = account

    if artist:
        qs_kwargs['artist'] = artist

    if date and period:
        min_post_time, max_post_time = get_post_times(date, period)
        qs_kwargs['min_post_time'] = min_post_time
        qs_kwargs['max_post_time'] = max_post_time

    qs = Album.objects.with_scrobble_counts(**qs_kwargs)\
                        .order_by('-scrobble_count')

    if limit != 'all':
        qs = qs[:limit]

    return qs


@register.assignment_tag
def top_artists(account=None, limit=10, date=None, period='day'):
    """Returns a QuerySet of the most-scrobbled Artists, with the
    most-scrobbled first.

    Restrict to only one user's scrobbles by supplying the `account`.

    By default gets all Artists.
    Restrict to a day, month or year by supplying a `date` within that
    day/month/year AND the `period` of 'day', 'month' or 'year'.

    Keyword arguments:
    account -- An Account object or None (for Scrobbles by all Accounts).
    limit -- Maximum number to fetch. Default is 10. 'all' for all Artists.
    date -- A datetime or date, for getting Artists from a single time period.
    period -- A String: 'day', 'month', or 'year'.
    """
    check_top_kwargs(**{
        'account': account,
        'limit': limit,
        'date': date,
        'period': period,
    })

    qs_kwargs = {}

    if account:
        qs_kwargs['account'] = account

    if date and period:
        min_post_time, max_post_time = get_post_times(date, period)
        qs_kwargs['min_post_time'] = min_post_time
        qs_kwargs['max_post_time'] = max_post_time

    qs = Artist.objects.with_scrobble_counts(**qs_kwargs)\
                        .order_by('-scrobble_count')

    if limit != 'all':
        qs = qs[:limit]

    return qs


@register.assignment_tag
def top_tracks(account=None, album=None, artist=None, limit=10, date=None, period='day'):
    """
    Returns a QuerySet of most-scrobbled Tracks, with the most-scrobbled
    first.

    Restrict to Tracks from one Album by supplying the 'album'.
    Restrict to Tracks by one Artist by suppling the `artist`.
    Restrict to only one user's scrobbles by supplying the `account`.

    By default gets all Tracks.
    Restrict to a day, month or year by supplying a `date` within that
    day/month/year AND the `period` of 'day', 'month' or 'year'.

    Keyword arguments:
    account -- An Account object or None (for Scrobbles by all Accounts).
    album -- An Album object or None.
    artist -- An Artist object or None.
    limit -- Maximum number to fetch. Default is 10. 'all' for all Tracks.
    date -- A datetime or date, for getting Tracks from a single time period.
    period -- A String: 'day', 'month', or 'year'.
    """

    check_top_kwargs(**{
        'account': account,
        'limit': limit,
        'date': date,
        'period': period,
    })

    if album is not None and type(album) is not Album:
        raise TypeError('album must be an Album instance, '
                        'not a %s' % type(album))

    if artist is not None and type(artist) is not Artist:
        raise TypeError('artist must be an Artist instance, '
                        'not a %s' % type(artist))

    qs_kwargs = {}

    if account:
        qs_kwargs['account'] = account

    if album:
        qs_kwargs['album'] = album

    if artist:
        qs_kwargs['artist'] = artist

    if date and period:
        min_post_time, max_post_time = get_post_times(date, period)
        qs_kwargs['min_post_time'] = min_post_time
        qs_kwargs['max_post_time'] = max_post_time

    qs = Track.objects.with_scrobble_counts(**qs_kwargs)\
                        .order_by('-scrobble_count')

    if limit != 'all':
        qs = qs[:limit]

    return qs


@register.assignment_tag
def recent_scrobbles(account=None, limit=10):
    """Returns a QuerySet of the most recent Scrobbles by all Accounts, or one,
    most recent first.

    Keyword arguments:
    account -- An Account object or None (for Scrobbles by all Accounts).
    limit -- Maximum number to fetch. Default is 10.
    """
    if account is not None and not isinstance(account, Account):
        raise TypeError('account must be an Account instance, '
                        'not a %s' % type(account))

    if isinstance(limit, int) == False:
        raise ValueError("`limit` must be an integer")

    if type(account) is Account:
        return account.get_recent_scrobbles(limit)
    else:
        return Scrobble.objects.all().order_by('-post_time')[:limit]


@register.assignment_tag
def day_scrobbles(date, account=None):
    """
    Returns a QuerySet of all Scrobbles from a particular day, in ascending
    order.

    Restrict to only one user's scrobbles by supplying the `account`.

    Keyword arguments:
    date -- A datetime or date. Required.
            If a datetime, we use the start and end of this day.
    account -- An Account object or None (default, Scrobbles by all Accounts).
    """
    if not isinstance(date, datetime.datetime) and not isinstance(
                                                        date, datetime.date):
        raise TypeError('date must be a datetime or date, '
                        'not a %s' % type(date))

    if account is not None and not isinstance(account, Account):
        raise TypeError('account must be an Account instance, '
                        'not a %s' % type(account))

    qs_kwargs = {}

    if isinstance(date, datetime.datetime):
        qs_kwargs['post_time__gte'] = date.replace(
                                hour=0, minute=0, second=0, microsecond=0)
        qs_kwargs['post_time__lte'] = date.replace(
                        hour=23, minute=59, second=59, microsecond=999999)
    else:
        # `date` is a datetime.date
        # __date filter is only available from Django >= 1.9
        qs_kwargs['post_time__contains'] = date

    qs = Scrobble.objects

    if account:
        qs_kwargs['account'] = account

    return qs.filter(**qs_kwargs).order_by('post_time')


@register.assignment_tag
def annual_scrobble_counts(account=None):
    """
    Get the number of Scrobbles per year.
    Returns a list of dicts, sorted by year, like:
        [ {'year': 2015, 'count': 1234}, {'year': 2016, 'count': 9876} ]

    Keyword arguments:
    account -- An Account object or None (for Scrobbles by all Accounts).
    """

    if account is not None and not isinstance(account, Account):
        raise TypeError('account must be an Account instance, '
                        'not a %s' % type(account))

    qs = Scrobble.objects

    if account:
        qs = qs.filter(account=account)

    return qs.values('post_year')\
            .annotate(count=Count('id'))\
            .values('post_year', 'count')\
            .order_by('post_year')

