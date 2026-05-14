package com.runbookagent.dto;

import java.util.Map;

public record AlertRequest(
        String ruleName,
        String category,
        String severity,
        String message,
        Map<String, String> labels
) {
}
