# Source: https://docs.cloud.google.com/run/docs/code-execution

Code execution in Cloud Run  |  Google Cloud Documentation



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

# Code execution in Cloud Run Stay organized with collections Save and categorize content based on your preferences.



A key advantage of using Cloud Run to host AI agents is that it
isolates code using its secure execution environment. By building a code sandbox tool
in Cloud Run and running it in your container, you can execute application code
using any programming language you choose.

## Secure two-layer sandboxing

Cloud Run isolates all instances by using a two-layer sandbox that
consists of a hardware-backed layer equivalent to individual VMs
(x86 virtualization) and a software kernel layer. For more information,
see [Security design overview](/run/docs/securing/security#compute-security).

When you deploy your code, Cloud Run confines the code within the
sandboxing environment. This isolation lets you run untrusted code, such as code generated
by a large language model (LLM), with greater security.
When you execute untrusted code, [restrict IAM permissions](/run/docs/securing/managing-access)
on your Cloud Run service and [use VPC firewall rules](/firewall/docs/using-firewalls)
to prevent your code from making calls to the internet.

## Code execution modes

Cloud Run provides the following modes for code execution:

* **Asynchronous execution**: to avoid disrupting the main application flow, execute tasks asynchronously
  by using a [Cloud Run job](/run/docs/create-jobs) for longer-running or background tasks.
  For example, execute a Cloud Run job that uploads code to Cloud Storage, installs the required
  dependencies, and then processes and stores the results back in Cloud Storage.
* **Synchronous execution**: for processes that require an immediate response, use a [Cloud Run service](/run/docs/deploying). A Cloud Run service
  has a maximum timeout of one hour, which provides a significant amount of time
  for your code to run. To limit instances to process one request at a time, [set the concurrency value](/run/docs/configuring/concurrency) to `1`. You can also retrieve the code to execute
  as part of the request body, return the result in the response, and then
  terminate the container instance.

  The following image shows the two modes of code execution:

  [![For asynchronous execution, code is uploaded to Cloud Storage, which is executed as a Cloud Run job. The job sends the results of the execution to Cloud Storage to be stored. For synchronous execution, the agent sends a request to the Cloud Run service, with code in the request body. The service has a one-hour timeout and a concurrency of `1`. The Cloud Run service processes the code and sends it to the service instance, which returns a response back to the agent.](https://docs.cloud.google.com/run/docs/images/code-sandbox.svg)](https://docs.cloud.google.com/run/docs/images/code-sandbox.svg)


  Figure 1. Code execution modes in Cloud Run

## What's next

* Read [50% faster merge and 50% fewer bugs: How CodeRabbit built its AI code review agent with Cloud Run](https://cloud.google.com/blog/products/ai-machine-learning/how-coderabbit-built-its-ai-code-review-agent-with-google-cloud-run?e=48754805).




Send feedback

Except as otherwise noted, the content of this page is licensed under the [Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/), and code samples are licensed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0). For details, see the [Google Developers Site Policies](https://developers.google.com/site-policies). Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2026-03-27 UTC.




Need to tell us more?

[[["Easy to understand","easyToUnderstand","thumb-up"],["Solved my problem","solvedMyProblem","thumb-up"],["Other","otherUp","thumb-up"]],[["Hard to understand","hardToUnderstand","thumb-down"],["Incorrect information or sample code","incorrectInformationOrSampleCode","thumb-down"],["Missing the information/samples I need","missingTheInformationSamplesINeed","thumb-down"],["Other","otherDown","thumb-down"]],["Last updated 2026-03-27 UTC."],[],[]]