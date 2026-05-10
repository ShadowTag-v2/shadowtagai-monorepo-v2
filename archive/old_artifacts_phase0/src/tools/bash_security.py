import re


class BashSecurityValidator:
    def validate(self, command: str) -> bool:
        if "\u00a0" in command or "\u200b" in command:
            raise ValueError("SECURITY BLOCK: Unicode whitespace hiding detected.")
        if "zmodload" in command:
            raise ValueError("SECURITY BLOCK: zmodload kernel module injection blocked.")
        if re.search(r"/proc/\d+/environ", command):
            raise ValueError("SECURITY BLOCK: /proc/*/environ read blocked.")
        if "$IFS" in command:
            raise ValueError("SECURITY BLOCK: $IFS injection detected.")
        if "\r" in command:
            raise ValueError("SECURITY BLOCK: Carriage return parsing differential detected.")
        return True
