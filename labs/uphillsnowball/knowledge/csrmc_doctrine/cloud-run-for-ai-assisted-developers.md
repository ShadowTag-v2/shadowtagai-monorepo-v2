# Source: https://docs.cloud.google.com/run/docs/ai/cloud-run-for-ai-assisted-developers

Introduction to Cloud Run for AI-assisted developers and vibe coders  |  Google Cloud Documentation



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

# Introduction to Cloud Run for AI-assisted developers and vibe coders Stay organized with collections Save and categorize content based on your preferences.



After creating an app with an AI-assisted tool like
[Google AI Studio](https://ai.google.dev/gemma/docs/core/deploy_to_cloud_run_from_ai_studio)
and [Vertex AI Studio](/vertex-ai/generative-ai/docs/start/quickstarts/deploy-vais-prompt),
you can use [Cloud Run](/run/docs/overview/what-is-cloud-run)
to deploy the app and make it available to users.

This guide describes the concepts of Cloud Run and some
modifications you can make after you use an AI-assisted tool or
[vibe coding](https://cloud.google.com/discover/what-is-vibe-coding)
tool to create and deploy an app. Understanding these concepts helps you
transition your application from a development environment to a scalable
platform.

## From code to container

Cloud Run runs your application inside a container. A container
is a standard package that includes your application code and all its
dependencies. This packaging ensures that your application runs reliably and
consistently in any computing environment.

If you're not familiar with containers, Cloud Run lets you
[deploy from source code](/run/docs/deploying-source-code), otherwise, you can
[deploy container images](/run/docs/deploying).

To deploy to Cloud Run, you first build your application into a
container image. You can create a container image using a `Dockerfile` or have
Google Cloud build one for you automatically from your source code
using buildpacks. You then store this image in an artifact registry.

## How Cloud Run works

Cloud Run uses a few core resources to manage and run your
containerized application. These resources work together to provide a seamless
deployment and scaling experience.

A *service* is the primary resource in Cloud Run. Each service
has a unique, permanent URL (`run.app`). When you deploy to a service,
Cloud Run creates a new, immutable revision. A *revision*
consists of a specific container image and settings that you configure, such as
memory limits and environment variables.

By default, Cloud Run automatically runs your revisions on one or
more instances. An *instance*, sometimes called a *container instance*, is a
single, isolated environment that runs a copy of your container within a
Cloud Run service. To manage costs, Cloud Run
scales the number of instances up or down to as low as to zero, based on the
number of incoming instances. Cloud Run also lets you
[configure different settings](/run/docs/configuring) to control the behavior of
your service, and
[connect to Google Cloud services](/run/docs/integrate/using-gcp-services)
to build a complete full-stack app that is highly scalable
.

When your Cloud Run service interacts with Google Cloud
APIs or other Cloud Run services, Cloud Run uses the
[service identity](/run/docs/securing/service-identity) to access
Google Cloud APIs. By default, Cloud Run automatically uses
the [default Compute Engine service account](/run/docs/securing/service-identity#types-of-service-accounts)
to make make calls to Google Cloud APIs to perform the operations it
needs. We recommend that you create a custom service account, and grant this
identity the minimal set of permissions needed for accessing a specific
Google Cloud resource.

## Update your service

After you've deployed your Cloud Run app using an AI-assisted
tool or vibe coding tool, you can update the default settings to optimize for
performance, cost, and security.

To modify your service:

1. Go to the Cloud Run **Services** page:

   [Go to Cloud Run](https://console.cloud.google.com/run/services)
2. Select your service.
3. Select **Edit and deploy new revision**.
4. Modify the [configuration settings](/run/docs/configuring) as needed.

   1. In the **Edit Container** section, you can modify the following:

      * [Container configuration](/run/docs/configuring/services/containers)
      * [CPU limits](/run/docs/configuring/services/cpu)
      * [Memory limits](/run/docs/configuring/services/memory-limits)
      * [Secrets](/run/docs/configuring/services/secrets)
      * [Environment variables](/run/docs/configuring/services/environment-variables)
   2. In the **Security** tab, select the available options, such as:

      * [HTTP/2](/run/docs/configuring/http2)
      * [VPC connection](/run/docs/configuring/connecting-vpc)
   3. In the **Security** tab, modify the default compute service account to a
      different [service accounts](/run/docs/configuring/services/service-identity)
      with minimal permissions.
   4. Under **Request**, modify the following if needed:

      * [Request timeout](/run/docs/configuring/request-timeout)
      * [Concurrency](/run/docs/configuring/concurrency)
   5. Under **Billing**, modify the [billing settings](/run/docs/configuring/billing-settings)
      if needed.

1. Under **Execution environment**, modify the
   [execution environment](/run/docs/configuring/execution-environments) if
   needed.

1. Under **Revision scaling**, if you use the default Cloud Run
   [autoscaling](/run/docs/about-instance-autoscaling), optionally specify
   the [minimum](/run/docs/configuring/min-instances) instances. If you use
   [manual scaling](/run/docs/configuring/services/manual-scaling), specify
   the number of instances for the service.
2. Click **Edit & deploy** new revision.

To learn more about viewing, copying, or deleting your service, see
[Manage services](/run/docs/managing/services).

## Best practices

For best practices to ensure your apps run efficiently on
Cloud Run, see [Develop your service](/run/docs/developing) and
[General development tips for services](/run/docs/tips/general).

Cloud Run and the Google Cloud services that your app uses
is a billable service. You can use the
[pricing calculator](https://cloud.google.com/products/calculator) to estimate
your costs based on your expected usage.

## What's next

* To get started, follow the quickstart to
  [deploy a container image](/run/docs/quickstarts/deploy-container).
* To learn about the different types of resources and deployment options, see
  [Resource model](/run/docs/resource-model).
* For information on preparing your code for deployment, see the
  [Container runtime contract](/run/docs/container-contract).
* To learn more about the benefits of using Cloud Run, See
  [Cloud Run AI use cases](/run/docs/ai/use-cases).




Send feedback

Except as otherwise noted, the content of this page is licensed under the [Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/), and code samples are licensed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0). For details, see the [Google Developers Site Policies](https://developers.google.com/site-policies). Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2026-03-27 UTC.




Need to tell us more?

[[["Easy to understand","easyToUnderstand","thumb-up"],["Solved my problem","solvedMyProblem","thumb-up"],["Other","otherUp","thumb-up"]],[["Hard to understand","hardToUnderstand","thumb-down"],["Incorrect information or sample code","incorrectInformationOrSampleCode","thumb-down"],["Missing the information/samples I need","missingTheInformationSamplesINeed","thumb-down"],["Other","otherDown","thumb-down"]],["Last updated 2026-03-27 UTC."],[],[]]
