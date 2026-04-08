package com.runbookagent.controller;

import com.runbookagent.dto.AlertRequest;
import com.runbookagent.dto.AlertResponse;
import com.runbookagent.service.AlertService;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/alerts")
public class AlertController {

    private final AlertService alertService;

    public AlertController(AlertService alertService) {
        this.alertService = alertService;
    }

    @PostMapping
    public ResponseEntity<AlertResponse> createAlert(@RequestBody AlertRequest request) {
        return ResponseEntity.ok(alertService.createAlert(request));
    }

    @GetMapping
    public ResponseEntity<List<AlertResponse>> listAlerts() {
        return ResponseEntity.ok(alertService.listAlerts());
    }

    @GetMapping("/{id}")
    public ResponseEntity<AlertResponse> getAlert(@PathVariable UUID id) {
        return ResponseEntity.ok(alertService.getAlert(id));
    }

    @PostMapping("/{id}/trigger")
    public ResponseEntity<Map<String, String>> triggerAgent(@PathVariable UUID id) {
        alertService.triggerAgentWorkflow(id);
        return ResponseEntity.ok(Map.of("status", "triggered", "alert_id", id.toString()));
    }

    @GetMapping("/health")
    public Map<String, String> health() {
        return Map.of("service", "alerts", "status", "ok");
    }
}
