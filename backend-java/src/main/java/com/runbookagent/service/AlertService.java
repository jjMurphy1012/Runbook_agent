package com.runbookagent.service;

import com.runbookagent.dto.AlertRequest;
import com.runbookagent.dto.AlertResponse;
import com.runbookagent.model.Alert;
import com.runbookagent.model.AlertStatus;
import com.runbookagent.repository.AlertRepository;
import java.security.MessageDigest;
import java.time.Instant;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

@Service
public class AlertService {

    private final AlertRepository alertRepository;
    private final RedisStreamPublisher streamPublisher;
    private final WebClient pythonClient;

    public AlertService(
            AlertRepository alertRepository,
            RedisStreamPublisher streamPublisher,
            @Value("${app.python-service-url:http://localhost:8000}") String pythonUrl) {
        this.alertRepository = alertRepository;
        this.streamPublisher = streamPublisher;
        this.pythonClient = WebClient.builder().baseUrl(pythonUrl).build();
    }

    public AlertResponse createAlert(AlertRequest request) {
        String fingerprint = computeFingerprint(request.ruleName());

        Alert alert = new Alert();
        alert.setId(UUID.randomUUID());
        alert.setFingerprint(fingerprint);
        alert.setRuleName(request.ruleName());
        alert.setCategory(request.category());
        alert.setSeverity(request.severity());
        alert.setStatus(AlertStatus.PENDING);
        alert.setMessage(request.message());
        alert.setCreatedAt(Instant.now());

        alert = alertRepository.save(alert);
        streamPublisher.publishAlertCreated(alert.getId().toString());

        return toResponse(alert);
    }

    public void triggerAgentWorkflow(UUID alertId) {
        Alert alert = alertRepository.findById(alertId)
                .orElseThrow(() -> new IllegalArgumentException("Alert not found"));

        alert.setStatus(AlertStatus.PROCESSING);
        alertRepository.save(alert);

        pythonClient.post()
                .uri("/agent/run")
                .bodyValue(Map.of(
                        "id", alert.getId().toString(),
                        "rule_name", alert.getRuleName(),
                        "category", alert.getCategory(),
                        "severity", alert.getSeverity(),
                        "message", alert.getMessage() != null ? alert.getMessage() : "",
                        "labels", Map.of()
                ))
                .retrieve()
                .bodyToMono(Map.class)
                .subscribe(
                        result -> {
                            alert.setStatus(AlertStatus.RESOLVED);
                            alertRepository.save(alert);
                        },
                        error -> {
                            alert.setStatus(AlertStatus.ESCALATED);
                            alertRepository.save(alert);
                        }
                );
    }

    public List<AlertResponse> listAlerts() {
        return alertRepository.findAll().stream().map(this::toResponse).toList();
    }

    public AlertResponse getAlert(UUID id) {
        Alert alert = alertRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Alert not found"));
        return toResponse(alert);
    }

    private AlertResponse toResponse(Alert alert) {
        return new AlertResponse(
                alert.getId(),
                alert.getFingerprint(),
                alert.getRuleName(),
                alert.getCategory(),
                alert.getSeverity(),
                alert.getStatus().name(),
                alert.getMessage(),
                alert.getCreatedAt()
        );
    }

    private String computeFingerprint(String ruleName) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] hash = md.digest(ruleName.getBytes());
            return HexFormat.of().formatHex(hash).substring(0, 32);
        } catch (Exception e) {
            return ruleName.hashCode() + "";
        }
    }
}
