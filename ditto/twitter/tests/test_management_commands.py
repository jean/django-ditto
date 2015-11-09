# coding: utf-8
from unittest.mock import patch, Mock

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.utils.six import StringIO

from .. import factories


class FetchTwitterArgs(TestCase):

    # Child classes should set this:
    fetcher_class_path = ''

    def setUp(self):
        self.patcher = patch(self.fetcher_class_path)
        self.fetcher_class = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()


class FetchTwitterArgsTweets(FetchTwitterArgs):

    fetcher_class_path = 'ditto.twitter.management.commands.fetch_twitter_tweets.RecentTweetsFetcher'

    def test_fail_with_no_args(self):
        "Fails when no arguments are provided"
        with self.assertRaises(CommandError):
            call_command('fetch_twitter_tweets')

    def test_fail_with_account_only(self):
        "Fails when only an account is provided"
        with self.assertRaises(CommandError):
            call_command('fetch_twitter_tweets', account='terry')

    def test_with_recent(self):
        "Calls the correct method when fetching recent tweets"
        call_command('fetch_twitter_tweets', recent='new', stdout=StringIO())
        self.fetcher_class.assert_called_once_with(screen_name=None)
        self.fetcher_class().fetch.assert_called_once_with(num='new')

    def test_with_recent_and_account(self):
        "Calls the correct method when fetching one account's recent tweets"
        call_command('fetch_twitter_tweets', recent='new', account='barbara',
                                                            stdout=StringIO())
        self.fetcher_class.assert_called_once_with(screen_name='barbara')
        self.fetcher_class().fetch.assert_called_once_with(num='new')

    def test_with_number(self):
        "Should send an int to fetch()."
        call_command('fetch_twitter_tweets', recent='25', stdout=StringIO())
        self.fetcher_class.assert_called_once_with(screen_name=None)
        self.fetcher_class().fetch.assert_called_once_with(num=25)


class FetchTwitterFavoritesArgs(FetchTwitterArgs):

    fetcher_class_path = 'ditto.twitter.management.commands.fetch_twitter_favorites.FavoriteTweetsFetcher'

    def test_fail_with_no_args(self):
        "Fails when no arguments are provided"
        with self.assertRaises(CommandError):
            call_command('fetch_twitter_favorites')

    def test_fail_with_account_only(self):
        "Fails when only an account is provided"
        with self.assertRaises(CommandError):
            call_command('fetch_twitter_favorites', account='terry')

    def test_with_favorites(self):
        "Calls the correct method when fetching favorite tweets"
        call_command('fetch_twitter_favorites', recent='new', stdout=StringIO())
        self.fetcher_class.assert_called_once_with(screen_name=None)
        self.fetcher_class().fetch.assert_called_once_with(num='new')

    def test_with_favorites_and_account(self):
        "Calls the correct method when fetching one account's favorite tweets"
        call_command('fetch_twitter_favorites', recent='new',
                                    account='barbara', stdout=StringIO())
        self.fetcher_class.assert_called_once_with(screen_name='barbara')
        self.fetcher_class().fetch.assert_called_once_with(num='new')

    def test_with_favorites(self):
        "Should send an int to fetch()"
        call_command('fetch_twitter_favorites', recent='25', stdout=StringIO())
        self.fetcher_class.assert_called_once_with(screen_name=None)
        self.fetcher_class().fetch.assert_called_once_with(num=25)


class FetchTwitterOutput(TestCase):

    # Child classes should set this:
    fetch_method_path = ''

    def setUp(self):
        self.patcher = patch(self.fetch_method_path)
        self.fetch_method = self.patcher.start()

        user = factories.UserFactory(screen_name='philgyford')
        self.account = factories.AccountFactory(user=user, is_active=True)
        self.out = StringIO()
        self.out_err = StringIO()

    def tearDown(self):
        self.patcher.stop()


class FetchTwitterOutputTweets(FetchTwitterOutput):

    fetch_method_path = 'ditto.twitter.management.commands.fetch_twitter_tweets.RecentTweetsFetcher.fetch'

    def test_success_output(self):
        "Responds correctly when recent tweets were successfully fetched"
        # What the mocked method will return:
        self.fetch_method.side_effect = [
            [{'account': 'philgyford', 'success': True, 'fetched': 23}]
        ]
        call_command('fetch_twitter_tweets', recent='new', stdout=self.out)
        self.assertIn('philgyford: Fetched 23 Tweets', self.out.getvalue())

    def test_error_output(self):
        "Responds correctly when there was an error fetching recent tweets"
        self.fetch_method.side_effect = [
            [{'account': 'philgyford', 'success': False, 'message': 'It broke'}]
        ]
        call_command('fetch_twitter_tweets', recent='new', stdout=self.out,
                                                        stderr=self.out_err)
        self.assertIn('philgyford: Failed to fetch Tweets: It broke',
                                                    self.out_err.getvalue())


class FetchTwitterOutputFavorites(FetchTwitterOutput):

    fetch_method_path = 'ditto.twitter.management.commands.fetch_twitter_favorites.FavoriteTweetsFetcher.fetch'

    def test_success_output(self):
        "Responds correctly when recent tweets were successfully fetched"
        self.fetch_method.side_effect = [
            [{'account': 'philgyford', 'success': True, 'fetched': 23}]
        ]
        call_command('fetch_twitter_favorites', recent='new', stdout=self.out)
        self.assertIn('philgyford: Fetched 23 Tweets', self.out.getvalue())

    def test_error_output(self):
        "Responds correctly when there was an error fetching recent tweets"
        self.fetch_method.side_effect = [
            [{'account': 'philgyford', 'success': False, 'message': 'It broke'}]
        ]
        call_command('fetch_twitter_favorites', recent='new', stdout=self.out,
                                                        stderr=self.out_err)
        self.assertIn('philgyford: Failed to fetch Tweets: It broke',
                                                    self.out_err.getvalue())


class FetchTwitterOutputAccounts(FetchTwitterOutput):

    fetch_method_path = 'ditto.twitter.management.commands.fetch_accounts.VerifyFetcher.fetch'

    def test_success_output(self):
        "Responds correctly when users were successfully fetched"
        self.fetch_method.side_effect = [
            [{'account': 'philgyford', 'success': True}]
        ]
        call_command('fetch_accounts', stdout=self.out)
        self.assertIn('Fetched @philgyford', self.out.getvalue())

    def test_error_output(self):
        "Responds correctly when there was an error fetching users"
        self.fetch_method.side_effect = [
                [{'account': 'philgyford', 'success': False,
                    'message': 'It broke'}]
        ]
        call_command('fetch_accounts', stdout=self.out, stderr=self.out_err)
        self.assertIn('Could not fetch @philgyford: It broke',
                                                        self.out_err.getvalue())


class ImportTweets(TestCase):

    def setUp(self):
        self.patcher = patch('ditto.twitter.management.commands.import_tweets.TweetIngester.ingest')
        self.ingest_mock = self.patcher.start()
        self.out = StringIO()
        self.out_err = StringIO()

    def tearDown(self):
        self.patcher.stop()

    def test_fails_with_no_args(self):
        "Fails when no arguments are provided"
        with self.assertRaises(CommandError):
            call_command('import_tweets')

    def test_fails_with_invalid_directory(self):
        with patch('os.path.isdir', return_value=False):
            with self.assertRaises(CommandError):
                call_command('import_tweets', path='/wrong/path')

    def test_calls_ingest_method(self):
        with patch('os.path.isdir', return_value=True):
            call_command('import_tweets', path='/right/path', stdout=self.out)
            self.ingest_mock.assert_called_once_with(
                                        directory='/right/path/data/js/tweets')

    def test_success_output(self):
        """Outputs the correct response if ingesting succeeds."""
        self.ingest_mock.return_value = {
            'success': True, 'tweets': 12345, 'files': 21
        }
        with patch('os.path.isdir', return_value=True):
            call_command('import_tweets', path='/right/path', stdout=self.out)
            self.assertIn('Imported 12345 tweets from 21 files',
                                                            self.out.getvalue())

    def test_error_output(self):
        """Outputs the correct error if ingesting fails."""
        self.ingest_mock.return_value = {
            'success': False, 'message': 'Something went wrong',
        }
        with patch('os.path.isdir', return_value=True):
            call_command('import_tweets', path='/right/path',
                                        stdout=self.out, stderr=self.out_err)
            self.assertIn('Something went wrong', self.out_err.getvalue())


class GenerateTweetHtml(TestCase):

    def setUp(self):
        user_1 = factories.UserFactory(screen_name='terry')
        user_2 = factories.UserFactory(screen_name='bob')
        tweets_1 = factories.TweetFactory.create_batch(2, user=user_1)
        tweets_2 = factories.TweetFactory.create_batch(3, user=user_2)
        account_1 = factories.AccountFactory(user=user_1)
        account_2 = factories.AccountFactory(user=user_2)
        self.out = StringIO()

    @patch('ditto.twitter.models.Tweet.save')
    def test_with_all_accounts(self, save_method):
        call_command('generate_tweet_html', stdout=self.out)
        self.assertEqual(save_method.call_count, 5)
        self.assertIn('Generated HTML for 5 Tweets', self.out.getvalue())

    @patch('ditto.twitter.models.Tweet.save')
    def test_with_one_account(self, save_method):
        call_command('generate_tweet_html', account='terry', stdout=self.out)
        self.assertEqual(save_method.call_count, 2)
        self.assertIn('Generated HTML for 2 Tweets', self.out.getvalue())

    def test_with_invalid_account(self):
        with self.assertRaises(CommandError):
            call_command('generate_tweet_html', account='thelma')

