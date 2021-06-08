import tweepy

# Authenticate to Twitter
auth = tweepy.OAuthHandler("FntFMPFx13PH4OvWVbqbFbqQ4", "mLtwuKXgOtHBF2WHW5GbYN9kqFg4bzp0jkwBn2rUYhLIYDD23G")
auth.set_access_token("1399406374107422721-kLr0L5tZBjoptCs5kRo0sDBAkRE3zj", "z7RVF5DvadcWXskhjPIeeqYVO5xQQJJFWcaoQuTe65Rmp")

# Create API object
api = tweepy.API(auth)

# Create a tweet
api.update_status("THis is just a test?")
