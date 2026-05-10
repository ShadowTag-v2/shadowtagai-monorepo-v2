# Source: https://docs.cloud.google.com/integration-connectors/docs/quickstart-mysql-connector

Perform CRUD operations on a MySQL database  |  Integration Connectors  |  Google Cloud Documentation



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

[![](https://docs.cloud.google.com/_static/clouddocs/images/icons/categories/devops-color.svg)](https://docs.cloud.google.com/integration-connectors/docs)

* [Integration Connectors](https://docs.cloud.google.com/integration-connectors/docs)

[Start free](//console.cloud.google.com/freetrial)



* [Home](https://docs.cloud.google.com/)
* [Documentation](https://docs.cloud.google.com/docs)
* [Application development](https://docs.cloud.google.com/docs/application-development)
* [Integration Connectors](https://docs.cloud.google.com/integration-connectors/docs)
* [Guides](https://docs.cloud.google.com/integration-connectors/docs/overview)

Send feedback



Stay organized with collections

Save and categorize content based on your preferences.



# Perform CRUD operations on a MySQL database

This tutorial shows you how to connect to a MySQL database instance from a
sample integration and perform List, Get, Create, Update, and Delete operations
on a MySQL database table.

To complete this tutorial, perform the following tasks:

* [Set up a database and table in your MySQL server](#setup-database)
* [Create a MySQL connection](#create-connection)
* [Configure an Integration to use the MySQL connection](#configure-integration)
* [Test the Integration](#test-integration)
* [Perform other operations on your MySQL database table](#other-operations)

## Before you begin

* Ensure that you have access to integrations.
* Do the following in your Google Cloud project:

  + Grant the following roles to the service account that you want to use to create the connection:
    - `roles/secretmanager.viewer`
    - `roles/secretmanager.secretAccessor`
  + Enable the following services:
    - `secretmanager.googleapis.com` (Secret Manager API)
    - `connectors.googleapis.com` (Connectors API)

    If these services have not been enabled for your project previously, you are prompted to enable them
    when creating the connection in the Create Connection page.
* Ensure that you have access to a MySQL server that you can use to create a database.

## Set up a database and table in your MySQL server

Connect to your MySQL server and create a database and a table to use in this tutorial.

1. To connect to your MySQL server, execute the following command from a system that has a MySQL client installed:

   ```
   mysql --host=MySQL server host name or IP address --port=MySQL server port number -uusername -ppassword
   ```

   In this example, replace:
   * `MySQL server host name or IP address` with the name or IP address of your MySQL server.
   * `MySQL server port number`  with the port number for your MySQL server.
   * `username` with the username for your MySQL server.
   * `password` with the password for your MySQL server.- To create a MySQL database to use in this tutorial, execute the following command from your MySQL client:

     ```
     CREATE DATABASE tutorialDB;
     ```
   - To create a table to use in this tutorial, execute the following command from your MySQL client:

     ```
     create table employee
       (
       employee_id int auto_increment primary key,
       employee_first_name varchar(500) NOT null,
       employee_last_name varchar(500) NOT null,
       employee_emailID varchar(500)
       );
     ```
   - To add rows to the `employee` table that you created, execute the following command from your MySQL client:

     ```
     INSERT INTO employee (employee_first_name,employee_last_name,employee_emailID) values ("Peter","Dilliard","test-01@test.com");
     INSERT INTO employee (employee_first_name,employee_last_name,employee_emailID) values ("Meaghan","Webb","test-02@test.com");
     ```
   - Verify that the table is created and rows are added by executing the following command:

     ```
     SELECT * FROM employee;
     ```

     The following table rows are displayed:

     ```
     +-------------+---------------------+--------------------+------------------+
     | employee_id | employee_first_name | employee_last_name | employee_emailID |
     +-------------+---------------------+--------------------+------------------+
     |           1 | Peter               | Dilliard           | test-01@test.com |
     |           2 | Meaghan             | Webb               | test-02@test.com |
     +-------------+---------------------+--------------------+------------------+
     ```

## Create a MySQL connection

To enable an integration to connect to your MySQL database, create a new connection
to your MySQL database:

1. Click **+Create new** to open the **Create Connection** page.
2. In the **Location** section, choose the location for the connection.
   1. From the **Region** list, select the region where you want to create the connection.

      For the list of all the supported regions, see [Locations](/integration-connectors/docs/locations).
   2. Click **Next**.
3. In the **Connection Details** section, enter the following details:
   1. From the **Connector** list, select **MySQL**.
   2. From the **Connector version** list, select the connector version.
   3. In the **Connection Name** field, enter a name for the connection instance.

      Connection names must meet the following criteria:
      * Use letters, numbers, or hyphens.
      * Letters must be lower-case.
      * Names must begin with a letter and end with a letter or number.
      * Names cannot exceed 49 characters.
   4. Optional: In the **Description** field, add a description of the connection instance.
   5. Optional: Enable **Cloud Logging**.
   6. From the **Service Account** list, select a service account that has the [required roles](#before-you-begin).
   7. In the **Database name** field, enter the name of the MySQL database.
   8. Optionally, configure the **Connection node settings**:

      * **Minimum number of nodes**: Enter the minimum number of connection nodes.
      * **Maximum number of nodes**: Enter the maximum number of connection nodes.

      A node is a unit (or replica) of a connection that processes transactions.
      More nodes are required to process more transactions for a connection and conversely,
      fewer nodes are required to process fewer transactions.
      To understand how the nodes affect your connector pricing, see
      [Pricing for connection nodes](/integration-connectors/docs/pricing#pricing-for-connection-nodes). If you don't enter any values, by default
      the minimum nodes are set to 2 (for better availability) and the maximum nodes are set to 50.
   **Note:** You can customize the connection node values only if you are
   a Pay-as-you-go customer.9. (Optional) In the **Advanced settings** section, select the **Use proxy** checkbox to configure a proxy server for the connection and configure the following values:
   * **Proxy Auth Scheme**: Select the authentication type to authenticate with the proxy server. The following authentication types are supported:
     + **Basic**: Basic HTTP authentication.
     + **Digest**: Digest HTTP authentication.
   * **Proxy User**: A user name to be used to authenticate with the proxy server.
   * **Proxy Password**: The Secret manager secret of the user's password.
   * **Proxy SSL Type**: The SSL type to use when connecting to the proxy server. The following authentication types are supported:
     + **Auto**: Default setting. If the URL is an HTTPS URL, then the Tunnel option is used. If the URL is an HTTP URL, then the NEVER option is used.
     + **Always**: The connection is always SSL enabled.
     + **Never**: The connection is not SSL enabled.
     + **Tunnel**: The connection is through a tunneling proxy. The proxy server opens a connection to the remote host and traffic flows back and forth through the proxy.
   * In the **Proxy Server** section, enter details of the proxy server.
     1. Click **+ Add destination**.
     2. Select a **Destination Type**.
        + **Host address**: Specify the hostname or IP address of the destination.

          If you want to establish a private connection to your backend system, do the following:

          - Create a [PSC service attachment](/integration-connectors/docs/configure-psc).
          - Create an [endpoint attachment](/integration-connectors/docs/create-ep-attachment) and
            then enter the details of the endpoint attachment in the **Host address** field.10. Optional: To add a label to the connection, click **+Add Label**.
   11. Click **Next**.
4. In the **Destinations** section, enter details of the remote host (backend system) to
   which you want to connect.
   * From the **Destination Type** list, select a host address.
     + To specify the destination hostname or IP address, select **Host address** and
       enter the address in the **Host 1** field.
     + To establish a private connection, select **Host Address** and add the endpoint attachment created for the SAP Gateway using the HTTPS protocol.
     **Note:** To understand how to create an endpoint attachment, see
     [PSC service attachment](/integration-connectors/docs/configure-psc)
     and [endpoint attachment](/integration-connectors/docs/create-ep-attachment). After you
     have created the endpoint attachment, it will be visible in the **Endpoint Attachment** list.

   If you want to establish a public connection to your backend systems with additional security, you can
   consider [configuring static outbound
   IP addresses for your connections](/integration-connectors/docs/configure-static-ip), and then configure
   your firewall rules to allowlist only the specific static IP addresses.

   To enter additional destinations, click **+Add Destination**.
5. Click **Next**.
6. In the **Authentication** section, you can provide credentials:
   * In the **Username** field, enter the MySQL username for the connection.
   * In the **Password** field, enter the [Secret Manager](https://console.cloud.google.com/security/secret-manager)
     secret containing the password associated with the MySQL username.
     + If you have previously created a secret, and it is not available in the list,
       select **Enter Secret Manually**. In the **Add a secret by resource
       ID** dialog, copy and paste the resource ID from
       the [Secret Manager](https://console.cloud.google.com/security/secret-manager).
       - To use the latest version, copy and paste the resource ID from the parent secret, in the format:
         `"projects/project-number/secrets/secret-name"`
       - To select a specific version, copy and paste the resource ID for that specific version, in the
         format `"projects/project-number/secrets/secret-name/versions/1"`

       To add the secret, click **Add Secret**.
     + If you have not created a secret for use with MySQL, click **Create
       New Secret**. In the **Create Secret** dialog enter the following details:
       - In the **Name** field, enter the secret name.
       - In the **Secret value** field, enter the contents of the secret or upload
         a file that contains the secret.
       - Click **Create Secret**.
   * From the **Secret version** list, select the version of the **Password** secret from the list of available versions in the drop-down.
   * Click **Next**.

- In the **Review** section, review your connection and authentication details.
- Click **Create**.

## Configure an Integration to use the MySQL connection

To use the MySQL connection that you created in an integration, add a **Connectors** task in an integration along with an **API Trigger**. The **API Trigger** is connected to the **Connectors** task using an **Edge** connection.

### Create a new Integration

1. In the Google Cloud console, go to the **Integration Connectors** page.

   [Go to Integration Connectors](https://console.cloud.google.com/integrations)
2. In the navigation menu, click **Integrations**.

   The **Integrations List** page appears.
3. Select an existing integration or create a new integration by clicking **CREATE INTEGRATION**.

   This opens the integration in the integration editor page.
4. In the integration editor, click **+Add a task/trigger > Tasks** to view the list of available tasks.
5. Click **CREATE NEW**.
6. Enter a name and (optionally) a description in the **Create Integration** dialog.
   **Note**: Integration names must meet the following requirements:
   * Names must start and end with letters or numbers.
   * Names cannot contain spaces or more than one dash or underscore in a row.
7. Click **Create** to open the integration editor.

### Add and configure an API trigger

To add and configure an **API** trigger to the integration, do the following:

1. In the integration editor, select **Add a task/trigger > Triggers** to display a list of available triggers.
2. Drag the **API Trigger** element to the integration editor.

### Add and configure a Connectors task

Perform the following steps to configure a **Connectors** task to list all the entities in the `employee` table:

1. Select **+Add a task/trigger > Tasks** in the integration editor to display the list of available tasks.
2. Drag the **Connectors** element to the integration editor.
3. Click the **Connectors** task element on the designer to view the task configuration pane.
4. Click **Configure task**.

   The **Configure connector task** dialog appears.
5. In the **Configure connector task** dialog, do the following:
   1. Select the connection region where you created your MySQL connection.
   2. Once a region is chosen, the **Connection** column appears. Select the MySQL connection that you created from the list of available connections.
   3. Once a connection is chosen, the **Type** column appears. Select **Entities** and then **employee** from the list of available entities.
   4. Once a type is chosen, the **Operation** column appears. Select **List**.
   5. Click **Done** to complete the connection configuration and close the dialog.

### Connect the API Trigger element to the Connectors task element

Next, add an edge connection to connect the API trigger to the Connectors task. An edge connection is a connection between any two elements in an integration. For more information on edges and edge conditions, see [Edges](/application-integration/docs/edge-and-edge-conditions).

To add the edge connection, click the **Fork** control point at the bottom of the API Trigger element. Drag and drop the edge connection at the **Join** control point at the top of the Connectors task element.

## Test the Integration

To test the integration, do the following:

1. Click the **Test** button in the integration editor toolbar.
2. Change the **Execution Deadline (in minutes)** value, if you like, and then click **Test Integration**.
3. Once the integration completes successfully, the **Test Integration** pane displays the message **Integration execution succeeded**. To view the logs, click **View logs**.
4. In **Response Parameters**, under **Connector output payload**, the following output is displayed:

   ```
   [ {
       "employee_id": 1.0,
       "employee_first_name": "Peter",
       "employee_last_name": "Dilliard",
       "employee_emailID": "test-01@test.com"
     },
     {
       "employee_id": 2.0,
       "employee_first_name": "Meaghan",
       "employee_last_name": "Webb",
       "employee_emailID": "test-02@test.com"
     } ]
   ```

## Perform other operations on your MySQL database table

When you configure a Connectors task in your integration, you can select any one of the following operations:

* List
* Get
* Create
* Update
* Delete

You've already used the List operation to view all the rows in the `employee` table. In the following sections of this tutorial, you'll use the Get, Create, Update, and Delete operations to add, modify or remove rows from the `employee` table.

### Get a row from a table

If you know the entity ID (or primary key) of the row that you want to fetch, provide that value as input to a Get operation in your integration. The details returned by the Get operation are similar to the details returned by the List operation. However, while the List operation fetches details of all the table rows that match the specified query, the Get operation fetches details of only the table row that matches the specified entity ID.

Remember that, while the List operation by default returns all the rows in the table, the Get operation requires an entity ID as a search parameter. So, to use the Get operation, you must know the entity ID of the row that you want to fetch, or provide a default value for the entity ID.

To get details of a specified row, perform the following steps to configure the **Connectors** task that you created earlier:

1. Click the **Connectors** task element on the designer to view the task configuration pane.
2. Click **Configure task**.

   The **Configure connector task** dialog appears.
3. In the **Configure connector task** dialog, in the **Operation** column, select **Get** and then click **Done**.
4. In the task configuration pane, under **Task Input** click **Entity ID**.
5. In the **Configure Variable** dialog, select **Use as an input to integration** and click **Save**.
6. Click the **Test** button in the integration editor toolbar.
7. Change the **Execution Deadline (in minutes)** value, if you like.
8. Enter the entity ID of the entity for which you want to fetch details. Enter **2**.
9. Click **Test Integration**.
10. Once the integration completes successfully, the **Test Integration** pane displays the message **Integration execution succeeded**. To view the logs, click **View logs**.
11. In **Response Parameters**, under **Connector output payload**, the following output is displayed:

    ```
    [ {
        "employee_id": 2.0,
        "employee_first_name": "Meaghan",
        "employee_last_name": "Webb",
        "employee_emailID": "test-02@test.com"
      } ]
    ```
12. You can verify that the information displayed here matches the information in the corresponding row in your MySQL table. To view this information in your MySQL table, execute the following command from your MySQL client:

    ```
    SELECT * FROM employee WHERE employee_id=2;
    ```

    The following table row is displayed:

    ```
    +-------------+---------------------+--------------------+------------------+
    | employee_id | employee_first_name | employee_last_name | employee_emailID |
    +-------------+---------------------+--------------------+------------------+
    |           2 | Meaghan             | Webb               | test-02@test.com |
    +-------------+---------------------+--------------------+------------------+
    ```

### Add a row to a table

The Create operation allows you to add a row in a table. When you use the Create operation, you must provide all the values for the entity in the connector input payload.

To add a row using the Create operation, perform the following steps to configure the **Connectors** task that you created earlier:

1. Click the **Connectors** task element on the designer to view the task
   configuration pane.
2. Click **Configure task**.

   The **Configure connector task** dialog appears.
3. In the **Configure connector task** dialog, in the **Operation** column, select **Create** and then click **Done**.
4. In the task configuration pane, under **Task Input** click **Connector input payload**.
5. In the **Configure Variable** dialog, select **Use as an input to integration** and click **Save**.
6. Click the **Test** button in the integration editor toolbar.
7. Change the **Execution Deadline (in minutes)** value, if you like.
8. Enter the details for the entity that you want to create. For example, to add a new employee in the `employee` table, enter the following JSON:

   ```
   {
     "employee_first_name": "Mary",
     "employee_last_name": "Smith",
     "employee_emailID": "test-03@test.com"
   }
   ```

   **Note**: Don't specify the primary key, `employee_id`, as it is a read-only value that is generated when the row is added to the table.
9. Click **Test Integration**.
10. Once the integration completes successfully, the **Test Integration** pane displays the message **Integration execution succeeded**. To view the logs, click **View logs**.
11. In **Response Parameters**, under **Connector input payload**, the payload that you provided is displayed:

    ```
    {
      "employee_first_name": "Mary",
      "employee_last_name": "Smith",
      "employee_emailID": "test-03@test.com"
    }
    ```

    Under **Connector output payload**, the entity ID is displayed as output:

    ```
    {
      "employee_id": 3.0
    }
    ```
12. You can verify that the row is added in your MySQL table. To view this information in your MySQL table, execute the following command from your MySQL client:

    ```
    SELECT * FROM employee;
    ```

    The following table rows are displayed:

    ```
    +-------------+---------------------+--------------------+------------------+
    | employee_id | employee_first_name | employee_last_name | employee_emailID |
    +-------------+---------------------+--------------------+------------------+
    |           1 | Peter               | Dilliard           | test-01@test.com |
    |           2 | Meaghan             | Webb               | test-02@test.com |
    |           3 | Mary                | Smith              | test-03@test.com |
    +-------------+---------------------+--------------------+------------------+
    ```

### Update a row in a table

Use the Update operation to make changes to the values in a table row. For example, you can use this operation to update the email ID of an employee in the `employee` table. To specify the entity that you want to update, you can provide the entity ID as you did for the Get operation. Alternatively, you can use the **Filter clause** parameter to pass values on which to filter the table rows. This is useful if you want to make the same change in multiple rows based on specific search criteria.

To update a table row, perform the following steps to configure the **Connectors** task that you created earlier:

1. Click the **Connectors** task element on the designer to view the task configuration pane.
2. Click **Configure task**.

   The **Configure connector task** dialog appears.
3. In the **Configure connector task** dialog, in the **Operation** column, select **Update** and then click **Done**.
4. In the task configuration pane, under **Task Input** click **Connector input payload**.
5. In the **Configure Variable** dialog, select **Use as an input to integration** and click **Save**.
6. Next, in the task configuration pane, under **Task Input** click **Filter clause**.
7. In the **Configure Variable** dialog, select **Use as an input to integration** and click **Save**.
8. Click the **Test** button in the integration editor toolbar.
9. Change the **Execution Deadline (in minutes)** value, if you like.
10. Enter the criteria that you want to filter by. For example, to find an employee with the email ID `test-03@test.com`, enter:

    ```
    employee_emailID="test-03@test.com"
    ```

    **Note**: If you have multiple table rows that match the filter criteria, the update that you specify in the next step is made on all the matching rows.
11. Enter the values that you want to update. For example, to update the email ID of all the employees in the `employee` table whose current email ID matches the filter clause `test-03@test.com`, enter the following JSON:

    ```
    {
      "employee_emailID": "msmith@test.com"
    }
    ```

    **Note**: You don't need to specify values for all the columns in the table. Enter the values that you want to update. The other values aren't modified.
12. Click **Test Integration**.
13. Once the integration completes successfully, the **Test Integration** pane displays the message **Integration execution succeeded**. To validate that the entity was updated, use the Get operation to get the details of the specified entity.
14. You can verify that the row is updated in your MySQL table. To view this information in your MySQL table, execute the following command from your MySQL client:

    ```
    SELECT * FROM employee;
    ```

    The following table rows are displayed:

    ```
    +-------------+---------------------+--------------------+------------------+
    | employee_id | employee_first_name | employee_last_name | employee_emailID |
    +-------------+---------------------+--------------------+------------------+
    |           1 | Peter               | Dilliard           | test-01@test.com |
    |           2 | Meaghan             | Webb               | test-02@test.com |
    |           3 | Mary                | Smith              | msmith@test.com  |
    +-------------+---------------------+--------------------+------------------+
    ```

### Delete a row in a table

You can use the Delete operation to delete one or more table rows. Provide the entity ID or use the filter clause to specify the rows that you want to delete. Remember that, if you use the filter clause to specify criteria for rows that you want to delete, it's possible to delete multiple rows that match the given filter. If you want to delete only one specific row, use the entity ID.

To delete a table row using the entity ID, perform the following steps to configure the **Connectors** task that you created earlier:

1. Click the **Connectors** task element on the designer to view the task configuration pane.
2. Click **Configure task**.

   The **Configure connector task** dialog appears.
3. In the **Configure connector task** dialog, in the **Operation** column, select **Delete** and then click **Done**.
4. In the task configuration pane, under **Task Input** click **Entity ID**.
5. In the **Configure Variable** dialog, select **Use as an input to integration** and click **Save**.
6. Click the **Test** button in the integration editor toolbar.
7. Change the **Execution Deadline (in minutes)** value, if you like.
8. Enter the entity ID of the table row that you want to delete. Enter **3**.
9. Click **Test Integration**.
10. Once the integration completes successfully, the **Test Integration** pane displays the message **Integration execution succeeded**. To validate that the table row was deleted, use the Get operation to get the details of the row that you deleted. This should return an error for the specified entity ID.

    You can also use the List operation and optionally provide a filter clause for the table row (or rows) that you deleted. This returns the list of rows remaining, which could be an empty list.

    For example, if you deleted the table row with entity ID 3, then if you specify the filter clause `employee_emailID="msmith@test.com"` or the entity ID **3** for the List operation, the response parameters in the logs display `[]`.
11. You can verify that the row is deleted in your MySQL table. To verify this in your MySQL table, execute the following command from your MySQL client:

    ```
    SELECT * FROM employee;
    ```

    The following table rows are displayed:

    ```
    +-------------+---------------------+--------------------+------------------+
    | employee_id | employee_first_name | employee_last_name | employee_emailID |
    +-------------+---------------------+--------------------+------------------+
    |           1 | Peter               | Dilliard           | test-01@test.com |
    |           2 | Meaghan             | Webb               | test-02@test.com |
    +-------------+---------------------+--------------------+------------------+
    ```

## What's next

* [Insert data into BigQuery using a For Each Parallel task](/application-integration/docs/insert-data-bigquery-for-each-parallel-task)
* [All triggers and tasks](/application-integration/docs/all-triggers-tasks)




Send feedback

Except as otherwise noted, the content of this page is licensed under the [Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/), and code samples are licensed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0). For details, see the [Google Developers Site Policies](https://developers.google.com/site-policies). Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2026-03-26 UTC.




Need to tell us more?

[[["Easy to understand","easyToUnderstand","thumb-up"],["Solved my problem","solvedMyProblem","thumb-up"],["Other","otherUp","thumb-up"]],[["Hard to understand","hardToUnderstand","thumb-down"],["Incorrect information or sample code","incorrectInformationOrSampleCode","thumb-down"],["Missing the information/samples I need","missingTheInformationSamplesINeed","thumb-down"],["Other","otherDown","thumb-down"]],["Last updated 2026-03-26 UTC."],[],[]]
