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
curl https://vertex-ai-summarization.fly.dev/summarize/2

# response
{
  "document": "Turkey has repeatedly refused to allow German MPs to visit the 260 soldiers stationed at the Incirlik airbase.\nThe Ankara government is angry that Germany gave asylum to soldiers accused of involvement in a botched coup.\nThe German contingent provides reconnaissance jets and tanker aircraft as part of a US-led operation against jihadist group so-called Islamic State.",
  "generated_summary": "Turkey denies German MP access to its Incirlik airbase, hosting 260 German soldiers, due to Germany granting asylum to soldiers allegedly involved in a failed coup attempt.",
  "ground_truth_summary": "Germany's cabinet has agreed to move military forces from Turkey to Jordan amid a diplomatic dispute."
}
```
