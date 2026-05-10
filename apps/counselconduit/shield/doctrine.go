package doctrine
import "strings"
type MitigationTier int
const (
    Tier1_Pass MitigationTier = iota + 1
    Tier2_Warn
    Tier3_Intervene
    Tier4_SwarmDispatch
    Tier5_RKILL
)
type ActionPayload struct {
    UserID  string `json:"user_id"`
    RawCode string `json:"raw_code"`
}
func EvaluateRisk(payload ActionPayload) MitigationTier {
    code := strings.ToUpper(payload.RawCode)
    if strings.Contains(code, "DROP TABLE") || strings.Contains(code, "RM -RF") {
        return Tier5_RKILL
    }
    if strings.Contains(code, "USER.AGE < 18") || strings.Contains(code, "GEOLOCATION") {
        return Tier4_SwarmDispatch
    }
    return Tier1_Pass
}
