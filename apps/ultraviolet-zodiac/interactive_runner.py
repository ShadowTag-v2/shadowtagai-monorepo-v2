import os
import pty
import select

# The command to run
command = [
  "/Users/pikeymickey/shadowtag_v4-stack/ShadowTag-v2/.venv/bin/python",
  "scripts/god_mode_admin.py",
]

# Set the environment variables
os.environ["GCP_PROJECT_ID"] = "shadowtag-omega-v4"
os.environ["PYTHONPATH"] = (
  os.environ.get("PYTHONPATH", "")
  + ":/Users/pikeymickey/shadowtag_v4-stack/ShadowTag-v2"
)
os.environ["BRAIN_DIR"] = (
  "/Users/pikeymickey/.gemini/antigravity/brain/0f155a4e-36e6-4528-a693-619a039e50"
)
os.environ["EXTERNAL_SDKS"] = "/Users/pikeymickey/shadowtag_v4-stack/ShadowTag-v2"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
  "/Users/pikeymickey/Library/Application Support/google-vscode-extension/auth/application_default_credentials.json"
)


# Change the working directory
os.chdir("/Users/pikeymickey/shadowtag_v4-stack/ShadowTag-v2")


def read_until_prompt(fd, prompt="Awaiting Command Flux..."):
  output = ""
  while prompt not in output:
    r, _, _ = select.select([fd], [], [], 60)  # 60 second timeout
    if r:
      try:
        data = os.read(fd, 1024)
        if not data:
          break
        output += data.decode()
      except OSError:
        break
    else:
      # Timeout
      break
  return output


# Create a new pseudo-terminal
pid, fd = pty.fork()

if pid == 0:
  # Child process
  # Execute the command
  os.execv(command[0], command)
else:
  # Parent process

  # Read the initial prompt
  initial_output = read_until_prompt(fd)

  # The command to send to the shell
  shell_command = "shell python3 /Users/pikeymickey/.gemini/antigravity/playground/ultraviolet-zodiac/pii_scrubber.py\\n"

  # Send the shell command
  os.write(fd, shell_command.encode())

  # Read until the next prompt
  final_output = read_until_prompt(fd)

  print(final_output)
  os.close(fd)
