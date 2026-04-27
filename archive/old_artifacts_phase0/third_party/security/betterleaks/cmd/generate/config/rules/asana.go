package rules

import (
	"github.com/betterleaks/betterleaks/cmd/generate/config/utils"
	"github.com/betterleaks/betterleaks/cmd/generate/secrets"
	"github.com/betterleaks/betterleaks/config"
)

func AsanaClientID() *config.Rule {
	// define rule
	r := config.Rule{
		Description: "Discovered a potential Asana Client ID, risking unauthorized access to Asana projects and sensitive task information.",
		RuleID:      "asana-client-id",
		Regex:       utils.GenerateSemiGenericRegex([]string{"asana"}, utils.Numeric("16"), true),
		Keywords:    []string{"asana"},
	}

	// validate
	tps := utils.GenerateSampleSecrets("asana", secrets.NewSecret(utils.Numeric("16")))
	return utils.Validate(r, tps, nil)
}

func AsanaClientSecret() *config.Rule {
	// define rule
	r := config.Rule{
		Description: "Identified an Asana Client Secret, which could lead to compromised project management integrity and unauthorized access.",
		RuleID:      "asana-client-secret",
		Regex:       utils.GenerateSemiGenericRegex([]string{"asana"}, utils.AlphaNumeric("32"), true),

		Keywords: []string{"asana"},
	}

	// validate
	tps := utils.GenerateSampleSecrets("asana", secrets.NewSecret(utils.AlphaNumeric("32")))
	return utils.Validate(r, tps, nil)
}
