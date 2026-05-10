//! JWT authentication module
//!
//! Matches the JWT structure from the Python backend (src/aiyou/auth.py)

use jsonwebtoken::{decode, Algorithm, DecodingKey, Validation};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tracing::{debug, warn};

use crate::{MediaEdgeError, Result};

/// JWT claims structure (matches Python backend)
#[derive(Debug, Serialize, Deserialize)]
pub struct Claims {
    /// User ID (subject)
    pub sub: String,

    /// Expiration timestamp
    pub exp: usize,

    /// Token ID (JWT ID)
    pub jti: String,

    /// Token type (optional)
    #[serde(rename = "type", default)]
    pub token_type: Option<String>,

    /// Issued at (optional)
    #[serde(default)]
    pub iat: Option<usize>,
}

/// JWT verification error types
#[derive(Debug)]
pub enum AuthError {
    MissingHeader,
    InvalidFormat,
    TokenExpired,
    ValidationFailed(String),
}

impl std::fmt::Display for AuthError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            AuthError::MissingHeader => write!(f, "Missing authorization header"),
            AuthError::InvalidFormat => write!(f, "Invalid token format"),
            AuthError::TokenExpired => write!(f, "Token expired"),
            AuthError::ValidationFailed(msg) => write!(f, "Validation failed: {}", msg),
        }
    }
}

impl std::error::Error for AuthError {}

impl From<AuthError> for MediaEdgeError {
    fn from(err: AuthError) -> Self {
        MediaEdgeError::Auth(err.to_string())
    }
}

/// JWT verifier
pub struct JwtVerifier {
    decoding_key: DecodingKey,
    validation: Validation,
}

impl JwtVerifier {
    /// Create a new JWT verifier
    ///
    /// # Arguments
    /// * `secret` - The JWT secret (must match Python backend)
    /// * `algorithm` - Algorithm string (e.g., "HS256")
    pub fn new(secret: &str, algorithm: &str) -> Self {
        let algo = match algorithm.to_uppercase().as_str() {
            "HS256" => Algorithm::HS256,
            "HS384" => Algorithm::HS384,
            "HS512" => Algorithm::HS512,
            "RS256" => Algorithm::RS256,
            "RS384" => Algorithm::RS384,
            "RS512" => Algorithm::RS512,
            _ => {
                warn!(algorithm = algorithm, "Unknown algorithm, defaulting to HS256");
                Algorithm::HS256
            }
        };

        let mut validation = Validation::new(algo);
        validation.validate_exp = true;
        validation.leeway = 60; // 60 second leeway for clock skew

        Self {
            decoding_key: DecodingKey::from_secret(secret.as_bytes()),
            validation,
        }
    }

    /// Verify a JWT token from Authorization header
    ///
    /// # Arguments
    /// * `auth_header` - The full Authorization header value (e.g., "Bearer eyJ...")
    ///
    /// # Returns
    /// The decoded claims if valid
    pub fn verify(&self, auth_header: &str) -> std::result::Result<Claims, AuthError> {
        // Extract token from "Bearer <token>" format
        let token = auth_header
            .strip_prefix("Bearer ")
            .or_else(|| auth_header.strip_prefix("bearer "))
            .ok_or(AuthError::InvalidFormat)?;

        // Decode and verify
        let token_data = decode::<Claims>(token, &self.decoding_key, &self.validation)
            .map_err(|e| {
                debug!(error = %e, "JWT verification failed");
                if e.to_string().contains("expired") {
                    AuthError::TokenExpired
                } else {
                    AuthError::ValidationFailed(e.to_string())
                }
            })?;

        debug!(user_id = %token_data.claims.sub, "JWT verified successfully");
        Ok(token_data.claims)
    }

    /// Extract user ID from Authorization header (if valid)
    pub fn get_user_id(&self, auth_header: &str) -> Option<String> {
        self.verify(auth_header).ok().map(|claims| claims.sub)
    }
}

/// Thread-safe JWT verifier handle
pub type JwtHandle = Arc<JwtVerifier>;

/// Create a new JWT handle
pub fn create_jwt_verifier(secret: &str, algorithm: &str) -> JwtHandle {
    Arc::new(JwtVerifier::new(secret, algorithm))
}

#[cfg(test)]
mod tests {
    use super::*;
    use jsonwebtoken::{encode, EncodingKey, Header};

    fn create_test_token(secret: &str, exp_offset: i64) -> String {
        let exp = (chrono::Utc::now().timestamp() + exp_offset) as usize;
        let claims = Claims {
            sub: "test_user".to_string(),
            exp,
            jti: "test_jti".to_string(),
            token_type: Some("access".to_string()),
            iat: Some((chrono::Utc::now().timestamp()) as usize),
        };

        encode(
            &Header::default(),
            &claims,
            &EncodingKey::from_secret(secret.as_bytes()),
        )
        .unwrap()
    }

    #[test]
    fn test_valid_token() {
        let secret = "test_secret";
        let verifier = JwtVerifier::new(secret, "HS256");
        let token = create_test_token(secret, 3600); // Valid for 1 hour

        let result = verifier.verify(&format!("Bearer {}", token));
        assert!(result.is_ok());
        assert_eq!(result.unwrap().sub, "test_user");
    }

    #[test]
    fn test_expired_token() {
        let secret = "test_secret";
        let verifier = JwtVerifier::new(secret, "HS256");
        let token = create_test_token(secret, -3600); // Expired 1 hour ago

        let result = verifier.verify(&format!("Bearer {}", token));
        assert!(matches!(result, Err(AuthError::TokenExpired)));
    }

    #[test]
    fn test_invalid_format() {
        let verifier = JwtVerifier::new("secret", "HS256");
        let result = verifier.verify("InvalidHeader");
        assert!(matches!(result, Err(AuthError::InvalidFormat)));
    }
}
