package com.runbookagent.repository;

import com.runbookagent.model.Runbook;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface RunbookRepository extends JpaRepository<Runbook, UUID> {
}
