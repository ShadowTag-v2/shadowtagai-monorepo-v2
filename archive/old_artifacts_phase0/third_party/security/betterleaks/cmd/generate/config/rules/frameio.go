package rules

import (
	"github.com/betterleaks/betterleaks/cmd/generate/config/utils"
	"github.com/betterleaks/betterleaks/cmd/generate/secrets"
	"github.com/betterleaks/betterleaks/config"
	"github.com/betterleaks/betterleaks/regexp"
)

func FrameIO() *config.Rule {
	// define rule
	r := config.Rule{
		Description: "Found a Frame.io API token, potentially compromising video collaboration and project management.",
		RuleID:      "frameio-api-token",
		Regex:       regexp.MustCompile(`fio-u-(?i)[a-z0-9\-_=]{64}`),
		Keywords:    []string{"fio-u-"},
	}

	// validate
	tps := utils.GenerateSampleSecrets("frameio", "fio-u-"+secrets.NewSecret(utils.AlphaNumericExtended("64")))
	return utils.Validate(r, tps, nil)
}
