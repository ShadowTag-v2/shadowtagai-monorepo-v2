import pexpect
import sys


def run_interactive_command():
  """
  TACSOP 4 / Headless CLI Doctrine:
  Bypass interactive TUI prompts using pexpect.
  """
  # Force CI mode just in case, though pexpect handles the PTY
  env = {"CI": "true", "DEBIAN_FRONTEND": "noninteractive"}

  print("Starting interactive CLI process...")
  # Example: starting an interactive CLI that prompts the user
  # Replace 'some_interactive_cli' with the actual command
  child = pexpect.spawn(
    "bash",
    ["-c", 'echo "Select option: " && read option && echo "You selected $option"'],
    encoding="utf-8",
    env=env,
  )

  # Log output to stdout
  child.logfile = sys.stdout

  try:
    # Expect the prompt
    child.expect("Select option:")

    # Send the response simulating a user hitting enter or typing
    child.sendline("1")

    # Wait for the process to finish
    child.expect(pexpect.EOF)
    print("\nProcess completed successfully.")

  except pexpect.TIMEOUT:
    print("\nTimeout waiting for expected output.")
    sys.exit(1)
  except pexpect.EOF:
    print("\nUnexpected end of file from the child process.")
    sys.exit(1)


if __name__ == "__main__":
  run_interactive_command()
