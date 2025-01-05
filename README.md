# Steps

1. enable the vertex ai and other google cloud services
2. Get json key for corresponding service account
3. Test the vertex ai api using the `python -m dev.test_vertex_ai.py`
4. Test locally using `uvicorn server.main:app --reload`
5. Test using Docker
6. Deploy to Fly.io
   1. `fly launch` # initial test deployment
   2. setup cicd in github actions with proper secrets

# end points

1. `/` - api health check

```bash
# request
curl https://vertex-ai-summarization.fly.dev/

# response
Hello, this API is to showcase Vertex AI based summarization!
```

2. `/summarize/{index}` - get summary of document by index

```bash
# request
curl https://vertex-ai-summarization.fly.dev/summarize/1

# response
{"document":"Media playback is not supported on this device\nThe QPR striker scored on his home debut to boost his hopes of making the squad for the Euro 2016 finals.\n\"Conor has strength, power and composure - he looks like he is going to be an asset for us,\" said O'Neill.\n\"It's a great achievement to go unbeaten in 10 games and now we just want to build on it.\"\nWashington struck his first goal for Northern Ireland before the break, while Roy Carroll kept out Milivoje Novakovic's penalty in the second half.\n\"Scoring the goal was crazy but overall the boys played well and we deserved the win,\" said a delighted Washington.\n\"To set the new 10-game unbeaten record is brilliant and hopefully we can take this form into the next few games and into the tournament in France.\n\"I'm pleased to get another start and a goal, and I just have to work hard and see where it takes me.\"\nCarroll was another Northern Ireland hero, with his fine penalty save ensuring the feel-good factor continues going into friendlies against Belarus on 27 May and Slovakia on 4 June.\n\"I had watched their penalties over the last couple of days so I guessed which way it was going,\" said Carroll.\n\"I've had some bad nights out there but with that save and clean sheet I really enjoyed it.\"","generated_summary":"Conor Washington scored on his home debut for QPR, boosting his chances of making the Euro 2016 squad for Northern Ireland, who extended their unbeaten streak to 10 games.","ground_truth_summary":"Northern Ireland boss Michael O'Neill praised scorer Conor Washington as a 1-0 win over Slovenia set a new record of 10 games unbeaten."}
```
