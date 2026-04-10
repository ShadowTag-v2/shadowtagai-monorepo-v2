# Source: https://firebase.blog/posts/2026/02/ai-agent-skills-for-firebase

 Better code, fewer tokens: Introducing Agent Skills for Firebase 

Skip to content

![]()

## [The Firebase Blog](/)

## Better code, fewer tokens: Introducing Agent Skills for Firebase

![Luke Schlangen](https://firebasestorage.googleapis.com/v0/b/first-class-blog.appspot.com/o/authors%2Fluke-schlangen_466x466.webp?alt=media&token=91f40149-cd4f-492e-9b50-20459013052f)

Luke Schlangen

Developer Advocate

Firebase

February 17, 2026

When you ask Antigravity, Gemini CLI, Claude Code, Cursor, or any other AI agent to “add a sign-in screen” to your app, the agent has to rely on its (possibly outdated) foundational training or burn tokens reading through documentation to find the right configuration. **What if you could give your agent the right answer, right away?**

Today, we’re releasing Agent Skills for Firebase to do exactly that.

### What are Agent Skills?

We want to enable both human *and* AI developers to build and operate Firebase apps with greater velocity, security, and control. Agent Skills are specialized instructions and context that you can give to your preferred AI agents to help them understand the nuances of Firebase, then execute tasks more effectively.

> Any AI agent that works with the [Agent Skills specification](https://agentskills.io/specification) can use Agent Skills for Firebase to write code that’s more accurate, secure, and ready for production.

Instead of an agent trying to process the entire Firebase documentation at once, **Skills enable an agent to pull in only the information required for the task at hand**. This reduces token consumption, lowers costs, and increases the accuracy of the agent’s output.

### How do Agent Skills save tokens?

Without Agent Skills, adding domain-specific context often means giving your agent all of the information it needs right away. That could be thousands of tokens before the agent is prompted with a question.

With Agent Skills, you have more control. You can inform the agent of available domain-specific context by just giving a short description of the skills available. These descriptions need very few tokens. As the agent works, it can decide to ‘activate’ the skill when it’s presented with a task. If the skill isn’t used, it won’t eat up any additional tokens. If your agent does use the skill, it doesn’t consume all of the documentation at once. Your agent can keep reading more of the reference documentation in the skill, bit-by-bit, until it has the information it needs to complete the task. This way it only uses what it needs to use.

The fancy term for this is “progressive disclosure.”

### Build and deploy full-stack web apps with ease

With our initial release, Agent Skills for Firebase are optimized specifically for full-stack web development. By using these Skills, your AI agent can now assist you with:

* **Project and app setup:** Automatically setting up your Firebase project and configuring your app to use Firebase
* **Authentication:** Adding sign-in screens and managing user flows.
* **Firestore:** Architecting your database based on your app’s specific data needs.
* **Security Rules:** Writing and deploying the security rules needed to protect your Firestore data from the start.
* **Firebase App Hosting:** Deploying your web application in a single step.
* **Firebase AI Logic**: Integrating Gemini-powered features to create intelligent, personalized user experiences.
* **And more!** This isn’t the full list, and we’re adding support for more Firebase features soon!

These Skills provide the agent with the knowledge needed to build accurate and secure applications on the first try.

### Choose the right path for AI assistance

Depending on your workflow and the tools you use, you might interact with Firebase through AI assistance in a few different ways. We recommend Firebase developers use Agent Skills for Firebase and Firebase MCP tools together.

Agent Skills and MCP are complementary offerings that should be used together. Think of this as the **relationship between expertise (knowing how to do a task) and capability (having the ability to actually do it)**. Skills provide LLMs with authoritative expertise on how to use Firebase. MCP provides LLMs with tools to set up, configure, and use Firebase services. Agent Skills for Firebase can teach models how to effectively use the Firebase CLI and Firebase MCP tools to accomplish complex tasks efficiently.

* [**Agent Skills for Firebase**](https://firebase.google.com/docs/ai-assistance/agent-skills)**:** Agent Skills provide the quick instructions and recommended practices that tell an agent how to perform Firebase tasks through token-efficient progressive disclosure. It educates AI agents to use tools like Firebase CLI and MCP server effectively.
* [**Firebase MCP server**](https://firebase.google.com/docs/ai-assistance/mcp-server)**:** Designed for AI-assisted development workflows, enabling LLMs to interact with your Firebase projects, resources, and data programmatically.
* [**Firebase CLI**](https://firebase.google.com/docs/cli)**:** A complete command-line tool for hands-on Firebase project and product management, deployment, and local development that can be automatically triggered by AI agents.

If you’re looking for a straightforward answer to the question, “Which one should I use?” We recommend all three. Giving your agent access to all of these tools enables it to choose the right tool for the job.

### Get started

To install Agent Skills for Firebase, navigate to your project directory and run:

$npx skills add firebase/agent-skills

Copied!Copy

[](https://firebasestorage.googleapis.com/v0/b/first-class-blog.appspot.com/o/video%2Finstall-agent-skills-for-firebase.mp4?alt=media&token=04bf0466-d72a-4f25-9ed4-f5e86c8c2239)

You’ll be prompted to select the skills you want to install. Pick the Firebase features you might work with in your current project.

Then you’ll be asked, “Which agents do you want to install to?” Agent Skills for Firebase works with over 30 agents, so you can use this with your favorite coding agent. Wherever you’re building Firebase applications, we want to meet you there.

### Dive deeper and tell us what you think

Want to explore the Skills or give us [feedback](https://firebase.uservoice.com/forums/948424-general?category_id=525325)? We’ve made the source code for these Agent Skills available in our [new GitHub skills repository](https://github.com/firebase/agent-skills). You can start using them now to accelerate your web development workflow. Want to learn more about AI assistance options for Firebase? Check out our documentation on [Developing with AI assistance](https://firebase.google.com/docs/ai-assistance/#develop-with-ai-assistance).

This space is changing fast, so stay tuned as we keep improving these tools. MCP was introduced 15 months ago, Agent Skills was introduced four months ago, and who knows what the next evolution will be in agent tooling. Whatever it is, we’ll be there to support Firebase developers building incredible applications with whatever tools they like best.

#### Categories

* [AI](/category/ai)

∏