# Source: https://github.com/GoogleCloudPlatform/cloud-workstations-custom-image-examples/tree/main/examples/images/gnome/noVnc

cloud-workstations-custom-image-examples/examples/images/gnome/noVnc at main · GoogleCloudPlatform/cloud-workstations-custom-image-examples · GitHub



[Skip to content](#start-of-content)







You signed in with another tab or window. Reload to refresh your session.
You signed out in another tab or window. Reload to refresh your session.
You switched accounts on another tab or window. Reload to refresh your session.



Dismiss alert

{{ message }}

[GoogleCloudPlatform](/GoogleCloudPlatform)
/
**[cloud-workstations-custom-image-examples](/GoogleCloudPlatform/cloud-workstations-custom-image-examples)**
Public

* [Notifications](/login?return_to=%2FGoogleCloudPlatform%2Fcloud-workstations-custom-image-examples) You must be signed in to change notification settings
* [Fork
  11](/login?return_to=%2FGoogleCloudPlatform%2Fcloud-workstations-custom-image-examples)
* [Star
   12](/login?return_to=%2FGoogleCloudPlatform%2Fcloud-workstations-custom-image-examples)

## FilesExpand file tree

main

/

# noVnc

/

Copy path

## Directory actions

## More options

More options

## Directory actions

## More options

More options

## Latest commit

## History

[History](/GoogleCloudPlatform/cloud-workstations-custom-image-examples/commits/main/examples/images/gnome/noVnc)

History

main

/

# noVnc

/

Top

## Folders and files

| Name | | Name | Last commit message | Last commit date |
| --- | --- | --- | --- | --- |
| parent directory [..](/GoogleCloudPlatform/cloud-workstations-custom-image-examples/tree/main/examples/images/gnome) | | |
| [assets](/GoogleCloudPlatform/cloud-workstations-custom-image-examples/tree/main/examples/images/gnome/noVnc/assets "assets") | | [assets](/GoogleCloudPlatform/cloud-workstations-custom-image-examples/tree/main/examples/images/gnome/noVnc/assets "assets") |  |  |
| [Dockerfile](/GoogleCloudPlatform/cloud-workstations-custom-image-examples/blob/main/examples/images/gnome/noVnc/Dockerfile "Dockerfile") | | [Dockerfile](/GoogleCloudPlatform/cloud-workstations-custom-image-examples/blob/main/examples/images/gnome/noVnc/Dockerfile "Dockerfile") |  |  |
| [README.md](/GoogleCloudPlatform/cloud-workstations-custom-image-examples/blob/main/examples/images/gnome/noVnc/README.md "README.md") | | [README.md](/GoogleCloudPlatform/cloud-workstations-custom-image-examples/blob/main/examples/images/gnome/noVnc/README.md "README.md") |  |  |
| [cloudbuild.yaml](/GoogleCloudPlatform/cloud-workstations-custom-image-examples/blob/main/examples/images/gnome/noVnc/cloudbuild.yaml "cloudbuild.yaml") | | [cloudbuild.yaml](/GoogleCloudPlatform/cloud-workstations-custom-image-examples/blob/main/examples/images/gnome/noVnc/cloudbuild.yaml "cloudbuild.yaml") |  |  |
| View all files | | |

## [README.md](#readme)

# Gnome Example

This example shows how to create a Cloud Workstations image that runs a desktop manager which can be accessed by remote desktop software. This sample uses [GNOME](https://www.gnome.org/) to provide the desktop environment and preinstalls [TigerVNC](https://tigervnc.org/) along with [noVNC](https://novnc.com/info.html) to provide a one-click, browser-based, interactive session.

This example can be built with the included cloudbuild.yaml by specifying substitutions for the base image and the image name for the newly built systemd image:

```
gcloud builds submit --substitutions _IMAGE_NAME=us-central1-docker.pkg.dev/your-project-id/your-repository/your-image-name
```

Or can be built locally using:

```
docker build -t gnome-vnc .
```

To run / test the container locally, use the following command:

```
docker run --rm -it --privileged -p 8080:80 gnome-vnc
```

> Note: this conainer must be started using the `--privileged` switch.

Then navigate to localhost:8080 on your local machine to access the NoVNC html client.

You can’t perform that action at this time.
