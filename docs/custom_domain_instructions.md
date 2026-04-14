# Firebase Custom Domain Implementation Framework

To resolve the DNS "Site Not Found" error for `shadowtagai.com` and `kovelai.com`, strict ownership validation steps must be completed manually via the Firebase Console to fully bind the custom domain mapping to the deployed Firebase sites.

## 1. Trigger the Firebase Verification Handshake
Navigate to:
`Project Overview > Hosting > Add Custom Domain`

Type the domain name (`shadowtagai.com`) and proceed. Firebase will generate a TXT verification string (e.g. `firebase=xxxxxxxxxx`).

## 2. Cloud DNS Record Mapping
Inside the Google Cloud Console (`Cloud DNS > shadowtagai-zone`), bind the primary domain via two explicit record chains:

### Verification Record
| Type | Name | Value | TTL |
|------|------|-----------------------|-----|
| TXT  | @    | firebase=xxxxxxxxxx | 300 |

### Routing Array
You must point the Root Domain (`@`) toward Firebase edge cache IPs:
| Type | Name | Value | TTL |
|------|------|-----------------------|-----|
| A    | @    | 199.36.158.100        | 300 |

*Note: The Firebase CLI deploy alone cannot authorize DNS mapping on the platform edge, hence the manual site-not-found override process documented here.*
