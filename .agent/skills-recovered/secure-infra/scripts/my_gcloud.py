import sys
import os
import subprocess

def run_gcloud_cmd(args):
    """
    Executes the native Google Cloud CLI.
    """
    cmd = ["gcloud"] + args
    print(f"Executing: {' '.join(cmd)}")
    
    try:
        # We don't capture output here so the agent can see interactive streaming if needed,
        # but for programmatic use capture_output=True is better.
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("--- GCLOUD OUTPUT ---")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("--- GCLOUD ERROR ---")
        print(e.stderr)
        if e.stdout:
           print(e.stdout)
        return False
        
def main():
    if len(sys.argv) < 2:
        print("Usage: python3 my_gcloud.py <gcloud_cli_args_without_gcloud>")
        print("Example: python3 my_gcloud.py run deploy my-service --source .")
        sys.exit(1)
        
    args = sys.argv[1:]
    success = run_gcloud_cmd(args)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
