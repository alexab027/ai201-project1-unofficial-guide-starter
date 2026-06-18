# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
I chose student advice given on public forums aimed at underclasses CS majors at MIT. This knowledge is valuable because it gives students information they cannot see on the official course catalogs centralized in one place and can give students advice navigating course selection.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Mit Admissions Website | Blog |https://mitadmissions.org/blogs/entry/every-class-ive-ever-taken/?utm_source=chatgpt.com
|
| 2 | Mit Admissions Website | Blog | https://mitadmissions.org/blogs/entry/how-i-chose-my-classes/?utm_source=chatgpt.com
|
| 3 | Mit Admissions Website |  Blog |https://mitadmissions.org/blogs/entry/6-3/?utm_source=chatgpt.com
 |
| 4 | Mit Admissions Website |  Blog | https://mitadmissions.org/blogs/entry/classes-im-taking-this-semester/?utm_source=chatgpt.com
|
| 5 | Mit Admissions Website |  Blog |https://mitadmissions.org/blogs/entry/curseroad/?utm_source=chatgpt.com |
| 6 | Mit Admissions Website |  Blog |https://mitadmissions.org/blogs/entry/a-not-at-all-comprehensive-guide-to-your-first-year/?utm_source=chatgpt.com |
| 7 | Reddit |  Forum |https://www.reddit.com/r/mit/comments/10gk3zf/the_workload_for_computer_science_students/?utm_source=chatgpt.com
 |
| 8 | Reddit | Forum | https://www.reddit.com/r/mit/comments/tya6z4/which_course6_classes_arewere_the_most_and_least/?utm_source=chatgpt.com
|
| 9 | Mit Admissions Website |Blog |https://mitadmissions.org/blogs/entry/pursuing-cs-as-a-near-beginner/?utm_source=chatgpt.com|
| 10 | Reddit | Forum | https://www.reddit.com/r/mit/comments/1n1yna8/61210_wo_61200/?utm_source=chatgpt.com |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->
 

**Chunk size:**
I will split forum pages into comments. subcomments will be related to their parent comment if < 75 words. Blog pages will be split by headings and subheadings. for any chunk > 700 words, chunks will be split by paragraph, preserving full sentences always if paragraph is > 700 words. the target for blogs will be 250-500 words and for forum comments 100-500 words.
**Overlap:**
Overlap 50-100 words for long sections. 
**Reasoning:**
Forums will have shorter form advice typically, with information related to parent post/comment, where Blogs will tend to be longer form but more structured in terms of headings and content. 

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**
all-MiniLM-L6-v2 via sentence-transformers

**Top-k:** I will take the top 8-10 chunks per query. 

**Production tradeoff reflection:**
I would weigh context, recency of advice (especially for a web crawler because courses change in contentover time). If cost wasn't a constraint, I might use text-embedding-3-large + reranker to handle messy student blog writing and informal forum posts. Then the reranker could organize my chunks, and i might use 12-15 instead of 8-10 for higher accuracy.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | How do I choose between 6-3 and 6-4? | 6-3 requires students to take 6.1220, a very challenging class, and focuses more on computer systems than Artificial intelligence. Students say 6-3 is challenging, but you can choose many paths, though usually they lead to software engineering. 6-4 is more flexible, as rigorous as you decide, and often paired with a double major. |
| 2 | Should I take 6.1210 and 6.1010 at the same time? | Your course options are up to you! But it is good to go into the semester being prepared for high rigor. 6.1010 is known to be a very challenging course for those with little programming experience, and many describe 6.1210 as a difficult algorithms class. Both are very helpful core CS classes, but it might be smart to take them alongside easier classes to avoid burnout. |
| 3 | I am struggling to feel like I fit in as a course 6. | That is completely normal! Many students have a hard time adjusting to MIT, even comparing it to drinking from a firehose. Try not to compare yourself to others around you, and focus on the experience. |
| 4 | How do course sixes find balance? | Course 6 is a difficult major ot balance at MIT! Other course sixes have suggested branching out to find new hobbies and joining clubs like salsa dancing or intramural sports teams.  |
| 5 | I don't know what courses to take next semester after 6.100A and 6.1200. | Many students take 6.1210 and 6.100B after those classes. After new policies, you must take 6.100B or 6.100 before 6.1010, but it is a good idea to take 6.1210 for sure next semester to advance through the 6.12 pipeline.  |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. The query itself may not have specific enough information for the AI to be helpful. For example, if it doesn't know your current courses, major, year, experience, the advice might not be directed toward the correct person. 

2. The blog posts might be too narrative, and weave in more niche stories that aren't relevant to advice, leading to difficulty in chunking and off-topic retrieval. 

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->
    [Document Ingestion]
MIT Admissions Blogs
Reddit Forums
        |
        v
[Preprocessing]
Forums -> split by comments
Blogs  -> split by headings
        |
        v
[Chunking]
Target: 100–500 words
Overlap: 50–100 words
Blogs: 250–500 words
Forums: 100–500 words
Max: 700 words
Split by paragraph
        |
        v
[Embedding + Vector Store]
sentence-transformers
all-MiniLM-L6-v2
ChromaDB
Local, no API key
No rate limits
        |
        v
[Retrieval]
Semantic search
ChromaDB query
        |
        v
[Relevant Chunks]
Return relevant chunks
        |
        v
[Generation]
Groq LLM
llama-3.3-70b-versatile

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->


**Milestone 3 — Ingestion and chunking:**
for ingestion and chunking ill give claude my chunking strategy section and as it to implement chunk_text() with my
chunk size and overlap specified. for ingestion i'll use a web scraping function to extract the text from specified web pages.
then i will clean and format the text so that I can use it for my chunking strategy

**Milestone 4 — Embedding and retrieval:**
I will convert each cleaned text chunk into an embedding using a sentence-transformer model and store the embeddings, chunk text, and metadata in ChromaDB. When a user asks a question, the system will embed the question and retrieve the most relevant chunks using semantic similarity search.

**Milestone 5 — Generation and interface:**
I will send the retrieved chunks and the user’s question to a Groq-hosted LLM, which will generate an answer grounded only in the provided sources. The interface will let users type natural-language questions and see a direct answer with citations to the source chunks used
