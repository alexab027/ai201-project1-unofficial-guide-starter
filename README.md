# The Unofficial Guide — Project 1

## Domain

## Document Sources

| #   | Source                 | Type | URL or file path                                                                         |
| --- | ---------------------- | ---- | ---------------------------------------------------------------------------------------- |
| 1   | Mit Admissions Website | Blog | https://mitadmissions.org/blogs/entry/every-class-ive-ever-taken/?utm_source=chatgpt.com |

|
| 2 | Mit Admissions Website | Blog | https://mitadmissions.org/blogs/entry/how-i-chose-my-classes/?utm_source=chatgpt.com
|
| 3 | Mit Admissions Website | Blog |https://mitadmissions.org/blogs/entry/6-3/?utm_source=chatgpt.com
|
| 4 | Mit Admissions Website | Blog | https://mitadmissions.org/blogs/entry/classes-im-taking-this-semester/?utm_source=chatgpt.com
|
| 5 | Mit Admissions Website | Blog |https://mitadmissions.org/blogs/entry/curseroad/?utm_source=chatgpt.com |
| 6 | Mit Admissions Website | Blog |https://mitadmissions.org/blogs/entry/a-not-at-all-comprehensive-guide-to-your-first-year/?utm_source=chatgpt.com |
| 7 | Reddit | Forum |https://www.reddit.com/r/mit/comments/10gk3zf/the_workload_for_computer_science_students/?utm_source=chatgpt.com
|
| 8 | Reddit | Forum | https://www.reddit.com/r/mit/comments/tya6z4/which_course6_classes_arewere_the_most_and_least/?utm_source=chatgpt.com
|
| 9 | Mit Admissions Website |Blog |https://mitadmissions.org/blogs/entry/pursuing-cs-as-a-near-beginner/?utm_source=chatgpt.com|
| 10 | Reddit | Forum | https://www.reddit.com/r/mit/comments/1n1yna8/61210_wo_61200/?utm_source=chatgpt.com |

---

## Chunking Strategy

**Chunk size:**
I chunked each document into groups of 4 sentences. I chose sentence-based chunks instead of word-based or character-based chunks because the documents are mostly blog posts and Reddit comments, where complete sentences are important for preserving meaning. This also prevents chunks from ending in the middle of a sentence.
**Overlap:**
I used a 1-sentence overlap between consecutive chunks. For example, one chunk contains sentences 1–4, and the next chunk contains sentences 4–7. This overlap helps preserve context between chunks without making the chunks too repetitive or too large
**Why these choices fit your documents:**
The source documents are mostly MIT Admissions blog posts and Reddit forum discussions. Blog sections often contain several connected paragraphs, while Reddit comments are shorter and more conversational. Four-sentence chunks are long enough to contain a complete idea, but short enough to stay focused on one topic. Because the documents discuss classes, workload, advice, and student experiences, sentence-based chunking makes each chunk easier to retrieve and cite as standalone evidence.
**Final chunk count:**
338

---

## Sample Chunks

CHUNK 1
[blog | 6-3 | Introduction]
Word count: 74

It’s no secret that Course 6-3 (Computer Science) is one of the most, if not the most popular major at MIT. According to the Registrar, there were 757 undergraduate students alone enrolled in Course 6-3 for the Fall 2017 term. That’s roughly a fifth of the undergrad population that declared a major. So it’s not just a meme when people say that if you had to guess what course someone was, it’s probably 6-3.

================================================================================
CHUNK 2
[blog | A (Not At All) Comprehensive Guide to Your First Year | GIRs, Major Requirements, Discovery Classes: Choosing Classes]
Word count: 55

You should have a list of at least 3 CI-Hs you’re interested in. CI-Hs are notoriously difficult to get into, especially the popular ones like 24.900, CMS.100, and 21M.030. As a result, you should always have backups because it’s not guaranteed you’ll get into your top choice CI-H. Look into registering for a PE class.

================================================================================
CHUNK 3
[blog | A (Not At All) Comprehensive Guide to Your First Year | Miscellaneous Things]
Word count: 50

If there’s any place to do it, it’s here at MIT, where diving headfirst into something scary and unknown is not only encouraged, but expected. There will be people to catch you if you fall. Mistakes are welcome. You’re bound to mess up a couple times here at this school.

================================================================================
CHUNK 4
[blog | Curseroad | 18-Wheeler Truck Roadmap]
Word count: 17

Junior Spring: 4.024, 4.440, 8.04. Total Units: 48. Hours Per Week: 52.9. Senior Fall: 4.025, 8.13, 8.05.

================================================================================
CHUNK 5
[blog | How I chose my classes | How Useful Is It?]
Word count: 82

“Usefulness” is a somewhat nebulous concept. Sure, a class is certainly useful if it helps me pass a job interview or teaches me how to use a specific tool in my research, but its usefulness can extend far beyond these “hard” skills. For example, 6.2060 (Microcomputer Project Laboratory) is a class that, at first glance, doesn’t seem very useful at all. The lab assignments all involve programming an obsolete Intel 8051 microprocessor to perform seemingly mundane tasks like striking a fluorescent lamp.

---

## Embedding Model

**Model used:** all-MiniLM-L6-v2 (via sentence-transformers). I picked it because it's small, runs locally for free, and is fast enough to embed the whole corpus and queries in seconds. not depending on an API key kept setup simple.

**Production tradeoff reflection:** If I were shipping this for real users and cost didn't matter, I'd probably move to a larger hosted embedding model (e.g. OpenAI text-embedding-3-large or a bigger sentence-transformer). MiniLM only has a 256-token window, so longer chunks get truncated, and it's English-only and trained on general text rather than my domain. A bigger model would give better accuracy on the kind of niche course/advice language in these docs, handle longer context, and support multilingual queries. The tradeoff is higher latency and a dependency on an external API (rate limits, network failures, data leaving my machine) — so I'd weigh that against just self-hosting a larger open model to keep things local.

---

## Retrieval Test Results

**Query 1:** Is 6-3 a hard major?

**Top returned chunks:**

- **[6-3 | Why Is It 6-3 and Not Just 6?]** (distance 0.5705): "The fact that it's called 6-3 doesn't mean that it's a lesser major or a minor. It's a full-fledged major that is one of many offered by the Electrical Engineering and Computer Science department, which itself falls under the general School of Engineering."
- **[6-3 | 6.046 — Design and Analysis of Algorithms]** (distance 0.7111): "I absolutely got destroyed on the final but managed to pass with a pretty okay grade. To all your friends that say Course 6 is an easy major, please tell them to look at 6.046."

Relevance explanation: Both chunks come from the dedicated 6-3 blog post, which is exactly the topic of the query. The second chunk is the most directly relevant: it speaks to difficulty ("Course 6 is an easy major... look at 6.046"), which is the heart of the question. The first chunk is retrieved because it densely repeats the term "6-3," even though it's more about the major's name than its difficulty — a sign the embedding model rewards keyword overlap as well as meaning.

---

**Query 2:** What are the most interesting and useful course 6 classes?

**Top returned chunks:**

- **[How I chose my classes | Introduction]** (distance 0.6784): "A major contributor to my enjoyment was Course 6's vast catalog of over 200 classes spanning everything under the sun, from music technology to open-heart surgery. The freedom to choose between so many classes enabled me to learn and apply interesting ideas across all of EECS..."
- **[Which Course-6 classes are/were the most and least fruitful to you? | post]** (distance 0.7272): "Which Course-6 classes are/were the most and least fruitful to you? Fruitful: You enjoyed / You learned something new and useful / Your skillset improved... Basically which classes in EECS have the highest and the lowest return on investment?"

Relevance explanation: Both chunks map closely to the query's two key ideas — "interesting" and "useful" course 6 classes. The first chunk discusses the breadth of interesting classes and the enjoyment of choosing them; the second is a Reddit thread explicitly asking which Course 6 classes were the most "fruitful" (enjoyable + useful + skill-building), which is essentially a reworded version of the query. This is a strong retrieval because a blog and a forum source converge on the same intent.

---

**Query 3:** Do MIT CS students think programming experience is enough to succeed?

**Top returned chunks:**

- **[Pursuing CS as a (near) beginner | Computer Science, My Old Friend...]** (distance 0.4179): "There's also plenty of examples of MIT students who graduated with a major in CS without having any programming experience before coming to MIT. According to what I've heard, the learning curve is steep, but it isn't a barrier."
- **[Pursuing CS as a (near) beginner | Computer Science, My Old Friend...]** (distance 0.6132): "...when I took 6.0001 in the fall semester, there were so many people in my vicinity who already had extensive experience in programming... The people who had a good amount of experience in programming say that 6.0001 wasn't bad, the people who had slightly less experience say that it's a hard but doable class."

Relevance explanation: This query returned the lowest distance of all three (0.4179 = strongest match), and all top chunks come from the "Pursuing CS as a (near) beginner" post, which is the single document in the corpus about prior programming experience. The chunks directly address whether experience is required: one says students succeed without prior experience, the other shows how experience level affects how hard 6.0001 feels. The retrieval is tightly on-topic but narrow — it pulls almost exclusively from one document, so the answer reflects one student's perspective.

---

## Grounded Generation

**System prompt grounding instruction:**
You are The Unofficial Guide, a question-answering assistant about MIT classes, Course 6, workload, and student life. You answer using ONLY the numbered context blocks provided by the user.

Rules:

Use only information found in the context blocks. Do not use outside knowledge.
Cite the blocks you draw from using bracketed numbers like [1], [2], [3]. Place a citation right after the claim it supports.
If the context does not contain enough information to answer, reply exactly: "I don't have enough information on that."
Keep the answer concise and grounded. Do not invent sources, links, or facts.
**How source attribution is surfaced in the response:**

Each chunk is assigned to a number before it is sent to the model, and the model cites the number in the asnwer. Additionally, the app builds final sources list from retrieved chunk metadata, so source attribution not entirely from the LLM.

---

## Example Responses

**Grounded response 1**

Query:
What advice do students give for choosing classes in your first year at MIT?

Response:
For choosing classes in the first year at MIT, students are advised to consider their goals and interests [1], and utilize tools like CourseRoad to plan their classes [2]. Additionally, first years should take at least 48 units in the fall to get a representative MIT experience [8]. It's also important to note that there's no one-size-fits-all approach to choosing classes, and students should consider what works best for them [3].

Source attribution:

1. How I chose my classes — Introduction (blog, https://mitadmissions.org/blogs/entry/how-i-chose-my-classes/)
2. Curseroad — Introduction (blog, https://mitadmissions.org/blogs/entry/curseroad/)
3. How I chose my classes — Introduction (blog, https://mitadmissions.org/blogs/entry/how-i-chose-my-classes/)
4. A (Not At All) Comprehensive Guide to Your First Year — GIRs, Major Requirements, Discovery Classes: Choosing Classes (blog, https://mitadmissions.org/blogs/entry/a-not-at-all-comprehensive-guide-to-your-first-year/)

---

**Grounded response 2**

Query:
How heavy is the workload for Course 6 / CS students at MIT?

Response:
The workload for Course 6 (CS) students at MIT is inherently rigorous and intellectually demanding [2]. It can vary depending on the specific classes and program of study, but it is generally considered to be challenging and demanding [4]. Students can expect to spend a significant amount of time on coursework, projects, and studying, with some classes requiring well over 18 hours of work per week [6]. To manage the workload, students typically try to pick a set of classes that add up to around 50 hours per week [8].

Source attribution:

2. The workload for computer science students? — comment (forum, https://www.reddit.com/r/mit/comments/10gk3zf/the_workload_for_computer_science_students/)
3. The workload for computer science students? — comment (forum, https://www.reddit.com/r/mit/comments/10gk3zf/the_workload_for_computer_science_students/)
4. Curseroad — 18-Wheeler Truck (blog, https://mitadmissions.org/blogs/entry/curseroad/)
5. How I chose my classes — Am I Prepared for the Workload? (blog, https://mitadmissions.org/blogs/entry/how-i-chose-my-classes/)

---

**Out-of-scope query**

Query:
What's the best dining hall to eat at on MIT campus?

System response (refusal):
I don't have enough information on that.

(The corpus is focused on Course 6 / CS class selection, workload, and survival advice. None of the retrieved chunks discuss dining hall quality, so the system correctly refuses instead of guessing.)

---

## Query Interface

**Input fields:**
I built the interface with Gradio, so it's just a simple web page. There's one input: a textbox where you type your question (it's a 2-line box with a placeholder showing example questions like "Is 6-3 a hard major?"). You hit submit and it runs the question through retrieval and the model.

**Output format:**
The output is a single textbox that shows two things. First the actual answer to your question, written in plain text with bracket citations like [1] or [2] dropped in after the claims they support. Then below that there's a "Sources:" list that maps each of those numbers to the chunk it came from — title, section, type (blog or forum), and the original URL. I build that sources list myself from the retrieved chunks instead of trusting the model to write it, so the links are always real even if the model miscites.

---

**Sample Interaction Transcript**

> **User:** How heavy is the workload for Course 6 / CS students at MIT?

> **System:**
> The workload for Course 6 (CS) students at MIT is inherently rigorous and intellectually demanding [2]. It can vary depending on the specific classes and program of study, but it is generally considered to be challenging and demanding [4]. Students can expect to spend a significant amount of time on coursework, projects, and studying, with some classes requiring well over 18 hours of work per week [6]. To manage the workload, students typically try to pick a set of classes that add up to around 50 hours per week [8].
>
> Sources: 2. The workload for computer science students? — comment (forum, https://www.reddit.com/r/mit/comments/10gk3zf/the_workload_for_computer_science_students/) 4. The workload for computer science students? — comment (forum, https://www.reddit.com/r/mit/comments/10gk3zf/the_workload_for_computer_science_students/) 6. Curseroad — 18-Wheeler Truck (blog, https://mitadmissions.org/blogs/entry/curseroad/) 8. How I chose my classes — Am I Prepared for the Workload? (blog, https://mitadmissions.org/blogs/entry/how-i-chose-my-classes/)

---

## Evaluation Report

| #   | Question                                                                 | Expected answer                                                                                                                                                                                                                                                                                                                                                                       | System response (summarized)                                                                                                         | Retrieval quality  | Response accuracy                                                                                                                                                                                             |
| --- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | How do I choose between 6-3 and 6-4?                                     | 6-3 requires students to take 6.1220, a very challenging class, and focuses more on computer systems than Artificial intelligence. Students say 6-3 is challenging, but you can choose many paths, though usually they lead to software engineering. 6-4 is more flexible, as rigorous as you decide, and often paired with a double major.                                           | I dont have enough information on that                                                                                               | Relevant           | Accurate — I did not take into account that 6-4 was not mentioned in the blogs or reddit pages when I wrote this question but the ai answered correctly.                                                      |
| 2   | Should I take 6.1210 and 6.1010 at the same time?                        | Your course options are up to you! But it is good to go into the semester being prepared for high rigor. 6.1010 is known to be a very challenging course for those with little programming experience, and many describe 6.1210 as a difficult algorithms class. Both are very helpful core CS classes, but it might be smart to take them alongside easier classes to avoid burnout. | I don't have enough infromation on                                                                                                   | Partially relevant | Inaccurate — i think it has enough information on 6.1210 to answer a question on it. i also didn't account for the fact that 6.1010 used to be called 6.0001 so the ai wouldn't be able to make that judgment |
| 3   | I am struggling to feel like I fit in as a course 6.                     | That is completely normal! Many students have a hard time adjusting to MIT, even comparing it to drinking from a firehose. Try not to compare yourself to others around you, and focus on the experience.                                                                                                                                                                             | You're not alone, people have gotten bad grades on finals. Many find the community to be supportive. many like the applied 6-3 route | Relevant           | Partially accurate -- it recommended a specific major because that was what was most focused on in the data which wasn't really related to the user input                                                     |
| 4   | How do course sixes find balance?                                        | Course 6 is a difficult major to balance at MIT! Other course sixes have suggested branching out to find new hobbies and joining clubs like salsa dancing or intramural sports teams.                                                                                                                                                                                                 | i dont have enough information                                                                                                       | Partially relevant | Inaccurate -- it pulled a lot of sources which some do talk about things outside of school they enjoy and it didn't find anything .                                                                           |
| 5   | I don't know what courses to take next semester after 6.100A and 6.1200. | Many students take 6.1210 and 6.100B after those classes. After new policies, you must take 6.100B or 6.100 before 6.1010, but it is a good idea to take 6.1210 for sure next semester to advance through the 6.12 pipeline.                                                                                                                                                          | You might consider taking 6.031 class in the fall, if you're unsure about your math background you might want to prepare             | Relevant           | Accurate -- I would say this is solid advice, just having the same problem with using old course numbers instead of the new ones                                                                              |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:**
"Should I take 6.1210 and 6.1010 at the same time?" (test question 2)

**What the system returned:**
"I don't have enough information on that." — a full refusal, even though the corpus actually has plenty to say about at least one of these classes.

**Root cause (tied to a specific pipeline stage):**
This is a retrieval failure caused by a vocabulary mismatch, not a generation problem. My corpus refers to the intro programming class by its old number, 6.0001, but I queried with its current number, 6.1010. The embedding model has no way to know those are the same class, so the chunks about 6.1010 get indexed under a course number my query never mentions, and retrieval comes back thin. On top of that, there's actually enough material about 6.1210 to partially answer, but the missing half (6.1010) seems to have dragged the overall retrieval below the bar to answer, so the model defaulted to the refusal line instead of using what it did have.

**What you would change to fix it:**
I'd normalize course numbers during preprocessing — map old numbers to new ones (6.0001 → 6.1010) or keep an alias table — so the query and the corpus are speaking the same vocabulary before anything gets embedded. I'd also loosen the "not enough information" threshold a bit so that when retrieval does surface solid chunks for part of the question (like 6.1210), the system answers the part it can support instead of refusing the whole thing.

---

## Spec Reflection

**One way the spec helped you during implementation:**
Having my 5 test questions and expected answers written out in planning.md before I built anything gave me a fixed bar to grade against, instead of just judging the system on whatever it happened to be good at. When I ran the eval, I could line up the real output against what I'd expected and immediately see where it drifted — like the refusals on questions 2 and 4 — rather than convincing myself the answers were fine. That kept my evaluation honest and made the failures easy to spot.

**One way your implementation diverged from the spec, and why:**
I wrote my expected answers in planning.md before I really knew what was in the corpus, so some of them assumed knowledge the documents don't actually contain — 6-4 details, course-balance/hobby advice, and the current course numbers (6.1010 instead of the old 6.0001). Because of that, my system "diverged" by refusing or answering narrowly in places where my spec expected a complete answer. Looking back, a lot of that is the system being honest about what its sources actually support rather than a real bug, but it's still a gap between what I planned for and what the corpus could back up.

---

## AI Usage

**Instance 1**

- _What I gave the AI:_ I gave it my chunking strategy from planning.md (4 sentences per chunk, 1-sentence overlap) and asked it to write the sentence splitter and `chunk_text()` for me.
- _What it produced:_ It returned a `split_into_sentences()` that just split on sentence-ending punctuation followed by whitespace (`re.split(r"(?<=[.!?])\s+", text)`) and a `chunk_text()` that grouped those sentences into 4s with the overlap.
- _What I changed or overrode:_ The naive split broke on my data because MIT course numbers like 6.1210 and 18.06 contain periods, so it was cutting "6.1210" into two separate "sentences" and wrecking chunks that were full of course numbers. I had it protect course numbers, common abbreviations (e.g., i.e., Prof.), and URLs by swapping the periods out before the split and restoring them after. That's specific to my domain — most text doesn't have decimals scattered through it the way course-selection advice does.

**Instance 2**

- _What I gave the AI:_ I gave it my grounding requirement — answer only from the retrieved chunks, cite them, and refuse if there isn't enough — and asked it to write the system prompt and the answer-formatting code in query.py.
- _What it produced:_ It wrote a system prompt telling the model to use only the context, cite blocks with bracket numbers, and produce the sources list itself as part of the answer.
- _What I changed or overrode:_ I didn't want to trust the model to write the source links, because if it miscites or hallucinates a URL the citations are worthless. So I overrode that and built the sources list myself in `format_sources()` from the retrieved chunk metadata (title, section, type, distance), and left the model responsible only for the bracket numbers in the text. I also pinned the refusal to the exact string "I don't have enough information on that." so the out-of-scope behavior is consistent instead of the model improvising a different refusal each time.
