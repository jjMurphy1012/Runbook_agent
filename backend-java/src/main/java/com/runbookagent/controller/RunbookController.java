package com.runbookagent.controller;

import com.runbookagent.dto.RunbookResponse;
import com.runbookagent.service.RunbookService;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/runbooks")
public class RunbookController {

    private final RunbookService runbookService;

    public RunbookController(RunbookService runbookService) {
        this.runbookService = runbookService;
    }

    @GetMapping
    public ResponseEntity<List<RunbookResponse>> listRunbooks() {
        return ResponseEntity.ok(runbookService.listRunbooks());
    }

    @GetMapping("/{id}")
    public ResponseEntity<RunbookResponse> getRunbook(@PathVariable UUID id) {
        return ResponseEntity.ok(runbookService.getRunbook(id));
    }

    @PostMapping("/{id}/approve")
    public ResponseEntity<RunbookResponse> approveRunbook(@PathVariable UUID id) {
        return ResponseEntity.ok(runbookService.approveRunbook(id));
    }

    @PostMapping("/{id}/reject")
    public ResponseEntity<RunbookResponse> rejectRunbook(@PathVariable UUID id) {
        return ResponseEntity.ok(runbookService.rejectRunbook(id));
    }

    @GetMapping("/health")
    public Map<String, String> health() {
        return Map.of("service", "runbooks", "status", "ok");
    }
}
