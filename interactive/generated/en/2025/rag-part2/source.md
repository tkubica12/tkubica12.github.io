---
format_version: 1
title: "Your own data (RAG) for your AI agent, part two - knowledge graph and advanced methods"
subtitle: "Knowledge graph, concept extraction, summarization, and breath-first/depth-first strategies without framework magic."
slug: "rag-part2"
date: "2025-03-12"
language: "en"
source_language: "cs-CZ"
source_slug: "rag-part2"
translation: "machine"
translated_from_hash: "00E57C9C6EA65F67F3DF801B11BF0C93373285107E2FCD6343169089CBF3590A"
translation_status: "current"
status: "experimental"
canonical_url: "/en/2025/rag-part2/"
agent_friendly:
  source: "source.md"
  caveman: "caveman.md"
design:
  theme: "simple-neutral"
  density: "presentation"
---

# Custom data (RAG) for your AI agent part two - knowledge graph and advanced methods

In the last part, we went without magic to try out techniques such as full-text and semantic search, query rewriting, reranking and hybrid search, so we didn't hide behind some framework or service and dived into Python and PostgreSQL. In this way, we were able to enrich our AI agent with targeted data and answer users' inquisitive movie questions. Today we will continue with more advanced methods and although we will be inspired by techniques such as GraphRAG, we are bribing ourselves again for study reasons.

::: summary-grid
- **Knowledge graph**: adds concepts, relationships and summaries over individual documents.
- **Breath-first**: starts from concepts and topics, has more insight.
- **Depth-first**: starts from specific movies, sticks to details.
- **Next step**: AI should choose the strategy dynamically, not have it hard-coded.
:::

# Knowledge graph
We saw last time that the basic approach to RAG is very successful especially for questions that require specific detailed context to answer. Typically, for example, a query about the name of a movie that the user can't remember, but is able to say what it was about and add a few such details. However, there are questions for which the context of only a few films is not enough to answer, but they need to be about aggregations, concepts, genres, scenery and the like. In order to answer them, it is ideal to have both a summarized view and an idea of ​​some properties, categories, their representatives and mutual relationships. Technically speaking, a table is not enough for us, but a graph of nodes and connections according to various relationships (edge), with the fact that for each concept (node ​​type) we also need a summary and explanation of this concept. So we want a **knowledge graph**.

In the following demo, I will be loosely inspired by the [GraphRAG](https://microsoft.github.io/graphrag/) method, but I will definitely deviate, simplify so that we can actually build it ourselves without magic. Let's start from the assumption that for movies we only have the title and description, nothing else (in the reality of movies, we would have some graph information pulled out straight away in the data set - actor, director, etc.). Similar to GraphRAG, let's use a language model (LLM) to extract concepts such as setting, character, genre, theme, and series. Based on this, we then build an overall graph and for each concept, we take the movies that belong to it and use LLM to create a summary of that feature. In some cases, we should start with the next layer, i.e. unify the occurrences in each concept into some supercategories (for example, the Middle Ages category, which will include various more detailed time eras) and summarize again (now it will be summarization by summarization) and include it in the graph.

At this point, it must be said that this preparation phase is very time-consuming and consumes LLM tokens. Additionally, if something is added to the data, the procedure must be run for it as well. This is the disadvantage of this approach, and there are also variants that postpone part of those LLM calls for later, ad-hoc, only when needed - for example [LazyGraphRAG](https://www.microsoft.com/en-us/research/blog/lazygraphrag-setting-a-new-standard-for-quality-and-cost/).

# How to ask?
The basic concept is to search for input nodes in the graph (nodes are movies, genres and similar concepts) and then some traversal of the graph (we follow edges, connectors), where we discover other nodes and possibly combine with some reduction in the number of found nodes through reranking or semantic similarity from the previous part.

The question is which entry points to focus on. We will show a **depth-first** approach, where we will first search for extreme nodes in the form of movies (actually the same as last time) and then we will look for superordinate concepts through the graph, we will add their summaries to the context and we will go back to the movies that have as many concepts in common as possible. The second approach is **breath-first**, where as input nodes we will search for concepts and their summaries and only from them will we move to films.

That's the end of it for today, but I still want to prepare another part, in which we will use LLM to plan and iteratively go through the whole process, similar to the DRIFT (Dynamic Reasoning and Inference with Flexible Traversal) method. This, albeit in a much improved and more complicated form, is under the hood of **Deep Research** on platforms like Perplexity, Google Gemini or ChatGPT.

# Advanced RAG via knowledge graph and no magic
As last time, **please open the corresponding [notebook](https://github.com/tkubica12/azure-workshops/tree/main/d-ai-rag)** - I will give a link to a specific one in each chapter.

## Concept extraction
First, we need to extract the concepts from the description of the movies. **Here is the [notebook](https://github.com/tkubica12/azure-workshops/blob/main/d-ai-rag/rag_level2_step1_extract.ipynb)**

More or less simply, we go movie by movie with a simple prompt:

```
Extract structured information from the following movie title and overview.

Title: {{title}}
Overview: {{overview}}

Please extract the following information in JSON format:
- genres: [list of genres]
- characters: [list of character names]
- themes: [list of thematic elements]
- setting: [time periods and/or locations]
- series: [list of series or saga names]

If there are no relevant details for a category, return an empty array.
```

supplemented by structure output, i.e. a predictable output format:

```python
class EnhancedMovie(BaseModel):
    genres: List[str]
    characters: List[str]
    themes: List[str]
    setting: List[str]
    series: List[str]
```

I dump everything into JSON files and finally create one big one (the result is [here](https://github.com/tkubica12/azure-workshops/blob/main/d-ai-rag/data/movies_graph.json))

## Save chart
**See this [notebook](https://github.com/tkubica12/azure-workshops/blob/main/d-ai-rag/rag_level2_step2_store.ipynb) for saving to PostgreSQL**

PostgreSQL has a special extension available that turns a classic relational database into a graph database supporting the extended cypher query language (an alternative is the Gremlin language, but this extension does not support that). Instead of some specialized database like Neo4J, we can use Apache AGE, which is compatible with Azure Database for PostgreSQL Flexible Server.

First, we create nodes of type Movie and then nodes of type Genre, Character, Theme, Setting and Series (so far there will be no more in them than a name, for example horror or Harry Potter) and we add their edges (IN_GENRE, FEATURES_CHARACTER, INCLUDES_THEME, SET_IN, PART_OF_SERIES).

A bit annoying for me is that the cypher query has to be enclosed in a SQL query, which made using parameters in psycopg2 not work for me, so I had to go through f-strings and escape single quotes. As it turns out later, this "bifurcation" is an annoying limit of the language, when it will be difficult to combine semantic search (requires classic PostgreSQL tables) with graph search - as you will see, I will glue it in Python (which, however, due to the need for reranking, it didn't matter in the end). I definitely plan to look into using CosmosDB and its vector search capability combined with graph queries to see if it's better there.

## Summary of concepts
**Going to [summarize notebook](https://github.com/tkubica12/azure-workshops/blob/main/d-ai-rag/rag_level2_step3_summarize.ipynb)**

In the next step, I need to make a summary for the individual concepts found (Sci-Fi, 13th century, Star Wars, Prague, Knight, Albert Einstein), i.e. summarize what they are. I will serve the LLM with a list of relevant films (for some concepts, for example, the drama genre, I will run out of the pop-up window - I didn't want to deal with that for a simple example, so I'll just cut it, there aren't that many that won't fit).

For example, the character extraction prompt looks like this:

```
TASK:
Create a comprehensive summary of the "{{name}}" character archetype based on movies featuring this type of character. Make sure all information is based on the movies in the collection and not on external knowledge.

Instructions:
1. Define essential traits, motivations, and narrative functions of the "{{name}}" archetype.
2. Provide examples of at least 5 movies prominently featuring this archetype.
3. Describe typical audience expectations and emotional responses associated with this archetype.
4. Highlight common narrative arcs and character development patterns involving this archetype.
5. Explain how this archetype typically interacts with specific genres, settings, or themes.
6. Include aggregated data from the movie collection to support your summary.
```

## Vectorization
**We will do vectorization in [notebook](https://github.com/tkubica12/azure-workshops/blob/main/d-ai-rag/rag_level2_step4_index.ipynb)**

Here it was necessary to solve one snag. Under the hood, AGE works by creating a table of nodes in PostgreSQL with a unique ID and a properties attribute, and then when I save some of their parameters for the nodes (for example, a description of the movie or a summary of the concept), it saves it in the properties column as JSON. If I were to add an embedding (vector) to it as a node property, it would end up somewhere inside the JSON and it would be impossible to use pgvektor to find similarities. This is an annoying limitation that I solved by keeping separate standard tables purely for embedding (id and vector) per movie or concepts.

## More advanced RAG - combination of semantic search and concept graph and concept summarization
Now comes the big finale and we're going to answer the questions, look **in this [notebook](https://github.com/tkubica12/azure-workshops/blob/main/d-ai-rag/rag_level2_step5_query.ipynb)**.

I expanded the range of questions to make it more interesting:

```python
questions = [
    "What movies are about Abby?",
    "I have seen all Star Wars movies and would like tips for something similar I can watch next.",
    "What is the most common genre of the movies where one of key figures is called Mark?",
    "Are there any movies where Prague takes major role and present city as mysterious and ancient?",
    "When movies about drugs are concerned, is it usually rather serious or funny?",
    "What are some movies featuring a strong female lead that also involve adventure?",
    "Which Western films feature outlaws riding to their doom in the American Southwest?"
]
```

::: group id="strategie" title="Strategie pohybu po grafu"

::: card number="01" title="Breath-first" default="open"
Let's find the input nodes, and I'll do it through all types, that is, both movie labels and all concept labels (Character, Genre, Theme, Series, Setting). We will do a semantic search on labels, take the 20 closest ones and serve them to LLM.

Note that the query on Abby overwhelmingly selects the Character node type, and everyone has something with Abby or a similar name. That's cool, but summarizing these concepts doesn't include movie references (maybe just some proxy examples), so the resulting answer isn't much.

The question about "something like Star Wars" was caught a lot on Setting (Imperial Era, Clone Wars Era, Various Planets) and there is Series - Star Wars Saga. The response to movies this time is very decent! The point is that I always wanted to include some typical representatives in summarizing the concept, so it is possible that there are other films in the text than Star Wars.

Question for Mark - all Character nodes, as expected.

The question about Prague as a mysterious city fits again, because it mainly returns nodes of the Setting type, although Prague is not there, but perhaps LLM did not extract it as a separate concept. However, there are many European cities and Czechoslovakia.

The aggregation question on movies about drugs and whether they are serious or funny gives a lot of Theme (Drug Trade, Substance Abuse) and two Genres (Stoner and comedy) that are important to us. Thanks to the films as examples in the summaries, I think the answer is already very decent.

The theme of adventure with a strong woman in the lead finds a lot of Character nodes.

A western from the southwest, logically enough Setting.

:::

::: card number="02" title="Breath-first + graph traversal" default="open"
Now let's do the important thing - add some graph movement to the results, especially from concepts to movies. If there are more, we select the best one through reranking and finally we limit the result and do the reranking again.

Abby has 6 movies instead of 2, much better.

Star Wars turned out similarly - we'll come back to that, even this process is not as perfect as we might like.

Mark's question turned out practically the same.

Prague rather worse, although we learn more about the film The Unbearable Lightness of Being.

Drug films are definitely an improvement for me and not only are there more results, but they seem more accurate to me.

Movies with a strong woman rather worse.

Westerns similar.

If I were to compare it with the tip from the last part, i.e. hybrid search, query rewriting and reranking, I think that the more advanced method was better (but I can't fully compare, we limited the number of films to 10 last time).

:::

::: card number="03" title="Depth-first" default="open"
Let's try it differently now. We will do a simple semantic search exclusively for movies, similar to the previous part (of course - we don't have the full-text part, only the semantic part) and we will send the 30 best movies directly to LLM.

Abby - a problem (we saw that last time, full-text saved us there).

Star Wars - great, more movies helped, exactly as we speculated last time.

Mark - it seems quite wrong, an aggregation query and we are missing a more global context.

Prague - quite ok, still the same one movie.

Drugs - the list of films is quite ok, but the answers lack a more global context. He doesn't describe how the films are serious or funny, he can only give a list.

Strong woman - sounds good to me.

Western - good.

:::

::: card number="04" title="Depth-first + graph traversal" default="open"
Here it's a bit more complicated in the code, but I tried this:
1. What we did in the previous step - semantic search over movies (depth, this time at 20)
2. From the selected films, we will go up the graph (breath) and along the way we will limit the numbers so that we don't explode. We will then look at which concepts are frequently repeated and sort it accordingly and trim the list. In this way, we obtain concepts that are common to the input films, and we will later use their summaries in the LLM.
3. Now we will go back down (depth) and find their connected films to these most common concepts, we will select interesting ones through reranking.
4. The resulting list is still long, however, we will perform deduplication, then we will eliminate the films that we already have from step number one and we will do another reranking on top of this and select the best ones.
5. Now we take it and send 20 films from the first step, 30 concepts from the second step and 20 films from the third step to the LLM

Abby - persistent condition.

Star Wars - less movies but seems more accurate to me. We still can't fully crack this and we'll try to think why later.

Mark - probably better, the global context helped. However, here I would probably need to go and sort it out manually.

Prague - an interesting change of film. As far as I know, The Illusionist takes place in Vienna, but the film is mainly shot in Prague. This is where the implicit knowledge of the LLM that did it obviously crept into our extraction.

Drugs - traditionally good, a little more context around.

Strong woman - strangely, rather a deterioration (probably due to the smaller number of films in step 1 compared to the previous paragraph).

Western - also rather aggravation.

:::

:::

# Summary and where to go next
The goal today was to try out the concepts and I think it will serve well as a demonstration. Real-world tasks will be larger and more complex, and I believe that the power of these procedures will be even more pronounced in them. For me, the main thing that is fascinating is how breath-first even without individual films gives interesting results and they are qualitatively different (more understanding of topics, but less knowledge of details - which is logical). However, I think the problem is that we have the procedure predetermined and we rely on semantics and reranking to solve everything. At the same time, we know that this tragically does not work with Star Wars - neither embedding nor reranking is strong enough to understand that we are looking for "like Star Wars" and not Star Wars.

What would it look like if we used the mentioned techniques, but on the example of Star Wars, they chose the procedure manually?

1. From the question, I would conclude that searching for movies directly is not optimal and I would start with concepts - especially Theme, Setting and Genre. Character or Series not so much, I don't find the Star Wars films similar, but rather the same.
2. For each of these concepts, I would perhaps reformulate the question so that the semantic search would be more accurate (query rewriting) and it would break down into a plan of three branches.
3. From the names of the closest concepts returned, I would contact the LLM with which one best fits the question. Here it will be about an advanced LLM who will understand that we don't want "Star Wars", "Imerial Era" or "Dark Side" concepts, but rather "Sci-Fi", "Space", "Planes", "Galaxy" and so on.
4. On the concepts thus selected, I would begin to traverse the graph towards the films. However, after a while I would stop and ask the LLM's opinion. We now have better evidence for an answer and can end the search or are we still missing something.
5. If something is missing, we will present our options to the LLM student at the beginning - how to search (full-text, depth, breath, ...). I expect that maybe they will change the strategy and maybe create keywords for the full-text and talk about it or generate something like a follow-up question for semantics.
6. It will go on like this until something expires or until the LLM feels that there is enough material and an answer can be created.

This is how **deep research** works, and there are already various open source frameworks or design proposals for it (like DRIFT). However, just like last time and today, I'll try to just take the basic ideas and put something together from scratch. Well, sometime next time.


::: closing
Sometimes a better similarity search is not enough; the agent must be able to decide where to go for the answer.
:::
