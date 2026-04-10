# Source: https://docs.cloud.google.com/dataform/docs/strict-act-as-mode

Use strict act-as mode  |  Dataform  |  Google Cloud Documentation



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
* 中文 – 简体
* 中文 – 繁體
* 日本語
* 한국어

Sign in

[![](https://docs.cloud.google.com/_static/clouddocs/images/icons/categories/data-analytics-color.svg)](https://docs.cloud.google.com/dataform/docs)

* [Dataform](https://docs.cloud.google.com/dataform/docs)

[Start free](//console.cloud.google.com/freetrial)



* [Home](https://docs.cloud.google.com/)
* [Documentation](https://docs.cloud.google.com/docs)
* [Data analytics](https://docs.cloud.google.com/docs/data)
* [Dataform](https://docs.cloud.google.com/dataform/docs)
* [Guides](https://docs.cloud.google.com/dataform/docs/overview)

Send feedback

# Use strict act-as mode Stay organized with collections Save and categorize content based on your preferences.



The strict act-as mode enables an additional security check for the following
user actions in Dataform:

* Creating or updating a repository.
* Creating or updating a workflow configuration.
* Creating a workflow invocation.
* Updating a release configuration.

This additional security check requires that the user performing these actions
has the `iam.serviceAccounts.actAs` permission on the effective service account,
which is the service account whose credentials are used to run workflows.
For more information, see
[Attach service accounts to resources](/iam/docs/attach-service-accounts).

You can enable the act-as mode by doing the following:

* When [creating a repository](/dataform/docs/create-repository#create-repository).
* When updating an existing repository with the `strict_act_as_checks`
  repository flag.

**Important:** For existing repositories, we recommend enabling strict act-as mode,
as this helps to ensure a more secure and predictable permissions model for
your Dataform projects.

## Required roles

To get the permissions that
you need to complete the tasks in this document,
ask your administrator to grant you the
following IAM roles:

* [Service Account User](/iam/docs/roles-permissions/iam#iam.serviceAccountUser)  (`roles/iam.serviceAccountUser`)
  on the custom service account
* View logs in Logging:
  [Logs Viewer](/iam/docs/roles-permissions/logging#logging.viewer)  (`roles/logging.viewer`)
  on the project
* Grant IAM roles to users or service accounts:
  [Service Account Admin](/iam/docs/roles-permissions/iam#iam.serviceAccountAdmin)  (`roles/iam.serviceAccountAdmin`)
  on the project

For more information about granting roles, see [Manage access to projects, folders, and organizations](/iam/docs/granting-changing-revoking-access).

You might also be able to get
the required permissions through [custom
roles](/iam/docs/creating-custom-roles) or other [predefined
roles](/iam/docs/roles-overview#predefined).

## Verify act-as permissions for the effective service account

To ensure your Dataform workflows run securely and without
interruption, it's important to verify the act-as permissions on the service
accounts they use. This section explains how to identify the effective service
account for your resources, use Cloud Logging to check for permission issues,
and then resolve any issues you find.

### Determine the effective service account

You can determine the effective service account that is running the workflows
according to the resource type and the following conditions:

| Resource type | Effective service account |
| --- | --- |
| Repositories | For new repositories, the custom service account you select when you [create a repository](/dataform/docs/create-repository#create-repository) is used. This service account is listed in the `Repository.ServiceAccount` field.  For existing repositories, this can be a custom service account (recommended) or the [Dataform service agent](/dataform/docs/access-control#about-service-accounts). |
| Workflow configuration | For new workflow configurations, the custom service account you select when you [create a workflow configuration](/dataform/docs/schedule-runs#create-workflow-configuration) is used. If no service account is selected, the repository's service account is used.  For existing workflow configurations, this can be a custom service account (recommended) or the repository's [Dataform service agent](/dataform/docs/access-control#about-service-accounts). |
| Workflow invocation | If the compilation result is a `WORKFLOW_CONFIG` resource, then the workflow configuration's effective service account is used.  If you create a workflow invocation from a compilation result, then the service account listed in the `WorkflowInvocation.InvocationConfig` field is used if it's set.  Otherwise, this defaults to the service account configured at the repository level. |

**Important:** You can't use the default Dataform service agent to
run workflows. You must use either a custom service account or your Google
Account user credentials.

### Check for permission issues in Cloud Logging

To enhance security, Dataform checks if the
`iam.serviceAccounts.actAs` permission is missing on the service accounts used
by Dataform resources.

The results of these checks, including any potential permission issues, are
recorded in Cloud Logging. You should review these logs regularly to
identify and grant any missing `iam.serviceAccounts.actAs` permissions. Checking
these logs ensures that your Dataform workflows and
configurations continue to function without interruption.

#### View logs in Cloud Logging

1. In the Google Cloud console, go to the **Logs Explorer** page.

   [Go to Logs Explorer](https://console.cloud.google.com/logs/query)
2. Select the Google Cloud project in which you want to check the logs.
3. Use the query editor to filter for the Dataform `actAs`
   logs with the following options:

   * To list only the `actAs` checks that failed and require action, use the
     following query:

     ```
     logName: "projects/PROJECT_ID/logs/dataform.googleapis.com%2Factas_dry_run_result"
     jsonPayload.dryRunResult = false
     ```
   * To list all of the `actAs` checks, use the following query:

     ```
     logName: "projects/PROJECT_ID/logs/dataform.googleapis.com%2Factas_dry_run_result"
     ```

   Replace `PROJECT_ID` with your
   Google Cloud project ID.
4. Click **Run query**.

#### Interpret log entries

Expand a log entry in the query results to view the following `jsonPayload`
fields:

| Field | Type | Description |
| --- | --- | --- |
| `dryRunResult` | Boolean | `true`: the permission check passed.  `false`: the check failed. The caller principal is missing the `iam.serviceAccounts.actAs` permission on the service account. |
| `caller` | String | The email address of the principal (user or service account) that initiated the API call. |
| `serviceAccount` | String | The service account that the caller principal attempted to act as. This field is typically present when the `dryRunResult` field is `false`. |
| `apiMethod` | String | The Dataform API method that triggered the check, for example, `CreateWorkflowInvocation` or `UpdateRepository`. |
| `*_context` | Object | An object containing resource names relevant to the API method called. For more information, see [Context objects](#context-objects). |

**Important:** An exception occurs when `dryRunResult` is `false`, `serviceAccount`
is empty, and `apiMethod` is `CreateWorkflowConfig`, `UpdateWorkflowConfig`, or
`CreateWorkflowInvocation`. This exception means that the check has failed,
because no service account was specified in the API call where it's required.
You must update your process to provide a service account for these operations.

##### Context objects

The log entry includes a context object within the `jsonPayload` fields. The
fields in this object contain the fully qualified Google Cloud resource
names of the Dataform entities involved. These names follow the
standard structures shown in the following list, allowing you to precisely
identify the resources.

* `create_workflow_invocation_context`: present when the API method is
  `CreateWorkflowInvocation`.

  + `workflowInvocation`: the resource name of the workflow invocation.
    - The format of the resource name is the following:
      `projects/PROJECT_ID/locations/LOCATION_ID/repositories/REPOSITORY_ID/workflowInvocations/WORKFLOW_INVOCATION_ID`.
  + `compilationResult` or `workflowConfig`: the resource name of the source
    used for the invocation.
    - The format of the resource name for `compilationResult` is the following:
      `projects/PROJECT_ID/locations/LOCATION_ID/repositories/REPOSITORY_ID/compilationResults/COMPILATION_RESULT_ID`.
    - The format of the resource name for `workflowConfig` is the following:
      `projects/PROJECT_ID/locations/LOCATION_ID/repositories/REPOSITORY_ID/workflowConfigs/WORKFLOW_CONFIG_ID`.
* `create_repository_context` or `update_repository_context`: present when the
  API method is `CreateRepository` or `UpdateRepository`.

  + `repository`: the resource name of the Dataform repository.
    - The format of the resource name is the following:
      `projects/PROJECT_ID/locations/LOCATION_ID/repositories/REPOSITORY_ID`
* `update_release_config_context`: present when the API method is
  `UpdateReleaseConfig`.

  + `releaseConfig`: the resource name of the release configuration.
    - The format of the resource name is the following:
      `projects/PROJECT_ID/locations/LOCATION_ID/repositories/REPOSITORY_ID/releaseConfigs/RELEASE_CONFIG_ID`.
* `create_workflow_config_context` or `update_workflow_config_context`: present
  when the API method is `CreateWorkflowConfig` or `UpdateWorkflowConfig`.

  + `workflowConfig`: the resource name of the workflow configuration.
    - The format of the resource name is the following:
      `projects/PROJECT_ID/locations/LOCATION_ID/repositories/REPOSITORY_ID/workflowConfigs/WORKFLOW_CONFIG_ID`.

To compare the documented formats to the logging entry, replace the following:

* `PROJECT_ID`: the unique identifier of your
  Google Cloud project.
* `LOCATION_ID`: the region where your
  Dataform repository is located.
* `REPOSITORY_ID`: the user-defined ID of the
  Dataform repository. This is the name given to the repository
  when it was created.
* `COMPILATION_RESULT_ID`: the system-generated unique
  identifier for a Dataform compilation result.
* `RELEASE_CONFIG_ID`: the user-defined ID of the
  Dataform release configuration.
* `WORKFLOW_CONFIG_ID`: the user-defined ID of the
  Dataform workflow configuration.

### Resolve permission issues

If you find log entries where the `dryRunResult` field is `false`, do the
following:

1. In the `jsonPayload` details, note the email address in the `caller` field
   to identify the principal.
2. Note the email address in the `serviceAccount` field to identify the
   service account.
3. Confirm that the caller principal *should* have permission to act as the
   service account. Granting this permission lets the caller use the permissions
   held by the service account.
4. If the access is intended, grant the
   [Service Account User role](/iam/docs/roles-permissions/iam#iam.serviceAccountUser)
   (`roles/iam.serviceAccountUser`) to the caller principal on the *target* service
   account. For more information, see
   [Grant the required IAM roles](#grant-iam-roles).

After granting the role, future logs for this combination of caller and
service account should show `dryRunResult: true`.

## Grant the required IAM roles

The [Service Account User role](/iam/docs/service-account-permissions#user-role)
(`roles/iam.serviceAccountUser`) contains the `iam.serviceAccounts.actAs`
permission, which is required for the strict act-as mode. When you use the
Dataform API, you must have the Service Account User role granted
for the effective service account based on the
[`projects.locations.repositories` method](/dataform/reference/rest/v1/projects.locations.repositories)
that you're calling:

* [`create`](/dataform/reference/rest/v1/projects.locations.repositories/create)
  or
  [`patch`](/dataform/reference/rest/v1/projects.locations.repositories/patch)
  + If the `Repository.ServiceAccount` property is set, then you should have
    the Service Account User role granted for that property.
  + If you're calling the `patch` method, then you should have
    the Service Account User role granted for all the effective service
    accounts in all the workflow configurations in the repository.
* [`workflowConfigs.create`](/dataform/reference/rest/v1/projects.locations.repositories.workflowConfigs/create)
  or
  [`workflowConfigs.patch`](/dataform/reference/rest/v1/projects.locations.repositories.workflowConfigs/patch)
  + You should have the Service Account User role granted for the effective
    service account used in the workflow configuration.
* [`releaseConfigs.patch`](/dataform/reference/rest/v1/projects.locations.repositories.releaseConfigs/patch)
  + You should have the Service Account User role granted for all the
    effective service accounts used in the workflow configurations using this
    release configuration.
* [`workflowInvocations.create`](/dataform/reference/rest/v1/projects.locations.repositories.workflowInvocations/create)
  + You should have the Service Account User role granted for the effective
    service account used in the workflow invocation.

To grant the Service Account User role to a custom service account, follow
these steps:

1. In the Google Cloud console, go to **IAM** >
   **Service accounts**.

   [Go to Service accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Select a project.
3. On the
   **Service accounts for project "PROJECT\_NAME"**
   page, select your custom service account.
4. Go to **Principals with access**, and then click **Grant Access**.
5. In the **New principals** field, enter your default Dataform
   service agent ID.

   Your default Dataform service agent ID is in the following
   format:

   ```
   service-PROJECT_NUMBER@gcp-sa-dataform.iam.gserviceaccount.com
   ```

   Replace `PROJECT_NUMBER` with your
   Google Cloud project number.
6. In the **Select a role** list, select the **Service Account User** role.
7. Click **Add another role** and select the **Service Account Token Creator** role.

   **Note:** This role is required for Dataform to generate
   the credentials necessary to run workflows as the custom service
   account. For more information, see
   [Required roles for Dataform service agents, custom service accounts, and Google Accounts](/dataform/docs/access-control#dataform-required-roles).
8. Click **Save**.

For more information, see the
[required roles for creating a workflow configuration](/dataform/docs/schedule-runs#required_roles)
and
[required roles for creating a release configuration](/dataform/docs/configure-compilation#required_roles)

## Effects of strict act-as mode on automatic releases and runs

When strict act-as mode is enabled, it impacts automatic repository releases
and automatic workflow executions as follows:

For repositories that *aren't* connected to third-party repositories:

* You can't set a
  [Cron schedule](/dataform/docs/configure-compilation#release-configuration-details)
  for automatic releases in release configurations. This is enforced to prevent
  code changes made by a user who might lack the necessary
  `iam.serviceAccounts.actAs` permissions on downstream service accounts from being automatically deployed.
* Scheduled workflow runs using a Cron schedule in workflow configurations remain enabled. For these automated runs to succeed, you must grant the default
  Dataform service agent the `iam.serviceAccounts.actAs`
  permission on the
  [effective service account](#determine-effective-service-account)
  specified in the workflow configuration.

For repositories that *are* connected to third-party repositories:

* Scheduled releases and scheduled workflow runs are permitted.
* To enable an automatic release from a release configuration or an automatic
  run from a workflow configuration, you must grant the default Dataform service agent the `iam.serviceAccounts.actAs` permission
  on the relevant
  [effective service account](#determine-effective-service-account):
  + For an automatic release configuration, grant the permission on the
    effective service accounts of all the workflow configurations that are
    triggered by this release configuration.
  + For an automatic workflow configuration, grant the permission on the
    effective service account used by that workflow configuration.

**Warning:** Because there is no guarantee that the user writing the code has the
`iam.serviceAccounts.actAs` permission on the effective service accounts for
a [third-party repository](/dataform/docs/connect-repository),
it's your responsibility to control the code changes in third-party
repositories with the code review process.

## What's next

* To learn how to create a repository, see
  [Create a repository](/dataform/docs/create-repository).
* To learn more about how Dataform works with BigQuery, see
  [Overview of workflows](/dataform/docs/sql-workflows).
* To learn how to create a workflow configuration, see
  [Schedule runs](/dataform/docs/schedule-runs).
* To learn how to create a release configuration, see
  [Configure compilations](/dataform/docs/configure-compilation).




Send feedback

Except as otherwise noted, the content of this page is licensed under the [Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/), and code samples are licensed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0). For details, see the [Google Developers Site Policies](https://developers.google.com/site-policies). Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2026-03-26 UTC.




Need to tell us more?

[[["Easy to understand","easyToUnderstand","thumb-up"],["Solved my problem","solvedMyProblem","thumb-up"],["Other","otherUp","thumb-up"]],[["Hard to understand","hardToUnderstand","thumb-down"],["Incorrect information or sample code","incorrectInformationOrSampleCode","thumb-down"],["Missing the information/samples I need","missingTheInformationSamplesINeed","thumb-down"],["Other","otherDown","thumb-down"]],["Last updated 2026-03-26 UTC."],[],[]]