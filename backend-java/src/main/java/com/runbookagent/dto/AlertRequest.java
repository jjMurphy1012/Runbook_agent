package com.runbookagent.dto;

public record AlertRequest(
        String ruleName,
        String category,
        String severity,
        String message
) {
}
