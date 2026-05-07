import pexpect
import sys
import time

def run_ingestor():
    print("Launching skill ingestor...")
    # TACSOP 4 skill ingestor prompt bypass
    # Force headless/non-interactive where possible, but pexpect handles the rest
    cmd = 'npx skills add google/skills'
    
    # We use spawn to trick the command into thinking it has a TTY
    child = pexpect.spawn(cmd, encoding='utf-8', timeout=120)
    child.logfile = sys.stdout

    try:
        while True:
            # Look for common interactive prompts from 'npx skills add'
            index = child.expect([
                pexpect.EOF,
                pexpect.TIMEOUT,
                r'Ok to proceed\? \(y\)',
                r'Proceed\?',
                r'Select a skill',
                r'Select skills to install',
                r'Which agents do you want to install to\?',
                r'Proceed with installation\?',
                r'\? '
            ])
            
            if index == 0:
                print("\n[+] Process completed successfully.")
                break
            elif index == 1:
                print("\n[-] Timeout reached.")
                break
            elif index == 2 or index == 3:
                print("\n[*] Answering yes to prompt...")
                child.sendline('y')
            elif index == 4 or index == 5:
                print("\n[*] Sending 'a' to select all, then enter...")
                child.send('a')
                time.sleep(0.5)
                child.send('\r')
                time.sleep(1)
            elif index == 6:
                print("\n[*] Sending enter for agents prompt...")
                child.send('\r')
                time.sleep(1)
            elif index == 7:
                print("\n[*] Sending enter for proceed with installation prompt...")
                child.send('\r')
                time.sleep(1)
            elif index == 8:
                print("\n[*] Sending enter to default prompt...")
                child.send('\r')
                time.sleep(1)
    except Exception as e:
        print(f"\n[-] Error: {e}")
        
    child.close()
    print(f"Exit status: {child.exitstatus}")

if __name__ == '__main__':
    run_ingestor()
