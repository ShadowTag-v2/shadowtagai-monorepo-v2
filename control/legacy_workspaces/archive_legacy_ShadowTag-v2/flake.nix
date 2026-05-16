{
  description = "Antigravity Swarm: Observable & Equipped";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    antigravity-nix.url = "github:jacopone/antigravity-nix";
  };

  outputs = { self, nixpkgs, antigravity-nix }: 
  let
    system = "x86_64-linux";
    pkgs = nixpkgs.legacyPackages.${system};
    
    # Extension URLs (Version Pinned)
    quotaWatcherUrl = "https://github.com/wusimpl/AntigravityQuotaWatcher/releases/download/v0.7.0/antigravity-quota-watcher-0.7.0.vsix";
    deepnoteUrl = "https://deepnote.gallerycdn.vsassets.io/extensions/deepnote/vscode-deepnote/0.2.5/1737736552124/Microsoft.VisualStudio.Services.VSIXPackage";
    
  in {
    devShells.${system}.default = pkgs.mkShell {
      buildInputs = [
        antigravity-nix.packages.${system}.default
        pkgs.python311
        pkgs.python311Packages.google-generativeai
        pkgs.python311Packages.python-dotenv
        pkgs.python311Packages.pandas  # For Deepnote analysis
        pkgs.mitmproxy                 # The Traffic Controller
        pkgs.curl
      ];

      shellHook = ''
        echo "🪐 Initializing Antigravity Swarm Environment..."

        # 1. Setup Extension Directory
        mkdir -p .antigravity-extensions

        # 2. Fetch Mission Control Tools
        if [ ! -f .antigravity-extensions/quota-watcher.vsix ]; then
            echo "📡 Downloading Telemetry (QuotaWatcher)..."
            curl -L -o .antigravity-extensions/quota-watcher.vsix "${quotaWatcherUrl}"
        fi
        
        if [ ! -f .antigravity-extensions/deepnote.vsix ]; then
            echo "🧪 Downloading Lab Equipment (Deepnote)..."
            curl -L -o .antigravity-extensions/deepnote.vsix "${deepnoteUrl}"
        fi

        # 3. Install Extensions (Atomic Check)
        AG_BIN=$(which antigravity)
        echo "🔧 Equipping IDE..."
        $AG_BIN --install-extension .antigravity-extensions/quota-watcher.vsix > /dev/null 2>&1
        $AG_BIN --install-extension .antigravity-extensions/deepnote.vsix > /dev/null 2>&1

        # 4. Proxy Configuration
        export PROXY_PORT=8080
        export HTTP_PROXY="http://localhost:8080"
        export HTTPS_PROXY="http://localhost:8080"
        
        # 5. Security & Trust (The Critical "Corner")
        if [ ! -f ~/.mitmproxy/mitmproxy-ca-cert.pem ]; then
            echo "⚠️  FIRST RUN DETECTED: Start 'mitmdump' once to generate certificates."
        else
            echo "✅ Certificates detected. Ensure ~/.mitmproxy/mitmproxy-ca-cert.pem is trusted by your OS."
        fi

        echo "🚀 System Ready. Run 'python src/swarm.py' to launch."
      '';
    };
  };
}
