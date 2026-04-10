package agent

import "fmt"

type Agent struct {
	Name string
}

func NewAgent(name string) *Agent {
	return &Agent{Name: name}
}

func (a *Agent) Run() {
	fmt.Printf("Agent %s is running...\n", a.Name)
}
