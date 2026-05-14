# Firebase Genkit vs. Antigravity

## Part 1: Opinion on Genkit vs. Antigravity

Since you are looking to use this in Antigravity (Google's new agentic IDE released Nov 2025), it is important to distinguish between the tooling and the framework:

**Firebase Genkit (The Framework):** The video (from July 2025) describes Genkit, which is a library/framework for coding agents. It handles the "plumbing"—unifying models (Gemini, Gemma), defining tools (like the weather API example), and managing traces.

**Google Antigravity (The IDE):** Antigravity is the environment where you build these apps.

**My Take:** Using Genkit inside Antigravity would be a powerful combination. Antigravity's autonomous agents can write the Genkit boilerplate for you.

**Pros:** You can use Antigravity's "Manager View" to orchestrate an agent that writes the Genkit code demonstrated in this video. The video shows manual setup (Express.js, TypeScript, Zod schemas); an Antigravity agent could generate that entire index.ts file in one shot based on this transcript.

**Observation:** The video focuses on "serverless" deployment to Cloud Run. Antigravity agents excel at this type of infrastructure-as-code task, meaning you could likely give an Antigravity agent this transcript and ask it to "scaffold a Genkit project that matches this tutorial and deploy it to Cloud Run," and it would handle both the coding and the gcloud CLI commands autonomously.

## Part 2: Video Transcript

Video: Build AI agents with Cloud Run and Firebase Genkit
Speakers: Martin Omander, Nohe

(0:00) Everybody is talking about AI agents calling APIs for you.
(0:04) I think I even saw an ad on the side of a bus about it this morning!
(0:08) Yeah, it's a pretty hot topic.
(0:10) The more tools you have to call, the more of an agentic system you can build.
(0:15) So let's say I want to tinker with it in my web app or native mobile app.
(0:19) And I'd like to do that with a minimum of code.
(0:22) Well, Firebase Genkit may be just what you need.
(0:24) Let me show you!
(0:34) Hi, Nohe!
(0:35) Thanks for joining me today.
(0:37) What do you do here at Google?
(0:39) I'm a Developer Relations Engineer in the Firebase team.
(0:43) My job is to make it easier for developers outside Google 
(0:46) to get more done by using Firebase and Google Cloud.
(0:51) That sounds great because I get questions in YouTube comments from developers 
(0:55) all the time about how to build AI agents into their applications.
(1:00) Well, good.
(1:02) I hope you're ready to talk about tool calling and agents with our Firebase 
(1:05) Agent Library.
(1:07) Yes, I have heard a lot about this new Firebase library called 
(1:11) what is it -- Genkit?
(1:13) That is right.
(1:14) Genkit is designed to bridge the gap 
(1:16) between your AI models and real world applications.
(1:20) It simplifies integrating generative AI into your projects.
(1:24) Very cool.
(1:25) What does Genkit bring to the table?
(1:29) Genkit brings three things.
(1:31) AI projects often use various models from different providers.
(1:35) For example, you might use Gemini for complex queries 
(1:38) with a very large context window and Gemma for quick local inference.
(1:43) Genkit simplifies this by providing a unified interface.
(1:47) You can even use it with models from outside Google,
(1:50) with things like the Ollama plugin or writing your own integration.
(1:54) That sounds useful.
(1:56) Also, Genkit makes it easy to define tools that we want our model 
(2:00) to have access to through a unified interface called defineTool().
(2:05) Genkit provides an observability tool that is integrated 
(2:07) with the Firebase console, so you can easily see and track 
(2:11) when your nondeterministic flows succeed and fail.
(2:15) I love it when things are easy.
(2:17) Could you show us a code example?
(2:19) Yes. Let's build a weather app.
(2:21) The user will ask our app a question like this.
(2:24) What's the weather in Sunnyvale, California?
(2:27) The AI understands that question.
(2:29) It can call an external API to get the weather in that location.
(2:33) And this I will use the API to read weather data.
(2:37) But the AI could also call the API to take some action right?
(2:42) Yes it can.
(2:43) We can have the AI execute actions on our behalf,
(2:46) like creating a new document, sending an email,
(2:49) or even start a separate task to hand off to another AI agent.
(2:53) There's a good docs page about how to do that with Genkit.
(2:56) It sounds like you can build some pretty smart applications
(2:59) by using multiple agents, taking actions.
(3:03) I will add a link to that doc from the description below.
(3:07) Very good.
(3:08) Today the AI will only use an API to read weather data.
(3:12) The AI will put that data in a nice human
(3:15) readable text and return it to the user.
(3:18) Let's start building it.
(3:19) Here is an Express application skeleton using TypeScript.
(3:23) Our code will go here in index.js.
(3:28) First I will import the Genkit libraries.
(3:33) Then I'll create a Genkit
(3:35) object that says that the AI should run in the us-central1
(3:38) region.
(3:42) Now let's start building the flow.
(3:44) I'll define what the input and the output schemas should look like
(3:47) using input schema and output schema.
(3:50) And what does the Z there mean?
(3:53) That means we are defining the schema using Zod syntax.
(3:58) Zod is a schema declaration and validation library.
(4:02) Oh right, I've used Zod to validate inputs for a REST API I built.
(4:07) So those are inputs and outputs.
(4:09) Where does the logic go?
(4:11) That's next.
(4:13) Here I will call ai.generate() and tell Genkit which model to use.
(4:18) How to configure it.
(4:19) Like what temperature to use.
(4:21) What system prompt you use and what user prompt to use.
(4:25) Okay, that seems pretty straightforward.
(4:28) Yes. And as I'm building this, I can test it
(4:30) by running “npx genkit start” at any point.
(4:34) That command creates this user interface where I can enter a prompt
(4:37) like “what is Cloud Run?”
(4:40) There's no response.
(4:43) Oh, I made a mistake.
(4:45) It shouldn't return the empty string.
(4:47) Let's return response.text instead.
(4:51) Do I have to run my apps all through this dashboard you showed us?
(4:56) No. The command that we ran
(4:58) merely launch the dashboard and listened for a Genkit process to be run.
(5:02) So we were able to inspect
(5:03) our Genkit flows without executing an entire application.
(5:07) This helps you go faster as a developer when you have a tight feedback loop.
(5:11) And it looks like there's the answer to our question about Cloud Run.
(5:15) Very nice!
(5:16) Now how do we make this into a weather app?
(5:21) First, let's use defineTool() to define the function
(5:24) that Genkit will call to get the weather for a given location.
(5:27) It takes name,
(5:29) description,
(5:32) input schema,
(5:34) and output schema.
(5:37) Oh, wow! Look at that.
(5:39) Gemini autocompleted the schemas for me.
(5:42) I love it.
