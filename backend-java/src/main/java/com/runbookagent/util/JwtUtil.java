package com.runbookagent.util;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import java.util.Date;
import javax.crypto.SecretKey;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Component
public class JwtUtil {

    private final SecretKey key;
    private static final long EXPIRATION_MS = 86400000; // 24 hours
    private static final long STREAM_TOKEN_TTL_MS = 300000; // 5 minutes

    public JwtUtil(@Value("${app.jwt-secret}") String secret) {
        byte[] keyBytes = secret.getBytes();
        if (keyBytes.length < 32) {
            byte[] padded = new byte[32];
            System.arraycopy(keyBytes, 0, padded, 0, keyBytes.length);
            keyBytes = padded;
        }
        this.key = Keys.hmacShaKeyFor(keyBytes);
    }

    public String generateToken(String username) {
        return Jwts.builder()
                .subject(username)
                .issuedAt(new Date())
                .expiration(new Date(System.currentTimeMillis() + EXPIRATION_MS))
                .signWith(key)
                .compact();
    }

    public String extractUsername(String token) {
        return parseClaims(token).getSubject();
    }

    public boolean isValid(String token) {
        try {
            Claims claims = parseClaims(token);
            return claims.getExpiration().after(new Date());
        } catch (Exception e) {
            return false;
        }
    }

    public String generateStreamToken(String username, String alertId) {
        return Jwts.builder()
                .subject(username)
                .claim("aid", alertId)
                .issuedAt(new Date())
                .expiration(new Date(System.currentTimeMillis() + STREAM_TOKEN_TTL_MS))
                .signWith(key)
                .compact();
    }

    public boolean isValidStreamToken(String token, String alertId) {
        try {
            Claims claims = parseClaims(token);
            if (!claims.getExpiration().after(new Date())) {
                return false;
            }
            return alertId.equals(claims.get("aid", String.class));
        } catch (Exception e) {
            return false;
        }
    }

    private Claims parseClaims(String token) {
        return Jwts.parser()
                .verifyWith(key)
                .build()
                .parseSignedClaims(token)
                .getPayload();
    }
}
