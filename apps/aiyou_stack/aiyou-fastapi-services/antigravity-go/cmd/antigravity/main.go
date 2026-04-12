package main

import (
	"flag"
	"fmt"
	"io/ioutil"
	"path/filepath"

	"github.com/ehanc69/antigravity-go/pkg/agent"
)

func main() {
	help := flag.Bool("help", false, "Show help")
	colab := flag.Bool("colab", false, "Show Colab integration info")
	flag.Parse()

	if *help {
		fmt.Println("Antigravity Go CLI")
		flag.PrintDefaults()
		return
	}

	if *colab {
		printColabInfo()
		return
	}

	a := agent.NewAgent("Antigravity")
	a.Run()
}

func printColabInfo() {
	// Try to read the markdown file if it exists relative to execution
	path := "ANTIGRAVITY_COLAB.md"
	absPath, _ := filepath.Abs(path)
	content, err := ioutil.ReadFile(absPath)
	if err == nil {
		fmt.Println(string(content))
	} else {
		// Fallback text
		fmt.Println("Antigravity Colab Integration:")
		fmt.Println("You use the Colab VS Code extension inside Antigravity when you want Antigravity’s agent-first IDE + toolchain, but you want your code to actually run on Google Colab’s free/cloud GPUs/TPUs.")
	}
}
