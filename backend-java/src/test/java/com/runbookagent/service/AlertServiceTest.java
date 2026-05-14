package com.runbookagent.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.doNothing;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.runbookagent.dto.AlertRequest;
import com.runbookagent.dto.AlertResponse;
import com.runbookagent.model.Alert;
import com.runbookagent.repository.AlertRepository;
import com.runbookagent.util.FingerprintUtil;
import java.util.LinkedHashMap;
import java.util.Map;
import org.junit.jupiter.api.Test;

class AlertServiceTest {

    @Test
    void createAlertComputesFingerprintFromRuleAndLabels() {
        AlertRepository repo = mock(AlertRepository.class);
        RedisStreamPublisher publisher = mock(RedisStreamPublisher.class);
        when(repo.save(any(Alert.class))).thenAnswer(inv -> inv.getArgument(0));
        doNothing().when(publisher).publishAlertCreated(anyString());

        AlertService service = new AlertService(repo, publisher, "http://localhost:8000");

        Map<String, String> labels = new LinkedHashMap<>();
        labels.put("service", "payment-api");
        labels.put("host", "db-01");
        AlertRequest req = new AlertRequest(
                "mysql_pool_exhausted", "database", "HIGH", "pool exhausted", labels);

        AlertResponse resp = service.createAlert(req);

        assertThat(resp.fingerprint())
                .isEqualTo(FingerprintUtil.compute("mysql_pool_exhausted", labels));
        assertThat(resp.labels()).containsEntry("service", "payment-api");
        assertThat(resp.status()).isEqualTo("PENDING");
        verify(publisher).publishAlertCreated(resp.id().toString());
    }

    @Test
    void createAlertTreatsNullLabelsAsEmpty() {
        AlertRepository repo = mock(AlertRepository.class);
        RedisStreamPublisher publisher = mock(RedisStreamPublisher.class);
        when(repo.save(any(Alert.class))).thenAnswer(inv -> inv.getArgument(0));
        doNothing().when(publisher).publishAlertCreated(anyString());

        AlertService service = new AlertService(repo, publisher, "http://localhost:8000");

        AlertResponse resp = service.createAlert(
                new AlertRequest("cpu_high_load", "compute", "HIGH", "spike", null));

        assertThat(resp.labels()).isEmpty();
        assertThat(resp.fingerprint())
                .isEqualTo(FingerprintUtil.compute("cpu_high_load", Map.of()));
    }
}
