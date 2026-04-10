# Source: https://docs.cloud.google.com/run/docs/browser-automation

Browser and OS automation in Cloud Run  |  Google Cloud Documentation



[Skip to main content](#main-content)

[![Google Cloud Documentation](https://www.gstatic.com/devrel-devsite/prod/vd3309c0d80f416d7367081c5c5ffd3cd171f6ea37becda6136423538d770ce20/clouddocs/images/lockup.svg)](/)

`/`

[Console](//console.cloud.google.com/)


* English
* Deutsch
* Español
* Español – América Latina
* Français
* Indonesia
* Italiano
* Português
* Português – Brasil
* עברית
* 中文 – 简体
* 中文 – 繁體
* 日本語
* 한국어

Sign in

[![](https://docs.cloud.google.com/_static/clouddocs/images/icons/products/run-color.svg)](https://docs.cloud.google.com/run/docs)

* [Cloud Run](https://docs.cloud.google.com/run/docs)

[Start free](//console.cloud.google.com/freetrial)



* [Home](https://docs.cloud.google.com/)
* [Documentation](https://docs.cloud.google.com/docs)
* [Application hosting](https://docs.cloud.google.com/docs/application-hosting)
* [Cloud Run](https://docs.cloud.google.com/run/docs)
* [Guides](https://docs.cloud.google.com/run/docs/overview/what-is-cloud-run)

Send feedback

# Browser and OS automation in Cloud Run Stay organized with collections Save and categorize content based on your preferences.



Build automation tools or run a full desktop operating system (OS) in your
Cloud Run container to allow AI agents to browse and extract information
from the web, and automate actions through mouse clicks and keyboard inputs.

## Build browser tools on Cloud Run

To build a browser tool on Cloud Run, use one of the following approaches:

* A [headless browser](#headless-chrome) for efficient and large-scale tasks
* A [full desktop OS](#operating-system) for complex scenarios that require human-computer interaction

To let your AI agent navigate the web, install [Chromium](https://www.chromium.org/getting-involved/download-chromium/) in your Cloud Run container, and
grant the necessary [permissions](/run/docs/reference/iam/roles) for the agent
to access Chromium. Cloud Run provides built-in streaming support
for streaming browser data back to the agent or the end user.

### Headless Chrome

Automate common browser tasks programmatically with headless Chrome. You can use
headless Chrome for the following use cases:

* Large-scale web scraping and data extraction
* Form submissions
* UI testing
* Create PDFs or screenshots of web pages

Implement headless Chrome using the following libraries:

* High-level API libraries like [Puppeteer](https://pptr.dev/) or [Playwright](https://playwright.dev/): use these libraries to control a browser, provide
  instructions to the browser to visit a website, extract content, and pass it to
  an AI model for summarization or structured data extraction.
* [Chrome DevTool protocol](https://chromedevtools.github.io/devtools-protocol/): provides a stable API used by Chrome DevTools. This API exposes
  all browser features programmatically. The agent controls actions like mouse
  clicks and retrieves the results as text or pixel data in the form of a screenshot.

### Desktop OS with virtual network computing (VNC) streaming

Implement a full desktop OS in your Cloud Run container for complex
processes, such as the following:

* Automate file uploads or downloads
* Interact with browser extensions or other desktop applications
* Test complex user journeys that involve drag-and-drop and other intricate mouse movements

This approach lets you run a full desktop OS on Cloud Run
and stream the results back through [Websockets](/run/docs/triggering/websockets).

When you install the standard Chromium browser on this desktop, the agent
interacts with the OS like a human would and then retrieves the
pixel configuration of the desktop.




Send feedback

Except as otherwise noted, the content of this page is licensed under the [Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/), and code samples are licensed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0). For details, see the [Google Developers Site Policies](https://developers.google.com/site-policies). Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2026-03-27 UTC.




Need to tell us more?

[[["Easy to understand","easyToUnderstand","thumb-up"],["Solved my problem","solvedMyProblem","thumb-up"],["Other","otherUp","thumb-up"]],[["Hard to understand","hardToUnderstand","thumb-down"],["Incorrect information or sample code","incorrectInformationOrSampleCode","thumb-down"],["Missing the information/samples I need","missingTheInformationSamplesINeed","thumb-down"],["Other","otherDown","thumb-down"]],["Last updated 2026-03-27 UTC."],[],[]]