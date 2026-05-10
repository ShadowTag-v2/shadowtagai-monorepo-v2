# Source: https://firebase.google.com/docs/ai-assistance/mcp-server

Firebase MCP server  |  Develop with AI assistance



[Skip to main content](#main-content)

[![Firebase](https://www.gstatic.com/devrel-devsite/prod/vd3309c0d80f416d7367081c5c5ffd3cd171f6ea37becda6136423538d770ce20/firebase/images/lockup.svg)](/)

`/`



* English
* Deutsch
* Español – América Latina
* Français
* Indonesia
* Italiano
* Polski
* Português – Brasil
* Tiếng Việt
* Türkçe
* Русский
* עברית
* العربيّة
* فارسی
* हिंदी
* বাংলা
* ภาษาไทย
* 中文 – 简体
* 中文 – 繁體
* 日本語
* 한국어
[Blog](//firebase.blog)
[Go to console](//console.firebase.google.com)

Sign in

* [Documentation](https://firebase.google.com/docs)
* [Develop with AI assistance](https://firebase.google.com/docs/ai-assistance)



* [Firebase](https://firebase.google.com/)
* [Documentation](https://firebase.google.com/docs)
* [Develop with AI assistance](https://firebase.google.com/docs/ai-assistance)
* [AI](https://firebase.google.com/docs/ai)

Send feedback

# Firebase MCP server Stay organized with collections Save and categorize content based on your preferences.



You can use the
[Firebase MCP server](https://github.com/firebase/firebase-tools/tree/master/src/mcp)
to give AI-powered development tools the ability to work with your
Firebase projects and your app's codebase.

The Firebase MCP server works with
any tool that can act as an MCP client, including: Antigravity, Gemini CLI and Gemini Code Assist, Claude Code and Claude Desktop, Cline, Cursor, VS Code Copilot, Windsurf, and more!

[arrow\_downward Jump to setup instructions](#setup)

## Benefits of the MCP server

An editor configured to use the Firebase MCP server can use its AI capabilities
to help you:

* Create and manage Firebase projects
* Manage your Firebase Authentication users
* Work with data in Cloud Firestore and Firebase Data Connect
* Retrieve Firebase Data Connect schemas
* Understand your security rules for Firestore and Cloud Storage for Firebase
* Send messages with Firebase Cloud Messaging

These are only partial lists; see the [server capabilities](#capabilities)
section for a complete list of tools available to your editor.

**Tip:** Consider using [Firebase agent skills](/docs/ai-assistance/agent-skills)
alongside the MCP server to help your AI assistant understand Firebase best
practices and execute complex tasks with higher accuracy and lower cost. For
example, for tasks like setting up services like Authentication, Cloud Firestore, or
Firebase AI Logic, or deploying web apps to Firebase Hosting or
App Hosting, agent skills can provide a more guided
and efficient experience than prompts like `/firebase:init` or
`/firebase:deploy`. When you have both the Firebase MCP server and
Firebase agent skills installed, skills can teach models how to use the MCP
tools to accomplish complex tasks efficiently.

## Set up your MCP client

The Firebase MCP server can work with any MCP client that supports standard I/O
(stdio) as the transport medium.

When the Firebase MCP server makes tool calls, it uses the same user
credentials that authorize the Firebase CLI in the environment where it's
running. This could be a logged-in user or
[Application Default Credentials](https://cloud.google.com/docs/authentication/application-default-credentials),
depending on the environment.

### Before you begin

Make sure you have a working installation of Node.js and npm.

### Basic configuration

Here are basic configuration instructions for using the Firebase MCP server with
some popular AI-assistive tools:

### Antigravity

To configure Antigravity to use the Firebase MCP server:

1. In Antigravity, click the
   more\_horiz menu in the Agent pane >
   **MCP Servers**.
2. Select **Firebase** > **Install**.

This automatically updates your `mcp_config.json` file, which you can view by
clicking **Manage MCP Servers** at the top of the MCP Store pane >
**View raw config**, with the following content:

```
{
  "mcpServers": {
    "firebase-mcp-server": {
      "command": "npx",
      "args": ["-y", "firebase-tools@latest", "mcp"]
    }
  }
}
```

### Gemini CLI

The recommended way to set up the Gemini CLI to use the
Firebase MCP server is to install the
[Firebase extension for Gemini CLI](/docs/ai-assistance/gcli-extension):

```
gemini extensions install https://github.com/gemini-cli-extensions/firebase/
```

Installing the Firebase extension automatically configures the Firebase MCP
server and also comes with a context file that can improve Gemini's Firebase
app development performance.

Alternatively, you can configure Gemini CLI to use the
Firebase MCP server (but not the Firebase extension context file), by editing
or creating one of the configuration files:

* In your project: `.gemini/settings.json`
* In your home directory: `~/.gemini/settings.json`

If the file doesn't yet exist, create it by right-clicking the parent
directory and selecting **New file**. Add the following contents to the file:

```
{
  "mcpServers": {
    "firebase": {
      "command": "npx",
      "args": ["-y", "firebase-tools@latest", "mcp"]
    }
  }
}
```

### Gemini Code Assist

The recommended way to set up Gemini Code Assist to use the
Firebase MCP server is to install the
[Firebase extension for Gemini CLI](/docs/ai-assistance/gcli-extension):

```
gemini extensions install https://github.com/gemini-cli-extensions/firebase/
```

Installing the Firebase extension automatically configures the Firebase MCP
server and also comes with a context file that can improve Gemini's Firebase
app development performance.

Alternatively, you can configure Gemini Code Assist to use the
Firebase MCP server (but not the Firebase extension context file), by editing
or creating one of the configuration files:

* In your project: `.gemini/settings.json`
* In your home directory: `~/.gemini/settings.json`

If the file doesn't yet exist, create it by right-clicking the parent
directory and selecting **New file**. Add the following contents to the file:

```
{
  "mcpServers": {
    "firebase": {
      "command": "npx",
      "args": ["-y", "firebase-tools@latest", "mcp"]
    }
  }
}
```

### Firebase Studio

To configure Firebase Studio to use the Firebase MCP server, edit or
create the configuration file: `.idx/mcp.json`.

If the file doesn't yet exist, create it by right-clicking the parent
directory and selecting **New file**. Add the following contents to the file:

```
{
  "mcpServers": {
    "firebase": {
      "command": "npx",
      "args": ["-y", "firebase-tools@latest", "mcp"]
    }
  }
}
```

### Claude

#### Claude Code

* **Option 1**: Install via plugin (Recommended)

  The easiest way to set up the Firebase MCP server in Claude Code is to
  install the official Firebase plugin:

  1. Add the Firebase marketplace for Claude plugins:

     ```
     claude plugin marketplace add firebase/firebase-tools
     ```
  2. Install the Claude plugin for Firebase:

     ```
     claude plugin install firebase@firebase
     ```
  3. Verify the installation:

     ```
     claude plugin marketplace list
     ```
* **Option 2**: Configure MCP server manually

  Alternatively, you can manually configure the Firebase MCP server:

  1. Run the following command under your app folder:

     ```
     claude mcp add firebase npx -- -y firebase-tools@latest mcp
     ```
  2. Verify the installation:

     ```
     claude mcp list
     ```

     It should show:

     ```
     firebase: npx -y firebase-tools@latest mcp - ✓ Connected
     ```

#### Claude Desktop

To configure Claude Desktop to use the Firebase MCP server, edit the
`claude_desktop_config.json` file. You can open or create this file from the
**Claude > Settings** menu. Select the **Developer** tab, then click
**Edit Config**.

```
{
  "mcpServers": {
    "firebase": {
      "command": "npx",
      "args": ["-y", "firebase-tools@latest", "mcp"]
    }
  }
}
```

### Cline

To configure Cline to use the Firebase MCP server, edit the
`cline_mcp_settings.json` file. You can open or create this file by clicking
the MCP Servers icon at the top of the Cline pane, then clicking the
**Configure MCP Servers** button.

```
{
  "mcpServers": {
    "firebase": {
      "command": "npx",
      "args": ["-y", "firebase-tools@latest", "mcp"],
      "disabled": false
    }
  }
}
```

### Cursor

**Option 1: Marketplace plugin *(recommended)***

Install the
[Firebase plugin from the Cursor Marketplace](https://cursor.com/marketplace/firebase).
This automatically configures the MCP server and provides access to
[Firebase agent skills](/docs/ai-assistance/agent-skills).

**Option 2: One-click MCP setup**

If you only want to add the MCP server to your global configuration, click the
following button:

[![Install MCP Server](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/en/install-mcp?name=firebase&config=eyJjb21tYW5kIjoibnB4IiwiYXJncyI6WyIteSIsImZpcmViYXNlLXRvb2xzQGxhdGVzdCIsIm1jcCJdfQ==)

**Option 3: Manual configuration**

If you prefer to configure the server for a specific project or want to edit
your settings manually, update your `mcp.json` file:

* For a specific project, edit `.cursor/mcp.json`
* For all projects (global), edit `~/.cursor/mcp.json`

```
"mcpServers": {
  "firebase": {
    "command": "npx",
    "args": ["-y", "firebase-tools@latest", "mcp"]
  }
}
```

### VS Code Copilot

To configure a single project, edit the `.vscode/mcp.json` file in your
workspace:

```
"servers": {
  "firebase": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "firebase-tools@latest", "mcp"]
  }
}
```

To make the server available in every project you open, edit your user
settings, for example:

```
"mcp": {
  "servers": {
    "firebase": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "firebase-tools@latest", "mcp"]
    }
  }
}
```

### Windsurf

To configure Windsurf Editor, edit the file
`~/.codeium/windsurf/mcp_config.json`:

```
"mcpServers": {
  "firebase": {
    "command": "npx",
    "args": ["-y", "firebase-tools@latest", "mcp"]
  }
}
```

### Optional configuration

In addition to the basic configuration for each client, shown earlier, there are
two optional parameters you can specify:

* `--dir ABSOLUTE_DIR_PATH`: The absolute path of a
  directory containing `firebase.json`, to set a project context for the MCP
  server. If unspecified, the `get_project_directory` and
  `set_project_directory` tools become available and the default directory will
  be the working directory where the MCP server was started.
* `--only FEATURE_1,FEATURE_2`: A
  comma-separated list of feature groups to activate. Use this to limit the
  tools exposed to only features you are actively using. Note that the core
  tools are always available

For example:

```
"firebase": {
  "command": "npx",
  "args": [
    "-y",
    "firebase-tools@latest", "mcp",
    "--dir", "/Users/turing/my-project",
    "--only", "auth,firestore,storage"
  ]
}
```

## MCP server capabilities

The Firebase MCP server provides three different categories of MCP features:

* [**Prompts**](#prompts): A library of pre-written prompts that you can run;
  they're optimized for developing and running an app with Firebase
* [**Tools**](#tools): A set of tools intended for use by LLMs that help them
  work directly with your Firebase project (with your approval!)
* [**Resources**](#resources): Documentation files intended for use by LLMs to
  give them more guidance and context to complete a task or goal

### Prompts

The Firebase MCP server comes with a library of pre-written prompts optimized
for developing and running an app with Firebase. You can use these prompts to
complete various common tasks or goals with your agentic AI assistants.

The following table describes the prompts the MCP server makes available.

Most development tools that support MCP provide a convenient way to run these
prompts. For example, Gemini CLI makes these prompts available as
slash commands:

```
/firebase:init
```

In the Gemini CLI, start typing `/firebase:` to see a list of available
commands.

**Note:** You can also see this information using the command:
`npx firebase-tools@latest mcp --generate-prompt-list`

| Prompt Name | Feature Group | Description |
| --- | --- | --- |
| firebase:deploy | core | Use this command to deploy resources to Firebase.   Arguments:  <prompt> (optional): any specific instructions you wish to provide about deploying |
| firebase:init | core | Use this command to set up Firebase services, like backend and AI features. |
| crashlytics:connect | crashlytics | Use this command to access a Firebase application's Crashlytics data. |

### Tools

The Firebase MCP server also provides a number of tools intended for use by LLMs
that help them work directly with your Firebase project (with your approval!).
Unlike with prompts, you don't call these tools directly; rather, models that
support tool calling (such as Gemini, Claude, and GPT) can automatically call
these tools to perform development tasks when needed.

The following table describes the tools the MCP server makes available.

**Note:** You can also see this information using the command:
`npx firebase-tools@latest mcp --generate-tool-list`

| Tool Name | Feature Group | Description |
| --- | --- | --- |
| firebase\_login | core | Use this to sign the user into the Firebase CLI and Firebase MCP server. This requires a Google Account, and sign in is required to create and work with Firebase Projects. |
| firebase\_logout | core | Use this to sign the user out of the Firebase CLI and Firebase MCP server. |
| firebase\_validate\_security\_rules | core | Use this to check Firebase Security Rules for Firestore, Storage, or Realtime Database for syntax and validation errors. |
| firebase\_get\_project | core | Use this to retrieve information about the currently active Firebase Project. |
| firebase\_list\_apps | core | Use this to retrieve a list of the Firebase Apps registered in the currently active Firebase project. Firebase Apps can be iOS, Android, or Web. |
| firebase\_list\_projects | core | Use this to retrieve a list of Firebase Projects that the signed-in user has access to. |
| firebase\_get\_sdk\_config | core | Use this to retrieve the Firebase configuration information for a Firebase App. You must specify EITHER a platform OR the Firebase App ID for a Firebase App registered in the currently active Firebase Project. |
| firebase\_create\_project | core | Use this to create a new Firebase Project. |
| firebase\_create\_app | core | Use this to create a new Firebase App in the currently active Firebase Project. Firebase Apps can be iOS, Android, or Web. |
| firebase\_create\_android\_sha | core | Use this to add the specified SHA certificate hash to the specified Firebase Android App. |
| firebase\_get\_environment | core | Use this to retrieve the current Firebase **environment** configuration for the Firebase CLI and Firebase MCP server, including current authenticated user, project directory, active Firebase Project, and more. |
| firebase\_update\_environment | core | Use this to update environment config for the Firebase CLI and Firebase MCP server, such as project directory, active project, active user account, accept terms of service, and more. Use `firebase_get_environment` to see the currently configured environment. |
| firebase\_init | core | Use this to initialize selected Firebase services in the workspace (Cloud Firestore database, Firebase Data Connect, Firebase Realtime Database, Firebase AI Logic). All services are optional; specify only the products you want to set up. You can initialize new features into an existing project directory, but re-initializing an existing feature may overwrite configuration. To deploy the initialized features, run the `firebase deploy` command after `firebase_init` tool. |
| firebase\_get\_security\_rules | core | Use this to retrieve the security rules for a specified Firebase service. If there are multiple instances of that service in the product, the rules for the defualt instance are returned. |
| firebase\_read\_resources | core | Use this to read the contents of `firebase://` resources or list available resources |
| firestore\_delete\_document | firestore | Use this to delete a Firestore documents from a database in the current project by full document paths. Use this if you know the exact path of a document. |
| firestore\_get\_documents | firestore | Use this to retrieve one or more Firestore documents from a database in the current project by full document paths. Use this if you know the exact path of a document. |
| firestore\_list\_collections | firestore | Use this to retrieve a list of collections from a Firestore database in the current project. |
| firestore\_query\_collection | firestore | Use this to retrieve one or more Firestore documents from a collection is a database in the current project by a collection with a full document path. Use this if you know the exact path of a collection and the filtering clause you would like for the document. |
| auth\_get\_users | auth | Use this to retrieve one or more Firebase Auth users based on a list of UIDs or a list of emails. |
| auth\_update\_user | auth | Use this to disable, enable, or set a custom claim on a specific user's account. |
| auth\_set\_sms\_region\_policy | auth | Use this to set an SMS region policy for Firebase Authentication to restrict the regions which can receive text messages based on an ALLOW or DENY list of country codes. This policy will override any existing policies when set. |
| dataconnect\_build | dataconnect | Use this to compile Firebase Data Connect schema, operations, and/or connectors and check for build errors. |
| dataconnect\_list\_services | dataconnect | Use this to list existing local and backend Firebase Data Connect services |
| dataconnect\_execute | dataconnect | Use this to execute a GraphQL operation against a Data Connect service or its emulator. |
| storage\_get\_object\_download\_url | storage | Use this to retrieve the download URL for an object in a Cloud Storage for Firebase bucket. |
| messaging\_send\_message | messaging | Use this to send a message to a Firebase Cloud Messaging registration token or topic. ONLY ONE of `registration_token` or `topic` may be supplied in a specific call. |
| functions\_get\_logs | functions | Use this to retrieve a page of Cloud Functions log entries using Google Cloud Logging advanced filters. |
| remoteconfig\_get\_template | remoteconfig | Use this to retrieve the specified Firebase Remote Config template from the currently active Firebase Project. |
| remoteconfig\_update\_template | remoteconfig | Use this to publish a new remote config template or roll back to a specific version for the project |
| crashlytics\_create\_note | crashlytics | Add a note to an issue from crashlytics. |
| crashlytics\_delete\_note | crashlytics | Delete a note from a Crashlytics issue. |
| crashlytics\_get\_issue | crashlytics | Gets data for a Crashlytics issue, which can be used as a starting point for debugging. |
| crashlytics\_list\_events | crashlytics | Use this to list the most recent events matching the given filters.  Can be used to fetch sample crashes and exceptions for an issue,  which will include stack traces and other data useful for debugging. |
| crashlytics\_batch\_get\_events | crashlytics | Gets specific events by resource name.  Can be used to fetch sample crashes and exceptions for an issue,  which will include stack traces and other data useful for debugging. |
| crashlytics\_list\_notes | crashlytics | Use this to list all notes for an issue in Crashlytics. |
| crashlytics\_get\_report | crashlytics | Use this to request numerical reports from Crashlytics. The result aggregates the sum of events and impacted users, grouped by a dimension appropriate for that report. |
| crashlytics\_update\_issue | crashlytics | Use this to update the state of Crashlytics issue. |
| apphosting\_fetch\_logs | apphosting | Use this to fetch the most recent logs for a specified App Hosting backend. If `buildLogs` is specified, the logs from the build process for the latest build are returned. The most recent logs are listed first. |
| apphosting\_list\_backends | apphosting | Use this to retrieve a list of App Hosting backends in the current project. An empty list means that there are no backends. The `uri` is the public URL of the backend. A working backend will have a `managed_resources` array that will contain a `run_service` entry. That `run_service.service` is the resource name of the Cloud Run service serving the App Hosting backend. The last segment of that name is the service ID. `domains` is the list of domains that are associated with the backend. They either have type `CUSTOM` or `DEFAULT`. Every backend should have a `DEFAULT` domain. The actual domain that a user would use to conenct to the backend is the last parameter of the domain resource name. If a custom domain is correctly set up, it will have statuses ending in `ACTIVE`. |
| realtimedatabase\_get\_data | realtimedatabase | Use this to retrieve data from the specified location in a Firebase Realtime Database. |
| realtimedatabase\_set\_data | realtimedatabase | Use this to write data to the specified location in a Firebase Realtime Database. |

### Resources

The MCP server provides resources, which are documentation files intended for
use by LLMs. Models that support using resources will automatically include
relevant resources in the session context.

The following table describes the resources the MCP server makes available.

**Note:** You can also see this information using the command:
`npx firebase-tools@latest mcp --generate-resource-list`

| Resource Name | Description |
| --- | --- |
| app\_id\_guide | Firebase App Id Guide: guides the coding agent through choosing a Firebase App ID in the current project |
| crashlytics\_investigations\_guide | Firebase Crashlytics Investigations Guide: Guides the coding agent when investigating bugs reported in Crashlytics issues, including procedures for diagnosing and fixing crashes. |
| crashlytics\_issues\_guide | Firebase Crashlytics Issues Guide: Guides the coding agent when working with Crashlytics issues, including prioritization rules and procedures for diagnosing and fixing crashes. |
| crashlytics\_reports\_guide | Firebase Crashlytics Reports Guide: Guides the coding agent through requesting Crashlytics reports, including setting appropriate filters and how to understand the metrics. The agent should read this guide before requesting any report. |
| backend\_init\_guide | Firebase Backend Init Guide: guides the coding agent through configuring Firebase backend services in the current project |
| ai\_init\_guide | Firebase GenAI Init Guide: guides the coding agent through configuring GenAI capabilities in the current project utilizing Firebase |
| data\_connect\_init\_guide | Firebase Data Connect Init Guide: guides the coding agent through configuring Data Connect for PostgreSQL access in the current project |
| firestore\_init\_guide | Firestore Init Guide: guides the coding agent through configuring Firestore in the current project |
| firestore\_rules\_init\_guide | Firestore Rules Init Guide: guides the coding agent through setting up Firestore security rules in the project |
| rtdb\_init\_guide | Firebase Realtime Database Init Guide: guides the coding agent through configuring Realtime Database in the current project |
| auth\_init\_guide | Firebase Authentication Init Guide: guides the coding agent through configuring Firebase Authentication in the current project |
| hosting\_init\_guide | Firebase Hosting Deployment Guide: guides the coding agent through deploying to Firebase Hosting in the current project |
| docs | Firebase Docs: loads plain text content from Firebase documentation, e.g. `https://firebase.google.com/docs/functions` becomes `firebase://docs/functions` |




Send feedback

Except as otherwise noted, the content of this page is licensed under the [Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/), and code samples are licensed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0). For details, see the [Google Developers Site Policies](https://developers.google.com/site-policies). Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2026-03-27 UTC.




Need to tell us more?

[[["Easy to understand","easyToUnderstand","thumb-up"],["Solved my problem","solvedMyProblem","thumb-up"],["Other","otherUp","thumb-up"]],[["Missing the information I need","missingTheInformationINeed","thumb-down"],["Too complicated / too many steps","tooComplicatedTooManySteps","thumb-down"],["Out of date","outOfDate","thumb-down"],["Samples / code issue","samplesCodeIssue","thumb-down"],["Other","otherDown","thumb-down"]],["Last updated 2026-03-27 UTC."],[],[]]
