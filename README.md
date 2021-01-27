# MovieAdvisor_TelegramBot
AI Telegram Bot which recommends movies based on a description of the movie genre by the user
The bot asks the user to provide a description of the movie they would like to see, extracts the keywords from the user's text and makes a query on DBPedia.

Based on the keywords, it assigns a score to each film found.

The bot returns 1 to 3 results based on the score obtained by each movie.

It is possible to choose the starting year to search from.
It is also possible to extend the search to more results if those obtained do not satisfy the user.

The bot computes keywords with a TF-IDF function on a corpus of movies taken from Wikipedia.
The score obtained from the keywords is used to query DBPedia and return the most relevant films.

