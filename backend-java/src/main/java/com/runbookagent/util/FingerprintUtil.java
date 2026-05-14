package com.runbookagent.util;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HexFormat;
import java.util.Map;
import java.util.TreeMap;

/**
 * Canonical alert fingerprint.
 *
 * Mirrors agents/fingerprint.py on the Python side. Any change here MUST be
 * mirrored there — the string is a Redis cache key and a join key against
 * incident_history, so drift silently breaks memory retrieval and cache hits.
 *
 * Canonical form:
 *     rule_name + "|" + json(sorted labels, no whitespace)
 */
public final class FingerprintUtil {

    private static final ObjectMapper MAPPER = new ObjectMapper();

    private FingerprintUtil() {}

    public static String compute(String ruleName, Map<String, String> labels) {
        String canonicalLabels;
        try {
            canonicalLabels = MAPPER.writeValueAsString(
                    new TreeMap<>(labels == null ? Map.of() : labels)
            );
        } catch (JsonProcessingException e) {
            // Unreachable for Map<String,String>; fail loud if it ever happens.
            throw new IllegalStateException("Failed to canonicalize labels", e);
        }

        String canonical = (ruleName == null ? "" : ruleName) + "|" + canonicalLabels;
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] hash = md.digest(canonical.getBytes(StandardCharsets.UTF_8));
            return HexFormat.of().formatHex(hash).substring(0, 32);
        } catch (NoSuchAlgorithmException e) {
            throw new IllegalStateException("SHA-256 unavailable", e);
        }
    }
}
