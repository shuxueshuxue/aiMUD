#game #aiMUD 

Now let's compose this together. Our LLM-based text MUD works like this:
1. The server launches
2. The player run the python client code in his terminal(presumedly windows powershell)
3. The player enters the game through login
4. All players share the same only game progress saved on the server. The server simply send its progress to the player when it's initialized or updated because another player's action. All players play on only 1 story with no branch. No secret, hidden moving.
5. The following data is saved on the server side and constantly updating: player account information(account name, password), player character reference(which character does the player control?), keywords, keyword graph, game progress(the most important one - the story!)
6. Notice there is no notion like "player xxx's turn". Player decide their moving on their side, nothing to do with the minimalist program.
7. So the game logic is really easy, multiple players is almost essentially treated as only one.
8. The main process that is not implemented yet is the call to openai api to let LLM continue the story whenever some player inputs some text like "go grab the sword". The prompt sent is the the instruction(general rules on how to continue the story, general styles), current game progress and the extracted keywords(currently set to depth 2, not directed).
