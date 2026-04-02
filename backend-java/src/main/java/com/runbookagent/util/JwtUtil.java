package com.runbookagent.util;

import org.springframework.stereotype.Component;

@Component
public class JwtUtil {

    public String generateToken(String username) {
        return "stub-token-for-" + username;
    }
}
