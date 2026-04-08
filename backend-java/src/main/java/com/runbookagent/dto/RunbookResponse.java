package com.runbookagent.dto;

import java.time.Instant;
import java.util.UUID;

public record RunbookResponse(
        UUID id,
        String title,
        String rootCause,
        Integer version,
        String status,
        String content,
        Instant updatedAt
) {
}
