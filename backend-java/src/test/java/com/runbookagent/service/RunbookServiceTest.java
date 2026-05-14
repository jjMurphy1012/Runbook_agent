package com.runbookagent.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.runbookagent.dto.RunbookResponse;
import com.runbookagent.model.Runbook;
import com.runbookagent.model.RunbookStatus;
import com.runbookagent.repository.RunbookRepository;
import jakarta.persistence.EntityManager;
import jakarta.persistence.Query;
import java.time.Instant;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

class RunbookServiceTest {

    @Test
    void approveRunbookFlipsStatusAndMarksHistoryHumanVerified() {
        RunbookRepository repo = mock(RunbookRepository.class);
        EntityManager em = mock(EntityManager.class);
        Query query = mock(Query.class);

        UUID rid = UUID.randomUUID();
        Runbook runbook = new Runbook();
        runbook.setId(rid);
        runbook.setTitle("MySQL pool exhausted");
        runbook.setStatus(RunbookStatus.DRAFT);
        runbook.setVersion(1);
        runbook.setUpdatedAt(Instant.now().minusSeconds(60));

        when(repo.findById(rid)).thenReturn(Optional.of(runbook));
        when(repo.save(any(Runbook.class))).thenAnswer(inv -> inv.getArgument(0));
        when(em.createNativeQuery(anyString())).thenReturn(query);
        when(query.setParameter(eq("rid"), any())).thenReturn(query);
        when(query.executeUpdate()).thenReturn(2);

        RunbookService service = new RunbookService(repo, em);

        RunbookResponse resp = service.approveRunbook(rid);

        assertThat(resp.status()).isEqualTo("APPROVED");
        assertThat(runbook.getStatus()).isEqualTo(RunbookStatus.APPROVED);
        verify(em).createNativeQuery(
                "UPDATE incident_history SET human_verified = true WHERE runbook_id = :rid");
        verify(query).setParameter("rid", rid);
        verify(query).executeUpdate();
    }
}
