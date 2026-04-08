package com.runbookagent.service;

import com.runbookagent.dto.RunbookResponse;
import com.runbookagent.model.Runbook;
import com.runbookagent.model.RunbookStatus;
import com.runbookagent.repository.RunbookRepository;
import jakarta.persistence.EntityManager;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class RunbookService {

    private final RunbookRepository runbookRepository;
    private final EntityManager entityManager;

    public RunbookService(RunbookRepository runbookRepository, EntityManager entityManager) {
        this.runbookRepository = runbookRepository;
        this.entityManager = entityManager;
    }

    public List<RunbookResponse> listRunbooks() {
        return runbookRepository.findAll().stream().map(this::toResponse).toList();
    }

    public RunbookResponse getRunbook(UUID id) {
        Runbook runbook = runbookRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Runbook not found"));
        return toResponse(runbook);
    }

    @Transactional
    public RunbookResponse approveRunbook(UUID id) {
        Runbook runbook = runbookRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Runbook not found"));
        runbook.setStatus(RunbookStatus.APPROVED);
        runbook.setUpdatedAt(Instant.now());
        runbookRepository.save(runbook);

        // Mark associated incident_history records as human-verified
        entityManager.createNativeQuery(
                        "UPDATE incident_history SET human_verified = true WHERE runbook_id = :rid")
                .setParameter("rid", id)
                .executeUpdate();

        return toResponse(runbook);
    }

    public RunbookResponse rejectRunbook(UUID id) {
        Runbook runbook = runbookRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Runbook not found"));
        runbook.setStatus(RunbookStatus.ARCHIVED);
        runbook.setUpdatedAt(Instant.now());
        runbookRepository.save(runbook);
        return toResponse(runbook);
    }

    private RunbookResponse toResponse(Runbook runbook) {
        return new RunbookResponse(
                runbook.getId(),
                runbook.getTitle(),
                runbook.getRootCause(),
                runbook.getVersion(),
                runbook.getStatus().name(),
                runbook.getContent(),
                runbook.getUpdatedAt()
        );
    }
}
