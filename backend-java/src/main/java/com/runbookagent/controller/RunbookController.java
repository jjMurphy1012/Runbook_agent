package com.runbookagent.controller;

import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/runbooks")
public class RunbookController {

    @GetMapping("/health")
    public Map<String, String> health() {
        return Map.of("service", "runbooks", "status", "ok");
    }
}
