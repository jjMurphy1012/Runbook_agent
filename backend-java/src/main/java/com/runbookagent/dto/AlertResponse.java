package com.runbookagent.dto;

import java.time.Instant;
import java.util.UUID;

public record AlertResponse(
        UUID id,
        String fingerprint,
        String ruleName,
        String category,
        String severity,
        String status,
        String message,
        Instant createdAt
) {
}
