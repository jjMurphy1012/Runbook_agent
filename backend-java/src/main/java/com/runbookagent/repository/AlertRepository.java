package com.runbookagent.repository;

import com.runbookagent.model.Alert;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AlertRepository extends JpaRepository<Alert, UUID> {
}
