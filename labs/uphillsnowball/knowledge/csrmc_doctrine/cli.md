# Source: https://firebase.google.com/docs/cli

Firebase CLI reference  |  Firebase Documentation



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



* [Firebase](https://firebase.google.com/)
* [Documentation](https://firebase.google.com/docs)
* [Reference](https://firebase.google.com/docs/reference)

Send feedback

# Firebase CLI reference Stay organized with collections Save and categorize content based on your preferences.




The Firebase CLI
([GitHub](https://github.com/firebase/firebase-tools)) provides a
variety of tools for managing, viewing, and deploying to Firebase projects.

**Before using the Firebase CLI,
[set up a Firebase project](/docs/guides).**

## Set up or update the CLI

### Install the Firebase CLI

You can install the Firebase CLI using a method that matches your operating
system, experience level, and/or use case. Regardless of how you install the
CLI, you have access to the same functionality and the `firebase` command.

**Note:** You can also run Firebase CLI commands in
Cloud Shell. [Cloud Shell](/docs/cloud-shell) is a
browser-based, pre-authenticated command-line environment, accessible from the Firebase console,
and comes with the Firebase CLI pre-installed. This makes it a convenient option for getting
started quickly, provided you add your project files to the Cloud Shell environment.

[Windows](#install-cli-windows)
[macOS](#install-cli-mac-linux)
[Linux](#install-cli-mac-linux)

#### **Windows**

You can install the Firebase CLI for Windows using one of the following
options:

| **Option** | **Description** | **Recommended for...** |
| --- | --- | --- |
| **standalone binary** | Download the standalone binary for the CLI. Then, you can access the executable to open a shell where you can run the `firebase` command. | New developers   Developers not using or unfamiliar with [Node.js](https://www.nodejs.org/) |
| **npm** | Use npm (the Node Package Manager) to install the CLI and enable the globally available `firebase` command. | Developers using [Node.js](https://www.nodejs.org/) |

### standalone binary

To download and run the binary for the Firebase CLI, follow these steps:

1. Download the
   [Firebase CLI binary for
   Windows](https://firebase.tools/bin/win/instant/latest).
2. Access the binary to open a shell where you can run the `firebase`
   command.
3. Continue to [log in and test the CLI](#sign-in-test-cli).

### npm

To use `npm` (the Node Package Manager) to install the
Firebase CLI, follow these steps:

1. Install [Node.js](https://www.nodejs.org/) using
   [nvm-windows](https://github.com/coreybutler/nvm-windows)
   (the Node Version Manager). Installing Node.js automatically installs
   the `npm` command tools.

   **Note:** The Firebase CLI requires **Node.js v18.0.0 or later**. Some
   Firebase features might require specific versions of Node.js, so check
   each Firebase product's getting started page for any specific Node.js
   requirements.
2. Install the Firebase CLI via `npm` by running the following command:

   ```
   npm install -g firebase-tools
   ```

   This command enables the globally available `firebase` command.

   **Note:** If the `npm install -g firebase-tools` command fails, you might
   need to
   [change npm permissions](https://docs.npmjs.com/getting-started/fixing-npm-permissions).
3. Continue to [log in and test the CLI](#sign-in-test-cli).

#### **macOS or Linux**

You can install the Firebase CLI for macOS or Linux using one of the
following options:

| **Option** | **Description** | **Recommended for...** |
| --- | --- | --- |
| **automatic install script** | Run a single command that automatically detects your operating system, downloads the latest CLI release, then enables the globally available `firebase` command. | New developers   Developers not using or unfamiliar with [Node.js](https://www.nodejs.org/)   Automated deploys in a [CI/CD](https://en.wikipedia.org/wiki/CI/CD) environment |
| **standalone binary** | Download the standalone binary for the CLI. Then, you can configure and run the binary to suit your workflow. | Fully customizable workflows using the CLI |
| **npm** | Use npm (the Node Package Manager) to install the CLI and enable the globally available `firebase` command. | Developers using [Node.js](https://www.nodejs.org/) |

### auto install script

To install the Firebase CLI using the automatic install script, follow
these steps:

1. Run the following cURL command:

   ```
   curl -sL https://firebase.tools | bash
   ```

   This script automatically detects your operating system, downloads the
   latest Firebase CLI release, then enables the globally available
   `firebase` command.

   **Note:** If you experience permission issues when installing on MacOS or
   Linux, you might need to use `sudo` to grant the script the required
   permissions: `sudo curl -sL https://firebase.tools | bash`
2. Continue to [log in and test the CLI](#sign-in-test-cli).

For more examples and details about the automatic install script, refer to
the script's source code at
[firebase.tools](https://firebase.tools/).

### standalone binary

To download and run the binary for the Firebase CLI that's specific
for your OS, follow these steps:

1. Download the Firebase CLI binary for your OS:
   [macOS](https://firebase.tools/bin/macos/latest) |
   [Linux](https://firebase.tools/bin/linux/latest)
2. *(Optional)* Set up the globally available `firebase` command.

   1. Make the binary executable by running `chmod +x ./firebase_tools`.
   2. [Add the binary's path to your
      PATH.](https://unix.stackexchange.com/a/26059)**Note:** If you choose not to set up the `firebase` command, you'll need to
   access the binary each time you want to run a Firebase CLI command.
3. Continue to [log in and test the CLI](#sign-in-test-cli).

### npm

To use `npm` (the Node Package Manager) to install the Firebase CLI,
follow these steps:

1. Install [Node.js](https://www.nodejs.org/) using
   [nvm](https://github.com/creationix/nvm/blob/master/README.md)
   (the Node Version Manager).  
   Installing Node.js automatically installs
   the `npm` command tools.

   **Note:** The Firebase CLI requires **Node.js v18.0.0 or later**. Some
   Firebase features might require specific versions of Node.js, so check
   each Firebase product's getting started page for any specific Node.js
   requirements.
2. Install the Firebase CLI via `npm` by running the following command:

   ```
   npm install -g firebase-tools
   ```

   This command enables the globally available `firebase` command.

   **Note:** If the `npm install -g firebase-tools` command fails, you might
   need to
   [change npm permissions](https://docs.npmjs.com/getting-started/fixing-npm-permissions).
3. Continue to [log in and test the CLI](#sign-in-test-cli).

### Log in and test the Firebase CLI

After installing the CLI, you must authenticate. Then you can confirm
authentication by listing your Firebase projects.

1. Log into Firebase using your Google account by running the following
   command:

   ```
   firebase login
   ```

   This command connects your local machine to Firebase and grants you
   access to your Firebase projects.

   **Note:** The `firebase login` command opens a web page that connects to
   `localhost` on your machine. If you're using a remote machine and don't have
   access to `localhost`, run the command with the flag `--no-localhost`.**Note:** You can also
   [use the Firebase CLI with CI systems](#cli-ci-systems).
2. Test that the CLI is properly installed and accessing your account by
   listing your Firebase projects. Run the following command:

   ```
   firebase projects:list
   ```

   The displayed list should be the same as the Firebase projects listed in
   the [Firebase console](https://console.firebase.google.com/).

### Update to the latest CLI version

Generally, you want to use the most up-to-date Firebase CLI version.

In many cases, new features and bug fixes are available
only with the latest version of the Firebase CLI. It's a good practice to
frequently update the CLI to its latest version.

How you update the CLI version depends on your operating system and how you
installed the CLI.

### Windows

* **standalone binary**: [Download the new
  version](https://firebase.tools/bin/win/instant/latest),
  then replace it on your system
* **npm**: Run `npm install -g firebase-tools`

### macOS

* **automatic install script**: Run `curl -sL https://firebase.tools | upgrade=true bash`

  **Note:** If you experience permission issues when installing on MacOS or
  Linux, you might need to use `sudo` to grant the script the required
  permissions: `sudo curl -sL https://firebase.tools | upgrade=true bash`
* **standalone binary**: [Download the new
  version](https://firebase.tools/bin/macos/latest), then
  replace it on your system
* **npm**: Run `npm install -g firebase-tools`

### Linux

* **automatic install script**: Run `curl -sL https://firebase.tools | upgrade=true bash`

  **Note:** If you experience permission issues when installing on MacOS or
  Linux, you might need to use `sudo` to grant the script the required
  permissions: `sudo curl -sL https://firebase.tools | upgrade=true bash`
* **standalone binary**: [Download the new
  version](https://firebase.tools/bin/linux/latest), then
  replace it on your system
* **npm**: Run `npm install -g firebase-tools`

### Uninstall the Firebase CLI

How you uninstall the CLI depends on your operating system and how you
installed the CLI.

### Windows

* **standalone binary**: Delete the `firebase.exe` binary that you downloaded.
* **npm**: Run `npm uninstall -g firebase-tools`

### macOS

* **automatic install script**: Run
  `curl -sL https://firebase.tools | uninstall=true bash`

  **Note:** If you experience permission issues when uninstalling on MacOS or
  Linux, you might need to use `sudo` to grant the script the required
  permissions: `sudo curl -sL https://firebase.tools | uninstall=true bash`
* **standalone binary**: Delete the `firebase` binary that you downloaded.
  If you added its location to your `PATH` environment variable, be sure to
  remove it.
* **npm**: Run `npm uninstall -g firebase-tools`

### Linux

* **automatic install script**: Run
  `curl -sL https://firebase.tools | uninstall=true bash`

  **Note:** If you experience permission issues when uninstalling on MacOS or
  Linux, you might need to use `sudo` to grant the script the required
  permissions: `sudo curl -sL https://firebase.tools | uninstall=true bash`
* **standalone binary**: Delete the `firebase` binary that you downloaded.
  If you added its location to your `PATH` environment variable, be sure to
  remove it.
* **npm**: Run `npm uninstall -g firebase-tools`

### Use the CLI with CI systems

We recommend that you authenticate using Application Default Credentials when
using the CLI with CI systems.

#### *(Recommended)* Use Application Default Credentials

The Firebase CLI will detect and use Application Default Credentials if
they're set. The simplest way to authenticate the CLI in CI and other
headless environments is to
[set up Application Default Credentials](https://cloud.google.com/docs/authentication/provide-credentials-adc).

#### *(Legacy)* Use `FIREBASE_TOKEN`

Alternatively, you can authenticate using `FIREBASE_TOKEN`. This is less secure
than Application Default Credentials and is no longer recommended.

1. On a machine with a browser,
   [install the Firebase CLI](#install_the_firebase_cli).
2. Start the signin process by running the following command:

   ```
   firebase login:ci
   ```
3. Visit the URL provided, then log in using a Google account.
4. Print a new
   [refresh token](https://developers.google.com/identity/protocols/OAuth2).
   The current CLI session will not be affected.
5. Store the output token in a secure but accessible way in your CI system.
6. Use this token when running `firebase` commands. You can use either of the
   following two options:

   * **Option 1:** Store the token as the environment variable
     `FIREBASE_TOKEN`. Your system will automatically use the token.
   * **Option 2:** Run all `firebase` commands with the
     `--token TOKEN` flag in your CI system.  
     This is the order of precedence for token loading: flag, environment
     variable, desired Firebase project.

**Note:** On any machine with the Firebase CLI installed, you can immediately
revoke access for the specified token by running the following command:
`firebase logout --token TOKEN`

## Initialize a Firebase project

Many common tasks performed using the CLI, such as deploying to a Firebase
project, require a **project directory**. You establish a project directory
using the `firebase init` command. A project directory is usually the same
directory as your source control root, and after running `firebase init`, the
directory contains a [`firebase.json`](#the_firebasejson_file) configuration
file.

To initialize a new Firebase project, run the following command from within your
app's directory:

```
firebase init
```

**Note:** The `firebase init` command does not create a new directory. If you're
starting a new app, you must first make a directory, then run `firebase init`
from within that directory.

The `firebase init` command steps you through setting up your project directory
and some Firebase products. During project initialization, the Firebase CLI
asks you to complete the following tasks:

* Select a default Firebase project.

  This step associates the current project directory with a Firebase project so
  that project-specific commands (like `firebase deploy`) run against the
  appropriate Firebase project.

  It's also possible to
  [associate multiple Firebase projects](/docs/cli#project_aliases)
  (such as a staging project and a production project) with the same project
  directory.
* Select Firebase products to set up in your Firebase project.

  This step prompts you to set configurations for specific files for the
  selected products. For more details on these configurations, refer to the
  specific product's documentation (for example,
  [Hosting](/docs/hosting/quickstart#initialize)). Note that you
  can always run `firebase init` later to set up more Firebase products.

At the end of initialization, Firebase automatically creates the following two
files at the root of your local app directory:

* A [`firebase.json`](#the_firebasejson_file) configuration file that lists
  your project configuration.
* A `.firebaserc` file that stores your project
  [aliases](/docs/cli#project_aliases).

### The `firebase.json` file

The [`firebase init`](#initialize_a_firebase_project) command creates a
`firebase.json` configuration file in the root of your project directory.

The `firebase.json` file is required to
[deploy assets with the Firebase CLI](#deployment) because it specifies
which files and settings from your project directory are deployed to your
Firebase project. Since some settings can be defined in either your project
directory or the
Firebase console, make sure that you resolve any potential
[deployment conflicts](#deployment_conflicts).

You can [configure most Firebase Hosting options](/docs/hosting/full-config)
directly in the `firebase.json` file. However, for other
[Firebase services that can be deployed with the Firebase CLI](#deployment),
the `firebase init` command creates specific files where you can define settings
for those services, such as an `index.js` file for Cloud Functions. You can
also set up [predeploy or postdeploy hooks](#hooks) in the `firebase.json` file.

**Note:** If you run `firebase init` again for any Firebase service, the command
will overwrite the corresponding section of the `firebase.json` file back to the
default configuration for that service.

The following `firebase.json` file is a comprehensive example showing
configuration options for many Firebase services. It also demonstrates features
like multi-codebase Cloud Functions, Local Emulator Suite setup, and
a Remote Config template. Note that a `firebase.json` file for any given
project will only contain configurations for the Firebase services set up for
that specific project (for example, only Firebase Hosting and
Cloud Functions). Adding the `$schema` key enables validation and
autocompletion in many code editors.

```
    {
      "$schema": "https://raw.githubusercontent.com/firebase/firebase-tools/master/schema/firebase-config.json",
      "hosting": {
        "public": "public",
        "ignore": [
          "firebase.json",
          "**/.*",
          "**/node_modules/**"
        ],
        "cleanUrls": true,
        "trailingSlash": false
      },
      "apphosting": {
        "backendId": "my-app",
        "rootDir": "backend",
        "ignore": [
          "firebase.json",
          "**/.*",
          "**/node_modules/**"
        ]
      },
      "firestore": {
        "rules": "firestore.rules",
        "indexes": "firestore.indexes.json"
      },
      "storage": {
        "rules": "storage.rules"
      },
      "database": {
        "rules": "database.rules.json"
      },
      "dataconnect": {
        "source": "dataconnect",
        "location": "us-central1"
      },
      "functions": [
        {
          "source": "functions",
          "codebase": "default",
          "ignore": [
            "**/.*",
            "**/node_modules/**"
          ],
          "predeploy": [
            "npm --prefix \"$RESOURCE_DIR\" run lint",
            "npm --prefix \"$RESOURCE_DIR\" run build"
          ]
        }
      ],
      "emulators": {
        "auth": {
          "port": 9099
        },
        "functions": {
          "port": 5001
        },
        "firestore": {
          "port": 8080
        },
        "hosting": {
          "port": 5000
        },
        "storage": {
          "port": 9199
        },
        "ui": {
          "enabled": true,
          "port": 4000
        },
        "singleProjectMode": true
      },
      "extensions": {
        "my-storage-resizer": "firebase/storage-resize-images@^0.1.0"
      },
      "remoteconfig": {
        "template": "remoteconfig.template.json"
      }
    }
```

While `firebase.json` is used by default, you can pass the
`--config PATH` flag to specify an alternate
configuration file.

#### Configuration for multiple Cloud Firestore databases

When you run `firebase init`, your `firebase.json` file will contain a single
`firestore` key corresponding to your project's default database, as shown
in the preceding example.

If your project contains multiple Cloud Firestore databases, edit your
`firebase.json` file to associate different Cloud Firestore Security Rules and
database index source files with each database. Modify the file with a
JSON array, with one entry for each database.

```
      "firestore": [
        {
          "database": "(default)",
          "rules": "firestore.default.rules",
          "indexes": "firestore.default.indexes.json"
        },
        {
          "database": "ecommerce",
          "rules": "firestore.ecommerce.rules",
          "indexes": "firestore.ecommerce.indexes.json"
        }
      ],
```

#### Cloud Functions files to ignore on deploy

At function deployment time, the CLI automatically specifies
a list of files in the `functions` directory to ignore. This
prevents deploying to the backend extraneous files that could
increase the data size of your deployment.

The list of files ignored by default, shown in JSON format, is:

```
"ignore": [
  ".git",
  ".runtimeconfig.json",
  "firebase-debug.log",
  "firebase-debug.*.log",
  "node_modules"
]
```

If you add your own custom values for `ignore` in `firebase.json`, make
sure that you keep (or add, if it is missing) the list of files shown in the
preceding list.

## Manage project aliases

You can associate multiple Firebase projects with the same project directory.
For example, you might want to use one Firebase project for staging and another
for production. By using different project environments, you can verify changes
before deploying to production. The `firebase use` command lets you switch
between aliases as well as create new aliases.

### Add a project alias

When you select a Firebase project during [project
initialization](#initialize_a_firebase_project), the project is automatically
assigned the alias of `default`. However, to allow project-specific commands to
run against a different Firebase project but still use the *same* project
directory, run the following command from within your project directory:

```
firebase use --add
```

This command prompts you to select another Firebase project and assign the
project as alias. Alias assignments are written to a `.firebaserc` file inside
your project directory.

### Use project aliases

To use assigned Firebase project aliases, run any of the following commands from
within your project directory.

| Command | Description |
| --- | --- |
| `firebase use` | View a list of defined aliases for your project directory |
| `firebase use \ PROJECT_ID|ALIAS` | Directs all commands to run against the specified Firebase project.  The CLI uses this project as the "active project". |
| `firebase use --clear` | Clears the active project.   Run `firebase use PROJECT_ID|ALIAS` to set a new active project before running other CLI commands. |
| `firebase use \ --unalias PROJECT_ALIAS` | Removes an alias from your project directory. |

You can override what's being used as the active project by passing
the `--project` flag with any CLI command. As an example: You can set your
CLI to run against a Firebase project that you've assigned the `staging`
alias. If you want to run a single command against the Firebase project that
you've assigned the `prod` alias, then you can run, for example,
`firebase deploy --project=prod`.

### Source control and project aliases

In general, you should check your `.firebaserc` file into source control to
allow your team to share project aliases. However, for open source projects or
starter templates, you should generally not check in your `.firebaserc` file.

If you have a development project that's for your use only, you can either pass
the `--project` flag with each command or run
`firebase use PROJECT_ID` without assigning an alias to
the Firebase project.

## Serve and test your Firebase project locally

You can view and test your Firebase project on locally hosted URLs before
deploying to production. If you only want to test select features, you can use
a comma-separated list in a flag on the `firebase serve` command.

Run the following command from the root of your local project directory if you
want to do either of the following tasks:

* View the static content for your Firebase-hosted app.
* Use Cloud Functions to [generate dynamic content for
  Firebase Hosting](/docs/hosting/functions) and you want to use your
  *production (deployed)* HTTP functions to emulate Hosting on a local URL.

```
firebase serve --only hosting
```

#### Emulate your project using *local* HTTP functions

Run any of the following commands from your project directory to emulate your
project using *local* HTTP functions.

* To emulate HTTP functions and hosting for testing on local URLs, use either
  of the following commands:

  ```
  firebase serve
  ```

  ```
  firebase serve --only functions,hosting // uses a flag
  ```
* To emulate HTTP functions only, use the following command:

  ```
  firebase serve --only functions
  ```

#### Test from other local devices

By default, `firebase serve` only responds to requests from `localhost`. This
means that you'll be able to access your hosted content from your computer's web
browser but not from other devices on your network. If you'd like to test from
other local devices, use the `--host` flag, like so:

```
firebase serve --host 0.0.0.0  // accepts requests to any host
```

## Deploy to a Firebase project

The Firebase CLI manages deployment of code and assets to your Firebase
project, including:

* New releases of your Firebase Hosting sites
* New, updated, or existing Cloud Functions for Firebase
* New or updated schemas and connectors for Firebase Data Connect
* Security Rules for Firebase Realtime Database
* Security Rules for Cloud Storage for Firebase
* Security Rules for Cloud Firestore
* Indexes for Cloud Firestore

To deploy to a Firebase project, run the following command from your project
directory:

```
firebase deploy
```

You can optionally add a comment to each of your deployments. This comment will
display with the other deployment information on your project's
[Firebase Hosting page](https://console.firebase.google.com/project/_/hosting/main).
For example:

```
firebase deploy -m "Deploying the best new feature ever."
```

When you use the `firebase deploy` command, be aware of the following:

* To deploy resources from a project directory, the project directory
  **must** have a [`firebase.json`](#the_firebasejson_file) file. This file is
  automatically created for you by the
  [`firebase init`](/docs/cli#initialize_a_firebase_project) command.
* By default, `firebase deploy` creates a release for *all* deployable resources
  in your project directory. To deploy specific Firebase services or features,
  [use partial deployment](#partial_deploys).

### Deploy specific Firebase services

If you only want to deploy specific Firebase services or features, you can use a
comma-separated list in a flag on the `firebase deploy` command. For example,
the following command deploys Firebase Hosting content and
Cloud Storage Security Rules.

```
firebase deploy --only hosting,storage
```

The following table lists the services and features available for partial
deployment. The names in the flags correspond to the keys in your
[`firebase.json`](#the_firebasejson_file) configuration file.

| Flag syntax | Service or feature deployed |
| --- | --- |
| `--only database` | Firebase Realtime Database Security Rules |
| `--only dataconnect` | Firebase Data Connect schemas and connectors |
| `--only firestore` | Cloud Firestore Security Rules *and* indexes for all configured databases |
| `--only functions` | Cloud Functions for Firebase |
| `--only hosting` | Firebase Hosting content |
| `--only storage` | Cloud Storage for Firebase Security Rules |

**Note:** The `--only rules` syntax used by earlier versions of the CLI is
deprecated.

#### Deployment conflicts for Security Rules

For Firebase Realtime Database, Cloud Storage for Firebase, and Cloud Firestore,
you can define Security Rules either in your local project directory or in the
[Firebase console](https://console.firebase.google.com/).

**Note:** **When you
[deploy security rules using the Firebase CLI](https://firebase.google.com/docs/cli/#deployment),
the rules defined in your project directory overwrite any existing rules in the
Firebase console.** So, if you choose to define or edit your security rules
using the Firebase console, make sure that you also update the rules defined
in your project directory.

Another option to avoid deployment conflicts is to
[use partial deployment](#partial_deploys) and only define Security Rules in
the Firebase console.

### Set up predeploy and postdeploy scripted tasks

You can connect shell scripts to the `firebase deploy` command to perform
predeploy or postdeploy tasks. For example, a predeploy script could
transpile TypeScript code into JavaScript, and a postdeploy hook could notify
administrators of new site content deploys to Firebase Hosting.

To set up predeploy or postdeploy hooks, add bash scripts to your
[`firebase.json`](#the_firebasejson_file) configuration file. You can define
brief scripts directly in the `firebase.json` file, or you can reference other
files that are in your project directory.

For example, the following script is the `firebase.json` expression for a
postdeploy task that sends a Slack message upon successful deployment to
Firebase Hosting.

```
"hosting": {
  // ...

  "postdeploy": "./messageSlack.sh 'Just deployed to Firebase Hosting'",
  "public": "public"
}
```

The `messageSlack.sh` script file resides in the project directory and looks
like this:

```
curl -X POST -H 'Content-type: application/json' --data '{"text":"$1"}'
     \https://SLACK_WEBHOOK_URL
```

You can set up `predeploy` and `postdeploy` hooks for any of the
[assets that you can deploy](#deployment). Note that running `firebase deploy`
triggers *all* the predeploy and postdeploy tasks defined in your
`firebase.json` file. To run only those tasks associated with a specific
Firebase service, [use partial deployment commands](#partial_deploys).

Both `predeploy` and `postdeploy` hooks print the standard output and error
streams of the scripts to the terminal. For failure cases, note the following:

* If a predeploy hook fails to complete as expected, deployment is canceled.
* If deployment fails for any reason, postdeploy hooks are not triggered.

#### Environment variables

Within scripts running in the predeploy and postdeploy hooks, the following
environment variables are available:

* `$GCLOUD_PROJECT`: The active project's project ID
* `$PROJECT_DIR`: The root directory containing the `firebase.json` file
* `$RESOURCE_DIR`: *(For `hosting` and `functions` scripts only)* The
  location of the directory that contains the Hosting or
  Cloud Functions resources to be deployed

### Deployment quotas

It's possible (though unlikely) that you might exceed a quota that limits the
rate or volume of your Firebase deployment operations. For example, when
deploying very large numbers of functions, you might receive an `HTTP 429 Quota`
error message. To solve such issues, try
[using partial deployment](#partial_deploys).

### Roll back a deployment

You can roll back a Firebase Hosting deployment from your project's
[Firebase Hosting page](https://console.firebase.google.com/project/_/hosting/main)
by selecting the **Rollback** action for the chosen release.

It's not possible to roll back releases of Security Rules for
Firebase Realtime Database, Cloud Storage for Firebase, or
Cloud Firestore.

## Command reference

### CLI administrative commands

| Command | Description |
| --- | --- |
| **help** | Displays help information about the CLI or specific commands. |
| **init** | Associates and sets up a new Firebase project in the current directory. This command creates a [`firebase.json`](https://firebase.google.com/docs/cli/#the_firebasejson_file) configuration file in the current directory. |
| **login** | Authenticates the CLI with your Google Account. Requires access to a web browser.  To log into the CLI in remote environments that don't allow access to `localhost`, use the `--no-localhost` flag. |
| **login:ci** | Generates an authentication token for use in non-interactive environments. |
| **login:add** | Logs in an additional Google Account. |
| **login:list** | Lists all authenticated Google Accounts. |
| **login:use** | Sets the active Google Account. |
| **logout** | Signs out your Google Account from the CLI. |
| **open** | Opens a browser to relevant project resources. |
| **projects:list** | Lists all the Firebase projects to which you have access. |
| **use** | Sets the active Firebase project for the CLI.  Manages [project aliases](#project_aliases). |

### Project management commands

| Command | Description |
| --- | --- |
| Management of Firebase projects | | |
| **projects:addfirebase** | Adds Firebase resources to an existing Google Cloud project. |
| **projects:create** | Creates a new Google Cloud project, then adds Firebase resources to the new project. |
| **projects:list** | Lists all the Firebase projects to which you have access. |
| Management of Firebase Apps (iOS, Android, Web) | | |
| **apps:create** | Creates a new Firebase App in the active project. |
| **apps:list** | Lists the registered Firebase Apps in the active project. |
| **apps:sdkconfig** | Prints the Google services configuration of a Firebase App. |
| **setup:web** | ***Deprecated. Instead, use `apps:sdkconfig` and specify `web` as the platform argument.*** Prints the Google services configuration of a Firebase Web App. |
| Management of SHA certificate hashes (Android only) | | |
| **apps:android:sha:create \  FIREBASE\_APP\_ID SHA\_HASH** | Adds the specified SHA certificate hash to the specified Firebase Android App. |
| **apps:android:sha:delete \  FIREBASE\_APP\_ID SHA\_HASH** | Deletes the specified SHA certificate hash from the specified Firebase Android App. |
| **apps:android:sha:list \  FIREBASE\_APP\_ID** | Lists the SHA certificate hashes for the specified Firebase Android App. |

### Deployment and local development

These commands let you deploy and interact with your Firebase Hosting site.

| Command | Description |
| --- | --- |
| **deploy** | Deploys code and assets from your project directory to the active project. For Firebase Hosting, a [`firebase.json`](/docs/cli#the_firebasejson_file) configuration file is required. |
| **serve** | Starts a local web server with your Firebase Hosting configuration. For Firebase Hosting, a [`firebase.json`](/docs/cli#the_firebasejson_file) configuration file is required. |

### App Distribution commands

| Command | Description |
| --- | --- |
| **appdistribution:distribute \ --app FIREBASE\_APP\_ID** | Makes the build available to testers. |
| **appdistribution:testers:add** | Adds testers to the project. |
| **appdistribution:testers:remove** | Removes testers from the project. |
| **appdistribution:testers:list** | Lists testers in the project. |
| **appdistribution:groups:create** | Creates a tester group. |
| **appdistribution:groups:delete** | Deletes a tester group. |
| **appdistribution:groups:list** | Lists tester groups in the project. |

### App Hosting commands

| Command | Description |
| --- | --- |
| **apphosting:backends:create \  --project PROJECT\_ID \  --location REGION --app APP\_ID** | Creates the collection of managed resources linked to a single codebase that comprises an App Hosting backend. Optionally specify an existing Firebase Web app by its Firebase app ID. |
| **apphosting:backends:get \  BACKEND\_ID \  --project PROJECT\_ID \  --location REGION** | Retrieves specific details, including the public URL, of a backend. |
| **apphosting:backends:list \  --project PROJECT\_ID** | Retrieves a list of all active backends associated with a project. |
| **firebase apphosting:backends:delete \  BACKEND\_ID \  --project PROJECT\_ID \  --location REGION** | Deletes a backend from the project. |
| **firebase apphosting:config:export \  --project PROJECT\_ID \  --secrets ENVIRONMENT\_NAME** | Exports secrets for use in app emulation.  Defaults to secrets stored in `apphosting.yaml`, or takes `--secrets` to specify any environment that has a corresponding `apphosting.ENVIRONMENT_NAME.yaml` file. |
| **firebase apphosting:rollouts:create \  BACKEND\_ID \  --git\_branch BRANCH\_NAME \  --git\_commit COMMIT\_ID** | Creates a manually triggered rollout.  Optionally specify the latest commit to a branch or a specific commit. If no options are provided, prompts selection from a list of branches. |
| **apphosting:secrets:set KEY --project PROJECT\_ID \  --location REGION \  --data-file DATA\_FILE\_PATH** | Stores secret material in Secret Manager.  Optionally provide a path from which to read secret data. Set to `_` to read secret data from standard input. |
| **apphosting:secrets:grantaccess KEY BACKEND\_ID \  --project PROJECT\_ID \  --location REGION** | Grants the [backend service account](/docs/app-hosting/about-app-hosting#service-account) access to the provided secret so that it can be accessed by App Hosting at build or run time. |
| **apphosting:secrets:describe KEY \  --project PROJECT\_ID** | Gets the metadata for a secret and its versions. |
| **firebase apphosting:secrets:access \  KEY[@version] \  --project PROJECT\_ID** | Accesses a secret value given the secret and its version. Defaults to accessing the latest version. |

### Authentication (user management) commands

| Command | Description |
| --- | --- |
| **auth:export** | Exports the active project's user accounts to a JSON or CSV file. For more details, refer to the [auth:import and auth:export page](/docs/cli/auth#auth-export). |
| **auth:import** | Imports the user accounts from a JSON or CSV file into the active project. For more details, refer to the [auth:import and auth:export page](/docs/cli/auth#auth-import). |

### Cloud Firestore commands

| Command | Description |
| --- | --- |
| **firestore:locations** | List available locations for your Cloud Firestore database. |
| **firestore:databases:create** DATABASE\_ID | Create a database instance in native mode in your Firebase project.  The command takes the following flags:   * **--location <region name>** to specify the   deployment location for the database. Note you can run   **firebase firestore:locations** to list available   locations. **Required**. * **--delete-protection <deleteProtectionState>**   to allow or prevent deletion of the specified database. Valid values   are `ENABLED` or `DISABLED`. Defaults to   `DISABLED`. * **--point-in-time-recovery <PITRState>** to   set whether point-in-time recovery is enabled. Valid values are   `ENABLED` or `DISABLED`. Defaults to   `DISABLED`. Optional. |
| **firestore:databases:list** | List databases in your Firebase project. |
| **firestore:databases:get** DATABASE\_ID | Get database configuration for a specified database in your Firebase project. |
| **firestore:databases:update** DATABASE\_ID | Update database configuration of a specified database in your Firebase project.  At least one flag is required. The command takes the following flags:   * **--delete-protection <deleteProtectionState>**   to allow or prevent deletion of the specified database. Valid values   are `ENABLED` or `DISABLED`. Defaults to   `DISABLED`. * **--point-in-time-recovery <PITRState>** to   set whether point-in-time recovery is enabled. Valid values are   `ENABLED` or `DISABLED`. Defaults to   `DISABLED`. Optional. |
| **firestore:databases:delete** DATABASE\_ID | Delete a database in your Firebase project. |
| **firestore:indexes** | List indexes for a database in your Firebase project.  The command takes the following flag:   * **--database** DATABASE\_ID to   specify the name of the database for which to list indexes. If not   provided, indexes are listed for the default database. |
| **firestore:delete** | Deletes documents in the active project's database. Using the CLI, you can recursively delete all the documents in a collection.  Note that deleting Cloud Firestore data with the CLI incurs read and delete costs. For more information, see [Understand Cloud Firestore billing](/docs/firestore/pricing).  The command takes the following flag:   * **--database** DATABASE\_ID   to specify the name of the database from which documents are deleted. If   not specified, documents are deleted from the default database.   Optional. |

### Cloud Functions for Firebase commands

| Command | Description |
| --- | --- |
| **functions:config:clone** | ***Deprecated.*** Clones another project's environment into the active Firebase project. |
| **functions:config:export** | Exports the active project's runtime configuration to Google Cloud Secret Manager. |
| **functions:config:get** | ***Deprecated.*** Retrieves existing configuration values of the active project's Cloud Functions. |
| **functions:config:set** | ***Deprecated.*** Stores runtime configuration values of the active project's Cloud Functions. |
| **functions:config:unset** | ***Deprecated.*** Removes values from the active project's runtime configuration. |
| **functions:delete \  FUNCTION\_NAME** | Deletes the specified function. |
| **functions:list** | Lists deployed functions. |
| **functions:log** | Reads logs from deployed Cloud Functions. |
| **functions:secrets:access \  SECRET\_NAME** | Accesses a secret value given the secret and its version. |
| **functions:secrets:destroy \  SECRET\_NAME** | Destroys a secret. |
| **functions:secrets:get \  SECRET\_NAME** | Gets the metadata for a secret and its versions. |
| **functions:secrets:prune** | Destroys unused secrets. |
| **functions:secrets:set \  SECRET\_NAME** | Creates or updates a secret. |
| **functions:shell** | Starts a local interactive shell for testing functions. |

For more information, refer to the [environment
configuration documentation](/docs/functions/config-env).

### Crashlytics commands

| Command | Description |
| --- | --- |
| **crashlytics:mappingfile:generateid \  --resource-file=PATH/TO/ANDROID\_RESOURCE.XML** | Generates a unique mapping file ID in the specified Android resource (XML) file. |
| **crashlytics:mappingfile:upload \  --app=FIREBASE\_APP\_ID \  --resource-file=PATH/TO/ANDROID\_RESOURCE.XML \  PATH/TO/MAPPING\_FILE.TXT** | Uploads a Proguard-compatible mapping (TXT) file for this app, and associates it with the mapping file ID declared in the specified Android resource (XML) file. |
| **crashlytics:symbols:upload \ --app=FIREBASE\_APP\_ID \ PATH/TO/SYMBOLS** | Generates a Crashlytics-compatible symbol file for native library crashes on Android and uploads it to Firebase servers. |

### Data Connect commands

These commands and their use cases are covered in more detail in the
[Data Connect CLI reference guide](/docs/data-connect/cli-reference).

| Command | Description |
| --- | --- |
| **dataconnect:services:list** | Lists all deployed Data Connect services in your Firebase project. |
| **dataconnect:sql:diff \  SERVICE\_ID** | For the specified service, displays the differences between a local Data Connect schema and your Cloud SQL database schema. |
| **dataconnect:sql:migrate \  --force \  SERVICE\_ID** | Migrates your Cloud SQL database's schema to match your local Data Connect schema. |
| **dataconnect:sql:grant\  --role=ROLE \  --email=EMAIL \  SERVICE\_ID** | Grants the SQL role to the specified user or service account email.  For the `--role` flag, the SQL role to grant is one of: `owner`, `writer`, or `reader`.  For the `--email` flag, provide the email address of the user or service account to grant the role to. |
| **dataconnect:sdk:generate** | Generates typed SDKs for your Data Connect connectors. |

### Extensions commands

| Command | Description |
| --- | --- |
| **ext** | Displays information on how to use Firebase Extensions commands.  Lists the extension instances installed in the active project. |
| **ext:configure \ EXTENSION\_INSTANCE\_ID** | Reconfigures the parameter values of an extension instance in your [extension manifest](/docs/extensions/manifest). |
| **ext:info \ PUBLISHER\_ID/EXTENSION\_ID** | Prints detailed information about an extension. |
| **ext:install \ PUBLISHER\_ID/EXTENSION\_ID** | Adds a new instance of an extension into your [extension manifest](/docs/extensions/manifest). |
| **ext:sdk:install** | Installs SDKs for defining extensions in functions. |
| **ext:list** | Lists all the extension instances installed in a Firebase project.  Prints the instance ID for each extension. |
| **ext:uninstall \ EXTENSION\_INSTANCE\_ID** | Removes an extension instance from your [extension manifest](/docs/extensions/manifest). |
| **ext:update \ EXTENSION\_INSTANCE\_ID** | Updates an extension instance to the latest version in your [extension manifest](/docs/extensions/manifest). |
| **ext:export** | Exports all installed extension instances from your project to your [extension manifest](/docs/extensions/manifest). |

### Extensions publisher commands

| Command | Description |
| --- | --- |
| **ext:dev:init** | Initializes a skeleton codebase for a new extension in the current directory. |
| **ext:dev:list \ PUBLISHER\_ID** | Prints a list of all extensions uploaded by a publisher. |
| **ext:dev:register** | Registers a Firebase project as an [extensions publisher project](/docs/extensions/publishers/register). |
| **ext:dev:deprecate \ PUBLISHER\_ID/EXTENSION\_ID \ VERSION\_PREDICATE** | [Deprecates](/docs/extensions/publishers/upload-and-publish#deprecate) extension versions that match the version predicate.  A version predicate can be a single version (such as `1.0.0`), or a range of versions (such as `>1.0.0`).  If no version predicate is provided, deprecates all versions of that extension. |
| **ext:dev:undeprecate \ PUBLISHER\_ID/EXTENSION\_ID \ VERSION\_PREDICATE** | [Undeprecates](/docs/extensions/publishers/upload-and-publish#deprecate) extension versions that match the version predicate.  A version predicate can be a single version (such as `1.0.0`), or a range of versions (such as `>1.0.0`).  If no version predicate is provided, undeprecates all versions of that extension. |
| **ext:dev:upload \ PUBLISHER\_ID/EXTENSION\_ID** | [Uploads a new version of an extension.](/docs/extensions/publishers/upload-and-publish#first-upload) |
| **ext:dev:usage \ PUBLISHER\_ID** | Displays install counts and usage metrics for extensions uploaded by a publisher. |

### Hosting commands

| Command | Description |
| --- | --- |
| **hosting:disable** | Stops serving Firebase Hosting traffic for the active Firebase project.  Your project's Hosting URL will display a "Site Not Found" message after running this command. |
| Management of Hosting sites | |
| **firebase hosting:sites:create \ SITE\_ID** | Creates a new Hosting site in the active Firebase project using the specified `SITE_ID`  *(Optional)* Specify an existing Firebase Web App to associate with the new site by passing the following flag: `--app FIREBASE_APP_ID` |
| **firebase hosting:sites:delete \ SITE\_ID** | Deletes the specified Hosting site  The CLI displays a confirmation prompt before deleting the site.  *(Optional)* Skip the confirmation prompt by passing the following flags: `-f` or `--force` |
| **firebase hosting:sites:get \ SITE\_ID** | Retrieves information about the specified Hosting site |
| **firebase hosting:sites:list** | Lists all Hosting sites for the active Firebase project |
| Management of preview channels | |
| **firebase hosting:channel:create \ CHANNEL\_ID** | Creates a new preview channel in the ***default*** Hosting site using the specified `CHANNEL_ID`  This command doesn't deploy to the channel. |
| **firebase hosting:channel:delete \ CHANNEL\_ID** | Deletes the specified preview channel  You cannot delete a site's live channel. |
| **firebase hosting:channel:deploy \ CHANNEL\_ID** | Deploys your Hosting content and config to the specified preview channel  If the preview channel doesn't yet exist, this command creates the channel in the ***default*** Hosting site before deploying to the channel. |
| **firebase hosting:channel:list** | Lists all channels (including the "live" channel) in the ***default*** Hosting site |
| **firebase hosting:channel:open \ CHANNEL\_ID** | Opens a browser to the specified channel's URL or returns the URL if opening in a browser isn't possible |
| Version cloning | |
| **firebase hosting:clone \  SOURCE\_SITE\_ID***:***SOURCE\_CHANNEL\_ID \  TARGET\_SITE\_ID***:***TARGET\_CHANNEL\_ID** | Clones the most recently deployed version on the specified "source" channel to the specified "target" channel  This command also deploys to the specified "target" channel. If the "target" channel doesn't yet exist, this command creates a new preview channel in the "target" Hosting site before deploying to the channel. |
| **firebase hosting:clone \  SOURCE\_SITE\_ID***:@***VERSION\_ID \  TARGET\_SITE\_ID***:***TARGET\_CHANNEL\_ID** | Clones the specified version to the specified "target" channel  This command also deploys to the specified "target" channel. If the "target" channel doesn't yet exist, this command creates a new preview channel in the "target" Hosting site before deploying to the channel.  You can find the `VERSION_ID` in the [Hosting dashboard](//console.firebase.google.com/project/_/hosting/main) of the Firebase console. |

### Realtime Database commands

Note that you can create your initial, default Realtime Database instance in the
Firebase console or by using the
[general `firebase init` workflow](#initialize_a_firebase_project) or the
specific `firebase init database` flow.

Once instances are created, you can manage them as described in
[Manage and interact with specific instances using the CLI](/docs/database/usage/sharding#manage-interact-with-instances-cli).

| Command | Description |
| --- | --- |
| **database:get** | Fetches data from the active project's database and displays it as JSON. Supports querying on indexed data. |
| **database:instances:create** | Creates a database instance with a specified instance name. Accepts the `--location` option for creating a database in a specified region. For region names to use with this option, see [select locations for your project](/docs/projects/locations#rtdb-locations). If no database instance exists for the current project, you are prompted to run the `firebase init` flow to create an instance. |
| **database:instances:list** | List all database instances for this project. Accepts the `--location` option for listing databases in a specified region. For region names to use with this option see [select locations for your project](/docs/projects/locations#rtdb-locations). |
| **database:profile** | Builds a profile of operations on the active project's database. For more details, refer to [Realtime Database operation types](/docs/cli/database-profile). |
| **database:push** | Pushes new data to a list at a specified location in the active project's database. Takes input from a file, STDIN, or a command-line argument. |
| **database:remove** | Deletes all data at a specified location in the active project's database. |
| **database:set** | Replaces all data at a specified location in the active project's database. Takes input from a file, STDIN, or a command-line argument. |
| **database:update** | Performs a partial update at a specified location in the active project's database. Takes input from a file, STDIN, or a command-line argument. |

### Remote Config commands

| Command | Description |
| --- | --- |
| **remoteconfig:versions:list \ --limit NUMBER\_OF\_VERSIONS** | Lists the most recent ten versions of the template. Specify `0` to return all existing versions, or optionally pass the `--limit` option to limit the number of versions being returned. |
| **remoteconfig:get \ --v, version\_number VERSION\_NUMBER  --o, output FILENAME** | Gets the template by version (defaults to the latest version) and outputs the parameter groups, parameters, and condition names and version into a table. Optionally, you can write the output to a specified file with `-o, FILENAME`. |
| **remoteconfig:rollback \ --v, version\_number VERSION\_NUMBER  --force** | Rolls back Remote Config template to a specified previous version number or defaults to the immediate previous version (current version -1). Unless `--force` is passed, prompts **Y/N** before proceeding to rollback. |
| **remoteconfig:experiments:list \ --filter EXPRESSION  --pageSize NUMBER  --pageToken TOKEN** | Lists all Remote Config experiments for a project, with optional filtering, number of experiments to return per page (defaults to 10), and page token as the starting offset for the list. |
| **remoteconfig:experiments:get \ EXPERIMENT\_ID** | Gets the details of the specified Remote Config experiment. |
| **remoteconfig:experiments:delete \ EXPERIMENT\_ID** | Deletes the specified Remote Config experiment. |
| **remoteconfig:rollouts:list \ --filter EXPRESSION  --pageSize NUMBER  --pageToken TOKEN** | Lists all Remote Config rollouts for a project, with optional filtering, number of rollouts to return per page (defaults to 10), and page token as the starting offset for the list. |
| **remoteconfig:rollouts:get \ ROLLOUT\_ID** | Gets the details of the specified Remote Config rollout. |
| **remoteconfig:rollouts:delete \ ROLLOUT\_ID** | Deletes the specified Remote Config rollout. |






Send feedback

Except as otherwise noted, the content of this page is licensed under the [Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/), and code samples are licensed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0). For details, see the [Google Developers Site Policies](https://developers.google.com/site-policies). Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2026-03-27 UTC.




Need to tell us more?

[[["Easy to understand","easyToUnderstand","thumb-up"],["Solved my problem","solvedMyProblem","thumb-up"],["Other","otherUp","thumb-up"]],[["Missing the information I need","missingTheInformationINeed","thumb-down"],["Too complicated / too many steps","tooComplicatedTooManySteps","thumb-down"],["Out of date","outOfDate","thumb-down"],["Samples / code issue","samplesCodeIssue","thumb-down"],["Other","otherDown","thumb-down"]],["Last updated 2026-03-27 UTC."],[],[]]