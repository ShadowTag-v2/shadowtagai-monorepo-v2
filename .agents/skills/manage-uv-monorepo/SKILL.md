---
name: manage-uv-monorepo
description: "Instructions for Antigravity agents on managing Python dependencies, virtual environments, and script execution using uv in the monorepo."
---

## Skill: Managing Python Workspaces with UV

**Description:** Instructions for Antigravity agents on how to handle Python dependencies, virtual environments, and script execution within the `Monorepo-Uphillsnowball` using `uv`.

### 1. Context: Agentic Setup vs. Legacy Manual Setup
Historically, human developers set up Python environments manually. For context, you may encounter legacy onboarding materials or tutorials resembling the following:

> "Hello guys, welcome. In this video, we will learn how to run Python in Google integrity IDE. So let's start. So first we will download Python. So for that I will come to this Chrome, open it. Here I will search for Python. Go to this first link python.org. Click on this downloads and here you can see you can download Python with Python install manager and you can download a stand alone installer. So I'll click on the standalone installer. Now you can see the download started. So now the download is complete. So I'll go to the show in folder. Right click on this and open it. We will check this check box as well as this one. And then we will click on this customize installation. Now keep this default and click next. And here check this install Python 3.14 for all users. Check this and click install. Click yes. And now you can see the installation started. So it will take some time. So now the installation is complete. So I'll close this and close this as well. Now we will verify our Python installation. So for that I will come to this search. Type in here cmd enter. And here I'll use python hyphen version. Now you can see here python 3.14 is installed. So I'll close this. Now we will open our integrity IDE. So I'll right click on integrity and open it. I'll maximize this. I'll go here to extensions and here I will search for python. Now you can see here Python MS Python. So click on this and install this. Now you can see it is installing. So it will take some time. So now the extension is installed. So I'll close this. I'll close this as well. All these files. I'll close this extensions tab as well. And I'll come to this explorer. I can create a file here. Python file here. But I will ask cloud to create me a simple Python program. addition program that takes input from user. Now it is working on it. Now here I will accept changes. You can see it has created this addition. py file and addit this code to it. Now if I right click on this and run python. So now you can see it is asking me to enter the first number. So I'll enter this and then the second number. And now you can see here it has shown me the"

**CRITICAL DIRECTIVE:** As an autonomous Antigravity agent, you must **ignore** the manual workflow described above. Do not attempt to use web browsers, graphical installers, or manual extension managers. You are operating in a headless workspace. You must use `uv` for all Python environment management.

### 2. Monorepo Navigation
The workspace is a monorepo. Dependencies are managed at the app level, but you must ensure you are targeting the correct workspace package.
* **Target App:** `apps/ShadowTag-v2_stack/ShadowTag-v2-fastapi-services`
* Always execute `uv` commands from the root of the monorepo using workspace flags, or navigate directly into the target app directory before running `uv`.

### 3. Core `uv` Commands for Agents

* **Adding Dependencies:** To add a package to a specific app without interactive prompts, use:
    `uv add <package_name> --package shadowtag-omega-v4-fastapi-services`
* **Syncing the Environment:** If you modify `pyproject.toml`, immediately sync the environment to lock dependencies:
    `uv sync`
* **Running Scripts:** Do not try to activate the virtual environment manually. Always prefix execution commands with `uv run`.
    `uv run --package shadowtag-omega-v4-fastapi-services uvicorn main:app --reload`
* **Running the Linter/Type-checker:** `uv run basedpyright`

### 4. Error Handling
* If `uv` throws a resolution error, read the structured stderr output.
* Do not attempt to switch to `pip` or `poetry` as a fallback.
* If a lockfile conflict occurs, use `uv lock` to regenerate it before attempting the installation again.
