import os
import subprocess
import time

import requests


def wait_for_sonarqube():
    print("⏳ Waiting for SonarQube to be ready (this may take 1-2 minutes)...")
    url = "http://localhost:9000/api/system/status"
    retries = 60
    for i in range(retries):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                status = response.json().get("status")
                if status == "UP":
                    print("✅ SonarQube is UP!")
                    return True
                print(f"   Status: {status} (waiting...)")
        except requests.exceptions.ConnectionError:
            print(f"   Connection refused (attempt {i + 1}/{retries})...")

        time.sleep(5)
    return False


def generate_token():
    print("🔑 Generating User Token...")
    # Default admin credentials
    auth = ("admin", "admin")

    # 1. We might need to change the password on first login?
    # SonarQube 9.x+ often forces password change. Let's try to generate token directly first.
    # If it fails due to "password change required", we handle that.

    token_name = f"autogen-token-{int(time.time())}"
    url = "http://localhost:9000/api/user_tokens/generate"
    params = {"name": token_name}

    try:
        response = requests.post(url, auth=auth, params=params)

        if response.status_code == 200:
            token = response.json().get("token")
            print("✅ Token generated successfully")
            return token
        if response.status_code == 401:
            print("❌ Authentication failed. Default admin:admin credentials didn't work.")
            return None
        print(f"❌ Failed to generate token: {response.text}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    # 1. Wait for SonarQube
    if not wait_for_sonarqube():
        print("❌ SonarQube failed to start in time.")
        raise SystemExit(1)

    # 2. Generate Token
    token = generate_token()
    if not token:
        print(
            "⚠️  Could not auto-generate token. You may need to log in to http://localhost:9000 (admin/admin) manually.",
        )
        raise SystemExit(1)

    # 3. Run Setup Script with Token
    print("\n🚀 Running setup_sonar_integration.sh with generated token...")

    env = os.environ.copy()
    env["SONAR_TOKEN"] = token

    # Assuming script is in scripts/setup_sonar_integration.sh
    script_path = os.path.join(os.getcwd(), "scripts", "setup_sonar_integration.sh")

    result = subprocess.run(["bash", script_path], env=env)
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
