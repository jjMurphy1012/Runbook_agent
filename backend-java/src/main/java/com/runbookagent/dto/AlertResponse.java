package com.runbookagent.dto;

import java.time.Instant;
import java.util.Map;
import java.util.UUID;

public record AlertResponse(
        UUID id,
        String fingerprint,
        String ruleName,
        String category,
        String severity,
        String status,
        String message,
        Map<String, String> labels,
        Instant createdAt
) {
}
